# AI Event Planner Chatbot - Setup Guide

## Overview

Your Ghana Events Marketplace now has an intelligent AI-powered chatbot that helps users plan their events and get personalized vendor recommendations!

## Features Implemented

✅ **Conversational AI** - Natural conversation using Groq (Llama 3.3)
✅ **Smart Questions** - Collects event type, date, budget, location, guest count, and requirements
✅ **Vendor Recommendations** - AI matches users with perfect vendors from your database
✅ **Floating Widget** - Chat bubble appears on every page
✅ **Dedicated Page** - Full chat interface at `/chatbot/plan-my-event/`
✅ **Admin Tracking** - All conversations saved with unique codes for review
✅ **Email Export** - Users can email recommendations to themselves
✅ **Share & PDF** - Share links and export features
✅ **Analytics** - Track which vendors are viewed, contacted, and favorited

---

## Setup Instructions

### Step 1: Install Groq Package

Add the Groq Python package to your project:

```bash
pip install groq
```

Or add to your `requirements.txt`:
```
groq>=0.5.0
```

Then install:
```bash
pip install -r requirements.txt
```

### Step 2: Get Groq API Key

1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up or log in
3. Go to **API Keys** section
4. Click **"Create Key"**
5. Copy the key (starts with `gsk-...`)

**Important:** Keep this key secret! Never commit it to Git.

### Step 3: Add API Key to .env File

Create or edit your `.env` file:

```bash
# Copy from example if needed
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```env
# Groq API (AI Chatbot)
GROQ_API_KEY=gsk-YOUR-ACTUAL-API-KEY-HERE
```

### Step 4: Run Database Migrations

The chatbot needs new database tables:

```bash
python manage.py makemigrations chatbot
python manage.py migrate
```

This creates 3 tables:
- `chat_conversations` - Stores conversations with unique codes
- `chat_messages` - Individual messages in conversations
- `chat_recommendations` - Vendor recommendations

### Step 5: Test the Chatbot

1. Start your Django server:
   ```bash
   python manage.py runserver
   ```

2. Visit the chatbot page:
   ```
   http://localhost:8000/chatbot/plan-my-event/
   ```

3. Or click the floating 🤖 button on any page!

4. Start chatting and test the flow:
   - Say "I'm planning a wedding"
   - Answer the AI's questions
   - Get personalized vendor recommendations

---

## Usage Guide

### For Users

1. **Start Conversation:**
   - Click the floating chatbot button (🤖) on any page
   - Or visit `/chatbot/plan-my-event/`

2. **Answer Questions:**
   - What type of event? (wedding, birthday, corporate)
   - When is it?
   - What's your budget?
   - Where in Accra?
   - How many guests?
   - Which vendors do you need?
   - Any special requirements?

3. **Get Recommendations:**
   - AI automatically finds matching vendors
   - See personalized suggestions with reasons
   - View profiles, contact vendors, add to favorites

4. **Export & Share:**
   - Email the list to yourself
   - Share link with friends/family
   - Export as PDF (coming soon)

### For Admins

1. **View All Conversations:**
   ```
   http://localhost:8000/admin/chatbot/chatconversation/
   ```

2. **Each conversation has:**
   - Unique code (e.g., `XJKA9PQ2WL3M`)
   - Full chat history
   - Extracted event details
   - Recommended vendors
   - User actions (viewed, contacted, favorited)

3. **Analytics:**
   - See which vendors get recommended most
   - Track conversion rates
   - Understand user needs

---

## Configuration

### Customize AI Behavior

Edit `chatbot/ai_service.py` to modify:

**System Prompt** (`get_system_prompt` method):
- Change the chatbot's personality
- Modify conversation flow
- Add/remove questions

**Recommendation Logic** (`generate_recommendations` method):
- Adjust matching algorithm
- Change number of recommendations
- Modify scoring system

### Model Selection

Groq offers several fast models. In `chatbot/ai_service.py`:

**For Conversational AI:**
```python
self.model = "llama-3.3-70b-versatile"  # High quality
# or
self.model = "llama-3.1-8b-instant"  # Faster, lower cost
```

**For Data Extraction:**
```python
model="llama-3.1-8b-instant"  # Already optimized for speed
```

### Cost Management

Groq offers free tier with generous limits. Paid tiers are very affordable:

**Estimated Costs:**
- Llama 3.3 70B: ~$0.00059 per 1M tokens (very low!)
- Llama 3.1 8B: ~$0.00005 per 1M tokens (extremely low!)

**Typical conversation cost:**
- ~$0.00001-0.00003 per conversation (essentially free!)

**To Monitor Usage:**
```
https://console.groq.com/usage
```

---

## Troubleshooting

### Error: "No module named 'groq'"
**Solution:** Install the package:
```bash
pip install groq
```

### Error: "Groq API key not found"
**Solution:** Check your .env file has:
```env
GROQ_API_KEY=gsk-...
```

### Chatbot not responding
**Solution:** Check:
1. Groq API key is valid
2. You have access to Groq's free tier
3. Check Django logs for errors

### No recommendations showing
**Solution:**
1. Make sure vendors exist in database
2. Run: `python manage.py count_vendors`
3. Vendors must be `status='active'` and `verified=True`

### Widget not appearing
**Solution:** Clear browser cache and refresh page

---

## Advanced Features

### Custom Email Templates

Edit `templates/chatbot/emails/recommendations.html` to customize the email design.

### PDF Export

To enable PDF export, install:
```bash
pip install reportlab
```

Then implement in `chatbot/views.py`.

### WhatsApp Integration

You can integrate with WhatsApp Business API to send recommendations via WhatsApp.

### Multi-language Support

Modify the system prompt to support multiple languages (Twi, Ga, Ewe, etc.).

---

## API Endpoints

The chatbot provides these API endpoints:

- `POST /chatbot/api/chat/start/` - Start new conversation
- `POST /chatbot/api/chat/message/` - Send message
- `GET /chatbot/api/chat/recommendations/<code>/` - Get recommendations
- `POST /chatbot/api/chat/email/` - Email recommendations
- `POST /chatbot/api/chat/track/` - Track user actions

---

## Security Notes

1. **Never commit `.env` file** - It's in `.gitignore`
2. **Rotate API keys** regularly
3. **Monitor usage** for suspicious activity
4. **Rate limit** API calls if needed
5. **Validate inputs** - Already implemented

---

## Next Steps

1. **Test thoroughly** with different event types
2. **Gather feedback** from real users
3. **Monitor costs** (should be minimal with Groq)
4. **Analyze data** to improve recommendations
5. **Add more features** (PDF export, WhatsApp, etc.)

---

## Support

If you encounter issues:

1. Check Django logs: `python manage.py runserver`
2. Check Groq status: https://status.groq.com
3. Review conversation in admin panel
4. Check your Groq usage dashboard

---

## Groq vs OpenAI

### Why Groq?

**Speed:** Groq's LPU (Language Processing Unit) provides 10x faster inference than traditional GPUs.

**Cost:** Groq is significantly cheaper than OpenAI, with a generous free tier.

**Models:** Groq hosts open-source models like Llama 3.3, Mixtral, and Gemma.

**Privacy:** Groq doesn't train on your data, unlike some other providers.

### Model Comparison

| Feature | Groq (Llama 3.3) | OpenAI (GPT-4) |
|---------|------------------|----------------|
| Speed | ~10x faster | Standard |
| Cost | ~$0.00059/1M tokens | ~$30/1M tokens |
| Quality | Excellent | Excellent |
| Privacy | No data training | Data may be used for training |
| Free Tier | Yes | No |

---

**Congratulations! Your AI Event Planner is ready! 🎉**

Users can now get intelligent, personalized vendor recommendations through natural conversation, powered by Groq's ultra-fast AI inference.
