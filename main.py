
# -*- coding: utf-8 -*-
import config
import telebot
from telebot import types
import json
bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start', 'help'])
def hello(message):
    if message.chat.id in config.adminid:
        bot.send_message(message.chat.id, 'Привет, хозяин')
        time.sleep(0.2)
        apteka(message)
    else:
        bot.send_message(message.chat.id, 'Доступ отклонен')
        
def apteka(message):
    if message.chat.id in config.adminid:
        keyboard = types.ReplyKeyboardMarkup(True, False)
        button_1 = types.KeyboardButton(text="Проверить лекарство")
        button_2 = types.KeyboardButton(text="Удалить лекарство")
        button_3 = types.KeyboardButton(text="Добавить лекарство")
        button_4 = types.KeyboardButton(text="Список всех лекарств")
        keyboard.row(button_1, button_2)
        keyboard.row(button_3, button_4)
        bot.send_message(message.chat.id, 'Что делаем?', reply_markup=keyboard)
        

@bot.message_handler(func=lambda message: message.text == 'Проверить лекарство' and message.content_type == 'text')
def zapros_medicine(message):
    if message.chat.id in config.adminid:
        keyboard0 = types.ForceReply(selective=True)
        bot.send_message(message.chat.id, 'Какое лекарство?', reply_markup=keyboard0)

@bot.message_handler(func=lambda message: message.text == 'Добавить лекарство' and message.content_type == 'text')
def zapros_medicine(message):
    if message.chat.id in config.adminid:
        keyboard0 = types.ForceReply(selective=True)
        bot.send_message(message.chat.id, 'Добавить лекарство?', reply_markup=keyboard0)

@bot.message_handler(func=lambda message: message.text == 'Удалить лекарство' and message.content_type == 'text')
def del_medicine(message):
    if message.chat.id in config.adminid:
        json_data = open("apteka.json",encoding='utf-8').read()
        data = json.loads(json_data)
        keyboard = types.InlineKeyboardMarkup()
        for med in  data["medicine"]:
            button = types.InlineKeyboardButton(text=(' '.join(map(str, [med, data["medicine"][med]["type"], data["medicine"][med]["date"]]))), callback_data="del_"+med)
            keyboard.row(button)
        bot.send_message(message.chat.id, 'Какое лекарство удалить?', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.content_type == 'text' and message.reply_to_message is not None and message.json['reply_to_message']['text'] == 'Какое лекарство?')
def check_medicine(message):
    if message.chat.id in config.adminid:
        json_data = open("apteka.json", encoding='utf-8').read()
        data = json.loads(json_data)
        try:
            if data["medicine"][message.text.lower()] is None:
                bot.send_message(message.chat.id, "Нет лекарства в аптечке")
            else:
                bot.send_message(message.chat.id, "Есть: "+message.text.lower()+" "+ data["medicine"][message.text.lower()]["type"]+" "+data["medicine"][message.text.lower()]["date"] )
        except KeyError:
            bot.send_message(message.chat.id, "Нет лекарства в аптечке")
        apteka(message)

@bot.message_handler(func=lambda message: message.text == 'Список всех лекарств' and message.content_type == 'text')
def list_medicine(message):
    if message.chat.id in config.adminid:
        json_data = open("apteka.json",encoding='utf-8').read()
        data = json.loads(json_data)
        b=[]
        for med in  data["medicine"]:
            b.append(str(med)+" ("+str(data["medicine"][med]["type"])+") " + str(data["medicine"][med]["date"]))
        for med1 in sorted(b):
            bot.send_message(message.chat.id, med1)      
        apteka(message)


@bot.message_handler(func=lambda message: message.content_type == 'text' and message.reply_to_message is not None and message.json['reply_to_message']['text'] == 'Добавить лекарство?')
def check_medicine(message):
    if message.chat.id in config.adminid:
        name=message.text.lower()
        json_data = open("apteka.json", encoding='utf-8').read()
        data = json.loads(json_data)
        try:
            if data["medicine"][message.text.lower()] is not None:
                bot.send_message(message.chat.id, "Такое лекарство уже есть...")
        except KeyError:
            keyboard0 = types.InlineKeyboardMarkup()
            for type in config.list_med:
                button = types.InlineKeyboardButton(text=type, callback_data=type)
                keyboard0.row(button)
            bot.send_message(message.chat.id, 'Тип лекарства?', reply_markup=keyboard0)

            @bot.callback_query_handler(func=lambda call: call.data in config.list_med)
            def callback_inline(call):
                type_med=call.data
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=type_med)

                keyboard1 = types.ForceReply(selective=True)
                bot.send_message(message.chat.id, 'Срок годности лекарства', reply_markup=keyboard1)

                @bot.message_handler(func=lambda message: message.content_type == 'text' and message.reply_to_message is not None and 'Срок годности лекарства' in message.json['reply_to_message']['text'])
                def add_date(message):
                    date_line = re.search('\d{4}-\d{2}-\d{4}|\d{2}.\d{2}.\d{4}|\d{2}-\d{4}|\d{2}.\d{4}', message.text)
                    date_l = date_line.group(0)


                    data["medicine"][name] = {"type": type_med, "date": date_l}
                    with open('apteka.json', 'w', encoding='utf-8') as f:
                        str_= json.dumps(data,
                                         indent=4,
                                         sort_keys=True,
                                         separators=(',', ': '),
                                         ensure_ascii=False)
                        f.write(str(str_))
                        f.close()
                        apteka(message)


@bot.callback_query_handler(func=lambda call: 'del_' in call.data)
def callback_inline2(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Удалил "+str(call.data[4:]))
    json_data = open("apteka.json", encoding='utf-8').read()
    data = json.loads(json_data)

    del data["medicine"][call.data[4:]]

    with open('apteka.json', 'w', encoding='utf-8') as f:
        str_ = json.dumps(data,
                          indent=4,
                          sort_keys=True,
                          separators=(',', ': '),
                          ensure_ascii=False)
        f.write(str(str_))
        f.close()
