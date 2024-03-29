import telebot
from telebot import types
import requests
from telegraph import Telegraph
from config import TG_token, TELEGRAPH_token, GPT_api, GPT_MODEL, Temperature, MAX_TOKEN

bot = telebot.TeleBot(TG_token)
telegraph = Telegraph(TELEGRAPH_token) #access token телеграфа, можна получити перейшовши по ссилці
user_inform = {} # словник, данні які вводить користувач попадають в нього
steps = {} # условні кроки по яким проходимся ( крок 1 - заголовок, після того як користувач вказав заголовок переключаємось на крок 2, це - імя юзера - і крок 3 - тема , по якій гпт буде генерувати статтю.) 



@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_menu = types.KeyboardButton('Генерація статті')
    faq_button = types.KeyboardButton('FAQ та проблеми')
    markup.add(button_menu, faq_button)
    bot.send_message(message.chat.id, "Привіт, я Jaba Project. За допомогою мене ти можеш згенерувати статтю на будь-яку тему!", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "FAQ та проблеми")
def faq_info(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"""
ChatGPT model : {GPT_MODEL}


Якщо використовується модель GPT 3.5, яка немає доступа до інтернету, то бот може якусь херню в статтях. Якщо ви не використовуєте GPT-4, то краще не юзати  сленгу, запитань про актуальні новини після 2021 року. Є велика ймовірність, що GPT напише якусь гадость..
----------------------------------------------------------------------------------
Швидкість генерації статті залежить від декількох факторів:
1. Тема статті.
2.Кількість токенів які вказані в конфіг файлі. Чим більше токенів, тим більше буде текст статт'ї, тим більше треба гпт думати і генереувати тексту.
""")

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
        user_inform[chat_id]['Your title'] = message.text
        bot.send_message(chat_id, "Добре. Тепер відправте ваше імя (воно буде вказано в якості автора статті)")
        steps[chat_id] = 2
    elif steps.get(chat_id) == 2:
        user_inform[chat_id]['Your name'] = message.text
        bot.send_message(chat_id, "Залишилось відправити тему для статті. Чим краще буде розписана тему статті - тим краще буде згенерована стаття.")
        steps[chat_id] = 3
    elif steps.get(chat_id) == 3 and 'Your story' not in user_inform[chat_id]: # додав перевірку, був баг, коли бот зібрав данні і відправив їх користувачу, можна було написати любий текст і бот перезаписував кожен раз словник
        user_inform[chat_id]['Your story'] = message.text
        show_info(message)

def show_info(message): # добавлена функція виводу тексту, щоб не засоряти функцію collect_user_info
    chat_id = message.chat.id
    info_text = "Бот отримав твою інформацію. Ось данні, які отримав бот:\n" # вивід данних які ми отримали від користувача
    for key, value in user_inform[chat_id].items(): 
            info_text += f"{key}: {value}\n" # форматуємо данні, без форматування бот відправляє данні в форматі "5342134", не помню як називається, в формі ключа чи як там
        
    inline = types.InlineKeyboardMarkup() # створюємо кнопки Так і Ні та присвоюєм їм по callback'у, 
    yes_button = types.InlineKeyboardButton('Так✏️', callback_data='yes',) 
    no_button = types.InlineKeyboardButton('Ні❌', callback_data='no')
    inline.add(yes_button, no_button)

    bot.send_message(chat_id, info_text) # відправлення інформації, яку ввів користувач 
    bot.send_message(chat_id, "Бажаєте редагувати інформацію?", reply_markup=inline) # відправлення повідомлення разом з кнопками


@bot.callback_query_handler(func=lambda call: call.data == 'yes')
def handle_edit_choice(call): #функція для обробки вибору користувача(редагувати текст який він відправив чи ні)
    chat_id = call.message.chat.id
    message_id = call.message.message_id 
    bot.answer_callback_query(call.id)
    edit_inline = types.InlineKeyboardMarkup() #створюємо клавіатуру з кнопками (заголовок, імя, тема статті) та присвоюємо кожній кнопці по callback'y
    title_button = types.InlineKeyboardButton('Заголовок', callback_data='edit_title')
    name_button = types.InlineKeyboardButton('Ім\'я', callback_data='edit_name')
    story_button = types.InlineKeyboardButton('Тему статті', callback_data='edit_story')
    edit_inline.add(title_button, name_button, story_button)
    bot.edit_message_text("Виберіть опцію для редагування:", chat_id=chat_id, message_id=message_id, reply_markup=edit_inline) #замість того щоб відправляти ще одне повідомлення з кнопкою редагуємо  повідомлення "Бажаєте редагувати інформацію?" на "Виберіть опцію для редагування:"  

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_')) # шукаємо callback'и які починаться з edit_
def handle_user_edit(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id 
    inform = call.data.split('_')[1]
    edit_message = bot.edit_message_text(f'Очікую відредаговану інформацію для {inform}:', chat_id=chat_id, message_id=message_id)
    #bot.send_message(chat_id, f'Очікую відредаговану інформацію для {inform}')
    bot.register_next_step_handler(edit_message, handle_new_information, inform, chat_id)
    bot.answer_callback_query(call.id)

#____нових коментарів буде менше бо я дороблював бота пізно_____#
def handle_new_information(message, inform, chat_id):
    newinfo = message.text
    if chat_id not in user_inform:
        user_inform[chat_id] = {}
    correct_key = 'Your ' + inform
    user_inform[chat_id][correct_key] = newinfo
    bot.send_message(chat_id, f'{inform} оновлений успішно.')

    actual_info_text = "Оновленні данні:\n"
    for key, value in user_inform[chat_id].items():
        actual_info_text += f"{key.capitalize()}: {value}\n"
    bot.send_message(chat_id, actual_info_text)
    bot.send_message(chat_id, "Чотко. Відправляємо данні в потрібне місце та генеруємо статтю. Це може зайняти деякий час(приблизно 20-30секунд).")
    
    if 'Your story' in user_inform[chat_id]:
        story_text = user_inform[chat_id]['Your story']
        send_to_chatgpt(story_text,chat_id)
        print(f"відправка в гпт: {story_text}") 
    article_url = createArticleTelegraph(chat_id)
    bot.send_message(chat_id, f"Ваша стаття успішно створена: {article_url}")
    print(f"url: {article_url}") 

@bot.callback_query_handler(func=lambda call: call.data == 'no') # випадок якщо користувач не хоче редагувати данні.
def handle_no_edit_choice(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    bot.edit_message_text(text="Чотко. Відправляємо данні в потрібне місце та генеруємо статтю. Це може зайняти деякий час (приблизно 20-30 секунд, залежить від теми статт'ї).", chat_id=chat_id, message_id=call.message.message_id)    
    if 'Your story' in user_inform[chat_id]:
        story_text = user_inform[chat_id]['Your story']
        print(f"відправка в гпт: {story_text}") 
        send_to_chatgpt(story_text,chat_id)
    article_url = createArticleTelegraph(chat_id)
    bot.edit_message_text(text=f"Ваша стаття успішно створена: {article_url}",chat_id=chat_id, message_id=call.message.message_id )
    bot.send_message(chat_id , "Бажаєте створити ще якусь статтю?")
    print(f"url: {article_url}") 




def send_to_chatgpt(story_text, chat_id):
    api_url = "https://api.openai.com/v1/chat/completions"
    headers = { #звичайні заголовки для авторизації
        "Authorization": f"Bearer {GPT_api}", 
        "Content-Type": "application/json"
    } 
    payload = {
        "model": GPT_MODEL,
        "messages": [
            {"role": "system", "content": "Ви користувач, який просить створити  зрозумілу та цікаву статтю на українській мові."},
            {"role": "user", "content": f"Створи, будь ласка, детальну та захоплюючу статтю українською мовою на тему: {story_text}. Включи історичні факти, цікаві інциденти та ключові особистості, які пов'язані з цією темою. Додай аналіз сучасного впливу теми та можливі прогнози на майбутнє."}
        ],
        "temperature": Temperature,
        "max_tokens": MAX_TOKEN
    }
    response = requests.post(api_url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        try:
            response_text = data["choices"][0].get("message", {}).get("content", "")
            user_inform[chat_id]['GPT Response'] = response_text # сохраняємо відповідь в словнику
        except (IndexError, KeyError) as e:
            print(f"Error accessing response data: {e}")
            response_text = "Не вдалося обробити відповідь."
        return response_text


def createArticleTelegraph(chat_id):
    title = user_inform[chat_id]['Your title']
    author_name = user_inform[chat_id]['Your name']
    content = user_inform[chat_id]['GPT Response']
    response = telegraph.create_page(
        title,
        html_content = ''.join(f"<p>{paragraph}</p>" for paragraph in content.split('\n') if paragraph), # розділення на абзаци, тепер стаття виглядає набагато акуратніше
        author_name=author_name
    )
    return response['url']

if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)
