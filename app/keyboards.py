from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# Клавиатура с командами
def get_main_keyboard():
    keyboard = [
        [KeyboardButton(text="/help")],
        [KeyboardButton(text="/subscribe"), KeyboardButton(text="/unsubscribe")],
        [KeyboardButton(text="/free_game"), KeyboardButton(text="/free_game_by_subscribe")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_void_inline():
    return InlineKeyboardMarkup(inline_keyboard=[])


# Клавиатура для отмены подписки
def get_action_keyboard(is_subscribe=True):
    action = "subscribe" if is_subscribe else "unsubscribe"
    action_text = "Подписаться на" if is_subscribe else "Отписаться от"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text=f"{action_text} жанр{"ы" if is_subscribe else "ов"}",
                              callback_data=f"_page_{action}_genres_1")])
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text=f"{action_text} особенност{"и" if is_subscribe else "ей"}",
                              callback_data=f"_page_{action}_features_1")])
    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text=f"{action_text} все{"" if is_subscribe else "х"}", callback_data=f"_{action}_all")])
    return keyboard


# Клавиатура для выбора жанров с пагинацией
def get_genre_keyboard(genres, have_genres, is_subscribe=True, page=1, per_page=4):
    start = (page - 1) * per_page
    remaining_genres = ((set(genres) - set(have_genres)) if is_subscribe else (set(genres) & set(have_genres)))
    end = min(start + per_page, len(remaining_genres))
    genres_to_display = list(remaining_genres)[start:end]
    action = 'subscribe' if is_subscribe else 'unsubscribe'

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for genre in genres_to_display:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=genre[1], callback_data=f"_{action}_genre_{genre[0]}")])

    # Кнопки навигации
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"_page_{action}_genres_{page - 1}"))
    if end < len(remaining_genres):
        nav.append(InlineKeyboardButton(text="Далее ▶️", callback_data=f"_page_{action}_genres_{page + 1}"))
    if nav:
        keyboard.inline_keyboard.append(nav)

    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="Вернуться в меню", callback_data=f"_back_to_menu_{action}")])

    return keyboard


# Клавиатура для выбора особенностей с пагинацией
def get_feature_keyboard(features, have_features, is_subscribe=False, page=1, per_page=4):
    start = (page - 1) * per_page
    remaining_features = ((set(features) - set(have_features)) if is_subscribe else (set(features) & set(have_features)))
    end = min(start + per_page, len(remaining_features))
    features_to_display = list(remaining_features)[start:end]
    action = 'subscribe' if is_subscribe else 'unsubscribe'

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for feature in features_to_display:
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=feature[1], callback_data=f"_{action}_feature_{feature[0]}")])

    # Кнопки навигации
    nav = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"_page_{action}_features_{page - 1}"))
    if end < len(remaining_features):
        nav.append(InlineKeyboardButton(text="Далее ▶️", callback_data=f"_page_{action}_features_{page + 1}"))
    if nav:
        keyboard.inline_keyboard.append(nav)

    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="Вернуться в меню", callback_data=f"_back_to_menu_{action}")])

    return keyboard
