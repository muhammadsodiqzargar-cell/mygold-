import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# ⚠️ BOT TOKEN VA ADMIN ID
BOT_TOKEN = "8949282370:AAGin5wPZwJLqE5SA6KAJod4VA0QUy0Zj_0"
ADMIN_ID = 1341336380  # Telegram ID raqamingiz

# Do'kon ma'lumotlari
SHOP_NAME = "MyGold tilla do'koni"
SHOP_ADDRESS = "Toshkent shahri, Novza Oltin Markazi"
SHOP_CARD = "8600 0000 0000 0000 (MyGold Do'koni)"
SHOP_PHONE = "+998 90 123 45 67"
GROUP_LINK = "https://t.me/mygold_zargarlik_guruhi"

SHOP_LATITUDE = 41.292915
SHOP_LONGITUDE = 69.223297

# Boshlang'ich 1 gramm 999 proba oltin narxi (so'mda)
live_gold_price_999 = 1050000

bot = Bot(token=BOT_TOKEN.strip())
dp = Dispatcher()

# States
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

# ---------------------------------------------------------
# KLAVIATURALAR
# ---------------------------------------------------------
def get_main_menu(user_id: int):
    buttons = [
        [KeyboardButton(text="📈 Bugungi Oltin Narxlari")],
        [KeyboardButton(text="💸 Tillamni sotmoqchiman"), KeyboardButton(text="🛍 Tilla sotib olish")],
        [KeyboardButton(text="📍 Bizning Manzil")]
    ]
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton(text="⚙️ Narxni o'zgartirish (Admin)")])
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

# ---------------------------------------------------------
# ASOSIY MENYU TUGMALARI (ISTALGAN VAQTDA ISHLAYDI)
# ---------------------------------------------------------
@dp.message(CommandStart())
@dp.message(F.text == "⬅️ Bosh menyuga qaytish")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()  # Jarayonni zudlik bilan tozalaymiz
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}! 🌟\n"
        f"**'{SHOP_NAME}' Zargarlik Botiga xush kelibsiz!**\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=get_main_menu(message.from_user.id),
        parse_mode="Markdown"
    )

@dp.message(F.text == "📈 Bugungi Oltin Narxlari")
async def show_live_price(message: types.Message, state: FSMContext):
    await state.clear()
    p999 = live_gold_price_999
    p750 = int(p999 * 750 / 999)
    p585 = int(p999 * 585 / 999)
    
    await message.answer(
        f"📊 **Bugungi rasmiy oltin narxlari (1 gr uchun):**\n\n"
        f"• **583 / 585 proba:** {p585:,} so'm\n"
        f"• **750 proba:** {p750:,} so'm\n"
        f"• **999 proba:** {p999:,} so'm\n",
        reply_markup=get_main_menu(message.from_user.id),
        parse_mode="Markdown"
    )

@dp.message(F.text == "📍 Bizning Manzil")
async def show_contact_info(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(f"🏢 **{SHOP_NAME}**\n📍 **Manzil:** {SHOP_ADDRESS}\n📞 **Tel:** {SHOP_PHONE}")
    await message.answer_location(
        latitude=SHOP_LATITUDE, 
        longitude=SHOP_LONGITUDE, 
        reply_markup=get_main_menu(message.from_user.id)
    )

# ---------------------------------------------------------
# ADMIN: NARXNI O'ZGARTIRISH
# ---------------------------------------------------------
@dp.message(F.text == "⚙️ Narxni o'zgartirish (Admin)")
async def set_price_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.clear()
    await state.set_state(AdminState.waiting_for_new_price)
    await message.answer(
        f"📊 Hozirgi 1 gr (999 proba) oltin narxi: **{live_gold_price_999:,} so'm**\n\n"
        f"Yangi narxni kiriting (masalan: 1080000):", 
        parse_mode="Markdown"
    )

@dp.message(AdminState.waiting_for_new_price, F.text)
async def set_price_finish(message: types.Message, state: FSMContext):
    global live_gold_price_999
    if message.text.isdigit():
        live_gold_price_999 = int(message.text)
        await state.clear()
        await message.answer(
            f"✅ Bugungi oltin narxi **{live_gold_price_999:,} so'm** ga yangilandi!", 
            reply_markup=get_main_menu(message.from_user.id), 
            parse_mode="Markdown"
        )
    else:
        await message.answer("⚠️ Iltimos, faqat raqamlarda kiriting!")

# ---------------------------------------------------------
# SOTIB OLISH BO'LIMI (BUY GOLD)
# ---------------------------------------------------------
@dp.message(F.text == "🛍 Tilla sotib olish")
async def buy_gold_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🛍 **Tilla sotib olish bo'limi:**\n\nBo'limni tanlang:",
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

@dp.message(F.text == "📸 Rasmini tashlash")
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
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=f"📥 **Sotib olish bo'yicha so'rov!**\nMijoz: {username}\nIsmi: {message.from_user.full_name}",
            parse_mode="Markdown"
        )
        await message.answer("🔎 So'rovingiz adminga yuborildi. Tanlang:", reply_markup=buy_action_menu)
    else:
        await message.answer("⚠️ Avval rasm yuboring!", reply_markup=buy_menu)

@dp.message(F.text == "💳 Olmoqchiman, karta raqamizni tashavoring")
async def send_card_info(message: types.Message):
    await message.answer(
        f"💳 **Karta raqamimiz:**\n\n`{SHOP_CARD}`\n\n📍 Dostavka uchun lokatsiya yuboring!",
        parse_mode="Markdown"
    )

@dp.message(F.text == "📉 Narxini kelishtirib bering")
async def ask_discount(message: types.Message):
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📉 **Mijoz narxni kelishtirishni so'ramoqda!**\nMijoz: {username}",
        parse_mode="Markdown"
    )
    await message.answer("⏳ So'rov adminga yetkazildi. Tez orada javob beramiz.")

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
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=f"💰 **ZAKLAD TO'LANDI!**\nMijoz: {username}",
        parse_mode="Markdown"
    )
    await message.answer("✅ Chek qabul qilindi! Tez orada bog'lanamiz.", reply_markup=get_main_menu(message.from_user.id))
    await state.clear()

# ---------------------------------------------------------
# SOTISH BO'LIMI (TILLAMNI SOTMOQCHIMAN)
# ---------------------------------------------------------
@dp.message(F.text == "💸 Tillamni sotmoqchiman")
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
        proba = int(message.text)
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
    proba = user_data.get('proba', 585)
    photo = user_data.get('photo')
    condition = user_data.get('condition', '-')
    stone = message.text
    
    total_price = int(weight * (live_gold_price_999 * (proba / 999)))
    
    caption_text = (
        f"🧮 **Tilla Baholash Natijasi:**\n\n"
        f"⚖️ Og'irligi: **{weight} gr**\n"
        f"🔍 Proba: **{proba}**\n"
        f"🛠 Holati: **{condition}**\n"
        f"💎 Tosh: **{stone}**\n\n"
        f"💰 Tahminiy narximiz: **{total_price:,} so'm**"
    )
    
    if photo:
        await message.answer_photo(photo=photo, caption=caption_text, reply_markup=get_main_menu(message.from_user.id), parse_mode="Markdown")
    else:
        await message.answer(caption_text, reply_markup=get_main_menu(message.from_user.id), parse_mode="Markdown")
        
    await state.clear()

# ---------------------------------------------------------
# MUG'OMBIR / MASHG'UL XABARLAR VA MULOQOT (ENG PASTDA!)
# ---------------------------------------------------------
@dp.message(F.chat.type == "private", F.from_user.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user_from_admin(message: types.Message):
    try:
        if message.reply_to_message.forward_from:
            target_user_id = message.reply_to_message.forward_from.id
            await bot.send_message(chat_id=target_user_id, text=f"💬 **Menejer:**\n\n{message.text}", parse_mode="Markdown")
            await message.answer("✅ Javob yuborildi!")
        else:
            await message.answer("⚠️ Mijoz maxfiylik sozlamalari tufayli qayta javob yuborib bo'lmadi.")
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")

@dp.message(F.chat.type == "private", F.from_user.id != ADMIN_ID)
async def forward_user_messages_to_admin(message: types.Message):
    await message.forward(chat_id=ADMIN_ID)

# ---------------------------------------------------------
# ISHGA TUSHIRISH
# ---------------------------------------------------------
async def main():
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
