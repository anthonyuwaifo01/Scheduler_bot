"""
Simple Scheduler Bot MVP
Basic booking system - Name, Phone, Service, Time
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, ContextTypes, filters
from datetime import datetime, timedelta
import logging
from database import Database
from config import BOT_TOKEN, ADMIN_TELEGRAM_ID

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Conversation states
GET_NAME, GET_PHONE, SELECT_SERVICE, SELECT_DATE, SELECT_TIME = range(5)

# Simple services
SERVICES = {
    'haircut': {'name': 'Haircut', 'duration': 30, 'price': 25},
    'beard': {'name': 'Beard Trim', 'duration': 20, 'price': 15},
    'color': {'name': 'Hair Color', 'duration': 90, 'price': 80},
    'style': {'name': 'Wash & Style', 'duration': 45, 'price': 40}
}

BUSINESS_HOURS = {'start': 9, 'end': 18}  # 9 AM to 6 PM
CLOSED_DAYS = [6]  # Sunday

db = Database()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    keyboard = [
        [InlineKeyboardButton("📅 Book Appointment", callback_data='book')],
        [InlineKeyboardButton("📋 My Bookings", callback_data='mybookings')],
    ]
    
    if update.message.from_user.id == ADMIN_TELEGRAM_ID:
        keyboard.append([InlineKeyboardButton("⚙️ Admin", callback_data='admin')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💈 *Welcome to Anthony Studio!*\n\n"
        "Book your appointment in 3 easy steps:\n"
        "1️⃣ Enter your details\n"
        "2️⃣ Choose service & time\n"
        "3️⃣ Confirm booking\n\n"
        "👇 What would you like to do?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle main menu buttons"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'book':
        return await start_booking(update, context)
    elif query.data == 'mybookings':
        return await show_bookings(update, context)
    elif query.data == 'admin':
        return await admin_panel(update, context)
    elif query.data == 'back':
        keyboard = [
            [InlineKeyboardButton("📅 Book Appointment", callback_data='book')],
            [InlineKeyboardButton("📋 My Bookings", callback_data='mybookings')],
        ]
        if query.from_user.id == ADMIN_TELEGRAM_ID:
            keyboard.append([InlineKeyboardButton("⚙️ Admin", callback_data='admin')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "💈 *Welcome Back!*\n\nWhat would you like to do?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )


async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start booking - ask for name"""
    query = update.callback_query
    
    await query.edit_message_text(
        "✨ *Let's Book Your Appointment!*\n\n"
        "Step 1 of 3\n\n"
        "👤 Please type your *full name*:",
        parse_mode='Markdown'
    )
    return GET_NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get name and ask for phone"""
    context.user_data['name'] = update.message.text
    
    await update.message.reply_text(
        f"Nice to meet you, {update.message.text}! 👋\n\n"
        "Step 2 of 3\n\n"
        "📱 Please enter your *phone number*:\n"
        "(Example: +1234567890 or 1234567890)",
        parse_mode='Markdown'
    )
    return GET_PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get phone and show services"""
    context.user_data['phone'] = update.message.text
    
    keyboard = []
    for key, service in SERVICES.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{service['name']} - ${service['price']} ({service['duration']}min)",
                callback_data=f'service_{key}'
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Perfect! 📞\n\n"
        "Step 3 of 3\n\n"
        "💇 *Choose Your Service:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return SELECT_SERVICE


async def service_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Service selected, show dates"""
    query = update.callback_query
    await query.answer()
    
    service_key = query.data.replace('service_', '')
    context.user_data['service'] = service_key
    context.user_data['service_name'] = SERVICES[service_key]['name']
    context.user_data['duration'] = SERVICES[service_key]['duration']
    context.user_data['price'] = SERVICES[service_key]['price']
    
    # Show next 7 days
    keyboard = []
    today = datetime.now()
    
    for i in range(7):
        date = today + timedelta(days=i)
        if date.weekday() not in CLOSED_DAYS:
            date_str = date.strftime('%Y-%m-%d')
            display_date = date.strftime('%a, %b %d')
            keyboard.append([InlineKeyboardButton(display_date, callback_data=f'date_{date_str}')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"Great choice! ✨\n\n"
        f"Service: *{SERVICES[service_key]['name']}*\n"
        f"Duration: {SERVICES[service_key]['duration']} minutes\n"
        f"Price: ${SERVICES[service_key]['price']}\n\n"
        f"📅 *Select a Date:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return SELECT_DATE


async def date_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Date selected, show available times"""
    query = update.callback_query
    await query.answer()
    
    date_str = query.data.replace('date_', '')
    context.user_data['date'] = date_str
    
    # Get available time slots
    booked_slots = db.get_booked_slots(date_str)
    duration = context.user_data['duration']
    
    keyboard = []
    current_time = datetime.now()
    selected_date = datetime.strptime(date_str, '%Y-%m-%d')
    
    for hour in range(BUSINESS_HOURS['start'], BUSINESS_HOURS['end']):
        for minute in [0, 30]:
            time_str = f"{hour:02d}:{minute:02d}"
            slot_datetime = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')
            
            # Skip past times for today
            if selected_date.date() == current_time.date() and slot_datetime <= current_time:
                continue
            
            # Check availability
            if db.is_slot_available(date_str, time_str, duration, booked_slots):
                display_time = slot_datetime.strftime('%I:%M %p')
                keyboard.append([InlineKeyboardButton(display_time, callback_data=f'time_{time_str}')])
    
    if not keyboard:
        await query.edit_message_text(
            "😔 Sorry, no slots available on this date.\n\n"
            "Please use /start to try another date."
        )
        return ConversationHandler.END
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    date_display = datetime.strptime(date_str, '%Y-%m-%d').strftime('%A, %B %d')
    
    await query.edit_message_text(
        f"📅 Date: *{date_display}*\n\n"
        f"🕐 *Select a Time:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return SELECT_TIME


async def time_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Time selected, confirm and save booking"""
    query = update.callback_query
    await query.answer()
    
    time_str = query.data.replace('time_', '')
    context.user_data['time'] = time_str
    
    # Get all booking details
    name = context.user_data['name']
    phone = context.user_data['phone']
    service = context.user_data['service']
    service_name = context.user_data['service_name']
    price = context.user_data['price']
    date = context.user_data['date']
    
    # Save to database
    user_id = query.from_user.id
    appointment_id = db.create_appointment(user_id, service, date, time_str, name, phone)
    
    # Format for display
    date_display = datetime.strptime(date, '%Y-%m-%d').strftime('%A, %B %d, %Y')
    time_display = datetime.strptime(time_str, '%H:%M').strftime('%I:%M %p')
    
    # Show confirmation
    await query.edit_message_text(
        f"✅ *Booking Confirmed!*\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎫 Booking ID: *#{appointment_id}*\n"
        f"👤 Name: {name}\n"
        f"📱 Phone: {phone}\n"
        f"💇 Service: {service_name}\n"
        f"💵 Price: ${price}\n"
        f"📅 Date: {date_display}\n"
        f"🕐 Time: {time_display}\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📍 Style Studio - 123 Main St\n\n"
        f"See you soon! ✨\n\n"
        f"Use /start to manage bookings.",
        parse_mode='Markdown'
    )
    
    # Notify admin
    try:
        admin_message = (
            f"🔔 *New Booking!*\n\n"
            f"ID: #{appointment_id}\n"
            f"Customer: {name}\n"
            f"Phone: {phone}\n"
            f"Service: {service_name}\n"
            f"Date: {date_display}\n"
            f"Time: {time_display}\n"
            f"Price: ${price}"
        )
        await context.bot.send_message(
            chat_id=ADMIN_TELEGRAM_ID,
            text=admin_message,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Failed to notify admin: {e}")
    
    return ConversationHandler.END


async def show_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's bookings"""
    query = update.callback_query
    user_id = query.from_user.id
    
    appointments = db.get_user_appointments(user_id)
    
    if not appointments:
        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📭 *No Bookings Found*\n\n"
            "You don't have any upcoming appointments.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return
    
    message = "📋 *Your Bookings*\n\n"
    
    for apt in appointments:
        date_display = datetime.strptime(apt['date'], '%Y-%m-%d').strftime('%b %d, %Y')
        time_display = datetime.strptime(apt['time'], '%H:%M').strftime('%I:%M %p')
        service_name = SERVICES.get(apt['service'], {}).get('name', apt['service'])
        
        message += (
            f"🎫 ID: #{apt['id']}\n"
            f"📅 {date_display} at {time_display}\n"
            f"💇 {service_name}\n\n"
        )
    
    keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin panel"""
    query = update.callback_query
    
    if query.from_user.id != ADMIN_TELEGRAM_ID:
        await query.answer("Unauthorized", show_alert=True)
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 Today's Bookings", callback_data='admin_today')],
        [InlineKeyboardButton("📅 Tomorrow's Bookings", callback_data='admin_tomorrow')],
        [InlineKeyboardButton("📤 Forward All Bookings", callback_data='admin_forward')],
        [InlineKeyboardButton("⬅️ Back", callback_data='back')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚙️ *Admin Panel*\n\nChoose an option:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def admin_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show today's bookings"""
    query = update.callback_query
    
    today = datetime.now().strftime('%Y-%m-%d')
    appointments = db.get_appointments_by_date(today)
    
    if not appointments:
        message = "📭 *No Bookings Today*"
    else:
        message = f"📊 *Today's Bookings* ({len(appointments)} total)\n\n"
        
        for apt in appointments:
            time_display = datetime.strptime(apt['time'], '%H:%M').strftime('%I:%M %p')
            service_name = SERVICES.get(apt['service'], {}).get('name', '')
            
            message += (
                f"🕐 {time_display}\n"
                f"👤 {apt['name']}\n"
                f"📱 {apt['phone']}\n"
                f"💇 {service_name}\n"
                f"ID: #{apt['id']}\n\n"
            )
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Admin", callback_data='admin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show tomorrow's bookings"""
    query = update.callback_query
    
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    appointments = db.get_appointments_by_date(tomorrow)
    
    if not appointments:
        message = "📭 *No Bookings Tomorrow*"
    else:
        message = f"📅 *Tomorrow's Bookings* ({len(appointments)} total)\n\n"
        
        for apt in appointments:
            time_display = datetime.strptime(apt['time'], '%H:%M').strftime('%I:%M %p')
            service_name = SERVICES.get(apt['service'], {}).get('name', '')
            
            message += (
                f"🕐 {time_display}\n"
                f"👤 {apt['name']}\n"
                f"📱 {apt['phone']}\n"
                f"💇 {service_name}\n"
                f"ID: #{apt['id']}\n\n"
            )
    
    keyboard = [[InlineKeyboardButton("⬅️ Back to Admin", callback_data='admin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def admin_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask for Telegram contact to forward bookings"""
    query = update.callback_query
    
    keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data='admin')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📤 *Forward All Bookings*\n\n"
        "Please enter the *Telegram User ID* you want to forward bookings to.\n\n"
        "Example: 123456789\n\n"
        "(Get User ID from @userinfobot)\n\n"
        "Or click Cancel to go back.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    context.user_data['awaiting_forward_id'] = True


async def handle_forward_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle forwarding bookings to specified user"""
    if not context.user_data.get('awaiting_forward_id'):
        return
    
    if update.message.from_user.id != ADMIN_TELEGRAM_ID:
        return
    
    try:
        target_id = int(update.message.text.strip())
        context.user_data['awaiting_forward_id'] = False
        
        # Get all upcoming bookings
        today = datetime.now().strftime('%Y-%m-%d')
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM appointments
            WHERE date >= ? AND status = 'confirmed'
            ORDER BY date, time
        ''', (today,))
        
        appointments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not appointments:
            await update.message.reply_text("📭 No upcoming bookings to forward.")
            return
        
        # Format all bookings
        message = f"📋 *All Upcoming Bookings* ({len(appointments)} total)\n\n"
        
        for apt in appointments:
            date_display = datetime.strptime(apt['date'], '%Y-%m-%d').strftime('%b %d, %Y')
            time_display = datetime.strptime(apt['time'], '%H:%M').strftime('%I:%M %p')
            service_name = SERVICES.get(apt['service'], {}).get('name', '')
            
            message += (
                f"🎫 ID: #{apt['id']}\n"
                f"📅 {date_display} at {time_display}\n"
                f"👤 {apt['name']}\n"
                f"📱 {apt['phone']}\n"
                f"💇 {service_name}\n\n"
            )
        
        # Forward to target user
        await context.bot.send_message(
            chat_id=target_id,
            text=message,
            parse_mode='Markdown'
        )
        
        await update.message.reply_text(
            f"✅ *Forwarded Successfully!*\n\n"
            f"Sent {len(appointments)} bookings to user ID: {target_id}\n\n"
            f"Use /start to return to menu.",
            parse_mode='Markdown'
        )
        
    except ValueError:
        await update.message.reply_text(
            "❌ Invalid User ID. Please enter numbers only.\n\n"
            "Use /start to try again."
        )
    except Exception as e:
        logger.error(f"Forward error: {e}")
        await update.message.reply_text(
            "❌ Failed to forward. Make sure the User ID is correct.\n\n"
            "Use /start to try again."
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation"""
    await update.message.reply_text("❌ Cancelled. Use /start to begin again.")
    return ConversationHandler.END


def main():
    """Start the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Booking conversation
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_booking, pattern='^book$')],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            SELECT_SERVICE: [CallbackQueryHandler(service_selected, pattern='^service_')],
            SELECT_DATE: [CallbackQueryHandler(date_selected, pattern='^date_')],
            SELECT_TIME: [CallbackQueryHandler(time_selected, pattern='^time_')],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(button_handler, pattern='^(mybookings|admin|back)$'))
    application.add_handler(CallbackQueryHandler(admin_today, pattern='^admin_today$'))
    application.add_handler(CallbackQueryHandler(admin_tomorrow, pattern='^admin_tomorrow$'))
    application.add_handler(CallbackQueryHandler(admin_forward, pattern='^admin_forward$'))
    
    # Handle forward ID input
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.User(user_id=ADMIN_TELEGRAM_ID),
        handle_forward_id
    ))
    
    logger.info("Simple MVP Bot started...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()


from telegram.ext import Application
from telegram.request import HTTPXRequest

request = HTTPXRequest(
    connect_timeout=10,
    read_timeout=20,
    write_timeout=20,
    pool_timeout=20
)

application = (
    Application.builder()
    .token(BOT_TOKEN)
    .request(request)
    .build()
)

