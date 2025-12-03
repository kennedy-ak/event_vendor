from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from vendors.models import Vendor


@login_required
def review_create_view(request, vendor_slug):
    """Create a review for a vendor"""
    vendor = get_object_or_404(Vendor, slug=vendor_slug, status='active')

    # Check if user has already reviewed this vendor
    existing_review = Review.objects.filter(vendor=vendor, user=request.user).first()
    if existing_review:
        messages.warning(request, 'You have already reviewed this vendor.')
        return redirect('vendor_detail', slug=vendor.slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.vendor = vendor
            review.user = request.user
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('vendor_detail', slug=vendor.slug)
    else:
        form = ReviewForm()

    return render(request, 'reviews/review_form.html', {
        'form': form,
        'vendor': vendor,
    })


@login_required
def review_update_view(request, review_id):
    """Update a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Review updated successfully!')
            return redirect('vendor_detail', slug=review.vendor.slug)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/review_form.html', {
        'form': form,
        'vendor': review.vendor,
        'is_update': True,
    })


@login_required
def review_delete_view(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    vendor_slug = review.vendor.slug

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Review deleted.')
        return redirect('vendor_detail', slug=vendor_slug)

    return render(request, 'reviews/review_confirm_delete.html', {
        'review': review,
    })
