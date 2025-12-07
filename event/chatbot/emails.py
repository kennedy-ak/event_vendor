"""Email functions for chatbot"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_recommendations_email(conversation, recipient_email):
    """Send vendor recommendations via email"""

    # Get recommendations
    recommendations = conversation.recommendations.all().select_related('vendor', 'vendor__category')

    # Prepare context
    context = {
        'conversation': conversation,
        'recommendations': recommendations,
        'site_url': settings.SITE_URL,
    }

    # Render email
    subject = f'Your Event Vendor Recommendations - {conversation.event_type}'
    html_message = render_to_string('chatbot/emails/recommendations.html', context)
    plain_message = f"""
Hi!

Here are your personalized vendor recommendations for your {conversation.event_type}:

"""

    for rec in recommendations:
        plain_message += f"\n{rec.vendor.name} - {rec.vendor.category.name}\n{rec.reason}\n{settings.SITE_URL}/vendors/{rec.vendor.slug}/\n"

    plain_message += f"\n\nView all recommendations online:\n{settings.SITE_URL}/chatbot/plan-my-event/?code={conversation.conversation_code}\n\nBest regards,\nGhana Events Marketplace Team"

    # Send email
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[recipient_email],
        html_message=html_message,
        fail_silently=False,
    )
