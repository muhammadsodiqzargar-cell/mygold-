import re
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# =========================================================
# ⚠️ BOT TOKEN VA ID SOZLAMALARI
# =========================================================
BOT_TOKEN = "8949282370:AAGin5wPZwJLqE5SA6KAJod4VA0QUy0Zj_0"  # Telegram Bot Tokeningiz
ADMIN_ID = 123456789          # Sizning shaxsiy Telegram ID-singiz
GROUP_ID = -1001234567890     # Tilla guruhingizning ID-si

# Do'koningiz ma'lumotlari
SHOP_NAME = "MyGold tilla do'koni"
SHOP_ADDRESS = "Toshkent shahri, Novza Oltin Markazi"
SHOP_CARD = "8600 0000 0000 0000"
SHOP_PHONE = "+998 90 123 45 67"
GROUP_LINK = "https://t.me/your_group_link"

SHOP_LATITUDE = 41.292915
SHOP_LONGITUDE = 69.223297

# =========================================================
# DINAMIK NARX XOTIRASI
# (Guruhga har kuni yangi narx tashlansa avtomatik yangilanadi,
#  tashlanmasa oxirgi saqlangan narx bo'yicha hisoblayveradi)
# =========================================================
live_prices = {
    "updated_at": None,
    "full_text": None,
    "parsed_rates": {
        "585": 780000,
        "750": 1000000,
        "999": 1650000
    }
}

bot = Bot(token=BOT_TOKEN.strip())
dp = Dispatcher()

# States (Bosqichlar)
class SellGoldState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_weight = State()
    waiting_for_proba = State()
    waiting_for_condition = State()
    waiting_for_stone_type = State()

class BuyGoldState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_receipt = State()

class AdminState(StatesGroup):
    waiting_for_new_price = State()

# =========================================================
# KLAVIATURALAR
# =========================================================
def get_main_menu(user_id: int):
    buttons = [
        [KeyboardButton(text="💰 Sotib olish"), KeyboardButton(text="💸 Tilla sotish")],
        [KeyboardButton(text="📈 Bugungi narx"), KeyboardButton(text="🚚 Yetkazib berish")],
        [KeyboardButton(text="🖼 Katalog / Buyumlar")],
        [KeyboardButton(text="📍 Bizning manzil"), KeyboardButton(text="⚙️ Sozlamalar")]
    ]
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton(text="⚙️ Narxni yangilash (Admin)")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

buy_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📸 Rasmini tashlash")],
        [KeyboardButton(text="👥 Guruh ssilkasi")],
        [KeyboardButton(text="⬅️ Bosh menyuga qaytish")]
    ],
    resize_keyboard=True
)

check_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔎 Bundan bor yoki yo'q?")],
        [KeyboardButton(text="⬅️ Bosh menyuga qaytish")]
    ],
    resize_keyboard=True
)

buy_action_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💳 Olmoqchiman, karta raqamizni tashavoring")],
        [KeyboardButton(text="📉 Narxini kelishtirib bering")],
        [KeyboardButton(text="🤝 Zaklad tashamoqchiman")],
        [KeyboardButton(text="⬅️ Bosh menyuga qaytish")]
    ],
    resize_keyboard=True
)

condition_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔨 Lom"), KeyboardButton(text="✨ Eski tilla"), KeyboardButton(text="🆕 Yangi tilla")],
        [KeyboardButton(text="⬅️ Bosh menyuga qaytish")]
    ],
    resize_keyboard=True
)

stone_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💎 Toshsiz"), KeyboardButton(text="✨ Mayda toshli")],
        [KeyboardButton(text="💍 Ko'p toshli"), KeyboardButton(text="🔮 Katta toshli")],
        [KeyboardButton(text="⬅️ Bosh menyuga qaytish")]
    ],
    resize_keyboard=True
)

# =========================================================
# GURUHINGIZDAN KUNLIK NARXNI TUSHIRIB OLISH
# =========================================================
@dp.message(F.chat.id == GROUP_ID)
async def catch_group_price(message: types.Message):
    global live_prices
    text = message.text or message.caption
    if not text:
        return

    # Guruhga har kuni e'lon tashlanganda avtomatik tutib oladi
    if "ТИЛЛА СОТИБ ОЛАМИЗ" in text or "585°" in text or "#narx" in text.lower():
        live_prices["full_text"] = text
        live_prices["updated_at"] = datetime.now().strftime("%d.%m.%Y %H:%M")

        # Matn ichidan 585, 750, 999 va boshqa proba narxlarini qidirib topadi
        rates = re.findall(r'(\d{3})[°\s]*[-–—:]*\s*([\d\.]+)', text)
        parsed = {}
        for proba, price_str in rates:
            clean_price = int(price_str.replace('.', ''))
            parsed[proba] = clean_price

        if parsed:
            live_prices["parsed_rates"].update(parsed)

        await message.reply("✅ Bugungi yangi narxlar bot bazasiga saqlandi!")

# =========================================================
# ASOSIY MENYU BUYRUQLARI
# =========================================================
@dp.message(CommandStart())
@dp.message(F.text == "⬅️ Bosh menyuga qaytish")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}! 🌟\n"
        f"**'{SHOP_NAME}' Botiga xush kelibsiz!**\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=get_main_menu(message.from_user.id),
        parse_mode="Markdown"
    )

@dp.message(F.text == "📈 Bugungi narx")
async def show_live_price(message: types.Message, state: FSMContext):
    await state.clear()
    if live_prices["full_text"]:
        msg = (
            f"📅 **Oxirgi yangilangan vaqt:** {live_prices['updated_at']}\n\n"
            f"{live_prices['full_text']}"
        )
    else:
        rates = live_prices["parsed_rates"]
        msg = (
            f"📊 **Bugungi rasmiy oltin narxlari:**\n\n"
            f"• **583 / 585 proba:** {rates.get('585', 0):,} so'm\n"
            f"• **750 proba:** {rates.get('750', 0):,} so'm\n"
            f"• **999 proba:** {rates.get('999', 0):,} so'm\n"
        )
    
    await message.answer(msg, reply_markup=get_main_menu(message.from_user.id), parse_mode="Markdown")

@dp.message(F.text == "📍 Bizning manzil")
async def show_contact_info(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"🏢 **{SHOP_NAME}**\n📍 **Manzil:** {SHOP_ADDRESS}\n📞 **Tel:** {SHOP_PHONE}")
    await message.answer_location(
        latitude=SHOP_LATITUDE, 
        longitude=SHOP_LONGITUDE, 
        reply_markup=get_main_menu(message.from_user.id)
    )

@dp.message(F.text == "🚚 Yetkazib berish va To'lov")
async def show_delivery_info(message: types.Message):
    msg = (
        "🚚 **Yetkazib berish:**\n"
        "• O'zbekiston bo'ylab yetkazib berish xizmati mavjud.\n"
        "• Viloyatlarga pochtadan xavfsiz yetkaziladi.\n\n"
        "💳 **To'lov usullari:**\n"
        "• Naqd pul yoki Karta orqali (Click/Payme).\n"
        "• Joyida ko'rib to'lov qilish imkoniyati."
    )
    await message.answer(msg)

@dp.message(F.text == "⚙️ Sozlamalar")
async def show_settings(message: types.Message):
    await message.answer("⚙️ **Sozlamalar bo'limi:**\n\nHozircha bot o'zbek tilida ishlamoqda.")

# =========================================================
# ADMIN: QO'LDA NARX O'ZGARTIRISH
# =========================================================
@dp.message(F.text == "⚙️ Narxni yangilash (admin)")
async def set_price_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await state.set_state(AdminState.waiting_for_new_price)
    await message.answer(
        f"📊 Hozirgi 1 gr (585 proba) narxi: **{live_prices['parsed_rates'].get('585', 0):,} so'm**\n\n"
        f"Yangi 585 proba narxini kiriting (masalan: 790000):", 
        parse_mode="Markdown"
    )

@dp.message(AdminState.waiting_for_new_price, F.text)
async def set_price_finish(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        new_price = int(message.text)
        live_prices["parsed_rates"]["585"] = new_price
        live_prices["updated_at"] = datetime.now().strftime("%d.%m.%Y %H:%M")
        await state.clear()
        await message.answer(
            f"✅ 585 proba narxi **{new_price:,} so'm** ga yangilandi!", 
            reply_markup=get_main_menu(message.from_user.id), 
            parse_mode="Markdown"
        )
    else:
        await message.answer("⚠️ Iltimos, faqat raqamlarda kiriting!")

# =========================================================
# SOTIB OLISH BO'LIMI (HARIDOR VA KATALOG)
# =========================================================
@dp.message(F.text == "💰 Sotib olish")
@dp.message(F.text == "🖼 Katalog / Buyumlar")
async def buy_gold_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🛍 **Tilla sotib olish va Katalog bo'limi:**\n\nBo'limni tanlang:",
        reply_markup=buy_menu,
        parse_mode="Markdown"
    )

@dp.message(F.text == "👥 Guruh ssilkasi")
async def send_group_link(message: types.Message):
    await message.answer(
        f"👥 **Bizning rasmiy guruhimiz:**\n\n👉 [Guruhga kirish]({GROUP_LINK})",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@dp.message(F.text == "📸 Olmoqchi bo'lgan tilangizni rasmini tashlash")
async def ask_buy_photo(message: types.Message, state: FSMContext):
    await state.set_state(BuyGoldState.waiting_for_photo)
    await message.answer("📸 Sotib olmoqchi bo'lgan tillangiz rasmini yuboring:")

@dp.message(BuyGoldState.waiting_for_photo, F.photo)
async def receive_buy_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(buy_photo=file_id)
    await message.answer("✅ Rasm qabul qilindi!", reply_markup=check_menu)

@dp.message(F.text == "🔎 Bundan bor yoki yo'q?")
async def check_availability(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    photo_id = user_data.get('buy_photo')
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    
    if photo_id:
        # Adminga boradigan so'rov
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=(
                f"📥 **SOTIB OLISH SO'ROVI!**\n\n"
                f"👤 Mijoz: {username}\n"
                f"📛 Ismi: {message.from_user.full_name}\n"
                f"❓ Savol: *\"Shu buyumdan bormi?\"*"
            ),
            parse_mode="Markdown"
        )
        await message.answer("🔎 So'rovingiz adminga yuborildi. Tanlang:", reply_markup=buy_action_menu)
    else:
        await message.answer("⚠️ Avval rasm yuboring!", reply_markup=buy_menu)

@dp.message(F.text == "💳 Olmoqchiman, karta raqamizni tashavoring")
async def send_card_info(message: types.Message):
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🛒 **HARIDOR KARTA SO'RADI!**\n\nMijoz: {username}\nIsmi: {message.from_user.full_name}",
        parse_mode="Markdown"
    )
    
    await message.answer(
        f"💳 **Karta raqamimiz:**\n\n`{SHOP_CARD}`\n\n📍 Dostavka uchun lokatsiya yuboring!",
        parse_mode="Markdown"
    )

@dp.message(F.text == "📉 Narxini kelishtirib bering")
async def ask_discount(message: types.Message):
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📉 **Mijoz narxni kelishtirishni so'ramoqda!**\nMijoz: {username}\nIsmi: {message.from_user.full_name}",
        parse_mode="Markdown"
    )
    await message.answer("⏳ So'rov adminga yetkazildi. Tez orada siz bilan bog'lanamiz.")

@dp.message(F.text == "🤝 Zaklad tashamoqchiman")
async def send_deposit_info(message: types.Message, state: FSMContext):
    await state.set_state(BuyGoldState.waiting_for_receipt)
    await message.answer(
        f"💳 **Karta raqamimiz:**\n\n`{SHOP_CARD}`\n\n📸 **To'lov cheki rasmini yuboring:**",
        parse_mode="Markdown"
    )

@dp.message(BuyGoldState.waiting_for_receipt, F.photo)
async def receive_receipt(message: types.Message, state: FSMContext):
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    
    # Adminga chek rasmi va ma'lumot yetkaziladi
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=(
            f"💰 **ZAKLAD TO'LANDI (CHEK)!**\n\n"
            f"👤 Mijoz: {username}\n"
            f"📛 Ismi: {message.from_user.full_name}"
        ),
        parse_mode="Markdown"
    )
    await message.answer("✅ Chek qabul qilindi! Murojaatingiz adminga yetkazildi.", reply_markup=get_main_menu(message.from_user.id))
    await state.clear()

# =========================================================
# SOTISH BO'LIMI (MIJOZDAN TILLA SOTIB OLISH)
# =========================================================
@dp.message(F.text == "💸 Tilla sotish")
async def start_sell(message: types.Message, state: FSMContext):
    await state.clear()
    await state.set_state(SellGoldState.waiting_for_photo)
    await message.answer(
        "📸 Sotmoqchi bo'lgan tillangiz **rasmini yuboring**:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⬅️ Bosh menyuga qaytish")]],
            resize_keyboard=True
        )
    )

@dp.message(SellGoldState.waiting_for_photo, F.photo)
async def get_sell_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(SellGoldState.waiting_for_weight)
    await message.answer("⚖️ Tillangiz vaznini kiriting (masalan: 5.5):")

@dp.message(SellGoldState.waiting_for_weight, F.text)
async def get_sell_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text.replace(",", "."))
        await state.update_data(weight=weight)
        await state.set_state(SellGoldState.waiting_for_proba)
        await message.answer("🔍 Probani kiriting (masalan: 585 yoki 750):")
    except ValueError:
        await message.answer("⚠️ Iltimos, faqat raqam ko'rinishida yozing! (Masalan: 5.5)")

@dp.message(SellGoldState.waiting_for_proba, F.text)
async def get_sell_proba(message: types.Message, state: FSMContext):
    try:
        proba = str(int(message.text))
        await state.update_data(proba=proba)
        await state.set_state(SellGoldState.waiting_for_condition)
        await message.answer("🛠 Holatini tanlang:", reply_markup=condition_menu)
    except ValueError:
        await message.answer("⚠️ Iltimos, probani raqamlarda kiriting! (Masalan: 585)")

@dp.message(SellGoldState.waiting_for_condition, F.text)
async def get_sell_condition(message: types.Message, state: FSMContext):
    await state.update_data(condition=message.text)
    await state.set_state(SellGoldState.waiting_for_stone_type)
    await message.answer("💎 Tosh holatini tanlang:", reply_markup=stone_menu)

@dp.message(SellGoldState.waiting_for_stone_type, F.text)
async def calculate_final_price(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    weight = user_data.get('weight', 0)
    proba = str(user_data.get('proba', '585'))
    photo = user_data.get('photo')
    condition = user_data.get('condition', '-')
    stone = message.text
    
    # Oxirgi saqlangan narxlardan hisoblaydi
    parsed_rates = live_prices["parsed_rates"]
    
    if proba in parsed_rates:
        gram_price = parsed_rates[proba]
    else:
        base_585 = parsed_rates.get("585", 780000)
        gram_price = int(base_585 * (int(proba) / 585))
    
    total_price = int(weight * gram_price)
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    
    caption_text = (
        f"🧮 **Tilla Baholash Natijasi:**\n\n"
        f"⚖️ Og'irligi: **{weight} gr**\n"
        f"🔍 Proba: **{proba}**\n"
        f"🛠 Holati: **{condition}**\n"
        f"💎 Tosh: **{stone}**\n\n"
        f"💰 Tahminiy narximiz: **{total_price:,} so'm**"
    )
    
    # Mijozga ko'rsatish
    if photo:
        await message.answer_photo(photo=photo, caption=caption_text, reply_markup=get_main_menu(message.from_user.id), parse_mode="Markdown")
    else:
        await message.answer(caption_text, reply_markup=get_main_menu(message.from_user.id), parse_mode="Markdown")

    # ADMINGA HAM XABAR BORADI (Kassa va sotuvlar hisobida ko'rinib turishi uchun)
    admin_caption = (
        f"📥 **MIJOZ TILLA SOTMOQCHI!**\n\n"
        f"👤 Mijoz: {username}\n"
        f"📛 Ismi: {message.from_user.full_name}\n"
        f"⚖️ Og'irligi: {weight} gr | Proba: {proba}\n"
        f"🛠 Holati: {condition} | Tosh: {stone}\n"
        f"💰 Hisoblangan baho: **{total_price:,} so'm**"
    )
    if photo:
        await bot.send_photo(chat_id=ADMIN_ID, photo=photo, caption=admin_caption, parse_mode="Markdown")
    else:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_caption, parse_mode="Markdown")
        
    await state.clear()

# =========================================================
# ADMIN VA MIJOZ O'RTASIDAGI CHAT (FORWARD TIZIMI)
# =========================================================
@dp.message(F.chat.type == "private", F.from_user.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user_from_admin(message: types.Message):
    try:
        if message.reply_to_message.forward_from:
            target_user_id = message.reply_to_message.forward_from.id
            await bot.send_message(chat_id=target_user_id, text=f"💬 **Menejer:**\n\n{message.text}", parse_mode="Markdown")
            await message.answer("✅ Javob yuborildi!")
        else:
            await message.answer("⚠️ Mijoz Telegram maxfiylik sozlamalari tufayli to'g'ridan-to'g'ri javob yuborib bo'lmadi.")
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")

@dp.message(F.chat.type == "private", F.from_user.id != ADMIN_ID)
async def forward_user_messages_to_admin(message: types.Message):
    # Mijoz oddiy matn yozsa ham adminga boradi
    await message.forward(chat_id=ADMIN_ID)

# =========================================================
# BOTNI ISHGA TUSHIRISH
# =========================================================
async def main():
    print("MyGold boti muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
