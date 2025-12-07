from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Lead
from .forms import LeadForm, LeadStatusForm
from vendors.models import Vendor
from vendors.emails import send_lead_notification_email


def lead_create_view(request, vendor_slug):
    """Create a lead/contact request for a vendor"""
    vendor = get_object_or_404(Vendor, slug=vendor_slug, status='active')

    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.vendor = vendor

            # Associate with user if logged in
            if request.user.is_authenticated:
                lead.user = request.user
                # Pre-fill user data if not provided
                if not lead.name:
                    lead.name = request.user.get_full_name() or request.user.username
                if not lead.email:
                    lead.email = request.user.email
                if not lead.phone and request.user.phone:
                    lead.phone = request.user.phone

            lead.save()

            # Send email notification to vendor
            try:
                send_lead_notification_email(lead)
            except Exception as e:
                # Log error but don't fail the request
                print(f"Failed to send lead notification email: {e}")

            messages.success(request, f'Your request has been sent to {vendor.name}!')

            return redirect('vendor_detail', slug=vendor.slug)
    else:
        # Pre-fill form with user data
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'phone': request.user.phone or '',
            }
        form = LeadForm(initial=initial)

    return render(request, 'leads/lead_form.html', {
        'form': form,
        'vendor': vendor,
    })


@login_required
def lead_update_status(request, lead_id):
    """Update lead status (vendor only)"""
    lead = get_object_or_404(Lead, id=lead_id)

    # Check if user owns the vendor
    if lead.vendor.user != request.user:
        messages.error(request, 'You do not have permission to update this lead.')
        return redirect('vendor_dashboard')

    if request.method == 'POST':
        form = LeadStatusForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lead status updated.')

    return redirect('vendor_dashboard')


@login_required
def leads_list_view(request):
    """View all leads for current user (vendors only)"""
    if request.user.role != 'vendor':
        messages.error(request, 'Access denied.')
        return redirect('home')

    # Get all vendor listings for this user
    from vendors.models import Vendor
    vendors = Vendor.objects.filter(user=request.user)

    # Get all leads for these vendors
    leads = Lead.objects.filter(vendor__in=vendors).order_by('-created_at')

    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        leads = leads.filter(status=status_filter)

    return render(request, 'leads/leads_list.html', {
        'leads': leads,
        'status_filter': status_filter,
    })
