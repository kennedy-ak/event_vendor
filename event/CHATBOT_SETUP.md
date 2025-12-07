# AI Event Planner Chatbot - Setup Guide

## Overview

Your Ghana Events Marketplace now has an intelligent AI-powered chatbot that helps users plan their events and get personalized vendor recommendations!

## Features Implemented

✅ **Conversational AI** - Natural conversation using OpenAI GPT-4
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

### Step 1: Install OpenAI Package

Add the OpenAI Python package to your project:

```bash
pip install openai
```

Or add to your `requirements.txt`:
```
openai==1.10.0
```

Then install:
```bash
pip install -r requirements.txt
```

### Step 2: Get OpenAI API Key

1. Go to [https://platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Go to **API Keys** section
4. Click **"Create new secret key"**
5. Copy the key (starts with `sk-proj-...`)

**Important:** Keep this key secret! Never commit it to Git.

### Step 3: Add API Key to .env File

Create or edit your `.env` file:

```bash
# Copy from example if needed
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
# OpenAI API (AI Chatbot)
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-API-KEY-HERE
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

### Cost Management

OpenAI API charges per token used:

**Estimated Costs:**
- GPT-4 Turbo: ~$0.01-0.03 per conversation
- GPT-3.5 Turbo: ~$0.001-0.005 per conversation

**To Reduce Costs:**

1. **Use GPT-3.5 instead of GPT-4:**

   In `chatbot/ai_service.py`, change:
   ```python
   self.model = "gpt-3.5-turbo"  # Was "gpt-4-turbo-preview"
   ```

2. **Set Usage Limits:**
   - Go to OpenAI dashboard
   - Set monthly spending limit
   - Get email alerts

3. **Monitor Usage:**
   ```
   https://platform.openai.com/usage
   ```

---

## Troubleshooting

### Error: "No module named 'openai'"
**Solution:** Install the package:
```bash
pip install openai
```

### Error: "OpenAI API key not found"
**Solution:** Check your .env file has:
```env
OPENAI_API_KEY=sk-proj-...
```

### Chatbot not responding
**Solution:** Check:
1. OpenAI API key is valid
2. You have credits/billing set up on OpenAI
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
3. **Monitor costs** and adjust model if needed
4. **Analyze data** to improve recommendations
5. **Add more features** (PDF export, WhatsApp, etc.)

---

## Support

If you encounter issues:

1. Check Django logs: `python manage.py runserver`
2. Check OpenAI status: https://status.openai.com
3. Review conversation in admin panel
4. Check your OpenAI usage dashboard

---

**Congratulations! Your AI Event Planner is ready! 🎉**

Users can now get intelligent, personalized vendor recommendations through natural conversation.
