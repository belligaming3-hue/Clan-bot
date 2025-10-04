import asyncio
import json
import os
from io import BytesIO
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Bot token - o'rnating
TOKEN = '8302312256:AAFRJat6pm3WbAoiSMUvdDl5P5n1kX-McpM'

# Admin ID
ADMIN_ID = 8411520144

# Clan chat ID yoki username (o'zgartiring)
CLAN_CHAT = '@uchiha_members'

# Uchiha clan a'zolari ro'yxati (rollar)
UCHIHA_ROLES = [
    "Madara Uchiha 🔥",
    "Izuna Uchiha ⚔️",
    "Itachi Uchiha 🦅",
    "Sasuke Uchiha ⚡",
    "Obito Uchiha 🌀",
    "Shisui Uchiha 🌊",
    "Fugaku Uchiha 👑",
    "Kagami Uchiha 🛡️",
    "Indra Otsutsuki 👁️",
    "Sarada Uchiha 📚",
    "Shin Uchiha 🧬",
    "Izumi Uchiha 💖",
    "Yashiro Uchiha 🏹",
    "Inabi Uchiha 🗡️"
]

# Ma'lumotlar saqlash fayli
DATA_FILE = 'clan_data.json'

# Ma'lumotlarni yuklash
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {role: [] for role in UCHIHA_ROLES}

# Ma'lumotlarni saqlash
def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Global data
clan_data = load_data()

# Foydalanuvchi clanda ekanligini tekshirish
def is_user_in_clan(user_id):
    for role, users in clan_data.items():
        for u in users:
            if u['id'] == user_id:
                return role, u
    return None, None

# User rolini topish
def get_user_role(user_id):
    for role, users in clan_data.items():
        for u in users:
            if u['id'] == user_id:
                return role
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    role, user_info = is_user_in_clan(user.id)
    
    if update.effective_chat.type in ['group', 'supergroup']:
        # Clan chat da /start
        await update.message.reply_text(
            f"👋 <b>Salom, {user.first_name}! Uchiha clani xush kelibsiz!</b>\n\n"
            f"Clan chat: <a href='https://t.me/{CLAN_CHAT[1:]}'>{CLAN_CHAT}</a>",
            parse_mode='HTML'
        )
        return
    
    if user.id == ADMIN_ID:
        keyboard = [
            [InlineKeyboardButton("📢 Barchaga xabar yuborish", callback_data="admin_broadcast")],
            [InlineKeyboardButton("📊 Ro'yxatni export qilish", callback_data="admin_export")],
            [InlineKeyboardButton("👥 Clan ro'yxati", callback_data="admin_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"👑 <b>Admin paneliga xush kelibsiz, {user.first_name}!</b>\n\n"
            "Quyidagi funksiyalardan foydalaning:",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    elif role:
        # Clanda bo'lsa
        keyboard = [
            [InlineKeyboardButton("🚪 Clanni tark etish", callback_data="leave_clan")],
            [InlineKeyboardButton("👥 Clan ro'yxati", callback_data="user_list")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        list_text = "👥 <b>Clan Ro'yxati:</b>\n\n"
        for r, users in clan_data.items():
            if users:
                list_text += f"<b>{r}:</b>\n"
                for u in users:
                    mention = f'<a href="tg://user?id={u["id"]}">{u["username"] or u["first_name"]}</a>'
                    list_text += f"• {mention}\n"
                list_text += "\n"
        await update.message.reply_text(
            f"🔥 <b>Siz {role} rolingizda Uchiha clani a'zosisiz!</b>\n\n{list_text}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    else:
        keyboard = [[InlineKeyboardButton("📝 Clanga ariza yuborish", callback_data="apply_clan")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"👋 <b>Salom, {user.first_name}!</b>\n\n"
            "Uchiha claniga xush kelibsiz! 🔥\n"
            "Clanga qo'shilish uchun quyidagi tugmani bosing.",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    if query.data == "apply_clan":
        keyboard = []
        for role in UCHIHA_ROLES:
            keyboard.append([InlineKeyboardButton(role, callback_data=f"role_{role}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🗡️ <b>Ro'lingizni tanlang:</b>\n\n"
            "Uchiha clanidagi buyuk jangchilardan birini tanlang!",
            parse_mode='HTML',
            reply_markup=reply_markup
        )

    elif query.data.startswith("role_"):
        selected_role = query.data.split("_", 1)[1]
        # Admin ga yuborish
        user_info = f"<b>Foydalanuvchi:</b> {user.mention_html()}\n"
        user_info += f"<b>ID:</b> <code>{user.id}</code>\n"
        user_info += f"<b>Tanlangan rol:</b> {selected_role}\n\n"
        user_info += "Qaror qabul qiling:"

        keyboard = [
            [
                InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{user.id}_{selected_role}"),
                InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user.id}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔥 <b>Clan uchun yangi so'rov!</b>\n\n{user_info}",
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        await query.edit_message_text(
            f"📤 <b>Arizangiz yuborildi!</b>\n\n"
            f"Admin ko'rib chiqmoqda... {selected_role} roliningiz uchun kutib turing. ⏳",
            parse_mode='HTML'
        )

    elif query.data.startswith("confirm_"):
        parts = query.data.split("_", 2)
        confirm_user_id = int(parts[1])
        role = parts[2]
        if is_user_in_clan(confirm_user_id)[0]:
            await query.edit_message_text("❌ Bu foydalanuvchi allaqachon ro'yxatda!")
            return
        # Foydalanuvchi ma'lumotlarini olish
        applicant = await context.bot.get_chat(confirm_user_id)
        clan_data[role].append({
            'id': confirm_user_id,
            'username': applicant.username or f"User_{confirm_user_id}",
            'first_name': applicant.first_name
        })
        save_data(clan_data)
        await context.bot.send_message(
            chat_id=confirm_user_id,
            text=f"🎉 <b>Tasdiqlandi!</b>\n\n"
            f"Siz endi Uchiha clani a'zosisiz! Rolingiz: {role} 🔥\n"
            f"Xush kelibsiz!",
            parse_mode='HTML'
        )
        await query.edit_message_text(
            f"✅ <b>{role} roliga qo'shildi!</b>\n\n"
            f"Foydalanuvchi: @{applicant.username or 'No username'} ({confirm_user_id})",
            parse_mode='HTML'
        )

    elif query.data.startswith("reject_"):
        reject_user_id = int(query.data.split("_", 1)[1])
        await context.bot.send_message(
            chat_id=reject_user_id,
            text="😔 <b>Arizangiz rad etildi.</b>\n\n"
            "Keyingi safar omad! Sabr qiling.",
            parse_mode='HTML'
        )
        await query.edit_message_text("❌ <b>Rad etildi!</b>", parse_mode='HTML')

    elif query.data == "leave_clan":
        role = get_user_role(user.id)
        if not role:
            await query.edit_message_text("❌ Siz clanda emassiz!")
            return
        for i, u in enumerate(clan_data[role]):
            if u['id'] == user.id:
                del clan_data[role][i]
                break
        save_data(clan_data)
        await query.edit_message_text(
            f"🚪 <b>Siz {role} roliningizdan chiqdingiz!</b>\n\n"
            "Clanga qaytish uchun ariza yuboring.",
            parse_mode='HTML'
        )

    elif query.data == "user_list":
        list_text = "👥 <b>Clan Ro'yxati:</b>\n\n"
        for r, users in clan_data.items():
            if users:
                list_text += f"<b>{r}:</b>\n"
                for u in users:
                    mention = f'<a href="tg://user?id={u["id"]}">{u["username"] or u["first_name"]}</a>'
                    list_text += f"• {mention}\n"
                list_text += "\n"
        await query.edit_message_text(list_text, parse_mode='HTML')

    elif query.data == "admin_broadcast":
        await query.edit_message_text(
            "📝 <b>Xabar matnini yuboring:</b>\n\n"
            "Bu xabar barcha clan a'zolariga yuboriladi.",
            parse_mode='HTML'
        )
        context.user_data['awaiting_broadcast'] = True

    elif query.data == "admin_export":
        # TXT fayl yaratish
        export_text = "📊 Uchiha Clan Ro'yxati\n\n"
        for role, users in clan_data.items():
            export_text += f"{role}:\n"
            for u in users:
                username = f"@{u['username']}" if u['username'] and not u['username'].startswith('@') else (f"@{u['username']}" if u['username'] else u['first_name'])
                export_text += f"• {username} (ID: {u['id']})\n"
            export_text += "\n"
        
        bio = BytesIO()
        bio.write(export_text.encode('utf-8'))
        bio.seek(0)
        await context.bot.send_document(
            chat_id=query.from_user.id,
            document=bio,
            filename='clan_ro_yxati.txt',
            caption="📄 Clan ro'yxati TXT fayl sifatida yuklandi!"
        )
        await query.edit_message_text("✅ Ro'yxat export qilindi va yuborildi!", parse_mode='HTML')

    elif query.data == "admin_list":
        list_text = "👥 <b>Clan Ro'yxati:</b>\n\n"
        for role, users in clan_data.items():
            if users:
                list_text += f"<b>{role}:</b>\n"
                for u in users:
                    mention = f'<a href="tg://user?id={u["id"]}">{u["username"] or u["first_name"]}</a>'
                    list_text += f"• {mention}\n"
                list_text += "\n"
            else:
                list_text += f"<b>{role}:</b> Bo'sh\n\n"
        await query.message.reply_text(list_text, parse_mode='HTML')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if context.user_data.get('awaiting_broadcast'):
        message_text = update.message.text
        sent_count = 0
        for role, users in clan_data.items():
            for u in users:
                try:
                    await context.bot.send_message(chat_id=u['id'], text=message_text, parse_mode='HTML')
                    sent_count += 1
                except:
                    pass
        await update.message.reply_text(f"📢 Xabar {sent_count} ta foydalanuvchiga yuborildi! ✅")
        context.user_data['awaiting_broadcast'] = False

async def royxat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Sizda ruxsat yo'q!")
        return
    list_text = "📋 <b>Clan Ro'yxati:</b>\n\n"
    for role, users in clan_data.items():
        if users:
            list_text += f"<b>{role}:</b>\n"
            for u in users:
                mention = f'<a href="tg://user?id={u["id"]}">{u["username"] or u["first_name"]}</a>'
                list_text += f"• {mention} (ID: {u['id']})\n"
            list_text += "\n"
        else:
            list_text += f"<b>{role}:</b> Bo'sh\n\n"
    await update.message.reply_text(list_text, parse_mode='HTML')

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("royxat", royxat))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    return application

if __name__ == '__main__':
    print("🤖 Bot ishga tushdi...")
    bot = main()
    bot.run_polling()