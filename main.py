import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

# ⚠️ UMBURG’I: BotFather bergan tokeningizni shu yerga yozing!
BOT_TOKEN = "8949282370:AAGin5wPZwJLqE5SA6KAJod4VA0QUy0Zj_0"

# ⚠️ ADMIN SOZLAMALARI:
# Telegram'dagi @my_id_bot ga kirib ID raqamingizni oling va shu yerga yozing (masalan: 123456789)
ADMIN_ID = 1341336380

# Do'kon ma'lumotlari
SHOP_NAME = "MyGold tilla do'koni"
SHOP_ADDRESS = "Toshkent shahri, Novza Oltin Markazi"
SHOP_CARD = "8600 0000 0000 0000 (MyGold Do'koni)"
SHOP_PHONE = "+998 90 123 45 67"
GROUP_LINK = "https://t.me/mygold_zargarlik_guruhi" # O'zingizning guruh havolangizni yozing

SHOP_LATITUDE = 41.292915
SHOP_LONGITUDE = 69.223297

# Boshlang'ich 1 gramm 999 proba oltin narxi
live_gold_price_999 = 1050000

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# FSM Bosqichlari
class SellGoldState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_weight = State()
    waiting_for_proba = State()
    waiting_for_condition = State()
    waiting_for_stone_type = State()

class BuyGoldState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_check_btn = State()
    waiting_for_receipt = State()

class AdminState(StatesGroup):
    waiting_for_new_price = State()

# ---------------------------------------------------------
# MENYULAR
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
        [KeyboardButton(text="🔨 Lom")],
        [KeyboardButton(text="✨ Eski tilla")],
        [KeyboardButton(text="🆕 Yangi tilla")]
    ],
    resize_keyboard=True
)

stone_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💎 Toshsiz")],
        [KeyboardButton(text="✨ Mayda toshli")],
        [KeyboardButton(text="💍 Ko'p toshli")],
        [KeyboardButton(text="🔮 Katta toshli")]
    ],
    resize_keyboard=True
)

# ---------------------------------------------------------
# START VA ASOSIY BUYRUQLAR
# ---------------------------------------------------------
@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}! 🌟\n\n"
        f"**'{SHOP_NAME}' ga xush kelibsiz!**\n"
        "Tillangizning holati, probasi va vazniga qarab baholab beraylikmi yoki tilla sotib olmoqchimisiz.",
        reply_markup=get_main_menu(message.from_user.id),
        parse_mode="Markdown"
    )

@dp.message(F.text == "⬅️ Bosh menyuga qaytish")
async def back_to_main(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Bosh menyu:", reply_markup=get_main_menu(message.from_user.id))

# ---------------------------------------------------------
# SOTIB OLISH BO'LIMI (BUY GOLD)
# ---------------------------------------------------------
@dp.message(F.text == "🛍 Tilla sotib olish")
async def buy_gold_start(message: types.Message):
    await message.answer(
        "🛍 **Tilla sotib olish bo'limiga xush kelibsiz!**\n\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=buy_menu,
        parse_mode="Markdown"
    )

@dp.message(F.text == "👥 Guruh ssilkasi")
async def send_group_link(message: types.Message):
    await message.answer(
        f"👥 **Bizning rasmiy tilla buyumlar guruhimiz:**\n\n"
        f"👉 [Guruhga kirish uchun bosing]({GROUP_LINK})",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@dp.message(F.text == "📸 Rasmini tashlash")
async def ask_buy_photo(message: types.Message, state: FSMContext):
    await state.set_state(BuyGoldState.waiting_for_photo)
    await message.answer("📸 Sotib olmoqchi bo'lgan tillangizning rasmini tashlang:")

@dp.message(BuyGoldState.waiting_for_photo, F.photo)
async def receive_buy_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(BuyGoldState.waiting_for_check_btn)
    await message.answer("Rasm qabul qilindi. Pastdagi tugmani bosing:", reply_markup=check_menu)

@dp.message(BuyGoldState.waiting_for_check_btn, F.text == "🔎 Bundan bor yoki yo'q?")
async def check_availability(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    photo_id = user_data.get('photo')
    username = f"@{message.from_user.username}" if message.from_user.username else "Username yo'q"
    
    # Adminga xabar yuboriladi (Faqat username ko'rsatiladi)
    if photo_id:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=f"📥 **Yangi buyurtma so'rovi!**\nMijoz: {username}",
            parse_mode="Markdown"
        )
    
    await message.answer(
        "🔎 **Buyum do'konimizda mavjudligini tekshirmoqdamiz...**\n\n"
        "Menejerimiz tez orada javob beradi yoki quyidagi variantlardan birini tanlang:",
        reply_markup=buy_action_menu,
        parse_mode="Markdown"
    )

@dp.message(F.text == "💳 Olmoqchiman, karta raqamizni tashavoring")
async def send_card_info(message: types.Message):
    await message.answer(
        f"💳 **Do'konimizning karta raqami:**\n\n"
        f"`{SHOP_CARD}`\n\n"
        f"📍 Buyurtma berish (Yandex) uchun iltimos lokatsiyangizni tashlab bering!",
        parse_mode="Markdown"
    )

@dp.message(F.text == "📉 Narxini kelishtirib bering")
async def ask_discount_from_admin(message: types.Message):
    username = f"@{message.from_user.username}" if message.from_user.username else "Username yo'q"
    
    # Adminga narxni kelishtirish so'rovini yuborish
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📉 **Mijoz narxni kelishtirishni so'ramoqda!**\nMijoz: {username}\n\n⚠️ *Iltimos, ushbu xabarga 'Reply' qilib eng taqalgan narxini ham ayting!*",
        parse_mode="Markdown"
    )
    await message.answer("⏳ So'rovingiz menejerga yetkazildi. Tez orada sizga eng taqalgan narxi aytiladi.")

@dp.message(F.text == "🤝 Zaklad tashamoqchiman")
async def send_deposit_info(message: types.Message, state: FSMContext):
    await state.set_state(BuyGoldState.waiting_for_receipt)
    await message.answer(
        f"💳 **Zaklad uchun do'konimiz karta raqami:**\n\n"
        f"`{SHOP_CARD}`\n\n"
        f"📸 **To'lov qilganingizni bilishimiz uchun chek rasmini shu yerga tashlang!**",
        parse_mode="Markdown"
    )

@dp.message(BuyGoldState.waiting_for_receipt, F.photo)
async def receive_receipt(message: types.Message, state: FSMContext):
    username = f"@{message.from_user.username}" if message.from_user.username else "Username yo'q"
    
    # Chek rasmini Adminga yuborish
    await bot.send_photo(
        chat_id=ADMIN_ID,
        photo=message.photo[-1].file_id,
        caption=f"💰 **ZAKLAD TO'LOVI QILINDI!**\nMijoz: {username}\n\nCheck rasm tepada.",
        parse_mode="Markdown"
    )
    
    await message.answer(
        "✅ **To'lov chekingiz qabul qilindi!**\n\n"
        "Menejerimiz to'lovni tasdiqlagach siz bilan bog'lanadi.",
        reply_markup=get_main_menu(message.from_user.id)
    )
    await state.clear()

# ---------------------------------------------------------
# ADMIN MONITORING VA JAVOB BERISH TIZIMI
# ---------------------------------------------------------
@dp.message(F.chat.type == "private", F.from_user.id != ADMIN_ID)
async def forward_user_messages_to_admin(message: types.Message):
    await message.forward(chat_id=ADMIN_ID)

@dp.message(F.chat.type == "private", F.from_user.id == ADMIN_ID, F.reply_to_message)
async def reply_to_user_from_admin(message: types.Message):
    try:
        if message.reply_to_message.forward_from:
            target_user_id = message.reply_to_message.forward_from.id
            await bot.send_message(chat_id=target_user_id, text=message.text)
            await message.answer("✅ Javobingiz mijozga yetkazildi!")
        else:
            await message.answer("⚠️ Ushbu xabarga javob qaytarib bo'lmadi (Mijoz maxfiylik sozlamalari tufayli).")
    except Exception as e:
        await message.answer(f"⚠️ Xatolik yuz berdi: {e}")

# ---------------------------------------------------------
# BOSHQA BO'LIMLAR (TILLAMNI SOTMOQCHIMAN VA ADMIN)
# ---------------------------------------------------------
@dp.message(F.text == "⚙️ Narxni o'zgartirish (Admin)")
async def set_price_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminState.waiting_for_new_price)
    await message.answer(f"📊 Hozirgi 1 gr (999 proba) narxi: **{live_gold_price_999:,} so'm**\nYangi narxni kiriting:", parse_mode="Markdown")

@dp.message(AdminState.waiting_for_new_price)
async def set_price_finish(message: types.Message, state: FSMContext):
    global live_gold_price_999
    if message.text.isdigit():
        live_gold_price_999 = int(message.text)
        await state.clear()
        await message.answer(f"✅ Bugungi oltin narxi **{live_gold_price_999:,} so'm** ga yangilandi!", reply_markup=get_main_menu(message.from_user.id), parse_mode="Markdown")

@dp.message(F.text == "📈 Bugungi Oltin Narxlari")
async def show_live_price(message: types.Message):
    p999 = live_gold_price_999
    await message.answer(
        f"📊 **Bugungi rasmiy oltin narxlari (1 gr uchun):**\n\n"
        f"• **583 / 585 proba:** {int(p999 * 585 / 999):,} so'm\n"
        f"• **750 proba:** {int(p999 * 750 / 999):,} so'm\n"
        f"• **999 proba:** {p999:,} so'm\n",
        parse_mode="Markdown"
    )

@dp.message(F.text == "📍 Bizning Manzil")
async def show_contact_info(message: types.Message):
    await message.answer(f"🏢 **{SHOP_NAME}**\n📍 **Manzil:** {SHOP_ADDRESS}")
    await message.answer_location(latitude=SHOP_LATITUDE, longitude=SHOP_LONGITUDE, reply_markup=get_main_menu(message.from_user.id))

@dp.message(F.text == "💸 Tillamni sotmoqchiman")
async def start_sell(message: types.Message, state: FSMContext):
    await state.set_state(SellGoldState.waiting_for_photo)
    await message.answer("📸 Sotmoqchi bo'lgan tillangizning **rasmini yuboring**:")

@dp.message(SellGoldState.waiting_for_photo, F.photo)
async def get_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(SellGoldState.waiting_for_weight)
    await message.answer("⚖️ Vaznini kiriting (masalan: 5.5):")

@dp.message(SellGoldState.waiting_for_weight)
async def get_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text.replace(",", "."))
        await state.update_data(weight=weight)
        await state.set_state(SellGoldState.waiting_for_proba)
        await message.answer("🔍 Probani yozing (masalan: 585):")
    except ValueError:
        await message.answer("⚠️ Iltimos, raqam yozing!")

@dp.message(SellGoldState.waiting_for_proba)
async def get_proba(message: types.Message, state: FSMContext):
    try:
        proba = int(message.text)
        await state.update_data(proba=proba)
        await state.set_state(SellGoldState.waiting_for_condition)
        await message.answer("🛠 Holatini tanlang:", reply_markup=condition_menu)
    except ValueError:
        await message.answer("⚠️ Iltimos, probani raqamda kiriting!")

@dp.message(SellGoldState.waiting_for_condition)
async def get_condition(message: types.Message, state: FSMContext):
    await state.update_data(condition=message.text)
    await state.set_state(SellGoldState.waiting_for_stone_type)
    await message.answer("💎 Tosh holatini tanlang:", reply_markup=stone_menu)

@dp.message(SellGoldState.waiting_for_stone_type)
async def calculate_final_price(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    weight = user_data['weight']
    proba = user_data['proba']
    photo = user_data['photo']
    condition = user_data['condition']
    
    total_price = int(weight * (live_gold_price_999 * (proba / 999)))
    await message.answer_photo(
        photo=photo,
        caption=f"🧮 **Tilla Baholash Natijasi:**\nVazni: {weight} gr | Proba: {proba}\n💰 Summa: **{total_price:,} so'm**",
        reply_markup=get_main_menu(message.from_user.id),
        parse_mode="Markdown"
    )
    await state.clear()

async def main():
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
