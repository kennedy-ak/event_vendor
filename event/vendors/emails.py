"""
Email notification utilities for the Ghana Events Marketplace
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_welcome_email(user):
    """Send welcome email to new user"""
    subject = f'Welcome to {settings.SITE_NAME}!'

    html_message = render_to_string('emails/welcome.html', {
        'user': user,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_vendor_pending_approval_email(vendor):
    """Notify vendor their listing is pending approval"""
    subject = 'Your vendor listing is under review'

    html_message = render_to_string('emails/vendor_pending.html', {
        'vendor': vendor,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_vendor_approved_email(vendor):
    """Notify vendor their listing has been approved"""
    subject = 'Your vendor listing has been approved!'

    html_message = render_to_string('emails/vendor_approved.html', {
        'vendor': vendor,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
        'vendor_url': f"{settings.SITE_URL}/vendors/{vendor.slug}/",
    })
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_lead_notification_email(lead):
    """Notify vendor of new lead"""
    vendor = lead.vendor
    subject = f'New lead for {vendor.name}'

    html_message = render_to_string('emails/new_lead.html', {
        'lead': lead,
        'vendor': vendor,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
        'dashboard_url': f"{settings.SITE_URL}/vendors/dashboard/",
    })
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_lead_confirmation_email(lead):
    """Send confirmation to the person who submitted the lead"""
    if not lead.email:
        return

    vendor = lead.vendor
    subject = f'Your enquiry to {vendor.name} has been sent'

    html_message = render_to_string('emails/lead_confirmation.html', {
        'lead': lead,
        'vendor': vendor,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
        'vendor_url': f"{settings.SITE_URL}/vendors/{vendor.slug}/",
    })
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[lead.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_subscription_confirmation_email(subscription):
    """Send subscription confirmation email"""
    vendor = subscription.vendor
    subject = f'Subscription Confirmed - {subscription.plan.display_name}'

    html_message = render_to_string('emails/subscription_confirmed.html', {
        'subscription': subscription,
        'vendor': vendor,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_subscription_renewal_reminder(subscription):
    """Send subscription renewal reminder"""
    vendor = subscription.vendor
    subject = f'Subscription Renewal Reminder - {subscription.plan.display_name}'

    html_message = render_to_string('emails/subscription_reminder.html', {
        'subscription': subscription,
        'vendor': vendor,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_boost_activation_email(boost):
    """Notify vendor their boost has been activated"""
    vendor = boost.vendor
    subject = f'Featured Listing Activated - {boost.get_type_display()}'

    html_message = render_to_string('emails/boost_activated.html', {
        'boost': boost,
        'vendor': vendor,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
    })
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor.email],
        html_message=html_message,
        fail_silently=True,
    )


def send_review_notification_email(review):
    """Notify vendor of new review"""
    vendor = review.vendor
    subject = f'New review for {vendor.name}'

    html_message = render_to_string('emails/new_review.html', {
        'review': review,
        'vendor': vendor,
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
        'vendor_url': f"{settings.SITE_URL}/vendors/{vendor.slug}/",
    })
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[vendor.email],
        html_message=html_message,
        fail_silently=True,
    )
