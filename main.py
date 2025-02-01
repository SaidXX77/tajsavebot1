import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Токен Telegram-бота
BOT_TOKEN = "7253180468:AAHnefrBaS5NFlbbzpgmQDyR_Zm8xq_xfjE"
RAPIDAPI_KEY = "1411a5f8b2msh5f11f24b1b60b0bp12c234jsn47579b7838e8"

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# Функция для получения ссылки на видео из Instagram
def get_instagram_video(shortcode):
    url = "https://instagram-bulk-profile-scrapper.p.rapidapi.com/clients/api/ig/media_by_id"
    querystring = {"shortcode": shortcode}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "instagram-bulk-profile-scrapper.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()  # Преобразуем ответ в формат JSON

        # Отладочная печать для просмотра полного ответа API
        print("Ответ API:")
        print(data)

        try:
            # Проверяем, есть ли элементы в "items"
            if "items" in data[0] and len(data[0]["items"]) > 0:
                item = data[0]["items"][0]

                # Проверяем, есть ли "video_versions"
                if "video_versions" in item and len(item["video_versions"]) > 0:
                    video_url = item["video_versions"][0]["url"]
                    if video_url:
                        return video_url
                    else:
                        return "Видео не найдено в ответе API."
                else:
                    return "Видео не доступно в этом посте."
            else:
                return "Не удалось найти элементы в ответе API."

        except (KeyError, IndexError) as e:
            return f"Ошибка при обработке данных: {str(e)}"
    else:
        return f"Ошибка API: {response.status_code} - {response.text}"


# Обработчик команды /start
@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Привет! Отправь мне ссылку на Reels Instagram, и я помогу скачать его.")


# Обработчик текстовых сообщений
@dp.message_handler()
async def handle_message(message: types.Message):
    instagram_url = message.text.strip()

    # Проверка на корректность ссылки
    if "instagram.com/reel/" not in instagram_url:
        await message.reply("Пожалуйста, отправьте ссылку на Reels Instagram.")
        return

    # Извлечение shortcode из ссылки
    try:
        shortcode = instagram_url.split("/reel/")[1].split("/")[0]
    except IndexError:
        await message.reply("Не удалось извлечь идентификатор Reels. Проверьте ссылку.")
        return

    await message.reply("Загружаю видео, подождите...")

    # Получение ссылки на видео
    video_url = get_instagram_video(shortcode)
    if video_url.startswith("http"):
        await bot.send_video(chat_id=message.chat.id, video=video_url)
    else:
        await message.reply(f"Ошибка: {video_url}")


# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
