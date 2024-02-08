import telebot
from telebot import types

TOKEN = ''  # Думаю зробити щоб токен зберігався файлом, в коді якось не кайф
bot = telebot.TeleBot(TOKEN)
 
user_inform = {} # словник, данні які вводить користувач попадають в нього
steps = {} # условні кроки по яким проходимся ( крок 1 - заголовок, після того як користувач вказав заголовок переключаємось на крок 2, це - імя юзера - і крок 3 - тема , по якій гпт буде генерувати статтю.) 

@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_menu = types.KeyboardButton('Генерація статті')
    markup.add(button_menu)
    bot.send_message(message.chat.id, "Привіт, я Jaba Project. За допомогою мене ти можеш згенерувати статтю на будь-яку тему!", reply_markup=markup)


# Ще не знаю як можна зібрати та зберегти інформацію кращим способом, так що буде поки що так.
# Ця функція базова, потім пізніше розберусь як її можна зробити кращим способом і перероблю її.
@bot.message_handler(func=lambda message: True)
def collect_user_info(message):
    chat_id = message.chat.id # щоб було комфортніше, бо message.chat.id довго писати і воно виглядає не дуже
    if message.text == "Генерація статті": # провірка якщо користувач клікнув на кнопку
            bot.send_message(message.chat.id, "Напишіть заголовок для теми")
            steps[chat_id] = 1 # встановлення першого кроку
            user_inform[chat_id] = {} # записуємо інфу в словник, далі те що в низу кода повторяється, поки користувач не заповне данні.
    elif steps.get(chat_id) == 1:
            user_inform[chat_id]['title'] = message.text
            bot.send_message(chat_id, "Добре. Тепер відправте ваше імя (воно буде вказано в якості автора статті)")
            steps[chat_id] = 2
    elif steps.get(chat_id) == 2:
            user_inform[chat_id]['Your name'] = message.text
            bot.send_message(chat_id, "Залишилось відправenити тему для статті")
            steps[chat_id] = 3
    elif steps.get(chat_id) == 3:
            user_inform[chat_id]['Your story'] = message.text
            bot.send_message(chat_id, "Бот отримав твою інформацію. Далі в розробці. \nДля перевірки роботоспосоності список відравлений нижче:") # Відправка списку буде потім реалізована




if __name__ == '__main__':
    bot.infinity_polling()