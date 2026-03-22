"""
AI Service for Event Planner Chatbot using Groq
"""
import json
import re
from django.conf import settings
from django.db.models import Q
from vendors.models import Vendor
from categories.models import Category
from .models import ChatConversation, ChatMessage, ChatRecommendation


# ---------------------------------------------------------------------------
# Category slug mapping — maps any user phrase to a DB category slug
# ---------------------------------------------------------------------------
CATEGORY_SLUG_MAP = {
    'venue': 'venues',
    'venues': 'venues',
    'hall': 'venues',
    'event center': 'venues',
    'event centre': 'venues',
    'banquet': 'venues',
    'catering': 'catering',
    'caterer': 'catering',
    'food': 'catering',
    'cook': 'catering',
    'chef': 'catering',
    'photographer': 'photographers',
    'photography': 'photographers',
    'photo': 'photographers',
    'videographer': 'photographers',
    'video': 'photographers',
    'filming': 'photographers',
    'dj': 'djs',
    'disc jockey': 'djs',
    'music': 'djs',
    'entertainment': 'djs',
    'band': 'djs',
    'mc': 'djs',
    'emcee': 'djs',
    'fashion': 'fashion-designers',
    'fashion designer': 'fashion-designers',
    'dress': 'fashion-designers',
    'gown': 'fashion-designers',
    'kente': 'fabrics',
    'fabric': 'fabrics',
    'fabrics': 'fabrics',
    'cloth': 'fabrics',
    'favour': 'favours',
    'favours': 'favours',
    'favor': 'favours',
    'favors': 'favours',
    'gift': 'favours',
    'souvenirs': 'favours',
    'drinks': 'drinks',
    'drink': 'drinks',
    'beverage': 'drinks',
    'bar': 'drinks',
    'wine': 'drinks',
    'alcohol': 'drinks',
    'planner': 'event-planners',
    'coordinator': 'event-planners',
    'organiser': 'event-planners',
    'organizer': 'event-planners',
    'event planner': 'event-planners',
    'event planners': 'event-planners',
    'decoration': 'decorators',
    'decor': 'decorators',
    'decorator': 'decorators',
    'flowers': 'decorators',
    'floral': 'decorators',
    'makeup': 'makeup-artists',
    'hair': 'makeup-artists',
    'beauty': 'makeup-artists',
    'cake': 'bakers',
    'baker': 'bakers',
    'pastry': 'bakers',
}

# City name normalisation
CITY_MAP = {
    'accra': 'Accra',
    'kumasi': 'Kumasi',
    'tema': 'Tema',
    'takoradi': 'Takoradi',
    'cape coast': 'Cape Coast',
    'sekondi': 'Takoradi',
    'obuasi': 'Kumasi',
    'sunyani': 'Sunyani',
}


def _safe_lower(value):
    """Return lowercase string or empty string if value is None."""
    return (value or '').lower()


def _resolve_city(location_text):
    """
    Try to find a canonical city name from a free-text location string.
    Returns canonical city name or None.
    """
    if not location_text:
        return None
    loc = location_text.lower()
    for keyword, canonical in CITY_MAP.items():
        if keyword in loc:
            return canonical
    return None


def _resolve_category_slugs(vendor_types):
    """Convert a list of user-supplied vendor type strings to DB category slugs."""
    slugs = []
    for vtype in (vendor_types or []):
        key = vtype.lower().strip()
        slug = CATEGORY_SLUG_MAP.get(key)
        if not slug:
            # Partial match fallback
            for phrase, mapped_slug in CATEGORY_SLUG_MAP.items():
                if phrase in key or key in phrase:
                    slug = mapped_slug
                    break
        if slug and slug not in slugs:
            slugs.append(slug)
    return slugs


class EventPlannerAI:
    """AI-powered event planner chatbot using Groq"""

    def __init__(self):
        api_key = getattr(settings, 'GROQ_API_KEY', None)
        if not api_key:
            raise ValueError("GROQ_API_KEY is not configured in settings.")
        from groq import Groq
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        self.fast_model = "llama-3.1-8b-instant"

    def get_system_prompt(self):
        """System prompt to guide the AI's behaviour"""
        # Fetch real category names from DB for accuracy
        try:
            categories = list(Category.objects.values_list('name', flat=True))
            categories_text = ', '.join(categories) if categories else 'Venues, Catering, Photographers, DJs, Fashion Designers, Fabrics, Favours, Drinks, Event Planners'
        except Exception:
            categories_text = 'Venues, Catering, Photographers, DJs, Fashion Designers, Fabrics, Favours, Drinks, Event Planners'

        return f"""You are an expert event planner assistant for Events Exclusive — Ghana's premier event vendor marketplace.
You help users find the perfect vendors for events across Ghana including Accra, Kumasi, Tema, Takoradi, and Cape Coast.

CONVERSATION FLOW — ask ONE question at a time in this order:
1. What type of event are you planning?
2. When is the event? (date or approximate month)
3. Where in Ghana? (city and neighbourhood if possible)
4. How many guests are you expecting?
5. What is your approximate budget in Ghanaian Cedis (GHS)?
6. Which vendors do you need? (e.g. venue, catering, photographer, DJ, decorator)
7. Any special requirements? (theme, dietary needs, indoor/outdoor, etc.)

After collecting all essential info (type, location, vendor types — at minimum), say:
"Perfect! I have everything I need. Let me find the best vendors for your [event_type]! 🎉"

GHANA CONTEXT:
- Currency: Ghanaian Cedi (GHS / ₵)
- Event types common in Ghana: wedding, traditional wedding (engagement), outdooring / naming ceremony, funeral / burial, birthday party, graduation, corporate event, baby shower, sod-cutting ceremony
- Neighbourhoods in Accra: East Legon, Cantonments, Labone, Airport Residential, Osu, Adabraka, Dansoman, Spintex, Tema, Madina
- Be culturally aware: funerals in Ghana are major celebrations with large crowds
- Kente fabric, libation, highlife music are Ghanaian traditions

AVAILABLE VENDOR CATEGORIES: {categories_text}

GUIDELINES:
- Be warm, friendly, and concise (2–3 sentences per reply)
- Ask ONE question at a time — never ask two questions in one message
- Use ₵ for Ghanaian Cedis
- Do NOT make up vendor names or prices — just gather info
- If the user seems unsure, offer examples (e.g. "For a wedding you might need a venue, caterer, photographer…")
- If user says they don't know something, skip it and move on
"""

    def chat(self, conversation, user_message):
        """
        Process user message and generate AI response.
        Returns AI response text.
        """
        # Guard: max message length
        user_message = user_message[:1000]

        # Save user message
        ChatMessage.objects.create(
            conversation=conversation,
            role='user',
            content=user_message,
        )

        messages = self._build_message_history(conversation)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=350,
            )

            ai_message = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else None

            ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=ai_message,
                token_count=tokens_used,
            )

            # Extract structured data from conversation (lighter call)
            self._extract_event_data(conversation)

            # Check completion
            if self._is_conversation_complete(conversation):
                conversation.is_completed = True
                conversation.save(update_fields=['is_completed'])

            return ai_message

        except Exception as e:
            error_message = "I'm sorry, I'm having a little trouble right now. Please try sending your message again."
            ChatMessage.objects.create(
                conversation=conversation,
                role='assistant',
                content=error_message,
            )
            # Log real error server-side only
            print(f"[EventPlannerAI] chat error: {e}")
            return error_message

    def _build_message_history(self, conversation):
        """Build message history for Groq API"""
        messages = [{"role": "system", "content": self.get_system_prompt()}]
        for msg in conversation.messages.all().order_by('created_at'):
            messages.append({"role": msg.role, "content": msg.content})
        return messages

    def _extract_event_data(self, conversation):
        """
        Use a fast LLM call to extract structured data from the conversation.
        Runs after each message. Silently fails — it is best-effort.
        """
        # Only extract every other message to save API calls
        msg_count = conversation.messages.count()
        if msg_count < 2 or msg_count % 2 != 0:
            return

        history = self._build_message_history(conversation)

        extraction_prompt = """Based on the conversation so far, extract the following as valid JSON only (no markdown, no explanation):
{
  "event_type": "wedding|birthday|corporate|funeral|naming_ceremony|graduation|baby_shower|engagement|other|null",
  "event_date": "YYYY-MM-DD or null",
  "budget_min": number_or_null,
  "budget_max": number_or_null,
  "location": "string or null",
  "guest_count": number_or_null,
  "vendor_types_needed": ["venue", "catering", "photographer", ...] or [],
  "special_requirements": "string or null"
}
Return ONLY the JSON object. Include only information the user explicitly stated."""

        try:
            response = self.client.chat.completions.create(
                model=self.fast_model,
                messages=history + [{"role": "user", "content": extraction_prompt}],
                temperature=0,
                max_tokens=250,
            )

            raw = response.choices[0].message.content.strip()

            # Strip markdown code fences if present
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)

            data = json.loads(raw)

            changed = False
            if data.get('event_type') and data['event_type'] != 'null':
                conversation.event_type = data['event_type']
                changed = True
            if data.get('budget_min'):
                conversation.budget_min = data['budget_min']
                changed = True
            if data.get('budget_max'):
                conversation.budget_max = data['budget_max']
                changed = True
            if data.get('location'):
                conversation.location = data['location']
                changed = True
            if data.get('guest_count'):
                conversation.guest_count = data['guest_count']
                changed = True
            if data.get('vendor_types_needed'):
                conversation.vendor_types_needed = data['vendor_types_needed']
                changed = True
            if data.get('special_requirements'):
                conversation.special_requirements = data['special_requirements']
                changed = True
            if data.get('event_date'):
                from datetime import datetime
                try:
                    conversation.event_date = datetime.strptime(data['event_date'], '%Y-%m-%d').date()
                    changed = True
                except ValueError:
                    pass

            if changed:
                conversation.save()

        except Exception as e:
            print(f"[EventPlannerAI] extraction error: {e}")

    def _is_conversation_complete(self, conversation):
        """
        Conversation is complete when we have at minimum:
        - event_type  AND
        - at least one of: location, vendor_types_needed
        We also consider it done if the last AI message contains the trigger phrase.
        """
        has_minimum = bool(conversation.event_type) and bool(
            conversation.location or conversation.vendor_types_needed
        )
        if has_minimum:
            return True

        # Also check trigger phrase in last AI message
        last_ai_msg = conversation.messages.filter(role='assistant').order_by('-created_at').first()
        if last_ai_msg and "let me find the best vendors" in last_ai_msg.content.lower():
            return True

        return False

    def generate_recommendations(self, conversation):
        """
        Generate vendor recommendations based on conversation data.
        Returns list of ChatRecommendation objects.
        """
        if not conversation.is_completed:
            return []

        # Resolve city from location text
        city = _resolve_city(conversation.location)

        # Resolve category slugs
        category_slugs = _resolve_category_slugs(conversation.vendor_types_needed)

        # Check which slugs actually exist in DB
        existing_slugs = set(Category.objects.values_list('slug', flat=True))
        valid_slugs = [s for s in category_slugs if s in existing_slugs]

        # Base queryset
        vendors = Vendor.objects.filter(status='active', verified=True).select_related('category')

        # Location filter
        if city:
            vendors = vendors.filter(city__iexact=city)

        # Category filter — if no valid slugs, skip category filter (show all)
        if valid_slugs:
            vendors = vendors.filter(category__slug__in=valid_slugs)

        # Budget filter
        if conversation.budget_max:
            bmax = float(conversation.budget_max)
            if bmax < 5000:
                vendors = vendors.filter(price_tier='low')
            elif bmax < 20000:
                vendors = vendors.filter(price_tier__in=['low', 'medium'])
            # else: show all tiers

        # Order: verified first, then by rating, then recency
        vendors = vendors.order_by('-rating', '-reviews_count', '-created_at')

        # Take top 12 to avoid overwhelming the user
        vendors = list(vendors[:12])

        # Fallback: if city filter yields nothing, retry without city
        if not vendors and city:
            vendors_qs = Vendor.objects.filter(status='active', verified=True).select_related('category')
            if valid_slugs:
                vendors_qs = vendors_qs.filter(category__slug__in=valid_slugs)
            vendors = list(vendors_qs.order_by('-rating', '-reviews_count')[:12])

        # Fallback: if still nothing, just return top-rated vendors
        if not vendors:
            vendors = list(
                Vendor.objects.filter(status='active', verified=True)
                .select_related('category')
                .order_by('-rating', '-reviews_count')[:12]
            )

        # Create recommendation records
        recommendations = []
        for idx, vendor in enumerate(vendors):
            match_score = max(10, 100 - (idx * 7))
            reason = self._generate_recommendation_reason(conversation, vendor)
            rec, _ = ChatRecommendation.objects.get_or_create(
                conversation=conversation,
                vendor=vendor,
                defaults={'reason': reason, 'match_score': match_score},
            )
            recommendations.append(rec)

        conversation.recommendations_sent = True
        conversation.save(update_fields=['recommendations_sent'])

        return recommendations

    def _generate_recommendation_reason(self, conversation, vendor):
        """Build a human-readable reason why this vendor is recommended."""
        reasons = []

        if vendor.rating >= 4.5:
            reasons.append(f"Exceptional rating ({vendor.rating}★)")
        elif vendor.rating >= 4.0:
            reasons.append(f"Highly rated ({vendor.rating}★)")

        # Safe neighbourhood comparison
        vendor_neighbourhood = _safe_lower(vendor.neighborhood)
        conv_location = _safe_lower(conversation.location)
        if conv_location and vendor_neighbourhood and conv_location in vendor_neighbourhood:
            reasons.append(f"In {vendor.neighborhood}")
        elif vendor.city:
            reasons.append(f"Based in {vendor.city}")

        if vendor.price_tier == 'low':
            reasons.append("Budget-friendly ₵")
        elif vendor.price_tier == 'high':
            reasons.append("Premium service")

        if vendor.reviews_count >= 10:
            reasons.append(f"{vendor.reviews_count} reviews")

        if not reasons:
            reasons.append(f"Trusted {(vendor.category.name or 'vendor').lower()}")

        return " · ".join(reasons)
