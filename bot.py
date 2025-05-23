from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import sqlite3
import os

# Database setup (SQLite for simplicity)
conn = sqlite3.connect('user_shares.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (user_id INTEGER PRIMARY KEY, shares INTEGER)''')
conn.commit()

TOKEN = os.environ.get("TOKEN")  # Get from Railway environment vars
GROUP_ID = -4969855570  # Replace with your group ID
VIP_LINK = "https://t.me/+q1Wg9YeCAKFlOGRl"  # Replace with your VIP link

def welcome(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    cursor.execute('INSERT OR IGNORE INTO users (user_id, shares) VALUES (?, 0)', (user_id,))
    conn.commit()
    
    keyboard = [
        [InlineKeyboardButton("🔗 SHARE GROUP (10 REQUIRED)", callback_data="share")],
        [InlineKeyboardButton("🚀 JOIN VIP (LOCKED)", callback_data="vip")]
    ]
    update.message.reply_text(
        "⚠️ **VIP ACCESS LOCKED**\n\n"
        "📢 Share this group with **10 friends** to unlock VIP:\n"
        "👉 https://t.me/yourgroup\n\n"
        "👇 Click **SHARE GROUP** first!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

def track_shares(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if update.message.forward_from_chat and update.message.forward_from_chat.id == GROUP_ID:
        cursor.execute('UPDATE users SET shares = shares + 1 WHERE user_id = ?', (user_id,))
        conn.commit()

def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    shares = cursor.execute('SELECT shares FROM users WHERE user_id = ?', (user_id,)).fetchone()[0]

    if query.data == "share":
        query.answer()
        query.edit_message_text(
            "📤 **SHARE THIS LINK 10 TIMES:**\n\n"
            "👉 https://t.me/yourgroup\n\n"
            "After sharing, click **✅ DONE SHARING** below.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ DONE SHARING", callback_data="check")]
            ]),
            parse_mode="Markdown"
        )
    elif query.data == "check":
        if shares >= 10:
            query.answer("🎉 VIP UNLOCKED!", show_alert=True)
            query.edit_message_text(
                f"✅ **ACCESS GRANTED!**\n\n"
                f"🚀 Join VIP Group: [Click Here]({VIP_LINK})",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )
        else:
            query.answer(f"❌ Need {10 - shares} more shares!", show_alert=True)
    elif query.data == "vip":
        query.answer("🔒 Complete sharing first!", show_alert=True)

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, welcome))
    dp.add_handler(CallbackQueryHandler(button_click))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, track_shares))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
