from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import timedelta
import json
import hmac
import hashlib

try:
    from pypaystack2 import Paystack
    PAYSTACK_AVAILABLE = True
except ImportError:
    PAYSTACK_AVAILABLE = False

from .models import SubscriptionPlan, Subscription, Boost
from vendors.models import Vendor
from vendors.emails import send_subscription_confirmation_email, send_boost_activation_email


# Initialize Paystack
if PAYSTACK_AVAILABLE and settings.PAYSTACK_SECRET_KEY:
    paystack = Paystack(secret_key=settings.PAYSTACK_SECRET_KEY)
else:
    paystack = None


@login_required
def subscription_plans_view(request):
    """Display available subscription plans"""
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')

    # Get user's vendors
    user_vendors = Vendor.objects.filter(user=request.user)

    # Get current subscriptions for user's vendors
    current_subscriptions = {}
    for vendor in user_vendors:
        active_sub = Subscription.objects.filter(
            vendor=vendor,
            status='active'
        ).first()
        if active_sub:
            current_subscriptions[vendor.id] = active_sub

    return render(request, 'billing/subscription_plans.html', {
        'plans': plans,
        'user_vendors': user_vendors,
        'current_subscriptions': current_subscriptions,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
    })


@login_required
def subscribe_view(request, plan_id):
    """Initiate subscription payment"""
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)

    # Get vendor (user must select which vendor to subscribe)
    vendor_id = request.GET.get('vendor_id')
    if not vendor_id:
        messages.error(request, 'Please select a vendor to subscribe.')
        return redirect('subscription_plans')

    vendor = get_object_or_404(Vendor, id=vendor_id, user=request.user)

    # Check for existing active subscription
    existing_sub = Subscription.objects.filter(
        vendor=vendor,
        status='active'
    ).first()

    if request.method == 'POST':
        # Create pending subscription
        subscription = Subscription.objects.create(
            vendor=vendor,
            plan=plan,
            price=plan.price,
            currency=plan.currency,
            start_date=timezone.now(),
            renewal_date=timezone.now() + timedelta(days=30),
            status='pending',
            payment_method='paystack'
        )

        # Prepare Paystack payment
        if not paystack:
            messages.error(request, 'Payment gateway not configured. Please contact support.')
            return redirect('subscription_plans')

        try:
            # Convert price to kobo (Ghanaian pesewas for GHS)
            amount_in_pesewas = int(plan.price * 100)

            # Initialize transaction
            response = paystack.transaction.initialize(
                email=request.user.email,
                amount=amount_in_pesewas,
                currency=plan.currency,
                callback_url=f"{settings.SITE_URL}/billing/verify-subscription/{subscription.id}/",
                metadata={
                    'subscription_id': str(subscription.id),
                    'vendor_id': str(vendor.id),
                    'plan_id': str(plan.id),
                    'user_id': str(request.user.id),
                }
            )

            if response['status']:
                # Save transaction reference
                subscription.transaction_id = response['data']['reference']
                subscription.save()

                # Redirect to Paystack payment page
                return redirect(response['data']['authorization_url'])
            else:
                messages.error(request, 'Failed to initialize payment. Please try again.')
                subscription.delete()
                return redirect('subscription_plans')

        except Exception as e:
            messages.error(request, f'Payment error: {str(e)}')
            subscription.delete()
            return redirect('subscription_plans')

    return render(request, 'billing/subscribe_confirm.html', {
        'plan': plan,
        'vendor': vendor,
        'existing_sub': existing_sub,
    })


@login_required
def verify_subscription_payment(request, subscription_id):
    """Verify Paystack subscription payment"""
    subscription = get_object_or_404(Subscription, id=subscription_id)

    # Verify the transaction
    if not paystack:
        messages.error(request, 'Payment gateway not configured.')
        return redirect('vendor_dashboard')

    try:
        reference = request.GET.get('reference') or subscription.transaction_id
        response = paystack.transaction.verify(reference=reference)

        if response['status'] and response['data']['status'] == 'success':
            # Update subscription status
            subscription.status = 'active'
            subscription.transaction_id = reference
            subscription.save()

            # Update vendor's subscription plan
            vendor = subscription.vendor
            vendor.subscription_plan = subscription.plan
            vendor.save()

            # Send confirmation email
            try:
                send_subscription_confirmation_email(subscription)
            except Exception as e:
                print(f"Failed to send subscription confirmation email: {e}")

            messages.success(request, f'Subscription activated successfully! You are now on the {subscription.plan.display_name} plan.')
            return redirect('vendor_dashboard')
        else:
            subscription.status = 'expired'
            subscription.save()
            messages.error(request, 'Payment verification failed. Please try again.')
            return redirect('subscription_plans')

    except Exception as e:
        messages.error(request, f'Payment verification error: {str(e)}')
        return redirect('subscription_plans')


@login_required
def purchase_boost_view(request):
    """Purchase featured listing boost"""
    vendor_id = request.GET.get('vendor_id')
    if not vendor_id:
        messages.error(request, 'Please select a vendor.')
        return redirect('vendor_dashboard')

    vendor = get_object_or_404(Vendor, id=vendor_id, user=request.user)

    # Boost pricing
    BOOST_PRICES = {
        'featured': 50.00,  # GHS 50 for 7 days
        'banner': 100.00,   # GHS 100 for 7 days
        'top': 150.00,      # GHS 150 for 7 days
    }

    if request.method == 'POST':
        boost_type = request.POST.get('boost_type', 'featured')
        duration_days = int(request.POST.get('duration_days', 7))

        price = BOOST_PRICES.get(boost_type, 50.00) * (duration_days / 7)

        # Create pending boost
        boost = Boost.objects.create(
            vendor=vendor,
            type=boost_type,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=duration_days),
            price=price,
            currency='GHS',
            is_active=False  # Will be activated after payment
        )

        # Initialize Paystack payment
        if not paystack:
            messages.error(request, 'Payment gateway not configured.')
            return redirect('vendor_dashboard')

        try:
            amount_in_pesewas = int(price * 100)

            response = paystack.transaction.initialize(
                email=request.user.email,
                amount=amount_in_pesewas,
                currency='GHS',
                callback_url=f"{settings.SITE_URL}/billing/verify-boost/{boost.id}/",
                metadata={
                    'boost_id': str(boost.id),
                    'vendor_id': str(vendor.id),
                    'user_id': str(request.user.id),
                }
            )

            if response['status']:
                boost.transaction_id = response['data']['reference']
                boost.save()
                return redirect(response['data']['authorization_url'])
            else:
                messages.error(request, 'Failed to initialize payment.')
                boost.delete()
                return redirect('vendor_dashboard')

        except Exception as e:
            messages.error(request, f'Payment error: {str(e)}')
            boost.delete()
            return redirect('vendor_dashboard')

    return render(request, 'billing/purchase_boost.html', {
        'vendor': vendor,
        'boost_prices': BOOST_PRICES,
        'paystack_public_key': settings.PAYSTACK_PUBLIC_KEY,
    })


@login_required
def verify_boost_payment(request, boost_id):
    """Verify Paystack boost payment"""
    boost = get_object_or_404(Boost, id=boost_id)

    if not paystack:
        messages.error(request, 'Payment gateway not configured.')
        return redirect('vendor_dashboard')

    try:
        reference = request.GET.get('reference') or boost.transaction_id
        response = paystack.transaction.verify(reference=reference)

        if response['status'] and response['data']['status'] == 'success':
            # Activate boost
            boost.is_active = True
            boost.transaction_id = reference
            boost.save()

            # Send activation email
            try:
                send_boost_activation_email(boost)
            except Exception as e:
                print(f"Failed to send boost activation email: {e}")

            messages.success(request, f'Featured listing activated! Your {boost.get_type_display()} is now live.')
            return redirect('vendor_dashboard')
        else:
            boost.delete()
            messages.error(request, 'Payment verification failed.')
            return redirect('vendor_dashboard')

    except Exception as e:
        messages.error(request, f'Payment verification error: {str(e)}')
        return redirect('vendor_dashboard')


@csrf_exempt
@require_POST
def paystack_webhook(request):
    """Handle Paystack webhook notifications"""
    # Verify webhook signature
    paystack_signature = request.headers.get('X-Paystack-Signature')

    if not paystack_signature:
        return HttpResponse(status=400)

    # Compute HMAC
    computed_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        request.body,
        hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(computed_signature, paystack_signature):
        return HttpResponse('Invalid signature', status=400)

    # Process webhook event
    try:
        payload = json.loads(request.body)
        event = payload.get('event')
        data = payload.get('data', {})

        if event == 'charge.success':
            # Handle successful charge
            reference = data.get('reference')
            metadata = data.get('metadata', {})

            # Check if it's a subscription payment
            if 'subscription_id' in metadata:
                try:
                    subscription = Subscription.objects.get(id=metadata['subscription_id'])
                    subscription.status = 'active'
                    subscription.transaction_id = reference
                    subscription.save()

                    # Update vendor's plan
                    vendor = subscription.vendor
                    vendor.subscription_plan = subscription.plan
                    vendor.save()
                except Subscription.DoesNotExist:
                    pass

            # Check if it's a boost payment
            elif 'boost_id' in metadata:
                try:
                    boost = Boost.objects.get(id=metadata['boost_id'])
                    boost.is_active = True
                    boost.transaction_id = reference
                    boost.save()
                except Boost.DoesNotExist:
                    pass

        return HttpResponse(status=200)

    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)


@login_required
def cancel_subscription_view(request, subscription_id):
    """Cancel a subscription"""
    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        vendor__user=request.user
    )

    if request.method == 'POST':
        subscription.status = 'cancelled'
        subscription.cancelled_at = timezone.now()
        subscription.auto_renew = False
        subscription.save()

        messages.success(request, 'Subscription cancelled successfully.')
        return redirect('vendor_dashboard')

    return render(request, 'billing/cancel_subscription.html', {
        'subscription': subscription,
    })
