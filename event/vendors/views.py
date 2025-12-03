from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from .models import Vendor
from .forms import VendorCreationForm, VendorUpdateForm, VendorSearchForm
from categories.models import Category
from reviews.models import Review
from leads.models import Lead


def home_view(request):
    """Homepage with category tiles and search"""
    categories = Category.objects.all()
    featured_vendors = Vendor.objects.filter(
        status='active',
        verified=True
    ).order_by('-rating', '-created_at')[:8]

    return render(request, 'home.html', {
        'categories': categories,
        'featured_vendors': featured_vendors,
    })


def vendor_list_view(request):
    """List view of vendors with search and filtering"""
    form = VendorSearchForm(request.GET or None)

    # Start with active and verified vendors
    vendors = Vendor.objects.filter(status='active', verified=True)

    # Apply filters
    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        city = form.cleaned_data.get('city')
        price_tier = form.cleaned_data.get('price_tier')
        min_rating = form.cleaned_data.get('min_rating')

        if q:
            vendors = vendors.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q) |
                Q(neighborhood__icontains=q) |
                Q(tags__icontains=q)
            )

        if category:
            vendors = vendors.filter(category__slug=category)

        if city:
            vendors = vendors.filter(city=city)

        if price_tier:
            vendors = vendors.filter(price_tier=price_tier)

        if min_rating:
            vendors = vendors.filter(rating__gte=float(min_rating))

    # Order by boosted, then rating
    vendors = vendors.order_by('-rating', '-created_at')

    # Pagination
    paginator = Paginator(vendors, settings.VENDORS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'vendors/vendor_list.html', {
        'form': form,
        'page_obj': page_obj,
        'total_count': vendors.count(),
    })


def vendor_detail_view(request, slug):
    """Detailed view of a single vendor"""
    vendor = get_object_or_404(Vendor, slug=slug, status='active')

    # Increment view count
    vendor.views_count += 1
    vendor.save(update_fields=['views_count'])

    # Get reviews
    reviews = Review.objects.filter(vendor=vendor, is_approved=True).order_by('-created_at')

    # Get similar vendors
    similar_vendors = Vendor.objects.filter(
        category=vendor.category,
        status='active',
        verified=True
    ).exclude(id=vendor.id).order_by('-rating')[:4]

    # Check if user has favorited
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = str(vendor.id) in (request.user.favorites or [])

    return render(request, 'vendors/vendor_detail.html', {
        'vendor': vendor,
        'reviews': reviews,
        'similar_vendors': similar_vendors,
        'is_favorited': is_favorited,
    })


@login_required
def vendor_create_view(request):
    """Create a new vendor listing"""
    # Check if user is a vendor
    if request.user.role != 'vendor':
        messages.error(request, 'Only vendors can create listings.')
        return redirect('home')

    if request.method == 'POST':
        form = VendorCreationForm(request.POST)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.status = 'pending'  # Awaiting admin approval
            vendor.save()
            messages.success(request, 'Your vendor listing has been submitted for review!')
            return redirect('vendor_dashboard')
    else:
        form = VendorCreationForm()

    return render(request, 'vendors/vendor_form.html', {
        'form': form,
        'title': 'Create Vendor Listing',
    })


@login_required
def vendor_update_view(request, slug):
    """Update vendor listing"""
    vendor = get_object_or_404(Vendor, slug=slug, user=request.user)

    if request.method == 'POST':
        form = VendorUpdateForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vendor listing updated successfully!')
            return redirect('vendor_detail', slug=vendor.slug)
    else:
        form = VendorUpdateForm(instance=vendor)

    return render(request, 'vendors/vendor_form.html', {
        'form': form,
        'title': 'Update Vendor Listing',
        'vendor': vendor,
    })


@login_required
def vendor_dashboard_view(request):
    """Vendor dashboard with stats and leads"""
    # Get vendor's listings
    vendors = Vendor.objects.filter(user=request.user)

    # Get leads for vendor's listings
    leads = Lead.objects.filter(vendor__in=vendors).order_by('-created_at')

    # Pagination for leads
    paginator = Paginator(leads, settings.LEADS_PER_PAGE)
    page_number = request.GET.get('page')
    leads_page = paginator.get_page(page_number)

    # Calculate stats
    total_views = sum(v.views_count for v in vendors)
    total_leads = sum(v.leads_count for v in vendors)
    pending_leads = leads.filter(status='new').count()

    return render(request, 'vendors/vendor_dashboard.html', {
        'vendors': vendors,
        'leads_page': leads_page,
        'total_views': total_views,
        'total_leads': total_leads,
        'pending_leads': pending_leads,
    })


def category_view(request, slug):
    """View vendors by category"""
    category = get_object_or_404(Category, slug=slug)
    vendors = Vendor.objects.filter(
        category=category,
        status='active',
        verified=True
    ).order_by('-rating', '-created_at')

    # Pagination
    paginator = Paginator(vendors, settings.VENDORS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'vendors/category_vendors.html', {
        'category': category,
        'page_obj': page_obj,
    })
