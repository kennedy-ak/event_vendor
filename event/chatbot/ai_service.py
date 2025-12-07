"""
AI Service for Event Planner Chatbot using OpenAI
"""
import json
import openai
from django.conf import settings
from vendors.models import Vendor
from categories.models import Category
from .models import ChatConversation, ChatMessage, ChatRecommendation


class EventPlannerAI:
    """AI-powered event planner chatbot"""

    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = "gpt-4-turbo-preview"  # or "gpt-3.5-turbo" for lower cost

    def get_system_prompt(self):
        """System prompt to guide the AI's behavior"""
        return """You are an expert event planner assistant for Ghana Events Marketplace in Accra, Ghana.
Your goal is to help users plan their events by asking questions and understanding their needs.

CONVERSATION FLOW:
1. Greet warmly and ask what type of event they're planning
2. Ask about the event date
3. Ask about their budget range (in Ghanaian Cedis - GHS)
4. Ask about preferred location/neighborhood in Accra
5. Ask about number of expected guests
6. Ask what vendors they need (venue, catering, photography, DJ, etc.)
7. Ask about any special requirements (theme, dietary restrictions, outdoor/indoor, etc.)

GUIDELINES:
- Be friendly, professional, and enthusiastic
- Ask ONE question at a time
- Use Ghanaian context (GHS currency, Accra neighborhoods)
- Keep responses concise (2-3 sentences max)
- After collecting all information, summarize and say you're preparing recommendations
- Use emojis sparingly for warmth

AVAILABLE VENDOR CATEGORIES:
- Venues
- Catering
- Photographers (Photography & Videography)
- DJs (DJ & Entertainment)
- Fashion Designers
- Fabrics
- Favours (Party Favours)
- Drinks
- Event Planners

When you have all the information, respond with: "Perfect! I have everything I need. Let me find the best vendors for your [event_type]! 🎉"
"""

    def chat(self, conversation, user_message):
        """
        Process user message and generate AI response

        Args:
            conversation: ChatConversation instance
            user_message: User's message text

        Returns:
            AI response text
        """
        # Save user message
        ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=user_message
        )

        # Get conversation history
        messages = self._build_message_history(conversation)

        try:
            # Call OpenAI API
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=300,
            )

            # Extract response
            ai_message = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Save AI response
            ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=ai_message,
                token_count=tokens_used
            )

            # Extract structured data from conversation
            self._extract_event_data(conversation)

            # Check if conversation is complete
            if self._is_conversation_complete(conversation):
                conversation.is_completed = True
                conversation.save()

            return ai_message

        except Exception as e:
            error_message = f"I'm having trouble right now. Please try again. Error: {str(e)}"
            ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=error_message
            )
            return error_message

    def _build_message_history(self, conversation):
        """Build message history for OpenAI API"""
        messages = [
            {"role": "system", "content": self.get_system_prompt()}
        ]

        # Add all previous messages
        for msg in conversation.messages.all():
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        return messages

    def _extract_event_data(self, conversation):
        """
        Use AI to extract structured data from conversation
        This runs after each message to keep data updated
        """
        messages = self._build_message_history(conversation)

        # Ask AI to extract structured information
        extraction_prompt = """Based on the conversation so far, extract the following information in JSON format:
{
  "event_type": "wedding|birthday|corporate|other",
  "event_date": "YYYY-MM-DD or null",
  "budget_min": number or null,
  "budget_max": number or null,
  "location": "string or null",
  "guest_count": number or null,
  "vendor_types_needed": ["venues", "catering", etc.],
  "special_requirements": "string or null"
}

Only include information that was explicitly mentioned. Return ONLY valid JSON, no other text."""

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # Cheaper model for extraction
                messages=messages + [{"role": "system", "content": extraction_prompt}],
                temperature=0,
                max_tokens=200,
            )

            # Parse JSON response
            data_json = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if data_json.startswith("```"):
                data_json = data_json.split("```")[1]
                if data_json.startswith("json"):
                    data_json = data_json[4:]

            data = json.loads(data_json)

            # Update conversation with extracted data
            if data.get('event_type'):
                conversation.event_type = data['event_type']
            if data.get('budget_min'):
                conversation.budget_min = data['budget_min']
            if data.get('budget_max'):
                conversation.budget_max = data['budget_max']
            if data.get('location'):
                conversation.location = data['location']
            if data.get('guest_count'):
                conversation.guest_count = data['guest_count']
            if data.get('vendor_types_needed'):
                conversation.vendor_types_needed = data['vendor_types_needed']
            if data.get('special_requirements'):
                conversation.special_requirements = data['special_requirements']
            if data.get('event_date'):
                from datetime import datetime
                try:
                    conversation.event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
                except:
                    pass

            conversation.save()

        except Exception as e:
            # Silently fail - extraction is nice-to-have
            print(f"Data extraction error: {e}")
            pass

    def _is_conversation_complete(self, conversation):
        """Check if we have enough information to make recommendations"""
        return bool(
            conversation.event_type and
            conversation.location and
            conversation.vendor_types_needed
        )

    def generate_recommendations(self, conversation):
        """
        Generate vendor recommendations based on conversation data

        Returns:
            List of recommended vendors with reasons
        """
        if not conversation.is_completed:
            return []

        # Start with all active vendors
        vendors = Vendor.objects.filter(status='active', verified=True)

        # Filter by location (city match)
        if conversation.location:
            location_lower = conversation.location.lower()
            if 'accra' in location_lower or 'legon' in location_lower:
                vendors = vendors.filter(city__icontains='Accra')

        # Filter by vendor types needed
        if conversation.vendor_types_needed:
            category_slugs = []
            for vendor_type in conversation.vendor_types_needed:
                # Map common names to slugs
                slug_mapping = {
                    'venue': 'venues',
                    'venues': 'venues',
                    'catering': 'catering',
                    'caterer': 'catering',
                    'photographer': 'photographers',
                    'photography': 'photographers',
                    'dj': 'djs',
                    'music': 'djs',
                    'fashion': 'fashion-designers',
                    'designer': 'fashion-designers',
                    'fabric': 'fabrics',
                    'favors': 'favours',
                    'favours': 'favours',
                    'drinks': 'drinks',
                    'beverage': 'drinks',
                    'planner': 'event-planners',
                    'planning': 'event-planners',
                }
                slug = slug_mapping.get(vendor_type.lower(), vendor_type.lower())
                category_slugs.append(slug)

            vendors = vendors.filter(category__slug__in=category_slugs)

        # Filter by budget (price tier)
        if conversation.budget_max:
            if conversation.budget_max < 10000:
                vendors = vendors.filter(price_tier='low')
            elif conversation.budget_max < 30000:
                vendors = vendors.filter(price_tier__in=['low', 'medium'])
            # else: all price tiers

        # Order by rating
        vendors = vendors.order_by('-rating', '-reviews_count')[:15]  # Top 15

        # Create recommendations
        recommendations = []
        for idx, vendor in enumerate(vendors):
            # Calculate match score
            match_score = 100 - (idx * 5)  # Simple scoring: best match = 100

            # Generate reason using AI
            reason = self._generate_recommendation_reason(conversation, vendor)

            # Create or update recommendation
            rec, created = ChatRecommendation.objects.get_or_create(
                conversation=conversation,
                vendor=vendor,
                defaults={
                    'reason': reason,
                    'match_score': match_score
                }
            )

            recommendations.append(rec)

        conversation.recommendations_sent = True
        conversation.save()

        return recommendations

    def _generate_recommendation_reason(self, conversation, vendor):
        """Generate a brief reason why this vendor is recommended"""
        reasons = []

        if vendor.rating >= 4.0:
            reasons.append(f"Highly rated ({vendor.rating}★)")

        if conversation.location and conversation.location.lower() in vendor.neighborhood.lower():
            reasons.append(f"Located in {vendor.neighborhood}")

        if vendor.price_tier == 'low':
            reasons.append("Budget-friendly")
        elif vendor.price_tier == 'high':
            reasons.append("Premium service")

        if not reasons:
            reasons.append(f"Excellent {vendor.category.name.lower()} service")

        return " • ".join(reasons)
