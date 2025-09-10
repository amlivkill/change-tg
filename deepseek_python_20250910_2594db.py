#!/usr/bin/env python3
"""
HimalayaChangeBot - basic Telegram bot for CHANGE (Himalaya).
Uses python-telegram-bot v20+ (async).
Replace YOUR_BOT_TOKEN_HERE with your bot token.
"""

import logging
import os
from http import HTTPStatus
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Add a simple HTTP server for health checks
from aiohttp import web

# ---------- Configuration ----------
BOT_USERNAME = "@HimalayaChangeBot"
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8322403658:AAGSJ_UOqxXsV6hlBDwXJl5AfEdojrRy-VA")  # Get token from environment

# Basic content in English and Hindi
CONTENT = {
    "en": {
        "welcome": "👋 Welcome to CHANGE — Centre for Himalaya Agriculture & Nature Group of Environment!\n\nChoose an option from the menu below.",
        "choose_lang": "Please choose your language / कृपया अपनी भाषा चुनें:",
        "about_title": "About CHANGE",
        "about_text": (
            "CHANGE (Centre for Himalaya Agriculture & Nature Group of Environment) "
            "works to empower rural Uttarakhand through sustainable agriculture, "
            "environmental conservation and community enterprise.\n\n"
            "Tagline: Empowering Rural Uttarakhand through Sustainable Agriculture, Nature Conservation & Community Enterprise."
        ),
        "products_title": "Products & Services",
        "products_text": (
            "We offer:\n"
            "- Organic millets & pulses (Shri Anna)\n"
            "- Herbal teas, aroma oils, spices\n"
            "- Vegan products, jams & pickles\n"
            "- Contract farming, certification support, microfinance and trainings\n\n"
            "For product inquiries, visit our website or type /contact."
        ),
        "membership_title": "Membership",
        "membership_text": (
            "Membership details:\n"
            "- One-time share contribution: ₹2,000\n"
            "- Benefits: microcredit, certification support, buy-back, training & voting rights.\n\n"
            "To apply, please fill the membership form: [link placeholder]"
        ),
        "events_title": "News & Events",
        "events_text": "Upcoming workshops and agro-tours will be posted here. To get notified, follow our social channels.",
        "contact_title": "Contact CHANGE",
        "contact_text": (
            "📧 Email: info@change.example\n"
            "📞 Phone: +91-XXXXXXXXXX\n"
            "📍 Office: Pauri / Rudraprayag, Uttarakhand\n\n"
            "Social: Facebook | Instagram | YouTube (links placeholder)"
        ),
        "back_button": "🔙 Back",
    },
    "hi": {
        "welcome": "👋 CHANGE में आपका स्वागत है — हिमालय एग्रीकल्चर एण्ड नेचर ग्रुप ऑफ़ एनवायरनमेंट!\n\nनीचे दिए गए मेन्यू में से चुनें।",
        "choose_lang": "Please choose your language / कृपया अपनी भाषा चुनें:",
        "about_title": "CHANGE के बारे में",
        "about_text": (
            "CHANGE ग्रामीण उत्तराखंड को सतत कृषि, पर्यावरण संरक्षण और सामुदायिक उद्यम के "
            "माध्यम से सशक्त बनाने का काम करता है।\n\n"
            "टैगलाइन: Empowering Rural Uttarakhand through Sustainable Agriculture, Nature Conservation & Community Enterprise."
        ),
        "products_title": "उत्पाद और सेवाएं",
        "products_text": (
            "हम प्रदान करते हैं:\n"
            "- ऑर्गेनिक बाजरा और दालें (श्री अन्न)\n"
            "- हर्बल चाय, एसेंसियल ऑयल, मसाले\n"
            "- वेगन उत्पाद, जाम और अचार\n"
            "- अनुबंध आधारित खेती, प्रमाणन सहायता, माइक्रोफाइनेंस और प्रशिक्षण\n\n"
            "उत्पाद जानकारी के लिए /contact टाइप करें।"
        ),
        "membership_title": "सदस्यता",
        "membership_text": (
            "सदस्यता विवरण:\n"
            "- एकमुश्त शेयर योगदान: ₹2,000\n"
            "- लाभ: माइक्रोक्रेडिट, प्रमाणन सहायता, खरीद-वारंटी, प्रशिक्षण और मतदान अधिकार\n\n"
            "आवेदन के लिए फॉर्म भरें: [link placeholder]"
        ),
        "events_title": "समाचार और इवेंट",
        "events_text": "कार्यशालाओं और कृषि भ्रमणों की जानकारी यहाँ दी जाएगी।",
        "contact_title": "संपर्क जानकारी",
        "contact_text": (
            "📧 ईमेल: info@change.example\n"
            "📞 फोन: +91-XXXXXXXXXX\n"
            "📍 कार्यालय: पौड़ी / रुड़्रप्रयाग, उत्तराखंड\n\n"
            "सोशल: Facebook | Instagram | YouTube (लिंक placeholder)"
        ),
        "back_button": "🔙 वापस",
    },
}


# ---------- Helpers ----------
def menu_keyboard(lang: str):
    """Return InlineKeyboardMarkup for main menu in given language."""
    texts = CONTENT[lang]
    keyboard = [
        [InlineKeyboardButton(texts["about_title"], callback_data=f"{lang}|about")],
        [InlineKeyboardButton(texts["products_title"], callback_data=f"{lang}|products")],
        [InlineKeyboardButton(texts["membership_title"], callback_data=f"{lang}|membership")],
        [InlineKeyboardButton(texts["events_title"], callback_data=f"{lang}|events")],
        [InlineKeyboardButton(texts["contact_title"], callback_data=f"{lang}|contact")],
    ]
    return InlineKeyboardMarkup(keyboard)


def language_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("English", callback_data="lang|en"),
            InlineKeyboardButton("हिन्दी", callback_data="lang|hi"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ---------- Handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send language choice on /start."""
    user = update.effective_user
    welcome_prompt = CONTENT["en"]["choose_lang"]
    text = f"Hello {user.first_name}!\n\n{welcome_prompt}"
    await update.message.reply_text(text, reply_markup=language_keyboard())


async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle language selection and show main menu."""
    query = update.callback_query
    await query.answer()
    _, lang = query.data.split("|")
    texts = CONTENT[lang]
    await query.edit_message_text(texts["welcome"], reply_markup=menu_keyboard(lang))


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu callbacks (about, products, membership, events, contact)."""
    query = update.callback_query
    await query.answer()
    data = query.data  # format: "<lang>|<action>"
    try:
        lang, action = data.split("|")
    except ValueError:
        # fallback to english menu
        lang, action = "en", data

    texts = CONTENT.get(lang, CONTENT["en"])

    if action == "about":
        await query.edit_message_text(f"*{texts['about_title']}*\n\n{texts['about_text']}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(texts["back_button"], callback_data=f"{lang}|back")]]
        ))
    elif action == "products":
        await query.edit_message_text(f"*{texts['products_title']}*\n\n{texts['products_text']}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(texts["back_button"], callback_data=f"{lang}|back")]]
        ))
    elif action == "membership":
        await query.edit_message_text(f"*{texts['membership_title']}*\n\n{texts['membership_text']}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Membership Form", url="https://example.com/membership-form")],
                [InlineKeyboardButton(texts["back_button"], callback_data=f"{lang}|back")]
            ]
        ))
    elif action == "events":
        await query.edit_message_text(f"*{texts['events_title']}*\n\n{texts['events_text']}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(texts["back_button"], callback_data=f"{lang}|back")]]
        ))
    elif action == "contact":
        await query.edit_message_text(f"*{texts['contact_title']}*\n\n{texts['contact_text']}", parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Email Us", url="mailto:info@change.example")],
                [InlineKeyboardButton(texts["back_button"], callback_data=f"{lang}|back")]
            ]
        ))
    elif action == "back":
        # show main menu again
        await query.edit_message_text(texts["welcome"], reply_markup=menu_keyboard(lang))
    else:
        await query.edit_message_text("Option not recognized. Please /start again.")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fallback for unknown commands."""
    await update.message.reply_text("Sorry, I didn't understand that command. Use /start to see options.")


# ---------- Web Server for Health Checks ----------
async def health_check(request):
    """Health check endpoint for Render.com"""
    return web.json_response({"status": "ok", "bot": "HimalayaChangeBot"}, status=HTTPStatus.OK)


async def start_web_server():
    """Start a simple web server for health checks"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    logging.info("Web server started on port 8000 for health checks")


# ---------- Main ----------
def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    
    # Check if BOT_TOKEN is set
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logging.error("BOT_TOKEN environment variable is not set!")
        return
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    # Callback handlers (language selection and menu)
    app.add_handler(CallbackQueryHandler(lang_callback, pattern=r"^lang\|"))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern=r"^(en|hi)\|"))
    # Unknown commands
    app.add_handler(CommandHandler(["help"], start))
    
    # Start the web server for health checks
    app.run_polling(allowed_updates=["callback_query", "message"], web_app=start_web_server())

if __name__ == "__main__":
    main()
