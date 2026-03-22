from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Lead
from .forms import LeadForm, LeadStatusForm, LeadNotesForm
from vendors.models import Vendor
from vendors.emails import send_lead_notification_email, send_lead_confirmation_email


def lead_create_view(request, vendor_slug):
    """Create a lead/contact request for a vendor"""
    vendor = get_object_or_404(Vendor, slug=vendor_slug, status='active')

    # Determine lead source from query param (set by vendor detail page)
    source = request.GET.get('source', 'direct')
    if source not in dict(Lead.SOURCE_CHOICES):
        source = 'direct'

    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.vendor = vendor
            lead.source = request.POST.get('source', source)

            # Associate with user if logged in
            if request.user.is_authenticated:
                lead.user = request.user
                if not lead.name:
                    lead.name = request.user.get_full_name() or request.user.username
                if not lead.email:
                    lead.email = request.user.email
                if not lead.phone and hasattr(request.user, 'phone') and request.user.phone:
                    lead.phone = request.user.phone

            lead.save()

            # Notify vendor
            try:
                send_lead_notification_email(lead)
            except Exception as e:
                print(f"Failed to send lead notification email: {e}")

            # Confirm to requester
            try:
                send_lead_confirmation_email(lead)
            except Exception as e:
                print(f"Failed to send lead confirmation email: {e}")

            messages.success(request, f'Your request has been sent to {vendor.name}! Check your email for a confirmation.')
            return redirect('vendor_detail', slug=vendor.slug)
    else:
        initial = {'source': source}
        if request.user.is_authenticated:
            initial.update({
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'phone': getattr(request.user, 'phone', '') or '',
            })
        form = LeadForm(initial=initial)

    return render(request, 'leads/lead_form.html', {
        'form': form,
        'vendor': vendor,
        'source': source,
    })


@require_POST
def phone_reveal_view(request, vendor_slug):
    """
    AJAX: reveal vendor phone number and silently log a phone_reveal lead.
    Returns JSON with the phone number.
    """
    vendor = get_object_or_404(Vendor, slug=vendor_slug, status='active')

    # Create a minimal lead to record the phone reveal
    lead = Lead(
        vendor=vendor,
        source='phone_reveal',
        contact_method='phone',
        name='',
        phone='',
        email='',
    )

    if request.user.is_authenticated:
        lead.user = request.user
        lead.name = request.user.get_full_name() or request.user.username
        lead.email = request.user.email
        lead.phone = getattr(request.user, 'phone', '') or ''
    else:
        lead.name = 'Guest'

    lead.save()

    # Notify vendor of the phone reveal
    try:
        send_lead_notification_email(lead)
    except Exception:
        pass

    return JsonResponse({'phone': vendor.phone_number})


@login_required
def lead_update_status(request, lead_id):
    """Update lead status (vendor only)"""
    lead = get_object_or_404(Lead, id=lead_id)

    if lead.vendor.user != request.user:
        messages.error(request, 'You do not have permission to update this lead.')
        return redirect('vendor_dashboard')

    if request.method == 'POST':
        form = LeadStatusForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead status updated.')

    return redirect('lead_detail', lead_id=lead_id)


@login_required
def lead_add_notes(request, lead_id):
    """Add/update vendor internal notes on a lead"""
    lead = get_object_or_404(Lead, id=lead_id)

    if lead.vendor.user != request.user:
        messages.error(request, 'You do not have permission to update this lead.')
        return redirect('vendor_dashboard')

    if request.method == 'POST':
        form = LeadNotesForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notes saved.')

    return redirect('lead_detail', lead_id=lead_id)


@login_required
def lead_detail_view(request, lead_id):
    """View a single lead (vendor only)"""
    lead = get_object_or_404(Lead, id=lead_id)

    if lead.vendor.user != request.user:
        messages.error(request, 'You do not have permission to view this lead.')
        return redirect('vendor_dashboard')

    status_form = LeadStatusForm(instance=lead)
    notes_form = LeadNotesForm(instance=lead)

    return render(request, 'leads/lead_detail.html', {
        'lead': lead,
        'status_form': status_form,
        'notes_form': notes_form,
    })


@login_required
def leads_list_view(request):
    """View all leads for current user (vendors only)"""
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied.')
        return redirect('home')

    vendors = Vendor.objects.filter(user=request.user)
    leads = Lead.objects.filter(vendor__in=vendors).select_related('vendor').order_by('-created_at')

    # Filters
    status_filter = request.GET.get('status')
    vendor_filter = request.GET.get('vendor')

    if status_filter:
        leads = leads.filter(status=status_filter)
    if vendor_filter:
        leads = leads.filter(vendor__id=vendor_filter)

    return render(request, 'leads/leads_list.html', {
        'leads': leads,
        'vendors': vendors,
        'status_filter': status_filter,
        'vendor_filter': vendor_filter,
    })
