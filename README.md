# 📅 Telegram Scheduler Bot - MVP

A complete appointment scheduling bot for small businesses built with Python and Telegram Bot API.

## 🎯 Features

### For Customers
- 📱 Book appointments 24/7 through Telegram
- 📅 View upcoming appointments
- ❌ Cancel appointments
- 🔔 Automatic 24-hour reminders
- ✅ Instant booking confirmation

### For Business Owners
- 📊 View daily schedules
- 📈 Basic statistics (weekly/monthly bookings)
- 🔔 Get notified of new bookings
- 👥 See customer information
- 📱 Manage everything from Telegram
- 📢 **Broadcast schedules to entire team** (one click)

## 📁 Project Structure

```
scheduler-bot/
├── bot.py              # Main bot logic with broadcast feature
├── database.py         # Database operations
├── scheduler.py        # Reminder system
├── config.py           # Configuration settings (add staff IDs here)
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── .env               # Environment variables (create this)
```

## 🚀 Quick Start

### 1. Create Your Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Choose a name (e.g., "Ace Barbershop Scheduler")
4. Choose a username (e.g., "ace_barbershop_bot")
5. **Save the token** BotFather gives you (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your Telegram User ID

1. Search for `@userinfobot` on Telegram
2. Start a chat with it
3. It will send you your user ID (a number like `123456789`)
4. **Save this number** - you'll use it as ADMIN_TELEGRAM_ID

### 3. Get Staff Telegram IDs (Optional - for broadcasts)

For each staff member:
1. Have them message `@userinfobot` on Telegram
2. They'll get their user ID
3. Collect all IDs to add to config later

### 3. Set Up Locally (Testing)

```bash
# Clone or download the project
mkdir scheduler-bot
cd scheduler-bot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
# On Windows:
echo BOT_TOKEN=your_token_here > .env
echo ADMIN_TELEGRAM_ID=your_user_id >> .env

# On Mac/Linux:
echo "BOT_TOKEN=your_token_here" > .env
echo "ADMIN_TELEGRAM_ID=your_user_id" >> .env

# Optional: Add staff IDs to config.py for broadcasts
# Edit config.py and add:
# STAFF_TELEGRAM_IDS = [123456789, 987654321]

# Run the bot
python bot.py
```

In another terminal (keep bot.py running), start the reminder scheduler:

```bash
# Activate virtual environment first
python scheduler.py
```

### 4. Test Your Bot

1. Open Telegram
2. Search for your bot username (e.g., `@ace_barbershop_bot`)
3. Click "Start"
4. Try booking an appointment!

## 🌐 Deploy to Render.com (Free Hosting)

### Step 1: Prepare Your Code

1. Create a GitHub account if you don't have one
2. Create a new repository (e.g., "scheduler-bot")
3. Upload all your files to GitHub:
   - bot.py
   - database.py
   - scheduler.py
   - config.py
   - requirements.txt
   - **DO NOT upload .env file** (keep tokens secret!)

4. Create a `render.yaml` file in your repository:

```yaml
services:
  # Main bot service
  - type: web
    name: scheduler-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python bot.py
    envVars:
      - key: BOT_TOKEN
        sync: false
      - key: ADMIN_TELEGRAM_ID
        sync: false
    
  # Reminder scheduler service
  - type: worker
    name: scheduler-bot-reminders
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python scheduler.py
    envVars:
      - key: BOT_TOKEN
        sync: false
      - key: ADMIN_TELEGRAM_ID
        sync: false
```

### Step 2: Deploy on Render

1. Go to [render.com](https://render.com) and sign up (free)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect your `render.yaml` file
5. Add environment variables:
   - `BOT_TOKEN`: Your bot token from BotFather
   - `ADMIN_TELEGRAM_ID`: Your Telegram user ID
6. Click "Apply"
7. Wait 5-10 minutes for deployment

### Step 3: Verify Deployment

1. Check the logs on Render dashboard
2. Look for "Bot started..." message
3. Test your bot on Telegram

## 🎨 Customization

### Change Business Information

Edit `config.py`:

```python
BUSINESS_NAME = "Your Business Name"

BUSINESS_HOURS = {
    'start': 9,   # Opening time (24-hour format)
    'end': 17     # Closing time
}

CLOSED_DAYS = [6]  # Days closed (0=Monday, 6=Sunday)
```

### Modify Services

Edit `config.py`:

```python
SERVICES = {
    'service_key': {
        'name': 'Service Name',
        'duration': 30,  # minutes
        'price': 25      # price
    }
}
```

Then update the same in `bot.py` and `scheduler.py`.

### Change Time Slots

Edit `config.py`:

```python
SLOT_INTERVAL = 30  # Change to 15, 30, 45, or 60 minutes
```

## 📊 Usage Commands

### For Customers
- `/start` - Main menu
- `/book` - Book appointment
- `/myappointments` - View bookings
- `/cancel` - Cancel appointment
- `/help` - Get help

### For Admin (Business Owner)
- `/start` - Access admin panel
- Admin panel shows:
  - Today's appointments (with summary stats)
  - Tomorrow's schedule
  - Week overview
  - **Broadcast schedules to staff** (one-click)
  - Statistics

## 🔧 Troubleshooting

### Bot doesn't respond
- Check if bot.py is running
- Verify BOT_TOKEN is correct
- Check Render logs for errors

### Reminders not sending
- Check if scheduler.py is running
- Verify both services are running on Render
- Check the worker logs

### Database errors
- Delete `scheduler.db` and restart
- Check file permissions
- On Render, database resets on each deploy (expected for MVP)

### "Unauthorized" error
- Verify ADMIN_TELEGRAM_ID is set correctly
- Make sure it's your actual Telegram user ID

## 💰 Free Tier Limits

**Render.com Free Tier:**
- 750 hours/month (enough for 1 month 24/7)
- Sleeps after 15 minutes of inactivity
- First request takes 30-60 seconds to wake up
- Database is not persistent (resets on restart)

**Telegram API:**
- Completely free
- Unlimited messages
- Unlimited broadcasts to staff
- No per-message costs

**For Production:**
- Upgrade to Render paid plan ($7/month)
- Add persistent disk for database
- Consider using PostgreSQL instead of SQLite

## 🚀 Next Steps (Post-MVP)

After validating with real users:

1. **Add Payment Integration**
   - Stripe for deposits
   - Reduce no-shows

2. **Google Calendar Sync**
   - Two-way synchronization
   - OAuth integration

3. **Web Dashboard**
   - React/Vue frontend
   - Better analytics
   - Calendar view

4. **SMS Reminders**
   - Use Twilio
   - More reliable than Telegram

5. **Multi-Business Support**
   - White-label solution
   - Per-business configuration

6. **Advanced Features**
   - Staff scheduling
   - Multiple locations
   - Waitlist management
   - Customer notes

## 📝 Database Schema

```sql
-- Customers table
customers (
    id INTEGER PRIMARY KEY,
    telegram_id INTEGER UNIQUE,
    name TEXT,
    phone TEXT,
    created_at TIMESTAMP
)

-- Appointments table
appointments (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    telegram_id INTEGER,
    service TEXT,
    date TEXT,
    time TEXT,
    name TEXT,
    phone TEXT,
    status TEXT,
    reminder_sent INTEGER,
    created_at TIMESTAMP
)

-- Settings table
settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
```

## 🔐 Security Notes

- Never commit `.env` file to GitHub
- Keep BOT_TOKEN secret
- Use environment variables for sensitive data
- ADMIN_TELEGRAM_ID restricts admin access
- Validate user inputs
- Rate limit API calls

## 📞 Support

For issues or questions:
1. Check the logs (Render dashboard or terminal)
2. Review this README
3. Check Telegram Bot API docs: https://core.telegram.org/bots/api

## 📄 License

Free to use and modify for your business needs.

## 🎉 Demo Script

When showcasing to potential clients:

1. **Show the problem:**
   - "How many calls do you get per day for bookings?"
   - "How much time does that take?"
   - "How many no-shows do you have?"

2. **Demo the solution:**
   - Book an appointment (2 minutes)
   - Show admin panel
   - View today's schedule
   - Show reminder notification

3. **Explain benefits:**
   - 24/7 booking availability
   - Automatic reminders (40% reduction in no-shows)
   - Time saved (2+ hours/day)
   - Professional image

4. **Pricing suggestion:**
   - Free trial: 1 month
   - Basic: $29/month (single location)
   - Pro: $79/month (multiple staff, analytics)

---

Built with ❤️ for small businesses