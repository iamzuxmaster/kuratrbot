import requests
from json import load

def strings(user_language):
    with open('titles/strings.json', 'r', encoding='UTF-8') as file:
        data = load(file)
    return data[user_language]

def select_language():
    # Please note Unused language
    text = "🇺🇿 Iltimos tilni tanlang...\n"
    text += "🇷🇺 Пожалуйста выберите язык...\n"
    text += "🇺🇸 Please select a language...\n"
    # ? Ex: text += "🇹🇷 Lütfen bir dil seçin" 
    return text

class Errors: 
    """
    Error messages is here
    """
    def name_error(user_language): 
        txt = strings(user_language=user_language)["Errors"]["name_error"]
        text = "❌ {}".format(txt)
        return text

def request_name(user_language): 
    txt = strings(user_language=user_language)["request_name"]
    text = "✍️ {}".format(txt[0])
    return text

def request_phone(user_language): 
    txt = strings(user_language=user_language)["request_phone"]
    text = "📞 {}".format(txt[0])
    return text

def request_group(user_language):
    txt = strings(user_language=user_language)["request_group"]
    text = "👇 {}".format(txt[0])
    return text

def main_menu(user_language):
    txt =strings(user_language=user_language)["main_menu"]
    text = "✅ {}".format(txt[0])
    return text



class Admin: 

    def new_user(self, user_language, user,group):
        txt = strings(user_language=user_language)["Admin"]["new_user"]
        text = f"{txt[0].format(user.fullname,group.title)}"
        return text

    def main_menu(self, user_language, admin, users:list, groups: list, messages:list):
        txt = strings(user_language=user_language)["Admin"]["main_menu"]
        text = "✋ {} <b>{}</b>\n\n".format(txt[0], admin.fullname)
        text += "📃 {}: <b>{}</b>\n".format(txt[1], len(groups))
        text += "👤 {}: <b>{}</b>\n".format(txt[2], len(users))
        text += "✉️ {}: <b>{}</b>".format(txt[3], len(messages))
        return text

    def groups(self, user_language, groups):
        txt = strings(user_language=user_language)["Admin"]["groups"]
        text = "👥 {}:\n\n".format(txt[0])
        return text
    
    
    def groups_list(self, user_language, groups):
        txt = strings(user_language=user_language)["Admin"]["groups"]
        text = ""
        if groups:
            count = 1
            for group in groups:
                text += "{}. {}\n".format(count,group.title)
                count +=1
        else: 
            text = "{}".format(txt[1])
        return text

    def detail_group(self, user_language, group): 
        txt = strings(user_language=user_language)["Admin"]["detail_group"]
        text = "✍️ {}: {}\n".format(txt[0], group.title)
        text += "📅 {}: {}".format(txt[1], group.date_created)
        return text

    def edit_name_group(self, user_language): 
        txt =strings(user_language=user_language)["Admin"]["edit_name_group"]
        text = f"{txt[0]}:"
        return text

    def delete_group(self, user_language, group): 
        txt =strings(user_language=user_language)["Admin"]["delete_group"]
        text = f"⚠️ {txt[0].format(group.title)}:"
        return text


    def add_group(self, user_language):
        txt = strings(user_language=user_language)["Admin"]["add_group"]
        text = "✍️ {}:".format(txt[0])
        return text

    def added_group(self, user_language):
        txt = strings(user_language=user_language)["Admin"]["added_group"]
        text = "✅ {}.".format(txt[0])
        return text
    
    def edited_group(self, user_language):
        txt = strings(user_language=user_language)["Admin"]["edited_group"]
        text = "✅ {}.".format(txt[0])
        return text
    
    def deleted_group(self, user_language):
        txt = strings(user_language=user_language)["Admin"]["deleted_group"]
        text = "🗑 {}.".format(txt[0])
        return text

    
    def users(self, user_language): 
        txt = strings(user_language=user_language)["Admin"]["users"]
        text = "👇 {}".format(txt[0])
        return text

    def checked_users(self, user_language, users):
        txt = strings(user_language=user_language)["Admin"]["checked_users"]
        text  = f"{txt[0]}:"
        return text


    def checked_users_list(self, user_language, users):
        txt = strings(user_language=user_language)["Admin"]["checked_users"]
        if users:
            text  = ""
            count = 1
            for user in users: 
                text += f"<b>{count}.{user.fullname}</b>\n"
                text += f"   └ {user.telegram_id}\n"
                text += f"   └ +{user.phone}\n"
                count +=1
        else: 
            text = f"{txt[1]}"

        return text

    def notchecked_users(self, user_language, users):
        txt = strings(user_language=user_language)["Admin"]["notchecked_users"]
        if users:
            text  = f"{txt[0]}:"
        else:
            text = f"{txt[1]}"
        return text

    def notchecked_user(self, user_language, user):
        if user:
            txt = strings(user_language=user_language)["Admin"]["notchecked_users"]
            text  = f"👤 {user.fullname}\n"    
            text += f"   └ `{user.telegram_id}`\n"
            text += f"   └ +{user.phone}\n"
        else:
            text = f"{txt[1]}"
        return text
    
    def user_add_to_group(self, user_language, user): 
        txt = strings(user_language=user_language)["Admin"]["user_add_to_group"]
        text = f"{txt[0]}"
        return text

    
    def user_added_group(self, user_language): 
        txt = strings(user_language=user_language)["Admin"]["user_added_group"]
        text = f"✅ {txt[0]}"
        return text
    
    def send_message(self, user_language): 
        txt = strings(user_language=user_language)["Admin"]["send_message"]
        text = "{}".format(txt[0])
        return text
    def send_message_send(self, user_language): 
        txt = strings(user_language=user_language)["Admin"]["send_message_send"]
        text = "✍️ {}".format(txt[0])
        return text

    def message_sended(self, user_language):
        txt = strings(user_language=user_language)["Admin"]["message_sended"]
        text = f"✅ {txt[0]}"
        return text
    