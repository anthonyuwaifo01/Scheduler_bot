"""
Simple Configuration File
Customize your salon/barbershop settings here
"""

import os
from dotenv import load_dotenv
load_dotenv()

# ===== BOT CREDENTIALS =====
# Get BOT_TOKEN from @BotFather on Telegram
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Get ADMIN_TELEGRAM_ID from @userinfobot on Telegram
ADMIN_TELEGRAM_ID = int(os.environ.get('ADMIN_TELEGRAM_ID', '0'))


# ===== BUSINESS INFORMATION =====
BUSINESS_NAME = "Anthony Studio"

# Business Hours (24-hour format)
BUSINESS_HOURS = {
    'start': 9,   # 9 AM
    'end': 18     # 6 PM
}

# Closed Days (0=Monday, 1=Tuesday, ..., 6=Sunday)
CLOSED_DAYS = [6]  # Sunday closed


# ===== SERVICES =====
# Add or modify services here
SERVICES = {
    'haircut': {
        'name': 'Haircut',
        'duration': 30,  # minutes
        'price': 25      # dollars
    },
    'beard': {
        'name': 'Beard Trim',
        'duration': 20,
        'price': 15
    },
    'color': {
        'name': 'Hair Color',
        'duration': 90,
        'price': 80
    },
    'style': {
        'name': 'Wash & Style',
        'duration': 45,
        'price': 40
    }
}


# ===== EXAMPLE: HOW TO ADD MORE SERVICES =====
# Uncomment and customize these to add more services:

# 'blowout': {
#     'name': 'Blowout',
#     'duration': 40,
#     'price': 35
# },
# 'perm': {
#     'name': 'Perm',
#     'duration': 120,
#     'price': 100
# },
# 'kids_cut': {
#     'name': 'Kids Haircut',
#     'duration': 25,
#     'price': 18
# },


# ===== CUSTOMIZATION EXAMPLES =====

# Example 1: Change business hours to 10 AM - 8 PM
# BUSINESS_HOURS = {'start': 10, 'end': 20}

# Example 2: Close on Monday and Sunday
# CLOSED_DAYS = [0, 6]

# Example 3: Open 7 days a week
# CLOSED_DAYS = []

# Example 4: Different pricing
# SERVICES = {
#     'basic_cut': {'name': 'Basic Cut', 'duration': 20, 'price': 15},
#     'premium_cut': {'name': 'Premium Cut', 'duration': 45, 'price': 50},
# }