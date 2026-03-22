from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
import json
import re

from .models import ChatConversation, ChatMessage, ChatRecommendation
from vendors.models import Vendor


def plan_my_event_view(request):
    """Dedicated page for event planning chatbot"""
    return render(request, 'chatbot/plan_my_event.html')


def _get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def _user_error(message, status=400):
    return JsonResponse({'success': False, 'error': message}, status=status)


@csrf_exempt
@require_POST
def chat_start(request):
    """Start a new chat conversation"""
    try:
        # Ensure session exists so session_key is not None
        if not request.session.session_key:
            request.session.create()

        conversation = ChatConversation.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key or '',
            ip_address=_get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )

        welcome_msg = (
            "Hi there! 👋 I'm your AI Event Planner for Events Exclusive Ghana. "
            "I'll help you find the perfect vendors for your event.\n\n"
            "What type of event are you planning? "
            "(e.g. wedding, birthday, corporate event, funeral, naming ceremony)"
        )

        ChatMessage.objects.create(
            conversation=conversation,
            role='assistant',
            content=welcome_msg,
        )

        return JsonResponse({
            'success': True,
            'conversation_code': conversation.conversation_code,
            'message': welcome_msg,
        })

    except Exception as e:
        print(f"[chat_start] error: {e}")
        return _user_error('Could not start a conversation. Please refresh and try again.', 500)


@csrf_exempt
@require_POST
def chat_message(request):
    """Send a message in an existing conversation"""
    try:
        data = json.loads(request.body)
        conversation_code = (data.get('conversation_code') or '').strip()
        user_message = (data.get('message') or '').strip()

        if not conversation_code:
            return _user_error('Missing conversation_code.')
        if not user_message:
            return _user_error('Message cannot be empty.')
        if len(user_message) > 1000:
            return _user_error('Message is too long (max 1000 characters).')

        conversation = get_object_or_404(ChatConversation, conversation_code=conversation_code)

        # Prevent messages to already-completed conversations (they have recommendations)
        # but still allow them — user may want to refine
        from .ai_service import EventPlannerAI
        try:
            ai = EventPlannerAI()
        except ValueError as e:
            return _user_error('AI service is not configured. Please contact support.', 503)

        ai_response = ai.chat(conversation, user_message)

        should_recommend = conversation.is_completed and not conversation.recommendations_sent

        return JsonResponse({
            'success': True,
            'message': ai_response,
            'is_completed': conversation.is_completed,
            'should_show_recommendations': should_recommend,
        })

    except json.JSONDecodeError:
        return _user_error('Invalid request format.')
    except Exception as e:
        print(f"[chat_message] error: {e}")
        return _user_error('Something went wrong. Please try again.', 500)


@require_GET
def chat_recommendations(request, conversation_code):
    """Get recommendations for a conversation"""
    try:
        conversation = get_object_or_404(ChatConversation, conversation_code=conversation_code)

        if conversation.is_completed and not conversation.recommendations_sent:
            from .ai_service import EventPlannerAI
            try:
                ai = EventPlannerAI()
                ai.generate_recommendations(conversation)
            except ValueError:
                pass  # AI not configured — still return any existing recs

        recommendations = (
            ChatRecommendation.objects.filter(conversation=conversation)
            .select_related('vendor', 'vendor__category')
            .order_by('-match_score')
        )

        recs_data = []
        for rec in recommendations:
            vendor = rec.vendor
            recs_data.append({
                'vendor_id': str(vendor.id),
                'vendor_name': vendor.name,
                'vendor_slug': vendor.slug,
                'category': vendor.category.name if vendor.category else '',
                'city': vendor.city or '',
                'neighborhood': vendor.neighborhood or '',
                'description': (vendor.description or '')[:200],
                'rating': float(vendor.rating or 0),
                'reviews_count': vendor.reviews_count or 0,
                'price_tier': vendor.price_tier or '',
                'phone': vendor.phone_number or '',
                'email': vendor.email or '',
                'primary_image': vendor.get_primary_image() if hasattr(vendor, 'get_primary_image') else '',
                'reason': rec.reason or '',
                'match_score': rec.match_score,
            })

        return JsonResponse({
            'success': True,
            'conversation_code': conversation_code,
            'event_type': conversation.event_type or '',
            'location': conversation.location or '',
            'recommendations': recs_data,
        })

    except Exception as e:
        print(f"[chat_recommendations] error: {e}")
        return _user_error('Could not load recommendations.', 500)


@csrf_exempt
@require_POST
def email_recommendations(request):
    """Email recommendations to user"""
    try:
        data = json.loads(request.body)
        conversation_code = (data.get('conversation_code') or '').strip()
        email = (data.get('email') or '').strip()

        if not conversation_code:
            return _user_error('Missing conversation_code.')
        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            return _user_error('Please enter a valid email address.')

        conversation = get_object_or_404(ChatConversation, conversation_code=conversation_code)

        from chatbot.emails import send_recommendations_email
        send_recommendations_email(conversation, email)

        return JsonResponse({
            'success': True,
            'message': f'Your vendor recommendations have been sent to {email}!',
        })

    except json.JSONDecodeError:
        return _user_error('Invalid request format.')
    except Exception as e:
        print(f"[email_recommendations] error: {e}")
        return _user_error('Could not send the email. Please try again.', 500)


@csrf_exempt
@require_POST
def track_recommendation_action(request):
    """Track user actions on recommendations (viewed / contacted / favorited)"""
    try:
        data = json.loads(request.body)
        conversation_code = (data.get('conversation_code') or '').strip()
        vendor_id = (data.get('vendor_id') or '').strip()
        action = (data.get('action') or '').strip()

        if not all([conversation_code, vendor_id, action]):
            return _user_error('Missing required fields.')
        if action not in ('viewed', 'contacted', 'favorited'):
            return _user_error('Invalid action.')

        conversation = get_object_or_404(ChatConversation, conversation_code=conversation_code)
        vendor = get_object_or_404(Vendor, id=vendor_id)

        rec, _ = ChatRecommendation.objects.get_or_create(
            conversation=conversation,
            vendor=vendor,
        )

        if action == 'viewed':
            rec.viewed = True
        elif action == 'contacted':
            rec.contacted = True
        elif action == 'favorited':
            rec.favorited = True
        rec.save(update_fields=[action])

        return JsonResponse({'success': True})

    except json.JSONDecodeError:
        return _user_error('Invalid request format.')
    except Exception as e:
        print(f"[track_recommendation_action] error: {e}")
        return _user_error('Could not track action.', 500)
