from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Ghana Events Marketplace.')

            # Redirect based on role
            if user.role == 'vendor':
                return redirect('vendor_create')
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')

            # Redirect to next parameter or home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def favorites_view(request):
    """View user's favorited vendors"""
    from vendors.models import Vendor

    favorite_ids = request.user.favorites or []
    vendors = Vendor.objects.filter(id__in=favorite_ids, status='active')

    return render(request, 'accounts/favorites.html', {'favorites': vendors})


@login_required
def toggle_favorite(request, vendor_id):
    """Toggle vendor in favorites"""
    from vendors.models import Vendor

    try:
        vendor = Vendor.objects.get(id=vendor_id)
        favorites = request.user.favorites or []

        vendor_id_str = str(vendor_id)
        if vendor_id_str in favorites:
            favorites.remove(vendor_id_str)
            messages.info(request, f'{vendor.name} removed from favorites.')
        else:
            favorites.append(vendor_id_str)
            messages.success(request, f'{vendor.name} added to favorites!')

        request.user.favorites = favorites
        request.user.save()
    except Vendor.DoesNotExist:
        messages.error(request, 'Vendor not found.')

    # Redirect back to the referring page
    return redirect(request.META.get('HTTP_REFERER', 'home'))
