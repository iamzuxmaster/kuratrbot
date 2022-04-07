""" LOCAL """
import jmespath
from app import *
import buttons as btn
import strings
from genius import chunk, request, touched, excel_download
""" Aiogram """
from aiogram import types,Bot, Dispatcher, executor
from aiogram.types import InputFile
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext 
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Filter
from db.models import User, Admin, Session, engine, Groups, Messages
from db.dispatcher import get_or_create, object_create, object_delete, object_get, objects_all, objects_filter

storage = RedisStorage2('localhost', 6379, db=5, pool_size=10, prefix='my_fsm_key') if REDIS_STORAGE else MemoryStorage()


bot = Bot(BOT_TOKEN, parse_mode=types.message.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
 
local_session = Session(bind=engine)

# All states
class States(StatesGroup):
    select_language = State()
    request_name = State()
    request_phone = State()
    request_group = State()
    main_menu = State()
    admin_page = State()
    admin_group = State()
    admin_group_add_name = State()
    admin_edit_name_group = State()
    admin_delete_group = State()
    admin_delete_group_accept = State()
    admin_users = State()
    add_user_to_group = State()
    send_message = State()
    send_message_send = State()


class IsAdmin(Filter):
    key = "is_admin"

    async def check(self, message: types.Message):
        admins = objects_all(session=local_session, model=Admin)
        list_admin = list(map(lambda i: int(i.telegram_id), admins))
        return message.chat.id in list_admin


class IsAdmin_Inline(Filter):
    key = "is_admin"

    async def check(self, callback: types.CallbackQuery):
        admins = objects_all(session=local_session, model=Admin)
        list_admin = list(map(lambda i: int(i.telegram_id), admins))
        return callback.message.chat.id in list_admin

@dp.message_handler(commands=['start'], state='*')
async def get_start(message: types.Message, state: FSMContext):

    chat_id = message.chat.id
    user, user_created = get_or_create(session=local_session, model=User, telegram_id=chat_id)
    user.telegram_name = message.from_user.first_name
    user.username = message.from_user.username
    user.lang = "uz"
    local_session.commit()

    admins = objects_all(session=local_session, model=Admin)
    list_admin = list(map(lambda i: int(i.telegram_id), admins))
    groups = objects_all(session=local_session, model=Groups)

    if chat_id in list_admin: 
        admin = object_get(session=local_session, model=Admin, telegram_id=chat_id)
        users = objects_all(session=local_session, model=User)
        groups = objects_all(session=local_session, model=Groups)
        messages = objects_all(session=local_session, model=Messages)
        if admin is not None:
            text = strings.Admin().main_menu(user_language=user.lang, admin=admin, users=users, groups=groups, messages=messages)
            markup = btn.Admin().main_menu(user_language=user.lang)
            await state.finish()
            await States.admin_page.set()

    elif user.lang: 
        if user.fullname is None:
            text = strings.request_name(user_language=user.lang)
            markup = btn.ReplyKeyboardRemove(selective=True)
            await state.finish()
            await States.request_name.set()

        elif user.phone is None:
            text = strings.request_phone(user_language=user.lang)
            markup = btn.request_phone(user_language=user.lang)
            await state.finish()
            await States.request_phone.set()

        elif user.request_group is None:
            text = strings.request_group(user_language=user.lang)
            markup = btn.request_group(user_language=user.lang, groups=groups)
            await state.finish()
            await States.request_group.set()

        else:
            if user.verified:
                text = "✅ Guruhga qabul qilindingiz.Va xabarlarni qabul qila olasiz."
                markup = btn.ReplyKeyboardRemove(selective=True) 
            else:
                text = strings.main_menu(user_language=user.lang)
                markup = btn.ReplyKeyboardRemove(selective=True)
                await state.finish()
                await States.main_menu.set()
    else:
        text = strings.select_language()
        markup = btn.select_language()
        await state.finish()
        await States.select_language.set()
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        

@dp.message_handler(commands=['chat_id'], state='*')
async def get_start(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await bot.send_message(chat_id=chat_id, text=str(chat_id))
    
    
# Request Name
@dp.message_handler(content_types=["text"], state=States.request_name)
async def get_name(message: types.Message, state:FSMContext):

    chat_id = message.chat.id
    user, user_created = get_or_create(session=local_session, model=User, telegram_id=chat_id)
    if len(message.text) > 6 and ' ' in message.text:
        user.fullname = message.text.title()
        local_session.commit()
        text = strings.request_phone(user_language=user.lang)
        markup = btn.request_phone(user_language=user.lang)
        await state.finish()
        await States.request_phone.set()
    else: 
        text = strings.Errors.name_error(user_language=user.lang)
        markup = btn.ReplyKeyboardRemove(selective=True)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

# Request Phone
@dp.message_handler(content_types=["contact"], state=States.request_phone)
async def get_phone_number(message:types.Message, state:FSMContext):

    chat_id = message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    phone = message.contact.phone_number.replace('+', '')
    user.phone = phone
    local_session.commit()
    groups = objects_all(session=local_session, model=Groups)
    text = strings.request_group(user_language=user.lang)
    markup = btn.request_group(user_language=user.lang, groups=groups)
    await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
    await bot.send_message(chat_id=chat_id, text="✅", reply_markup=btn.ReplyKeyboardRemove(selective=True))
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
    await state.finish()
    await States.request_group.set()

@dp.callback_query_handler(lambda callback: callback.data.startswith(SELECT_GROUP), state=States.request_group)
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    group_id = callback.data.replace(SELECT_GROUP, '')
    print(group_id)
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    user.request_group = group_id
    local_session.commit()
    await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)
    text = strings.main_menu(user_language=user.lang)
    markup = btn.ReplyKeyboardRemove(selective=True)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
    admins = objects_all(session=local_session, model=Admin)
    group = object_get(session=local_session, model=Groups, id=group_id)
    text = strings.Admin().new_user(user_language=user.lang, user=user,group=group)
    markup = btn.Admin().notchecked_user(user_language=user.lang, user=user)
    await state.finish()
    await States.add_user_to_group.set()
    for admin in admins:
        await bot.send_message(chat_id=admin.telegram_id,text="🔔", reply_markup=btn.ReplyKeyboardMarkup(keyboard=[[btn.back(user_language=user.lang)]], resize_keyboard=True))
        await bot.send_message(chat_id=admin.telegram_id, text=text, reply_markup=markup)


# ! ADMIN PAGE
@dp.message_handler(IsAdmin(), lambda message: message.text[2:] in jmespath.search('*.back', touched()), state=[States.admin_group, States.admin_group_add_name, States.admin_delete_group, States.admin_users, States.add_user_to_group, States.send_message, States.send_message_send])
async def admin_get_message(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    admin = object_get(session=local_session, model=Admin, telegram_id=chat_id)
    users = objects_all(session=local_session, model=User)
    groups = objects_all(session=local_session, model=Groups)
    messages = objects_all(session=local_session, model=Messages)
    if admin is not None:
        text = strings.Admin().main_menu(user_language=user.lang, admin=admin, users=users, groups=groups, messages=messages)
        markup = btn.Admin().main_menu(user_language=user.lang)
        await state.finish()
        await States.admin_page.set()
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


@dp.message_handler(IsAdmin(), state=States.admin_page)
async def admin_get_message(message: types.Message, state:FSMContext):
    chat_id = message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    if message.text[2:] in jmespath.search('*.Admin.main_menu[0]', touched()):
        users = objects_all(session=local_session, model=Groups)
        text = strings.Admin().groups(user_language=user.lang, groups=users)
        markup = btn.ReplyKeyboardMarkup(keyboard=[[btn.back(user_language=user.lang)]], resize_keyboard=True)
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        text = strings.Admin().groups_list(user_language=user.lang, groups=users)
        markup = btn.Admin().groups(user_language=user.lang, groups=users)
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        await state.finish()
        await States.admin_group.set()

    if message.text[2:] in jmespath.search('*.Admin.main_menu[1]', touched()):
        users = objects_all(session=local_session, model=User)
        text = strings.Admin().users(user_language=user.lang)
        markup = btn.Admin().users(user_language=user.lang)
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        await state.finish()
        await States.admin_users.set()

    if message.text[3:] in jmespath.search('*.Admin.main_menu[2]', touched()):
        text= message.text
        markup = btn.ReplyKeyboardMarkup(keyboard=[[btn.back(user_language=user.lang)]], resize_keyboard=True)
        await bot.send_message(chat_id=chat_id, text=message.text, reply_markup=markup)
        groups = objects_all(session=local_session, model=Groups)
        text = strings.Admin().send_message(user_language=user.lang)
        markup = btn.Admin().send_message(user_language=user.lang, groups=groups)
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        await state.finish()
        await States.send_message.set()
        
    if message.text.startswith('SET_ADMIN_'):
        admin_id = message.text.replace('SET_ADMIN_', '')
        _admin, _admin_created = get_or_create(session=local_session, model=Admin, telegram_id=admin_id)
        local_session.commit()
        await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        await bot.send_message(chat_id=chat_id, text="Success")
        
        
    if message.text.startswith('REMOVE_USER_'):
        user_id = message.text.replace('REMOVE_USER_', '')
        _user, _user_created = get_or_create(session=local_session, model=User, telegram_id=user_id)
        delete = object_delete(session=local_session, model=User, id=_user.id)
        local_session.commit()
        await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        await bot.send_message(chat_id=chat_id, text="DELETED")
        
        
    if message.text.startswith('REMOVE_ADMIN_'):
        user_id = message.text.replace('REMOVE_ADMIN_', '')
        _user, _user_created = get_or_create(session=local_session, model=Admin, telegram_id=user_id)
        delete = object_delete(session=local_session, model=Admin, id=_user.id)
        local_session.commit()
        await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        await bot.send_message(chat_id=chat_id, text="DELETED")
        
        


@dp.callback_query_handler(IsAdmin_Inline(), text=ADMIN_GROUP_ADD, state=States.admin_group)
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    text = strings.Admin().add_group(user_language=user.lang)
    markup = btn.ReplyKeyboardMarkup(keyboard=[[btn.back(user_language=user.lang)]], resize_keyboard=True)
    await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
    await state.finish()
    await States.admin_group_add_name.set()


@dp.callback_query_handler(IsAdmin_Inline(), lambda callback: callback.data.startswith(GROUP_DETAIL), state=States.admin_group)
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    group_id = callback.data.replace(GROUP_DETAIL, '')
    group = object_get(session=local_session, model=Groups, id=int(group_id))
    text = strings.Admin().detail_group(user_language=user.lang, group=group)
    markup = btn.Admin().detail_group(user_language=user.lang, group=group)
    await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


@dp.callback_query_handler(IsAdmin_Inline(), lambda callback: callback.data.startswith(EDIT_NAME_GROUP), state=States.admin_group)
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    group_id = callback.data.replace(EDIT_NAME_GROUP, '')
    async with state.proxy() as data:
        data["edit_name_group"] = group_id
        text = strings.Admin().edit_name_group(user_language=user.lang)
        await bot.send_message(chat_id=chat_id, text=text)
        await state.finish()
        await States.admin_edit_name_group.set()



@dp.callback_query_handler(IsAdmin_Inline(), lambda callback: callback.data.startswith(DELETE_GROUP), state=States.admin_group)
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    group_id = callback.data.replace(DELETE_GROUP, '')
    async with state.proxy() as data:
        data["delete_group"] = group_id
        group = object_get(session=local_session, model=Groups, id=int(group_id))
        text = strings.Admin().delete_group(user_language=user.lang, group=group)
        await bot.edit_message_text(chat_id=chat_id, text=text, message_id=callback.message.message_id, reply_markup=btn.Admin().delete_group(user_language=user.lang, group=group))
        await state.finish()
        await States.admin_delete_group.set()


@dp.callback_query_handler(IsAdmin_Inline(), lambda callback: callback.data.startswith(YES_I_ACCEPT_DELETE), state=States.admin_delete_group)
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    async with state.proxy() as data:
        group_id = data["delete_group"]
        group = object_delete(session=local_session, model=Groups, id=int(group_id))
        local_session.commit()
        groups = objects_all(session=local_session, model=Groups)
        text = strings.Admin().deleted_group(user_language=user.lang)
        await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)
        await bot.send_message(chat_id=chat_id, text=text)
        text = strings.Admin().groups_list(user_language=user.lang, groups=groups)
        markup = btn.Admin().groups(user_language=user.lang, groups=groups)
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        await state.finish()
        await States.admin_group.set()



@dp.callback_query_handler(IsAdmin_Inline(), lambda callback: callback.data.startswith(BACK_TO_GROUPS), state=[States.admin_group,  States.admin_delete_group])
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    groups = objects_all(session=local_session, model=Groups)
    text = strings.Admin().groups_list(user_language=user.lang, groups=groups)
    markup = btn.Admin().groups(user_language=user.lang, groups=groups)
    await bot.edit_message_text(chat_id=chat_id, text=text, message_id=callback.message.message_id,reply_markup=markup)
    await state.finish()
    await States.admin_group.set()


@dp.message_handler(IsAdmin(), state=States.admin_group_add_name)
async def admin_get_message(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    group = object_create(session=local_session, model=Groups, title=message.text.capitalize())
    text = strings.Admin().added_group(user_language=user.lang)
    await bot.send_message(chat_id=chat_id, text=text)
    admin = object_get(session=local_session, model=Admin, telegram_id=chat_id)
    users = objects_all(session=local_session, model=User)
    groups = objects_all(session=local_session, model=Groups)
    messages = objects_all(session=local_session, model=Messages)
    if admin is not None:
        text = strings.Admin().main_menu(user_language=user.lang, admin=admin, users=users, groups=groups, messages=messages)
        markup = btn.Admin().main_menu(user_language=user.lang)
        await state.finish()
        await States.admin_page.set()
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


@dp.message_handler(IsAdmin(), state=States.admin_edit_name_group)
async def admin_get_message(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    if message.text[2:] in jmespath.search('*.back', touched()):
        user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
        admin = object_get(session=local_session, model=Admin, telegram_id=chat_id)
        users = objects_all(session=local_session, model=User)
        groups = objects_all(session=local_session, model=Groups)
        messages = objects_all(session=local_session, model=Messages)
        if admin is not None:
            text = strings.Admin().main_menu(user_language=user.lang, admin=admin, users=users, groups=groups, messages=messages)
            markup = btn.Admin().main_menu(user_language=user.lang)
            await state.finish()
            await States.admin_page.set()
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)

    else:
        user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
        groups = objects_all(session=local_session, model=Groups)
        async with state.proxy() as data:
            group = object_get(session=local_session, model=Groups, id=data["edit_name_group"])
            group.title = message.text.capitalize()
            local_session.commit()
            text = strings.Admin().edited_group(user_language=user.lang)
            await bot.send_message(chat_id=chat_id, text=text)
            text = strings.Admin().groups_list(user_language=user.lang, groups=groups)
            markup = btn.Admin().groups(user_language=user.lang, groups=groups)
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
            await state.finish()
            await States.admin_group.set()


@dp.message_handler(IsAdmin(), state=States.admin_users)
async def admin_get_message(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    
    if message.text in jmespath.search('*.Admin.users[0]', touched()):
        user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
        admin = object_get(session=local_session, model=Admin, telegram_id=chat_id)
        users = objects_filter(session=local_session, model=User, verified=True)[:20]
        if admin is not None:
            text = strings.Admin().checked_users(user_language=user.lang, users=users)
            markup = btn.ReplyKeyboardMarkup(keyboard=[[btn.back(user_language=user.lang)]],resize_keyboard=True)
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
            text = strings.Admin().checked_users_list(user_language=user.lang, users=users)
            markup = btn.Admin().checked_users(user_language=user.lang, users=users)
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
    
    if message.text in jmespath.search('*.Admin.users[1]', touched()):
        user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
        admin = object_get(session=local_session, model=Admin, telegram_id=chat_id)
        users = objects_filter(session=local_session, model=User, verified=False)[:20]
        if admin is not None:
            text = strings.Admin().notchecked_users(user_language=user.lang, users=users)
            markup = btn.ReplyKeyboardMarkup(keyboard=[[btn.back(user_language=user.lang)]],resize_keyboard=True)
            await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
            for user in users:
                text = strings.Admin().notchecked_user(user_language=user.lang, user=user)
                markup = btn.Admin().notchecked_user(user_language=user.lang, user=user)
                await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)




@dp.callback_query_handler(IsAdmin_Inline(), lambda callback: callback.data.startswith(USER_ADD_TO_GROUP), state='*')
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user_id = callback.data.replace(USER_ADD_TO_GROUP, '')
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    groups = objects_all(session=local_session, model=Groups)
    async with state.proxy() as data:
        data["user_id"] = user_id
        text = strings.Admin().user_add_to_group(user_language=user.lang, user=user)
        markup = btn.Admin().user_add_to_group(user_language=user.lang, groups=groups)
        await bot.edit_message_text(chat_id=chat_id, text=text, message_id=callback.message.message_id, reply_markup=markup)
        await state.finish()
        await States.add_user_to_group.set()


@dp.callback_query_handler(IsAdmin_Inline(), lambda callback: callback.data.startswith(ADD_USER_GROUP), state=[States.add_user_to_group])
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    group_id = callback.data.replace(ADD_USER_GROUP, '')
    
    async with state.proxy() as data:
        _user = object_get(session=local_session, model=User, id=data["user_id"])
        _user.group_id = group_id
        _user.verified = True
        local_session.commit()
        text = strings.Admin().user_added_group(user_language=user.lang)
        markup = None
        await bot.edit_message_text(chat_id=chat_id, text=text, message_id=callback.message.message_id, reply_markup=markup)
        await bot.send_message(chat_id=_user.telegram_id, text="✅ Guruhga qabul qilindingiz.Va xabarlarni qabul qila olasiz.")

@dp.callback_query_handler(IsAdmin_Inline(), lambda callback: callback.data.startswith(BACK_TO_USERS), state=[States.admin_users, States.add_user_to_group])
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)
    users = objects_all(session=local_session, model=User)
    text = strings.Admin().users(user_language=user.lang)
    markup = btn.Admin().users(user_language=user.lang)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
    await state.finish()
    await States.admin_users.set()

@dp.callback_query_handler(IsAdmin_Inline(), lambda callback: callback.data.startswith(USERS_EXCEL_DOWNLOAD), state=[States.admin_users, States.add_user_to_group])
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    groups = objects_all(session=local_session, model=Groups)
    file = InputFile(path_or_bytesio=excel_download(session=local_session, groups=groups))
    await bot.send_document(chat_id=chat_id, document=file)
    

@dp.callback_query_handler(IsAdmin_Inline(), lambda callback: callback.data.startswith(SEND_MESSAGE_TO_GROUP), state=[States.send_message])
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    group_id = callback.data.replace(SEND_MESSAGE_TO_GROUP, '')
    async with state.proxy() as data:
        data["send_message"] = "to_group"
        data["send_message_group_id"] = group_id
        await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)
        await state.finish()
        await States.send_message_send.set()
        text = strings.Admin().send_message_send(user_language=user.lang)
        markup = btn.ReplyKeyboardMarkup(keyboard=[[btn.back(user_language=user.lang)]], resize_keyboard=True)
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)


@dp.callback_query_handler(IsAdmin_Inline(), lambda callback: callback.data.startswith(SEND_MESSAGE_TO_ALL), state=[States.send_message])
async def admin_get_message(callback: types.CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    async with state.proxy() as data:
        data["send_message"] = "to_all"
        await bot.delete_message(chat_id=chat_id, message_id=callback.message.message_id)
        await state.finish()
        await States.send_message_send.set()
        text = strings.Admin().send_message_send(user_language=user.lang)
        markup = btn.ReplyKeyboardMarkup(keyboard=[[btn.back(user_language=user.lang)]], resize_keyboard=True)
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        
        

@dp.message_handler(IsAdmin(),content_types=types.ContentType.ANY, state=[States.send_message_send])
async def admin_get_message(message: types.Message, state: FSMContext):
    chat_id =message.chat.id
    user, user_created = get_or_create(session=local_session,model=User, telegram_id=chat_id)
    async with state.proxy() as data:
        if data["send_message"] == "to_all":
            _users = objects_filter(session=local_session, model=User, verified=True)
            for _user in _users:
                await bot.forward_message(chat_id=_user.telegram_id, from_chat_id=chat_id, message_id=message.message_id)
                    
        elif data["send_message"] == "to_group":
            _users = objects_filter(session=local_session, model=User, verified=True, group_id=data["send_message_group_id"])
            for _user in _users:
                await bot.forward_message(chat_id=_user.telegram_id, from_chat_id=chat_id, message_id=message.message_id)
    
    text =strings.Admin().message_sended(user_language=user.lang)
    markup = btn.Admin().main_menu(user_language=user.lang)
    await bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
    await state.finish()
    await States.admin_page.set()
    

    
executor.start_polling(dp)