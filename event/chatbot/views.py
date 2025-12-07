from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json

from .models import ChatConversation, ChatMessage, ChatRecommendation
from .ai_service import EventPlannerAI
from vendors.models import Vendor


def plan_my_event_view(request):
    """Dedicated page for event planning chatbot"""
    return render(request, 'chatbot/plan_my_event.html')


@csrf_exempt
@require_POST
def chat_start(request):
    """Start a new chat conversation"""
    try:
        # Create new conversation
        conversation = ChatConversation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key or '',
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )

        # Generate welcome message
        ai = EventPlannerAI()
        welcome_msg = "Hi there! 👋 I'm your AI Event Planner. I'm here to help you find the perfect vendors for your event in Accra! What type of event are you planning? (e.g., wedding, birthday party, corporate event)"

        ChatMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=welcome_msg
        )

        return JsonResponse({
            'success': True,
            'conversation_code': conversation.conversation_code,
            'message': welcome_msg
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_POST
def chat_message(request):
    """Send a message in an existing conversation"""
    try:
        data = json.loads(request.body)
        conversation_code = data.get('conversation_code')
        user_message = data.get('message', '').strip()

        if not conversation_code or not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Missing conversation_code or message'
            }, status=400)

        # Get conversation
        conversation = get_object_or_404(ChatConversation, conversation_code=conversation_code)

        # Process message with AI
        ai = EventPlannerAI()
        ai_response = ai.chat(conversation, user_message)

        # Check if we should generate recommendations
        should_recommend = conversation.is_completed and not conversation.recommendations_sent

        return JsonResponse({
            'success': True,
            'message': ai_response,
            'is_completed': conversation.is_completed,
            'should_show_recommendations': should_recommend
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_GET
def chat_recommendations(request, conversation_code):
    """Get recommendations for a conversation"""
    try:
        conversation = get_object_or_404(ChatConversation, conversation_code=conversation_code)

        # Generate recommendations if not already done
        if conversation.is_completed and not conversation.recommendations_sent:
            ai = EventPlannerAI()
            ai.generate_recommendations(conversation)

        # Get recommendations
        recommendations = ChatRecommendation.objects.filter(
            conversation=conversation
        ).select_related('vendor', 'vendor__category').order_by('-match_score')

        # Format response
        recs_data = []
        for rec in recommendations:
            vendor = rec.vendor
            recs_data.append({
                'vendor_id': str(vendor.id),
                'vendor_name': vendor.name,
                'vendor_slug': vendor.slug,
                'category': vendor.category.name,
                'description': vendor.description[:200],
                'rating': float(vendor.rating),
                'reviews_count': vendor.reviews_count,
                'price_tier': vendor.price_tier,
                'phone': vendor.phone_number,
                'email': vendor.email,
                'primary_image': vendor.get_primary_image(),
                'reason': rec.reason,
                'match_score': rec.match_score,
            })

        return JsonResponse({
            'success': True,
            'conversation_code': conversation_code,
            'event_type': conversation.event_type,
            'recommendations': recs_data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_POST
def email_recommendations(request):
    """Email recommendations to user"""
    try:
        data = json.loads(request.body)
        conversation_code = data.get('conversation_code')
        email = data.get('email')

        if not conversation_code or not email:
            return JsonResponse({
                'success': False,
                'error': 'Missing conversation_code or email'
            }, status=400)

        conversation = get_object_or_404(ChatConversation, conversation_code=conversation_code)

        # Send email (we'll implement this)
        from chatbot.emails import send_recommendations_email
        send_recommendations_email(conversation, email)

        return JsonResponse({
            'success': True,
            'message': 'Recommendations sent to your email!'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_POST
def track_recommendation_action(request):
    """Track user actions on recommendations"""
    try:
        data = json.loads(request.body)
        conversation_code = data.get('conversation_code')
        vendor_id = data.get('vendor_id')
        action = data.get('action')  # 'viewed', 'contacted', 'favorited'

        if not all([conversation_code, vendor_id, action]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields'
            }, status=400)

        conversation = get_object_or_404(ChatConversation, conversation_code=conversation_code)
        vendor = get_object_or_404(Vendor, id=vendor_id)

        # Get or create recommendation
        rec, created = ChatRecommendation.objects.get_or_create(
            conversation=conversation,
            vendor=vendor
        )

        # Track action
        if action == 'viewed':
            rec.viewed = True
        elif action == 'contacted':
            rec.contacted = True
        elif action == 'favorited':
            rec.favorited = True

        rec.save()

        return JsonResponse({
            'success': True,
            'message': f'Action "{action}" tracked'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
