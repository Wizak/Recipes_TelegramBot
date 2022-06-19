import logging
import io
import os
import time

from config import Config

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from werkzeug.datastructures import auth_property

from app import db
from app.models import User, Recipe, Description


logging.basicConfig(level=logging.INFO)
bot = Bot(token=Config.API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())



class Form_recipe(StatesGroup):
    title = State()
    review = State()
    components = State()
    description = State()



def check_user(user_id):
    return User.query.filter(User.user_id == user_id).scalar()       


def check_admin(user_id):
    return check_user(user_id).acess == True


def update_acess(user_id):
    User.query.filter(User.user_id == user_id).update({User.acess: True})
    db.session.commit()


def add_user(*args):
    query_user = check_user(args[0])
    if not query_user:
        user = User(user_id=args[0], username=args[1], first_name=args[2], last_name=args[3])
        db.session.add(user)
        db.session.commit()


def add_recipe(*args):
    query_user = check_user(args[1])
    if query_user:
        recipe = Recipe(title=args[0], user_id=query_user.id)
        db.session.add(recipe)
        db.session.commit()


def add_description(*args):
    query_recipe = query_recipe_title(args[3])
    if query_recipe:
        description = Description(review=args[0],components=args[1], description=args[2], recipe_id=query_recipe.id)
        db.session.add(description)
        db.session.commit()


def query_recipe_title(title):
    query_recipe = Recipe.query.filter(Recipe.title == title).scalar()
    return query_recipe


def query_recipe():
    query_recipe = Recipe.query.all()
    return query_recipe


def query_description(title):
    recipe_id = query_recipe_title(title).id
    query_description = Description.query.filter(Description.recipe_id == recipe_id).scalar()
    return query_description


@dp.message_handler(commands=['start'])
async def start_user(message: types.Message):
    user_id = message['from']['id']
    username = message['from']['username']
    user_first_name = message['from']['first_name']
    user_last_name = message['from']['last_name']
    add_user(user_id, username, user_first_name, user_last_name)
    answer_message = f'<b>Hello, <u>{username}</u>.\nLet`s start working!</b>'
    await message.answer(answer_message)


@dp.message_handler(commands=['admin'])
async def start_user(message: types.Message):
    user_id = message['from']['id']
    username = message['from']['username']
    password = message.text.split()
    if len(password) == 1:
        answer_message = f'<b><u>{username}</u>, please, enter password.</b>'
    elif password[-1] == Config.PASSWORD:
        update_acess(user_id)
        answer_message = f'<b><u>{username}</u> is admin now.</b>'
    else:
        answer_message = f'<b><u>{username}</u>, your password is incorrect.</b>'
    await message.answer(answer_message)  


@dp.message_handler(commands=['show'])
async def add_post(message: types.Message):
    context = message.text.split()
    if len(context) >= 2:
        user_id = message['from']['id']
        title = ' '.join(context[1:])
        desc = query_description(title)
        components = desc.components.splitlines()
        description = desc.description
        review = desc.review
        comp_answer = ''.join([f'<b>{i}.</b> {c}\n' for i, c in zip(range(1, len(components)+1), components)])
        answer_message = title + '\n' + '<b>-</b>'*10 + '\n' + comp_answer + '<b>-</b>'*10 + '\n' + description
        with open('photos/file.jpg', 'wb') as f:
            f.write(review)
        await bot.send_photo(chat_id=user_id, photo=open('photos/file.jpg', 'rb'))
    elif len(context):
        answer_message = '<b>Recipe is`t exist.</b>'
    else:
        answer_message = '<b>Title is missed.</b>'
    await message.answer(answer_message)
    

@dp.message_handler(commands=['recipes'])
async def add_post(message: types.Message):
    titles = [r.title for r in query_recipe()]
    if titles:
        answer_message = f'<b>Recipe titles:</b>\n' + ''.join([f'<b>{i}.</b> {t}\n' for i, t in zip(range(1, len(titles)+1), titles)])
    else:
        answer_message = '<b>Recipes is empty.</b>'
    await message.answer(answer_message)  


@dp.message_handler(commands=['info'])
async def start_user(message: types.Message):
    title = message.text.split()
    if len(title) >= 2:
        title = ' '.join(title[1:])
        recipe_query = query_recipe_title(title)
        if recipe_query:
            user_id = recipe_query.user_id
            user_query = User.query.filter(User.id == user_id).scalar()
            username = user_query.username
            datetime = str(recipe_query.date_time)[:-7]
            answer_message = f'<b>Title:</b>  {title}\n<b>User:</b>  {username}\n<b>Date:</b>  {datetime}'
            await message.answer(answer_message) 


@dp.message_handler(commands=['admins'])
async def start_user(message: types.Message):
    users_query = User.query.filter(User.acess == True).scalar()
    if users_query:
        try:
            usernames = [user.username for user in users_query]
            answer_message = '<b>Admins:</b>\n' + '\n'.join([f'<b>{i}.</b> {n}' for i, n in zip(range(1, len(usernames)+1), usernames)])
        except:
            username = users_query.username
            answer_message = f'<b>Admins:\n1.</b> {username}'
    else:
        answer_message = '<b>Admins is`t exist.</b>'
    await message.answer(answer_message) 


@dp.message_handler(commands=['users'])
async def start_user(message: types.Message):
    users = len(User.query.all())
    answer_message = f'<b>Count users:</b>  {users}'
    await message.answer(answer_message) 


@dp.message_handler(commands=['add'])
async def add_post(message: types.Message):
    user_id = message['from']['id']
    username = message['from']['username']
    if check_admin(user_id):
        answer_message = '<b>Title</b>'
        await message.answer(answer_message)
        await Form_recipe.title.set()
    else:
        answer_message = f'<b><u>{username}</u> is`t admin. Please, pick command: "/admin".</b>'
        await message.answer(answer_message)


@dp.message_handler(state=Form_recipe.title)
async def add_title(message: types.Message, state: FSMContext):
    answer_message = message.text
    query = Recipe.query.filter(Recipe.title == answer_message).scalar()
    if query:
        await message.answer('<b>Title recipe is already exist!</b>')
        await state.finish()
    else:
        await state.update_data(answer_title=answer_message)
        await message.answer('<b>Components</b>')
        await Form_recipe.components.set()


@dp.message_handler(state=Form_recipe.components)
async def add_components(message: types.Message, state: FSMContext):
    answer_message = message.text
    await state.update_data(answer_components=answer_message)
    await message.answer('<b>Description</b>')
    await Form_recipe.description.set()


@dp.message_handler(state=Form_recipe.description)
async def add_descriptions(message: types.Message, state: FSMContext):
    answer_message = message.text
    await state.update_data(answer_description=answer_message)
    await message.answer('<b>Photo</b>')
    await Form_recipe.review.set()


@dp.message_handler(content_types=['photo'], state=Form_recipe.review)
async def add_review(message: types.Message, state: FSMContext):
    user_id = message['from']['id']
    data = await state.get_data()
    title = data.get('answer_title')
    components = data.get('answer_components')
    description = data.get('answer_description')
    path = await message.photo[0].download()
    with open(path.name, 'rb') as f:
        review = f.read()
    add_recipe(title, user_id)
    add_description(review, components, description, title)
    await message.answer('<b>Yep!</b>')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)