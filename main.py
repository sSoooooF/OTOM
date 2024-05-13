from aiogram.dispatcher import router
from aiogram.handlers import message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import Bot, types, Dispatcher
from aiogram.filters.command import Command
import asyncio
import sqlite3

token = '7029817281:AAHx7Na5_5VuwzMCreyPo0iFC6IiGt1V6zM'

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, phone_number TEXT)")


def save_contact(user_id, phone_number):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.execute("UPDATE users SET phone_number=? WHERE user_id=?", (phone_number, user_id))
    else:
        cursor.execute("INSERT INTO users (user_id, phone_number) VALUES (?,?)", (user_id, phone_number))
    conn.commit()



bot = Bot(token=token)
dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Отправить контакт", request_contact=True)
    )
    await bot.send_message(chat_id=message.chat.id, text="Привет, я бот ОТОМА")

    await message.answer(
        "Отправьте контактные данные",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@dp.message(Command("send"))
async def send_message_to_user(message: types.Message):
    args = message.get_args().split(" ")
    if len(args) < 2:
        await message.answer("Использование: /send_message user_id текст_сообщения")
        return

    try:
        user_id = int(args[0])
    except ValueError:
        await message.answer("Некорректный user_id. Пожалуйста, укажите целое число.")
        return

    text_message = " ".join(args[1:])
    try:
        await bot.send_message(chat_id=user_id, text=text_message)
        await message.answer("Сообщение успешно отправлено.")
    except Exception as e:
        await message.answer(f"Ошибка при отправке сообщения: {e}")


@dp.message()
async def handle_contact(msg: types.Message):
    user_id = msg.from_user.id
    phone_number = msg.contact.phone_number
    save_contact(user_id, phone_number)
    await msg.answer("Контакт сохранен")

async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

conn.close()
