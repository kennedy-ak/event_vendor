from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Sum, Q, Avg, F
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from django.http import HttpResponse, Http404
from django.urls import reverse
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
import csv
from datetime import datetime, timedelta

from accounts.models import User
from vendors.models import Vendor
from billing.models import Subscription, Boost, SubscriptionPlan
from leads.models import Lead
from chatbot.models import ChatConversation, ChatMessage, ChatRecommendation

from .decorators import admin_required


# ============================================================================
# DASHBOARD
# ============================================================================

@admin_required
def dashboard_view(request):
    """Admin dashboard with statistics and recent activity"""
    # Get current date and 7 days ago
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)
    thirty_days_ago = today - timedelta(days=30)

    # Statistics
    total_users = User.objects.count()
    total_vendors = Vendor.objects.count()
    pending_vendors = Vendor.objects.filter(status='pending').count()
    total_leads = Lead.objects.count()

    active_subscriptions = Subscription.objects.filter(status='active').count()

    # Revenue calculations
    subscription_revenue = Subscription.objects.filter(status='active').aggregate(
        total=Sum('price')
    )['total'] or 0

    boost_revenue = Boost.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).aggregate(total=Sum('price'))['total'] or 0

    total_revenue = subscription_revenue + boost_revenue

    # Monthly revenue for the last 6 months
    monthly_revenue = []
    for i in range(6):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = (month_start.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        subs = Subscription.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end,
            status='active'
        ).aggregate(total=Sum('price'))['total'] or 0

        boosts = Boost.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        ).aggregate(total=Sum('price'))['total'] or 0

        monthly_revenue.append({
            'month': month_start.strftime('%b'),
            'revenue': float(subs + boosts)
        })

    monthly_revenue.reverse()

    # Recent activity (last 7 days)
    recent_vendors = Vendor.objects.filter(
        created_at__gte=seven_days_ago
    ).select_related('user', 'category').order_by('-created_at')[:5]

    recent_leads = Lead.objects.filter(
        created_at__gte=seven_days_ago
    ).select_related('vendor', 'vendor__category').order_by('-created_at')[:5]

    recent_subscriptions = Subscription.objects.filter(
        created_at__gte=seven_days_ago
    ).select_related('vendor', 'plan', 'vendor__user').order_by('-created_at')[:5]

    # Pending vendors count for sidebar
    pending_count = pending_vendors

    context = {
        'total_users': total_users,
        'total_vendors': total_vendors,
        'pending_vendors': pending_vendors,
        'total_leads': total_leads,
        'active_subscriptions': active_subscriptions,
        'total_revenue': total_revenue,
        'subscription_revenue': subscription_revenue,
        'boost_revenue': boost_revenue,
        'monthly_revenue': monthly_revenue,
        'recent_vendors': recent_vendors,
        'recent_leads': recent_leads,
        'recent_subscriptions': recent_subscriptions,
        'pending_count': pending_count,
        'page_title': 'Dashboard',
    }

    return render(request, 'admin_panel/dashboard.html', context)


# ============================================================================
# USER MANAGEMENT
# ============================================================================

@admin_required
def users_list_view(request):
    """List all users with filtering and pagination"""
    # Get filters
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    # Base queryset
    users = User.objects.all().order_by('-created_at')

    # Apply filters
    if role_filter:
        users = users.filter(role=role_filter)

    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)

    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(phone__icontains=search_query)
        )

    # Statistics
    stats = {
        'total': User.objects.count(),
        'admin': User.objects.filter(role='admin').count(),
        'vendor': User.objects.filter(role='vendor').count(),
        'user': User.objects.filter(role='user').count(),
    }

    # Pagination
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'search_query': search_query,
        'stats': stats,
        'page_title': 'Users',
    }

    return render(request, 'admin_panel/users/list.html', context)


@admin_required
def user_detail_view(request, user_id):
    """Display user details"""
    user = get_object_or_404(User, id=user_id)

    # Get related data
    vendors = user.vendors.all().select_related('category', 'subscription_plan')
    leads = user.leads.all().select_related('vendor', 'vendor__category')[:10]
    conversations = user.chat_conversations.all()[:5]

    context = {
        'user': user,
        'vendors': vendors,
        'leads': leads,
        'conversations': conversations,
        'page_title': f'User: {user.email}',
    }

    return render(request, 'admin_panel/users/detail.html', context)


@admin_required
def user_toggle_status_view(request, user_id):
    """Toggle user active status"""
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    user = get_object_or_404(User, id=user_id)

    # Don't allow deactivating yourself
    if user.id == request.user.id:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('admin_panel:user_detail', user_id=user_id)

    user.is_active = not user.is_active
    user.save()

    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.email} has been {status}.')

    return redirect('admin_panel:user_detail', user_id=user_id)


@admin_required
def user_change_role_view(request, user_id):
    """Change user role"""
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    user = get_object_or_404(User, id=user_id)
    new_role = request.POST.get('role')

    # Don't allow changing your own role
    if user.id == request.user.id:
        messages.error(request, 'You cannot change your own role.')
        return redirect('admin_panel:user_detail', user_id=user_id)

    if new_role in ['user', 'vendor', 'admin']:
        old_role = user.get_role_display()
        user.role = new_role
        user.save()
        messages.success(request, f'User role changed from {old_role} to {user.get_role_display()}.')
    else:
        messages.error(request, 'Invalid role selected.')

    return redirect('admin_panel:user_detail', user_id=user_id)


# ============================================================================
# VENDOR MANAGEMENT
# ============================================================================

@admin_required
def vendors_list_view(request):
    """List all vendors with filtering and pagination"""
    # Get filters
    status_filter = request.GET.get('status', '')
    verified_filter = request.GET.get('verified', '')
    category_filter = request.GET.get('category', '')
    city_filter = request.GET.get('city', '')
    search_query = request.GET.get('search', '')

    # Base queryset
    vendors = Vendor.objects.select_related(
        'user', 'category', 'subscription_plan'
    ).order_by('-created_at')

    # Apply filters
    if status_filter:
        vendors = vendors.filter(status=status_filter)

    if verified_filter == 'verified':
        vendors = vendors.filter(verified=True)
    elif verified_filter == 'unverified':
        vendors = vendors.filter(verified=False)

    if category_filter:
        vendors = vendors.filter(category_id=category_filter)

    if city_filter:
        vendors = vendors.filter(city__icontains=city_filter)

    if search_query:
        vendors = vendors.filter(
            Q(name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(vendors, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'verified_filter': verified_filter,
        'category_filter': category_filter,
        'city_filter': city_filter,
        'search_query': search_query,
        'page_title': 'Vendors',
    }

    return render(request, 'admin_panel/vendors/list.html', context)


@admin_required
def vendors_pending_view(request):
    """List pending vendors"""
    vendors = Vendor.objects.filter(
        status='pending'
    ).select_related('user', 'category').order_by('-created_at')

    # Pagination
    paginator = Paginator(vendors, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'page_title': 'Pending Vendors',
    }

    return render(request, 'admin_panel/vendors/pending.html', context)


@admin_required
def vendor_detail_view(request, vendor_id):
    """Display vendor details"""
    vendor = get_object_or_404(
        Vendor.objects.select_related('user', 'category', 'subscription_plan'),
        id=vendor_id
    )

    # Get vendor's leads and subscriptions
    recent_leads = vendor.leads.all().select_related('user').order_by('-created_at')[:10]
    subscriptions = vendor.subscriptions.all().select_related('plan').order_by('-created_at')
    boosts = vendor.boosts.all().order_by('-start_date')

    context = {
        'vendor': vendor,
        'recent_leads': recent_leads,
        'subscriptions': subscriptions,
        'boosts': boosts,
        'page_title': f'Vendor: {vendor.name}',
    }

    return render(request, 'admin_panel/vendors/detail.html', context)


@admin_required
def vendor_approve_view(request, vendor_id):
    """Approve a pending vendor"""
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    vendor = get_object_or_404(Vendor, id=vendor_id)

    if vendor.status != 'pending':
        messages.warning(request, 'This vendor is not pending approval.')
        return redirect('admin_panel:vendor_detail', vendor_id=vendor_id)

    vendor.status = 'active'
    vendor.verified = True
    vendor.save()

    messages.success(request, f'Vendor "{vendor.name}" has been approved and is now active.')

    return redirect('admin_panel:vendor_detail', vendor_id=vendor_id)


@admin_required
def vendor_suspend_view(request, vendor_id):
    """Suspend or reactivate a vendor"""
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    vendor = get_object_or_404(Vendor, id=vendor_id)

    if vendor.status == 'suspended':
        vendor.status = 'active'
        messages.success(request, f'Vendor "{vendor.name}" has been reactivated.')
    else:
        vendor.status = 'suspended'
        messages.success(request, f'Vendor "{vendor.name}" has been suspended.')

    vendor.save()

    return redirect('admin_panel:vendor_detail', vendor_id=vendor_id)


@admin_required
def vendor_verify_view(request, vendor_id):
    """Toggle vendor verification badge"""
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.verified = not vendor.verified
    vendor.save()

    status = 'verified' if vendor.verified else 'unverified'
    messages.success(request, f'Vendor "{vendor.name}" has been {status}.')

    return redirect('admin_panel:vendor_detail', vendor_id=vendor_id)


@admin_required
def vendor_edit_view(request, vendor_id):
    """Edit vendor information"""
    vendor = get_object_or_404(
        Vendor.objects.select_related('user', 'category', 'subscription_plan'),
        id=vendor_id
    )

    if request.method == 'POST':
        # Get form data
        vendor.name = request.POST.get('name')
        vendor.description = request.POST.get('description')
        vendor.address = request.POST.get('address')
        vendor.city = request.POST.get('city', 'Accra')
        vendor.neighborhood = request.POST.get('neighborhood', '')
        vendor.phone_number = request.POST.get('phone_number')
        vendor.email = request.POST.get('email')
        vendor.website = request.POST.get('website', '')
        vendor.price_tier = request.POST.get('price_tier', 'medium')
        vendor.estimated_price_range = request.POST.get('estimated_price_range', '')
        vendor.status = request.POST.get('status', 'pending')
        vendor.verified = request.POST.get('verified') == 'on'

        # Handle category change
        from categories.models import Category
        category_id = request.POST.get('category')
        if category_id:
            try:
                vendor.category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                pass

        # Handle subscription plan change
        plan_id = request.POST.get('subscription_plan')
        if plan_id:
            try:
                vendor.subscription_plan = SubscriptionPlan.objects.get(id=plan_id)
            except SubscriptionPlan.DoesNotExist:
                pass
        else:
            vendor.subscription_plan = None

        # Handle images
        import os
        import uuid
        from django.conf import settings

        # Get current images
        current_images = vendor.images.copy() if vendor.images else []

        # Remove images marked for deletion
        removed_images_json = request.POST.get('removed_images')
        if removed_images_json:
            import json
            try:
                removed_images = json.loads(removed_images_json)
                for img_url in removed_images:
                    if img_url in current_images:
                        current_images.remove(img_url)
                        # Try to delete the file from filesystem
                        try:
                            file_path = os.path.join(settings.MEDIA_ROOT, img_url.replace(settings.MEDIA_URL, ''))
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        except:
                            pass
            except json.JSONDecodeError:
                pass

        # Add new images
        new_images = request.FILES.getlist('images')
        if new_images:
            for image in new_images:
                # Generate unique filename
                ext = image.name.split('.')[-1]
                filename = f"{uuid.uuid4()}.{ext}"

                # Create vendor directory if it doesn't exist
                vendor_dir = os.path.join(settings.MEDIA_ROOT, 'vendors', str(vendor.id))
                os.makedirs(vendor_dir, exist_ok=True)

                # Save file
                file_path = os.path.join(vendor_dir, filename)
                with open(file_path, 'wb') as f:
                    for chunk in image.chunks():
                        f.write(chunk)

                # Add to images list
                image_url = f"{settings.MEDIA_URL}vendors/{vendor.id}/{filename}"
                current_images.append(image_url)

        # Update vendor images
        vendor.images = current_images

        vendor.save()
        messages.success(request, f'Vendor "{vendor.name}" has been updated successfully.')
        return redirect('admin_panel:vendor_detail', vendor_id=vendor_id)

    # Get categories and plans for dropdowns
    from categories.models import Category
    categories = Category.objects.all()
    plans = SubscriptionPlan.objects.all()

    context = {
        'vendor': vendor,
        'categories': categories,
        'plans': plans,
        'page_title': f'Edit Vendor: {vendor.name}',
    }

    return render(request, 'admin_panel/vendors/edit.html', context)


@admin_required
def vendor_delete_view(request, vendor_id):
    """Delete a vendor"""
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor_name = vendor.name

    # Delete vendor (this will cascade delete related data)
    vendor.delete()

    messages.success(request, f'Vendor "{vendor_name}" has been deleted successfully.')
    return redirect('admin_panel:vendors_list')


# ============================================================================
# BILLING & SUBSCRIPTIONS
# ============================================================================

@admin_required
def billing_overview_view(request):
    """Billing overview with revenue analytics"""
    # Get current date
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    # Revenue by source
    subscription_revenue = Subscription.objects.filter(status='active').aggregate(
        total=Sum('price')
    )['total'] or 0

    active_boosts = Boost.objects.filter(
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )

    boost_revenue = active_boosts.aggregate(total=Sum('price'))['total'] or 0

    total_revenue = subscription_revenue + boost_revenue

    # Monthly revenue (last 6 months)
    monthly_data = []
    for i in range(6):
        month_start = today.replace(day=1) - timedelta(days=30*i)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        subs = Subscription.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        ).aggregate(count=Count('id'), total=Sum('price'))

        boosts = Boost.objects.filter(
            created_at__gte=month_start,
            created_at__lte=month_end
        ).aggregate(count=Count('id'), total=Sum('price'))

        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'subscription_count': subs['count'] or 0,
            'subscription_revenue': float(subs['total'] or 0),
            'boost_count': boosts['count'] or 0,
            'boost_revenue': float(boosts['total'] or 0),
        })

    # Active subscriptions by plan
    subscriptions_by_plan = SubscriptionPlan.objects.filter(
        is_active=True
    ).annotate(
        active_count=Count('subscriptions', filter=Q(subscriptions__status='active'))
    )

    # Active boosts
    active_boosts_list = active_boosts.select_related('vendor').order_by('-start_date')[:10]

    context = {
        'total_revenue': total_revenue,
        'subscription_revenue': subscription_revenue,
        'boost_revenue': boost_revenue,
        'monthly_data': monthly_data,
        'subscriptions_by_plan': subscriptions_by_plan,
        'active_boosts': active_boosts_list,
        'page_title': 'Billing Overview',
    }

    return render(request, 'admin_panel/billing/overview.html', context)


@admin_required
def subscriptions_list_view(request):
    """List all subscriptions"""
    # Get filters
    status_filter = request.GET.get('status', '')
    plan_filter = request.GET.get('plan', '')

    # Base queryset
    subscriptions = Subscription.objects.select_related(
        'vendor', 'plan', 'vendor__user'
    ).order_by('-created_at')

    # Apply filters
    if status_filter:
        subscriptions = subscriptions.filter(status=status_filter)

    if plan_filter:
        subscriptions = subscriptions.filter(plan_id=plan_filter)

    # Pagination
    paginator = Paginator(subscriptions, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'plan_filter': plan_filter,
        'page_title': 'Subscriptions',
    }

    return render(request, 'admin_panel/billing/subscriptions.html', context)


@admin_required
def boosts_list_view(request):
    """List all boosts"""
    # Get filters
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('type', '')

    # Base queryset
    boosts = Boost.objects.select_related('vendor').order_by('-created_at')

    # Apply filters
    if status_filter == 'active':
        boosts = boosts.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        )
    elif status_filter == 'expired':
        boosts = boosts.filter(
            Q(is_active=False) | Q(end_date__lt=timezone.now())
        )

    if type_filter:
        boosts = boosts.filter(type=type_filter)

    # Pagination
    paginator = Paginator(boosts, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'page_title': 'Featured Boosts',
    }

    return render(request, 'admin_panel/billing/boosts.html', context)


# ============================================================================
# LEADS MANAGEMENT
# ============================================================================

@admin_required
def leads_list_view(request):
    """List all leads with filtering and pagination"""
    # Get filters
    status_filter = request.GET.get('status', '')
    billed_filter = request.GET.get('billed', '')
    vendor_filter = request.GET.get('vendor', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # Base queryset
    leads = Lead.objects.select_related(
        'vendor', 'user', 'vendor__category'
    ).order_by('-created_at')

    # Apply filters
    if status_filter:
        leads = leads.filter(status=status_filter)

    if billed_filter == 'billed':
        leads = leads.filter(billed=True)
    elif billed_filter == 'unbilled':
        leads = leads.filter(billed=False)

    if vendor_filter:
        leads = leads.filter(vendor_id=vendor_filter)

    if date_from:
        date_from_obj = parse_date(date_from)
        if date_from_obj:
            leads = leads.filter(created_at__date__gte=date_from_obj)

    if date_to:
        date_to_obj = parse_date(date_to)
        if date_to_obj:
            leads = leads.filter(created_at__date__lte=date_to_obj)

    # Pagination
    paginator = Paginator(leads, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'billed_filter': billed_filter,
        'vendor_filter': vendor_filter,
        'date_from': date_from,
        'date_to': date_to,
        'page_title': 'Leads',
    }

    return render(request, 'admin_panel/leads/list.html', context)


@admin_required
def leads_analytics_view(request):
    """Leads analytics and statistics"""
    # Get current date
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)

    # Leads by status
    leads_by_status = Lead.objects.values('status').annotate(
        count=Count('id')
    )

    # Leads by vendor (top 10)
    top_vendors = Vendor.objects.annotate(
        leads_count=Count('leads')
    ).order_by('-leads_count')[:10]

    # Conversion rate
    total_leads = Lead.objects.count()
    closed_leads = Lead.objects.filter(status='closed').count()
    conversion_rate = (closed_leads / total_leads * 100) if total_leads > 0 else 0

    # Billed vs unbilled
    billed_count = Lead.objects.filter(billed=True).count()
    unbilled_count = total_leads - billed_count

    # Leads over time (last 30 days)
    leads_over_time = []
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        count = Lead.objects.filter(created_at__date=date).count()
        leads_over_time.append({
            'date': date.strftime('%b %d'),
            'count': count
        })

    context = {
        'leads_by_status': leads_by_status,
        'top_vendors': top_vendors,
        'total_leads': total_leads,
        'closed_leads': closed_leads,
        'conversion_rate': round(conversion_rate, 1),
        'billed_count': billed_count,
        'unbilled_count': unbilled_count,
        'leads_over_time': leads_over_time,
        'page_title': 'Leads Analytics',
    }

    return render(request, 'admin_panel/leads/analytics.html', context)


@admin_required
def leads_export_view(request):
    """Export all leads to CSV"""
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="leads_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Email', 'Phone', 'Vendor', 'Category', 'Status',
        'Event Date', 'Message', 'Billed', 'Created At'
    ])

    leads = Lead.objects.select_related('vendor', 'vendor__category').order_by('-created_at')

    for lead in leads:
        writer.writerow([
            lead.name,
            lead.email or '',
            lead.phone or '',
            lead.vendor.name,
            lead.vendor.category.name if lead.vendor.category else '',
            lead.get_status_display(),
            lead.event_date or '',
            lead.message or '',
            'Yes' if lead.billed else 'No',
            lead.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    return response


@admin_required
def lead_mark_billed_view(request, lead_id):
    """Mark a lead as billed"""
    if request.method != 'POST':
        return HttpResponse('Method not allowed', status=405)

    lead = get_object_or_404(Lead, id=lead_id)
    lead.billed = True
    lead.save()

    messages.success(request, f'Lead from {lead.name} has been marked as billed.')

    return redirect('admin_panel:leads_list')


# ============================================================================
# CHATBOT MONITORING
# ============================================================================

@admin_required
def chatbot_conversations_view(request):
    """List all chatbot conversations"""
    # Get filters
    status_filter = request.GET.get('status', '')
    event_type_filter = request.GET.get('event_type', '')

    # Base queryset
    conversations = ChatConversation.objects.select_related('user').order_by('-created_at')

    # Apply filters
    if status_filter == 'completed':
        conversations = conversations.filter(is_completed=True)
    elif status_filter == 'incomplete':
        conversations = conversations.filter(is_completed=False)

    if event_type_filter:
        conversations = conversations.filter(event_type__icontains=event_type_filter)

    # Statistics
    stats = {
        'total': ChatConversation.objects.count(),
        'completed': ChatConversation.objects.filter(is_completed=True).count(),
        'recommendations_sent': ChatConversation.objects.filter(recommendations_sent=True).count(),
    }

    # Pagination
    paginator = Paginator(conversations, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'event_type_filter': event_type_filter,
        'stats': stats,
        'page_title': 'Chatbot Conversations',
    }

    return render(request, 'admin_panel/chatbot/list.html', context)


@admin_required
def chatbot_detail_view(request, conversation_id):
    """Display chatbot conversation details"""
    conversation = get_object_or_404(
        ChatConversation.objects.prefetch_related('messages', 'recommendations__vendor'),
        id=conversation_id
    )

    messages = conversation.messages.all()
    recommendations = conversation.recommendations.select_related('vendor').order_by('-match_score')

    context = {
        'conversation': conversation,
        'messages': messages,
        'recommendations': recommendations,
        'page_title': f'Conversation {conversation.conversation_code}',
    }

    return render(request, 'admin_panel/chatbot/detail.html', context)
