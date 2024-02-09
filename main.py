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
    generate_settings = types.KeyboardButton('Налаштування генерації', callback_data = 'generate_settings')
    markup.add(button_menu, generate_settings)
    bot.send_message(message.chat.id, "Привіт, я Jaba Project. За допомогою мене ти можеш згенерувати статтю на будь-яку тему!", reply_markup=markup)


# Ще не знаю як можна зібрати та зберегти інформацію кращим способом, так що буде поки що так.
# Ця функція базова, потім пізніше розберусь як її можна зробити кращим способом і перероблю її.
@bot.message_handler(func=lambda message: True)
def collect_user_info(message):
    chat_id = message.chat.id
    if message.text == "Генерація статті":
        bot.send_message(chat_id, "Напишіть заголовок для теми")
        steps[chat_id] = 1
        user_inform[chat_id] = {}
    elif steps.get(chat_id) == 1:
        user_inform[chat_id]['title'] = message.text
        bot.send_message(chat_id, "Добре. Тепер відправте ваше імя (воно буде вказано в якості автора статті)")
        steps[chat_id] = 2
    elif steps.get(chat_id) == 2:
        user_inform[chat_id]['Your name'] = message.text
        bot.send_message(chat_id, "Залишилось відправити тему для статті")
        steps[chat_id] = 3
    elif steps.get(chat_id) == 3:
        user_inform[chat_id]['Your story'] = message.text
        info_text = "Бот отримав твою інформацію. Ось данні, які отримав бот:\n" # вивід данних які ми отримали від користувача
        for key, value in user_inform[chat_id].items(): 
            info_text += f"{key}: {value}\n" # форматуємо данні, без форматування бот відправляє данні в форматі "5342134", не помню як називається, в формі ключа чи як там
        
        inline = types.InlineKeyboardMarkup() # створюємо кнопки Так і Ні та присвоюєм їм по callback'у, 
        yes_button = types.InlineKeyboardButton('Так', callback_data='yes',) 
        no_button = types.InlineKeyboardButton('Ні', callback_data='no')
        inline.add(yes_button, no_button)

        bot.send_message(chat_id, info_text) # відправлення інформації, яку ввів користувач 
        bot.send_message(chat_id, "Бажаєте редагувати інформацію?", reply_markup=inline) # відправлення повідомлення разом з кнопками

@bot.callback_query_handler(func=lambda call: True)
def handle_edit_choice(call): #функція для обробки вибору користувача(редагувати текст який він відправив чи ні)
    chat_id = call.message.chat.id
    message_id = call.message.message_id 
    if call.data == 'yes': # перевірка, якщо користувач натиснув на кнопку з callback'ом  yes(тобто кнопка Так)
        bot.answer_callback_query(call.id)
        edit_inline = types.InlineKeyboardMarkup() #створюємо клавіатуру з кнопками (заголовок, імя, тема статті) та присвоюємо кожній кнопці по callback'y
        title_button = types.InlineKeyboardButton('Заголовок', callback_data='edit_title')
        name_button = types.InlineKeyboardButton('Ім\'я', callback_data='edit_name')
        story_button = types.InlineKeyboardButton('Тему статті', callback_data='edit_story')
        edit_inline.add(title_button, name_button, story_button)
        bot.edit_message_text("Виберіть опцію для редагування:", chat_id=chat_id, message_id=message_id, reply_markup=edit_inline) #замість того щоб відправляти ще одне повідомлення з кнопкою редагуємо  повідомлення "Бажаєте редагувати інформацію?" на "Виберіть опцію для редагування:"  
        # логіка редагування ще не зроблена, 
    elif call.data == 'no':
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "Чотко")
        # далі логіки ще немає



if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)
