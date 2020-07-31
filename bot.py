import telebot
from telebot import types
import tables
import config
from sqlalchemy.exc import IntegrityError

bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=["start", ])
def start_message(message):
    """Func adds user to bd"""
    PAGINATOR_STATUS = 1
    user_id = message.chat.id
    user_name = message.from_user.first_name
    last_user_name = message.from_user.last_name
    nickname = message.from_user.username
    sess = tables.Session()
    try:
        new_row = tables.User(user_id=user_id, user_name=user_name,
                              last_user_name=last_user_name,
                              nickname=nickname, paginator_status=PAGINATOR_STATUS)
        sess.add(new_row)
        sess.flush()
    except IntegrityError:
        bot.send_message(user_id, f'С возращаением,{message.from_user.first_name}', reply_markup=user_keyboard())
    else:
        sess.commit()
        bot.send_message(user_id, f'Hi,{message.from_user.first_name}', reply_markup=user_keyboard())
    finally:
        sess.close()


@bot.message_handler(commands=["orders", ])
def start_message(message):
    """Func dhows all orders. It uses for group chat"""
    chat_id = message.chat.id
    show_all_orders(chat_id)


def show_all_orders(chat_id):
    sess = tables.Session()
    orders_objs = sess.query(tables.Order).all()
    if orders_objs:
        for order_obj in orders_objs:
            order_longitude = order_obj.longitude
            order_latitude = order_obj.latitude
            user_phone = order_obj.phone
            order_id = order_obj.order_id
            dish_quantity = order_obj.quantity
            total_cost = order_obj.total_cost
            dish_id = order_obj.dish_id
            dish_obj = sess.query(tables.Dish).filter(tables.Dish.id == dish_id).first()
            dish_name = dish_obj.dish_name
            image = dish_obj.image
            content = dish_obj.content
            text_to_user = f'Номер заказа: {order_id}\n' \
                f'Наименование: {dish_name}\nОписание: {content}\nКоличество: {dish_quantity}' \
                f'\nСтоимость: {total_cost}\nТелефон: {user_phone}\n Локация:'
            bot.send_photo(chat_id, photo=image, caption=text_to_user)
            bot.send_location(chat_id, longitude=order_longitude, latitude=order_latitude)


@bot.message_handler(content_types=['text', ])
def commands(message):
    """Message handler"""
    user_text = message.text
    user_id = message.from_user.id
    if user_text == 'Меню 🍔':
        reset_curr_user_category(user_id)
        reset_user_dish(user_id)
        reset_paginator_status(user_id)
        menu_categories(message)
    elif user_text == 'Корзина 📦':
        show_orders(user_id)
    elif user_text == 'Заказы 💸':
        user_orders(user_id)


def user_orders(user_id):
    sess = tables.Session()
    orders_objs = sess.query(tables.Order).filter(tables.Order.user_id == user_id).all()
    if orders_objs:
        for order_obj in orders_objs:
            order_longitude = order_obj.longitude
            order_latitude = order_obj.latitude
            user_phone = order_obj.phone
            order_id = order_obj.order_id
            dish_quantity = order_obj.quantity
            total_cost = order_obj.total_cost
            dish_id = order_obj.dish_id
            dish_obj = sess.query(tables.Dish).filter(tables.Dish.id == dish_id).first()
            dish_name = dish_obj.dish_name
            image = dish_obj.image
            content = dish_obj.content
            text_to_user = f'Номер заказа: {order_id}\n' \
                f'Наименование: {dish_name}\nОписание: {content}\nКоличество: {dish_quantity}' \
                f'\nСтоимость: {total_cost}\nТелефон: {user_phone}\n Локация:'
            bot.send_photo(user_id, photo=image, caption=text_to_user, )
            bot.send_location(user_id, longitude=order_longitude, latitude=order_latitude)

    else:
        text_to_user = 'Заказов нет, перейди в корзину,чтобы оформить заказ'
        bot.send_message(user_id, text_to_user)


def show_orders(user_id):
    sess = tables.Session()
    orders_objs = sess.query(tables.Basket).filter(tables.Basket.user_id == user_id).all()
    if orders_objs:
        for order_obj in orders_objs:
            order_id = order_obj.order_id
            dish_quantity = order_obj.quantity
            total_cost = order_obj.total_cost
            dish_id = order_obj.dish_id
            dish_obj = sess.query(tables.Dish).filter(tables.Dish.id == dish_id).first()
            dish_name = dish_obj.dish_name
            image = dish_obj.image
            content = dish_obj.content
            text_to_user = f'Номер заказа: {order_id}\n' \
                f'Наименование: {dish_name}\nОписание: {content}\nКоличество: {dish_quantity}' \
                f'\nСтоимость: {total_cost}'
            bot.send_photo(user_id, photo=image, caption=text_to_user, reply_markup=basket_keyboard(order_id))

    else:
        text_to_user = 'Корзина пуста'
        bot.send_message(user_id, text_to_user)


def menu_categories(message):
    """Dunc sends keyboard with categories"""
    chat_id = message.chat.id
    text_to_user = 'Список категорию, выбери нужную:'
    bot.send_message(chat_id, text=text_to_user, reply_markup=category_keyboard())


def category_keyboard():
    """Make keyboard for category"""
    keyboard = types.InlineKeyboardMarkup()
    sess = tables.Session()
    category_objects = sess.query(tables.Category)
    for category_object in category_objects:
        category_name = category_object.category_name
        category_id = category_object.id
        button = types.InlineKeyboardButton(text=category_name, callback_data=f'category_{category_id}')
        keyboard.add(button)
    return keyboard


def dish_keyboard(call_data, user_id):
    """Make keyboard for dishes"""
    CATEGORY_ID_INDEX = 1  # call_data in format f'category_{category.index}'
    CATEGORY_FROM_BD_INDEX = 0
    sess = tables.Session()
    if 'category' in call_data:
        category_id = int(call_data.split('_')[CATEGORY_ID_INDEX])
        add_user_curr_category(user_id, category_id)
    else:
        category_id = sess.query(tables.User.curr_category).filter(tables.User.user_id == user_id).first()[
            CATEGORY_FROM_BD_INDEX]
    paginator_status = sess.query(tables.User.paginator_status).filter(tables.User.user_id == user_id)
    keyboard = types.InlineKeyboardMarkup()
    dish_objs = sess.query(tables.Dish).filter(tables.Dish.category == category_id,
                                               tables.Dish.page == paginator_status)
    for dish_obj in dish_objs:
        dish_name = dish_obj.dish_name
        dish_cost = dish_obj.cost
        dish_id = dish_obj.id
        button = types.InlineKeyboardButton(text=f'{dish_name} - {dish_cost}', callback_data=f'dish_{dish_id}')
        keyboard.add(button)
    keyboard = validate_dish_paginator(user_id, category_id, keyboard)
    return keyboard


def validate_dish_paginator(user_id, category_id, keyboard):
    PAGINATOR_STATUS_INDEX = 0
    START_PAGINATOR_PAGE = 1
    sess = tables.Session()
    paginator_status = sess.query(tables.User.paginator_status).filter(tables.User.user_id == user_id).first()[
        PAGINATOR_STATUS_INDEX]
    last_paginator_page = sess.query(tables.Dish.page).filter(tables.Dish.category == category_id).order_by(
        tables.Dish.page.desc()).first()[PAGINATOR_STATUS_INDEX]
    if paginator_status == START_PAGINATOR_PAGE and paginator_status < last_paginator_page:
        more_btn = types.InlineKeyboardButton(text='⏩', callback_data='more')
        keyboard.add(more_btn)
        return keyboard
    elif paginator_status == START_PAGINATOR_PAGE and paginator_status == last_paginator_page:
        return keyboard
    elif paginator_status > START_PAGINATOR_PAGE and paginator_status == last_paginator_page:
        back_btn = types.InlineKeyboardButton(text='⏪', callback_data='back')
        keyboard.add(back_btn)
        return keyboard
    elif paginator_status > START_PAGINATOR_PAGE and paginator_status < last_paginator_page:
        more_btn = types.InlineKeyboardButton(text='⏩', callback_data='more')
        back_btn = types.InlineKeyboardButton(text='⏪', callback_data='back')
        keyboard.row(back_btn, more_btn)
        return keyboard


def menu_dish(chat_id, message_id, call_data, user_id):
    """Edit dishes_keyboard"""
    text_to_user = 'Выбери блюдо:'
    bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                          text=text_to_user, reply_markup=dish_keyboard(call_data, user_id))


def first_dish(chat_id, message_id, call_data, user_id):
    DISH_ID_INDEX = 1  # call_ data in format dish_dish_id (dist_1(1 in dish id))
    DEFAULT_DISH_QUANTITY = 1
    dish_id = int(call_data.split('_')[DISH_ID_INDEX])
    give_user_dish(dish_id, user_id)
    sess = tables.Session()
    curr_dish_obj = sess.query(tables.Dish).filter(tables.Dish.id == dish_id).first()
    dish_name = curr_dish_obj.dish_name
    dish_content = curr_dish_obj.content
    dish_cost = curr_dish_obj.cost
    dish_image = curr_dish_obj.image
    text_to_user = f'Наименование: {dish_name}\nОписание: {dish_content}'
    keyboard = one_dish_keyboard(dish_cost, DEFAULT_DISH_QUANTITY)
    send_one_dish(text_to_user, chat_id, message_id, keyboard, dish_image)


def one_dish_keyboard(dish_cost, dish_quantity, dish_btn_caption='Блюдо'):
    keyboard = types.InlineKeyboardMarkup()
    cost_bnt = types.InlineKeyboardButton(text=f'Цена: {dish_cost}', callback_data='#')  # No callBack handler
    quantity_btn = types.InlineKeyboardButton(text=f'Количество:{dish_quantity}', callback_data='#')
    add_quantity_bnt = types.InlineKeyboardButton(text='⏩', callback_data='add_quantity')
    minus_quantity_btn = types.InlineKeyboardButton(text='⏪', callback_data='minus_quantity')
    add_to_basket_btn = types.InlineKeyboardButton(text='Добавить в корзину 🗑', callback_data='add_to_basket')
    add_commit_btn = types.InlineKeyboardButton(text='Добавить комментарий', callback_data='add_commit')
    show_commit_btn = types.InlineKeyboardButton(text='Смотреть комментарии', callback_data='show_commits')
    next_dish_btn = types.InlineKeyboardButton(text='⏩', callback_data='next_dish')
    previous_dish_btn = types.InlineKeyboardButton(text='⏪', callback_data='previous_dish')
    dish_btn = types.InlineKeyboardButton(text=dish_btn_caption, callback_data='#')  # No callback handler
    keyboard.add(cost_bnt)
    keyboard.row(minus_quantity_btn, quantity_btn, add_quantity_bnt)
    keyboard.row(previous_dish_btn, dish_btn, next_dish_btn)
    keyboard.add(add_to_basket_btn)
    keyboard.row(add_commit_btn, show_commit_btn)
    return keyboard


def send_one_dish(text_to_user, chat_id, message_id, keyboard, dish_image):
    delete_previous_message(chat_id, message_id)
    bot.send_photo(chat_id, photo=dish_image, caption=text_to_user, reply_markup=keyboard)


def delete_previous_message(chat_id, message_id):
    bot.delete_message(chat_id, message_id)


def give_user_dish(dish_id, user_id):
    """Func adds current dish_id and it quantity in bd"""
    DEFAULT_DISH_QUANTITY = 1
    sess = tables.Session()
    user_obj = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    user_obj.curr_dish = dish_id
    user_obj.quantity_dish = DEFAULT_DISH_QUANTITY
    user_obj.cost_curr_dish = sess.query(tables.Dish.cost).filter(tables.Dish.id == dish_id).first()
    sess.commit()


def reset_user_dish(user_id):
    """Func resets current dish_id and it quantity in bd"""
    sess = tables.Session()
    user_obj = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    user_obj.curr_dish = None
    user_obj.quantity_dish = None
    sess.commit()


def user_keyboard():
    """Inline keyboard"""
    markup = types.ReplyKeyboardMarkup()
    menu_button = types.KeyboardButton('Меню 🍔')
    basket_button = types.KeyboardButton('Корзина 📦')
    order_button = types.KeyboardButton('Заказы 💸')
    markup.add(menu_button)
    markup.add(basket_button)
    markup.add(order_button)
    return markup


def plus_paginator_status(user_id):
    """Minus 1 to user_paginator_status in bd"""
    STEP = 1
    sess = tables.Session()
    user = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    user.paginator_status += STEP
    sess.commit()


def minus_paginator_status(user_id):
    """Plus 1 to user paginator_status in bd"""
    STEP = 1
    sess = tables.Session()
    user = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    user.paginator_status -= STEP
    sess.commit()


def add_user_curr_category(user_id, category_id):
    """Func writes current user category in bd"""
    sess = tables.Session()
    user = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    user.curr_category = category_id
    sess.commit()


def reset_curr_user_category(user_id):
    """Func resets current user category in bd"""
    sess = tables.Session()
    user = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    user.curr_category = None
    sess.commit()


def reset_paginator_status(user_id):
    """Change user paginator status to 1 in bd"""
    DEFAULT_PAGINATOR_STATUS = 1
    sess = tables.Session()
    user = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    user.paginator_status = DEFAULT_PAGINATOR_STATUS
    sess.commit()


def add_quantity_dish(user_id):
    """func adds one to auntity of dish"""
    STEP = 1
    sess = tables.Session()
    user_obj = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    curr_dish_id = user_obj.curr_dish
    dish_quantity = user_obj.quantity_dish + STEP
    one_dish_cost = sess.query(tables.Dish.cost).filter(tables.Dish.id == curr_dish_id).first()
    total_cost = int(one_dish_cost[0]) * dish_quantity
    user_obj.quantity_dish = dish_quantity
    user_obj.cost_curr_dish = total_cost
    sess.commit()


def minus_quantity_dish(user_id):
    STEP = 1
    sess = tables.Session()
    user_obj = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    curr_dish_id = user_obj.curr_dish
    curr_dish_quantity = user_obj.quantity_dish
    if curr_dish_quantity > 1:
        new_dish_quantity = curr_dish_quantity - STEP
        one_dish_cost = sess.query(tables.Dish.cost).filter(tables.Dish.id == curr_dish_id).first()
        total_cost = int(one_dish_cost[0]) * new_dish_quantity
        user_obj.quantity_dish = new_dish_quantity
        user_obj.cost_curr_dish = total_cost
        sess.commit()


def add_minus_data_for_keyboard(user_id, chat_id, message_id):
    """Func retrievers new cost and new quantity for curr dish from bd
     and edits one_dish message"""
    sess = tables.Session()
    user_obj = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    dish_id = user_obj.curr_dish
    total_cost = user_obj.cost_curr_dish
    dish_quantity = user_obj.quantity_dish
    dish_obj = sess.query(tables.Dish).filter(tables.Dish.id == dish_id).first()
    dish_name = dish_obj.dish_name
    dish_content = dish_obj.content
    text_to_user = f'Название: {dish_name}\nОписание: {dish_content}\n'
    keyboard = one_dish_keyboard(total_cost, dish_quantity)
    edit_dish(text_to_user, chat_id, message_id, keyboard)


def edit_dish(text_to_user, chat_id, message_id, keyboard):
    bot.edit_message_caption(chat_id=chat_id, message_id=message_id,
                             caption=text_to_user, reply_markup=keyboard)


def add_dish_to_basket(user_id):
    sess = tables.Session()
    user_obj = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    curr_dish_id = user_obj.curr_dish
    curr_dish_quantity = user_obj.quantity_dish
    total_cost = user_obj.cost_curr_dish
    new_order = tables.Basket(user_id=user_id, dish_id=curr_dish_id,
                              quantity=curr_dish_quantity, total_cost=total_cost)
    sess.add(new_order)
    sess.commit()
    text_to_user = 'Заказ добавлен,для просмотра заказа перейдите в корзину'
    bot.send_message(user_id, text_to_user)


def basket_keyboard(order_id):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text='Оформить заказ', callback_data=f'make_order_{order_id}')
    keyboard.add(button)
    return keyboard


def make_order(user_id, call_data):
    ORDER_ID_INDEX = 2
    order_id = call_data.split('_')[ORDER_ID_INDEX]
    text_to_user = 'Нажмите на кнопку,чтобы мы получили ваш номер'
    msg = bot.send_message(user_id, text_to_user, reply_markup=phone_keyboard())
    bot.register_next_step_handler(msg, lambda msg: get_user_phone(msg, order_id))


def phone_keyboard():
    keyboard = types.ReplyKeyboardMarkup()
    phone_btn = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard.add(phone_btn)
    return keyboard


def get_user_phone(message, order_id):
    chat_id = message.chat.id
    text_to_user = 'Нажми на кнопку,чтобы отправить адрес'
    try:
        phone = message.contact.phone_number
    except AttributeError:
        text_to_user = 'Номер телефона не добавлен'
        bot.send_message(chat_id, text_to_user, reply_markup=user_keyboard())
    else:
        msg = bot.send_message(chat_id, text_to_user, reply_markup=location_keyboard())
        bot.register_next_step_handler(msg, lambda msg: get_user_location(msg, phone, order_id))


def location_keyboard():
    keyboard = types.ReplyKeyboardMarkup()
    location_btn = types.KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard.add(location_btn)
    return keyboard


def get_user_location(message, phone_number, order_id):
    user_id = message.from_user.id
    chat_id = message.chat.id
    try:
        latitude = message.location.latitude
        longitude = message.location.longitude
    except AttributeError:
        text_to_user = 'Номер местоположение не добавлено'
        bot.send_message(chat_id, text_to_user, reply_markup=user_keyboard())
    else:
        sess = tables.Session()
        basket_order_obj = sess.query(tables.Basket).filter(tables.Basket.order_id == order_id).first()
        dish_id = basket_order_obj.dish_id
        dish_quantity = basket_order_obj.quantity
        total_cost = basket_order_obj.total_cost
        save_order_data(user_id, latitude, longitude, dish_id, dish_quantity, total_cost, phone_number)
        sess.query(tables.Basket).filter(tables.Basket.order_id == order_id).delete()
        sess.commit()


def save_order_data(user_id, latitude, longitude, dish_id, dish_quantity, total_cost, phone_number):
    sess = tables.Session()
    order = tables.Order(user_id=user_id, latitude=latitude, longitude=longitude,
                         dish_id=dish_id, quantity=dish_quantity,
                         total_cost=total_cost, phone=phone_number)
    sess.add(order)
    sess.commit()
    text_to_user = 'Заказ оформлен'
    bot.send_message(user_id, text_to_user, reply_markup=user_keyboard())


def add_commit(chat_id, user_id):
    """Func sends message Отправь коммент to user and redirects to get_commit func """
    text_to_user = 'Отправь комментарий к данному товару'
    msg = bot.send_message(chat_id, text_to_user)
    bot.register_next_step_handler(msg, lambda msg: get_commit(msg, user_id))


def get_commit(message, user_id):
    """Func gets commit from user and saves to bd"""
    commit_text = message.text
    chat_id = message.chat.id
    sess = tables.Session()
    user_obj = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    curr_dish = user_obj.curr_dish
    commit = tables.DishCommits(dish_id=curr_dish, commit_content=commit_text, author=user_id)
    sess.add(commit)
    sess.commit()
    bot.send_message(chat_id, 'Отзыв добавлен')


def show_commits(chat_id, user_id):
    sess = tables.Session()
    user_obj = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    curr_dish_id = user_obj.curr_dish
    commits_for_curr_dish = sess.query(tables.DishCommits).filter(tables.DishCommits.dish_id == curr_dish_id).order_by(
        tables.DishCommits.add_date.desc()).limit(5).all()
    if commits_for_curr_dish:
        for commit_obj in commits_for_curr_dish:
            commit_text = commit_obj.commit_content
            author_id = commit_obj.author
            add_date = commit_obj.add_date
            author_obj = sess.query(tables.User).filter(tables.User.user_id == author_id).first()
            author_name = author_obj.user_name
            text_to_user = f'Автор:{author_name}\nКомментарий: {commit_text}\nДата: {add_date}'
            bot.send_message(chat_id, text_to_user)
    else:
        text_to_user = 'Комментариев в данному товару на данный момент нет'
        bot.send_message(chat_id, text_to_user)


def send_next_dish(chat_id, user_id, message_id):
    DEFAULT_DISH_QUANTITY = 1
    STEP = 1
    sess = tables.Session()
    user_obj = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    curr_dish_id = user_obj.curr_dish
    curr_category = user_obj.curr_category
    curr_dish_obj = sess.query(tables.Dish).filter(tables.Dish.id == curr_dish_id).first()
    all_dish_in_this_category_objs = sess.query(tables.Dish).filter(
        tables.Dish.category == curr_category).all()  # all dishes in curr category
    curr_dish_position = all_dish_in_this_category_objs.index(curr_dish_obj)
    next_dish_position = curr_dish_position + STEP
    last_dish_index = len(all_dish_in_this_category_objs) - 1
    if next_dish_position <= last_dish_index:
        next_dish_obj = all_dish_in_this_category_objs[next_dish_position]
        next_dish_name = next_dish_obj.dish_name
        next_dish_content = next_dish_obj.content
        next_dish_cost = next_dish_obj.cost
        next_dish_image = next_dish_obj.image
        next_dish_id = next_dish_obj.id
        text_to_user = f'Наименование: {next_dish_name}\nОписание: {next_dish_content}'
        dish_btn_cation = 'Конец' if next_dish_position == last_dish_index else None
        if not dish_btn_cation:
            keyboard = one_dish_keyboard(next_dish_cost, DEFAULT_DISH_QUANTITY)
        else:
            keyboard = one_dish_keyboard(next_dish_cost, DEFAULT_DISH_QUANTITY, dish_btn_cation)
        send_one_dish(text_to_user, chat_id, message_id, keyboard, next_dish_image)
        user_obj.curr_dish_pos_in_list = curr_dish_position
        sess.commit()
        change_user_curr_dish(user_id, STEP, next_dish_id, next_dish_cost)


def send_previous_dish(chat_id, user_id, message_id):
    DEFAULT_DISH_QUANTITY = 1
    STEP = -1
    FIRST_DISH_INDEX = 0
    sess = tables.Session()
    user_obj = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    curr_dish_id = user_obj.curr_dish
    curr_category = user_obj.curr_category
    curr_dish_obj = sess.query(tables.Dish).filter(tables.Dish.id == curr_dish_id).first()
    all_dish_in_this_category_objs = sess.query(tables.Dish).filter(
        tables.Dish.category == curr_category).all()  # all dishes in curr category
    curr_dish_position = all_dish_in_this_category_objs.index(curr_dish_obj)
    previous_dish_position = curr_dish_position + STEP
    if previous_dish_position >= FIRST_DISH_INDEX:
        previous_dish_obj = all_dish_in_this_category_objs[previous_dish_position]
        previous_dish_name = previous_dish_obj.dish_name
        previous_dish_content = previous_dish_obj.content
        previous_dish_cost = previous_dish_obj.cost
        previous_dish_image = previous_dish_obj.image
        previous_dish_id = previous_dish_obj.id
        text_to_user = f'Наименование: {previous_dish_name}\nОписание: {previous_dish_content}'
        dish_btn_cation = 'Начало' if previous_dish_position == FIRST_DISH_INDEX else None
        if not dish_btn_cation:
            keyboard = one_dish_keyboard(previous_dish_cost, DEFAULT_DISH_QUANTITY)
        else:
            keyboard = one_dish_keyboard(previous_dish_cost, DEFAULT_DISH_QUANTITY, dish_btn_cation)
        send_one_dish(text_to_user, chat_id, message_id, keyboard, previous_dish_image)
        user_obj.curr_dish_pos_in_list = curr_dish_position
        sess.commit()
        change_user_curr_dish(user_id, STEP, previous_dish_id, previous_dish_cost)


def change_user_curr_dish(user_id, step, next_dish_id, next_dish_cost):
    """Func change information about current user dish in bd"""
    DEFAULT_QUANTITY_DISH = 1
    sess = tables.Session()
    user_obj = sess.query(tables.User).filter(tables.User.user_id == user_id).first()
    curr_dish_pos_in_list = user_obj.curr_dish_pos_in_list
    next_dish_pos_in_list = curr_dish_pos_in_list + step
    user_obj.curr_dish_pos_in_list = next_dish_pos_in_list
    user_obj.curr_dish = next_dish_id
    user_obj.cost_curr_dish = next_dish_cost
    user_obj.quantity_dish = DEFAULT_QUANTITY_DISH
    sess.commit()


@bot.callback_query_handler(func=lambda call: True)
def keyboard_callback_handler(call):
    call_data = call.data
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    user_id = call.from_user.id
    print(call_data)
    if 'category' in call_data:
        menu_dish(chat_id, message_id, call_data, user_id)
    elif call_data == 'more':
        plus_paginator_status(user_id)
        menu_dish(chat_id, message_id, call_data, user_id)
    elif call_data == 'back':
        minus_paginator_status(user_id)
        menu_dish(chat_id, message_id, call_data, user_id)
    elif call_data == 'add_quantity':
        add_quantity_dish(user_id)
        add_minus_data_for_keyboard(user_id, chat_id, message_id)
    elif call_data == 'minus_quantity':
        minus_quantity_dish(user_id)
        add_minus_data_for_keyboard(user_id, chat_id, message_id)
    elif call_data == 'add_to_basket':
        add_dish_to_basket(user_id)
    elif 'make_order' in call_data:
        make_order(user_id, call_data)
    elif call_data == 'add_commit':
        add_commit(chat_id, user_id)
    elif call_data == 'show_commits':
        show_commits(chat_id, user_id)
    elif call_data == 'next_dish':
        send_next_dish(chat_id, user_id, message_id)
    elif call_data == 'previous_dish':
        send_previous_dish(chat_id, user_id, message_id)
    elif 'dish' in call_data:
        first_dish(chat_id, message_id, call_data, user_id)


if __name__ == '__main__':
    bot.polling(none_stop=True)
