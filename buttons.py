from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
import json
from app import *
from genius import chunk

def strings(user_language):
    with open('titles/buttons.json', 'r', encoding='UTF-8') as file:
        data = json.load(file)

    return data[user_language]

def style():
    with open('titles/style.json', 'r', encoding='UTF-8') as file:
        data = json.load(file)
    return data

def back(user_language):
    text = strings(user_language=user_language)["back"]
    key = KeyboardButton(text="🔙 " + text)
    return key

def back_inline(user_language, callback_data):
    text = strings(user_language=user_language)["back"]
    key = InlineKeyboardButton(text="🔙 " + text, callback_data=callback_data)
    return key


def select_language():
    langs = [
        {
            "title": "🇺🇿 O'zbek",
            "code": "uz"
        },
        {
            "title": "🇷🇺 Русские",
            "code": "ru"
        },
        {
            "title": "🇺🇸 English",
            "code": "en"
        }
    ]
    keys = [
        [InlineKeyboardButton(text=i["title"], callback_data=i["code"])]
        for i in langs
    ]

    return InlineKeyboardMarkup(inline_keyboard=keys)

def request_phone(user_language, settings=False):
    text = strings(user_language=user_language)["request_phone"]
    key = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="📲 {}".format(text), request_contact=True)]], resize_keyboard=True)
    if settings:
        key.add(back(user_language=user_language))
    return key

def main_menu(user_language): 
    texts = strings(user_language=user_language)["main_menu"]
    emojis = style()["main_menu"]
    keys = []
    count = 0
    for text in texts:
        keys.append(KeyboardButton(text="{} {}".format(emojis[count], text)))
        count +=1
    key = ReplyKeyboardMarkup(keyboard=chunk([*keys], 2), resize_keyboard=True)
    return key

    
def request_group(user_language, groups):
    text  = strings(user_language=user_language)
    keys = []
    for group in groups:
        keys.append(InlineKeyboardButton(text=group.title, callback_data=SELECT_GROUP+str(group.id)))
    key = InlineKeyboardMarkup(inline_keyboard=chunk([*keys], 1))
    return key


class Admin:

    def main_menu(self, user_language): 
        texts = strings(user_language=user_language)["Admin"]["main_menu"]
        emojis = style()["admin_page"]
        keys = []
        count = 0
        for text in texts:
            keys.append(KeyboardButton(text="{} {}".format(emojis[count], text)))
            count +=1
        key = ReplyKeyboardMarkup(keyboard=chunk([*keys], 2), resize_keyboard=True)
        return key
    
    
    def groups(self, user_language, groups):
        text = strings(user_language=user_language)["Admin"]["groups"]
        keys = []
        for group in groups: 
            keys.append(InlineKeyboardButton(text="✏️ {}".format(group.title), callback_data=GROUP_DETAIL + str(group.id)))
        key = InlineKeyboardMarkup(inline_keyboard=chunk([*keys], 2))
        key.add(InlineKeyboardButton(text="➕ " + text[0], callback_data=ADMIN_GROUP_ADD))
        return key 
    
    def detail_group(self, user_language, group):
        texts = strings(user_language=user_language)["Admin"]["detail_group"]
        emojis = style()["detail_group"]
        callback_datas = [EDIT_NAME_GROUP, DELETE_GROUP]
        keys = [] 
        count = 0
        for text in texts:
            keys.append(InlineKeyboardButton(text="{} {}".format(emojis[count], text), callback_data=callback_datas[count]+ str(group.id)))
            count +=1
        key = InlineKeyboardMarkup(inline_keyboard=chunk([*keys], 2))
        key.add(back_inline(user_language=user_language, callback_data=BACK_TO_GROUPS))
        return key

    def delete_group(self, user_language, group): 
        text = strings(user_language=user_language)["Admin"]["delete_group"]
        keys = InlineKeyboardButton(text="🗑 " + text[0], callback_data=YES_I_ACCEPT_DELETE + str(group.id))
        key = InlineKeyboardMarkup(inline_keyboard=[[keys]])
        key.add(back_inline(user_language=user_language, callback_data=BACK_TO_GROUPS))
        return key

    def users(self, user_language):
        texts = strings(user_language=user_language)["Admin"]["users"]
        keys = []
        for text in texts:
            keys.append(KeyboardButton(text=text))
        key = ReplyKeyboardMarkup(keyboard=chunk([*keys], 2), resize_keyboard=True)
        key.add(back(user_language=user_language))
        return key
    
    def checked_users(self, user_language, users): 
        texts = strings(user_language=user_language)["Admin"]["checked_users"]
        callback_datas = [USERS_EXCEL_DOWNLOAD]
        keys = []
        count = 0
        if users:
            for text in texts:
                keys.append(InlineKeyboardButton(text=text, callback_data=callback_datas[count]))
            key = InlineKeyboardMarkup(inline_keyboard=chunk([*keys], 1))
            key.add(back_inline(user_language=user_language, callback_data=BACK_TO_USERS))
        else: key = InlineKeyboardMarkup(inline_keyboard=[[back_inline(user_language=user_language, callback_data=BACK_TO_USERS)]])
        return key

    def notchecked_user(self, user_language, user): 
        if user:
            keys = [InlineKeyboardButton(text="✅", callback_data=USER_ADD_TO_GROUP+str(user.id))]
            key  = InlineKeyboardMarkup(inline_keyboard=[keys])
        else: key = None
        return key

    def user_add_to_group(self, user_language, groups): 
        keys = []
        for group in groups:
            keys.append(InlineKeyboardButton(text=group.title, callback_data=ADD_USER_GROUP+str(group.id)))
        key = InlineKeyboardMarkup(inline_keyboard=chunk([*keys], 1))
        key.add(back_inline(user_language=user_language, callback_data=BACK_TO_USERS))
        return key
        

    
    
    def send_message(self, user_language, groups): 
        text = strings(user_language=user_language)["Admin"]["send_message"]
        if groups: 
            keys = []
            for group in groups:
                keys.append(InlineKeyboardButton(text="👥 "  + group.title, callback_data=SEND_MESSAGE_TO_GROUP+str(group.id)))
            key =  InlineKeyboardMarkup(inline_keyboard=chunk([*keys], 1))
            key.add(InlineKeyboardButton(text="📤 " + text, callback_data=SEND_MESSAGE_TO_ALL))
        else: key=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=text, callback_data=SEND_MESSAGE_TO_ALL)]])
        return key