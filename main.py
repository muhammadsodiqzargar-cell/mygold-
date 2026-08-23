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

# Boshlang'ich 1 gramm 999 proba oltin narxi (Agar o'zgarsa, bot ichidan yangilaysiz)
live_gold_price_999 = 1050000

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Bosqichlar (FSM)
class SellGoldState(StatesGroup):
    waiting_for_photo = State()
    waiting_for_weight = State()
    waiting_for_proba = State()
    waiting_for_condition = State()
    waiting_for_stone_type = State()

class AdminState(StatesGroup):
    waiting_for_new_price = State()

# Do'kon ma'lumotlari
SHOP_NAME = "MyGold tilla do'koni"
SHOP_ADDRESS = "Toshkent shahri, Novza Oltin Markazi"

# Do'koningizning koordinatalari
SHOP_LATITUDE = 41.292915
SHOP_LONGITUDE = 69.223297

# Dinamik Bosh menyu (Admin uchun qo'shimcha tugma chiqadi)
def get_main_menu(user_id: int):
    buttons = [
        [KeyboardButton(text="📈 Bugungi Oltin Narxlari")],
        [KeyboardButton(text="💸 Tillamni sotmoqchiman"), KeyboardButton(text="🛍 Tilla sotib olish")],
        [KeyboardButton(text="📍 Bizning Manzil")]
    ]
    if user_id == ADMIN_ID:
        buttons.append([KeyboardButton(text="⚙️ Narxni o'zgartirish (Admin)")])
        
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Buyum holati menyusi
condition_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔨 Lom")],
        [KeyboardButton(text="✨ Eski tilla")],
        [KeyboardButton(text="🆕 Yangi tilla")]
    ],
    resize_keyboard=True
)

# Tosh hajmiga qarab menyu
stone_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💎 Toshsiz")],
        [KeyboardButton(text="✨ Mayda toshli")],
        [KeyboardButton(text="💍 Ko'p toshli")],
        [KeyboardButton(text="🔮 Katta toshli")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        f"Assalomu alaykum, {message.from_user.first_name}! 🌟\n\n"
        f"**'{SHOP_NAME}' Botiga xush kelibsiz!**\n"
        "Tillangizning holati, probasi va vazniga qarab baholab beraylikmi yoki tilla sotib olmoqchimisiz.",
        reply_markup=get_main_menu(message.from_user.id),
        parse_mode="Markdown"
    )

# ⚙️ ADMIN: Kunlik oltin narxini yangilash
@dp.message(F.text == "⚙️ Narxni o'zgartirish (Admin)")
async def set_price_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(AdminState.waiting_for_new_price)
    await message.answer(
        f"📊 Hozirgi 1 gramm (999 proba) narxi: **{live_gold_price_999:,} so'm**\n\n"
        f"Yangi narxni kiriting (masalan: **1060000**):",
        parse_mode="Markdown"
    )

@dp.message(AdminState.waiting_for_new_price)
async def set_price_finish(message: types.Message, state: FSMContext):
    global live_gold_price_999
    if message.text.isdigit():
        live_gold_price_999 = int(message.text)
        await state.clear()
        await message.answer(
            f"✅ Bugungi 999 proba oltin narxi **{live_gold_price_999:,} so'm** ga o'zgartirildi!\n"
            f"Barcha probalar va hisob-kitoblar yangilandi.",
            reply_markup=get_main_menu(message.from_user.id),
            parse_mode="Markdown"
        )
    else:
        await message.answer("⚠️ Iltimos, faqat raqam ko'rinishida kiriting! Masalan: 1050000")

@dp.message(F.text == "📈 Bugungi Oltin Narxlari")
async def show_live_price(message: types.Message):
    price_999 = live_gold_price_999
    
    price_375 = int(price_999 * (375 / 999))
    price_585 = int(price_999 * (585 / 999))
    price_750 = int(price_999 * (750 / 999))
    price_875 = int(price_999 * (875 / 999))
    price_916 = int(price_999 * (916 / 999))
    price_958 = int(price_999 * (958 / 999))
    
    await message.answer(
        f"📊 **Bugungi rasmiy oltin narxlari (1 gramm uchun):**\n\n"
        f"• **375 proba:** {price_375:,} so'm\n"
        f"• **583 / 585 proba:** {price_585:,} so'm\n"
        f"• **750 proba:** {price_750:,} so'm\n"
        f"• **875 proba:** {price_875:,} so'm\n"
        f"• **916 proba:** {price_916:,} so'm\n"
        f"• **958 proba:** {price_958:,} so'm\n"
        f"• **999 proba (Toza oltin):** {price_999:,} so'm\n\n"
        f"🔄 *Narxlar har kuni admin tomonidan do'konga moslab yangilanib boriladi.*",
        parse_mode="Markdown"
    )

# 📍 MANZIL VA GEOLOKATSIYA YUBORISH
@dp.message(F.text == "📍 Bizning Manzil")
async def show_contact_info(message: types.Message):
    await message.answer(
        f"🏢 **{SHOP_NAME}**\n\n"
        f"📍 **Manzil:** {SHOP_ADDRESS}\n"
        f"⏰ **Ish vaqti:** Har kuni 09:00 dan 20:00 gacha\n\n"
        f"👇 *Quyida do'konimizning xaritadagi joylashuvi:*",
        parse_mode="Markdown"
    )
    
    await message.answer_location(
        latitude=SHOP_LATITUDE,
        longitude=SHOP_LONGITUDE,
        reply_markup=get_main_menu(message.from_user.id)
    )

@dp.message(F.text == "💸 Tillamni sotmoqchiman")
async def start_sell(message: types.Message, state: FSMContext):
    await state.set_state(SellGoldState.waiting_for_photo)
    await message.answer("📸 Sotmoqchi bo'lgan tillangizning **rasmini yuboring**:")

@dp.message(SellGoldState.waiting_for_photo, F.photo)
async def get_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(SellGoldState.waiting_for_weight)
    await message.answer("⚖️ Buyumning umumiy vaznini kiriting (masalan: **5.5** gramm):")

@dp.message(SellGoldState.waiting_for_weight)
async def get_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text.replace(",", "."))
        await state.update_data(weight=weight)
        await state.set_state(SellGoldState.waiting_for_proba)
        await message.answer("🔍 Probani yozing (masalan: **585**, **750** yoki **583**):")
    except ValueError:
        await message.answer("⚠️ Iltimos, faqat raqam yozing! Masalan: 4.8")

@dp.message(SellGoldState.waiting_for_proba)
async def get_proba(message: types.Message, state: FSMContext):
    try:
        proba = int(message.text)
        await state.update_data(proba=proba)
        await state.set_state(SellGoldState.waiting_for_condition)
        await message.answer("🛠 **Tillangizning holatini tanlang:**", reply_markup=condition_menu)
    except ValueError:
        await message.answer("⚠️ Iltimos, probani to'g'ri kiriting (masalan: 585)!")

@dp.message(SellGoldState.waiting_for_condition)
async def get_condition(message: types.Message, state: FSMContext):
    await state.update_data(condition=message.text)
    await state.set_state(SellGoldState.waiting_for_stone_type)
    await message.answer("💎 **Buyumdagi tosh holatini tanlang:**", reply_markup=stone_menu)

@dp.message(SellGoldState.waiting_for_stone_type)
async def calculate_final_price(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    weight = user_data['weight']
    proba = user_data['proba']
    photo = user_data['photo']
    condition = user_data['condition']
    
    price_999 = live_gold_price_999
    base_gram_price = price_999 * (proba / 999)
    
    condition_coef = 1.0
    if condition == "🔨 Lom":
        condition_coef = 0.95
    elif condition == "✨ Eski tilla":
        condition_coef = 0.98
    elif condition == "🆕 Yangi tilla":
        condition_coef = 1.00

    stone_choice = message.text
    stone_minus_percent = 0.0

    if stone_choice == "✨ Mayda toshli":
        stone_minus_percent = 0.02
    elif stone_choice == "💍 Ko'p toshli":
        stone_minus_percent = 0.05
    elif stone_choice == "🔮 Katta toshli":
        stone_minus_percent = 0.10

    clean_weight = weight * (1 - stone_minus_percent)
    final_gram_price = base_gram_price * condition_coef
    total_price = int(clean_weight * final_gram_price)
    
    await message.answer_photo(
        photo=photo,
        caption=(
            f"🧮 **Tilla Baholash Natijasi:**\n\n"
            f"• Umumiy vazni: **{weight} gramm**\n"
            f"• Proba: **{proba}**\n"
            f"• Buyum holati: **{condition}**\n"
            f"• Tosh holati: **{stone_choice}**\n\n"
            f"💰 **Xarid qilish summasi (Taxminiy):**\n"
            f"👉 **{total_price:,} so'm**\n\n"
            f"📌 *Izoh: Aniq narx do'konda tekshirilgach tasdiqlanadi.*"
        ),
        reply_markup=get_main_menu(message.from_user.id),
        parse_mode="Markdown"
    )
    await state.clear()

@dp.message(F.text == "🛍 Tilla sotib olish")
async def buy_gold_info(message: types.Message):
    await message.answer(
        "🛍 **Do'konimizdan tilla sotib olish:**\n\n"
        "Bizda turli xil zargarlik buyumlari mavjud."
    )

async def main():
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
