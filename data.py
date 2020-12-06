import dbworker
import config
from aiogram import types


class Button(config.Enum):
    B_HELLO = 'Привет, Ванда'
    B_YES = 'Да'
    B_NO = 'Нет'
    B_TO_MAIN_MENU = 'В главное меню'
    B_BACK = '<< Назад'

    B_MENU_MOOD = 'Отметить настроение'
    B_MENU_ABOUT = 'Обо мне'
    B_MENU_STAT = 'Статистика'
    B_MENU_SETTINGS = 'Настройки'

    B_SETTINGS_TIME_ZONE = 'Изменить часовой пояс'
    B_SETTINGS_NOTIFICATIONS_CHANGE = 'Изменить время напоминаний'
    B_SETTINGS_NOTIFICATION_REMOVE = 'Отменить напоминания'

    E_ANGER = 'Гнев'
    E_FEAR = 'Страх'
    E_SADNESS = 'Печаль'
    E_JOY = 'Радость'


hello = types.ReplyKeyboardMarkup(resize_keyboard=True)
hello.row(Button.B_HELLO.value)

yes_or_no = types.ReplyKeyboardMarkup(resize_keyboard=True)
yes_or_no.row(Button.B_YES.value, Button.B_NO.value)

to_main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
to_main_menu.row(Button.B_TO_MAIN_MENU.value)

back_or_to_main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
back_or_to_main_menu.row(Button.B_BACK.value, Button.B_TO_MAIN_MENU.value)

main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row(Button.B_MENU_MOOD.value, Button.B_MENU_ABOUT.value)
main_menu.row(Button.B_MENU_STAT.value, Button.B_MENU_SETTINGS.value)

settings = types.ReplyKeyboardMarkup(resize_keyboard=True)
settings.row(Button.B_SETTINGS_TIME_ZONE.value)
settings.row(Button.B_SETTINGS_NOTIFICATIONS_CHANGE.value)
settings.row(Button.B_SETTINGS_NOTIFICATION_REMOVE.value)
settings.row(Button.B_TO_MAIN_MENU.value)

mood_groups = types.ReplyKeyboardMarkup(resize_keyboard=True)
mood_groups.row(Button.E_ANGER.value, Button.E_FEAR.value)
mood_groups.row(Button.E_SADNESS.value, Button.E_JOY.value)
mood_groups.row(Button.B_TO_MAIN_MENU.value)

mood_anger = ['Бешенство', 'Ярость', 'Злость', 'Раздражение',
              'Ненависть', 'Презрение', 'Отвращение', 'Неприязнь',
              'Возмущение', 'Негодование', 'Уязвленность', 'Обида',
              'Ожесточение', 'Зависть', 'Досада']

mood_fear = ['Ужас', 'Испуг', 'Тревога', 'Беспокойство',
             'Опасение', 'Растерянность', 'Робость']

mood_sadness = ['Скорбь', 'Горе', 'Тоска', 'Грусть',
                'Отчаяние', 'Уныние', 'Опустошенность', 'Беспомощность',
                'Жалость', 'Сожаление', 'Бессилие', 'Подавленность']

mood_joy = ['Восторг', 'Восхищение', 'Упоение', 'Ликование',
            'Счастье', 'Радость', 'Приподнятость', 'Умиротворение',
            'Любовь', 'Нежность', 'Гордость', 'Благодарность',
            'Вдохновение', 'Наслаждение']

M_SEP = '\n\n'

M_WELCOME_MESSAGE = 'Привет! Меня зовут Ванда и я помогу тебе следить за своим настроением и эмоциями.'
M_WELCOME_NOTIFICATIONS = 'Ты хочешь получать напоминания? Я буду писать тебе ежедневно в выбранное время, ' \
                          'чтобы помочь не забыть отметить своё настроение.'

M_NOTIFICATIONS_TIME_QUESTION = 'Отлично! Скажи, пожалуйста, во сколько ты хочешь получать напоминание? '
M_NOTIFICATIONS_TIME_FORMAT = 'Напиши время в формате \"h:mm\" или \"hh:mm\", как, например, 7:00 или 14:00.'
M_NOTIFICATIONS_DONE = 'Спасибо, напоминания будут приходить ежедневно в '
M_NOTIFICATIONS_REMOVE = 'Ты хочешь отменить напоминания? Я больше не буду ежедневно тебе писать, ' \
                         'но ты всё ещё будешь иметь возможность отметить своё настроение из главного меню.'
M_NOTIFICATIONS_CANCELLED = 'Ежедневные напоминания отменены.'
M_NOTIFICATIONS_NOT_CANCELLED = 'Ежедневные напоминания не были отменены.'

M_MAIN_MENU = 'Добро пожаловать в главное меню.'
M_SETTINGS = 'Здесь ты можешь настроить свой часовой пояс и напоминания.'

M_ABOUT = 'Это Ванда — бот, который помогает отслеживать настроение и эмоции.\n\n' \
          'Любая эмоция — это реакция организма на внешние воздействия, и здоровый подход к ' \
          'эмоциям предполагает, что все они важны для душевной гармонии. Эмоции — это маяки, которые подают сигнал: ' \
          'здесь комфортно, там опасно, с этим человеком можно подружиться, а того лучше остерегаться. Именно поэтому ' \
          'важно научиться осознавать свои эмоции, и для того, чтобы помочь в этом нелегком деле, была создана Ванда.' \
          '\n\n' \
          'Эмоции можно отмечать раз в час, а запрашивать статистику - раз в сутки. Это сделано, чтобы исключить' \
          'возможность бездумно засылать десяток эмоций, не размышляя особо, что конкретно ты сейчас чувствуешь.\n\n' \
          'Если у тебя есть пожелания, предложения или вопросы, то ' \
          'заполни, пожалуйста, форму. Любой фидбек приветствуется и помогает Ванде становиться лучше :)'

M_MOOD_START = 'Для твоего удобства все эмоции разбиты по группам. Выбери, пожалуйста, группу, которой соответствует' \
               ' твоя эмоция. Если ошибёшься, ничего страшного: всегда можно будет вернуться в это меню и выбрать ' \
               'другую группу.'
M_MOOD_UNKNOWN_GROUP = 'Выбери, пожалуйста, одну группу из предложенных.'
M_MOOD_EMOTION = 'Прислушайся к себе, выбери эмоцию из списка и сообщи её мне. Учти, что тебе нужно написать ' \
                 'всего одну эмоцию, и она обязательно должна быть из списка выше. Если ты не видишь в списке ' \
                 'подходящую эмоцию, то, возможно, тебе стоит вернуться в предыдущее меню и выбрать другую группу.'
M_MOOD_UNKNOWN_EMOTION = 'Выбери, пожалуйста, одна эмоцию из перечисленных в списке выше.'
M_MOOD_EMOTION_GOT = 'Спасибо, записала эту эмоцию.'


async def call_notifications(message):
    await message.answer('Хорошо! Укажи свой часовой пояс, пожалуйста, в формате UTC+_. '
                         'Например, в Москве или Санкт-Петербурге время UTC+3', reply_markup=to_main_menu)
    dbworker.set_state(message.chat.id, config.State.SET_TIME_ZONE.value)


async def call_notifications_exit(message):
    await message.answer('Хорошо! Ты всегда можешь настроить напоминания в пункте "Настройки" главного меню.' + M_SEP,
                         reply_markup=main_menu)
    dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)


async def call_set_time_zone_fail(message):
    await message.answer('Пожалуйста, проверь, что отправленное тобой время имеет формат \"UTC+_\". Узнать свой '
                         'часовой пояс можно, например, на сайте time.is', reply_markup=to_main_menu)
    dbworker.set_state(message.chat.id, config.State.SET_TIME_ZONE.value)


async def call_set_time_zone_ask_time(hours, minutes):
    return 'Сейчас у тебя ' + hours + ':' + minutes + ', так?'


async def call_set_notifications_time(message):
    dbworker.set_state(message.chat.id, config.State.SET_NOTIFICATIONS.value)
    await message.answer(M_NOTIFICATIONS_TIME_QUESTION + M_NOTIFICATIONS_TIME_FORMAT, reply_markup=back_or_to_main_menu)


async def get_emotions_by_group(message, emotions_list):
    dbworker.set_state(message.chat.id, config.State.SET_EMOTION.value)
    await message.answer(M_MOOD_EMOTION + M_SEP)
    await message.answer(''.join(str('·  ' + e + '\n') for e in emotions_list), reply_markup=back_or_to_main_menu)


async def call_mood_exit(message):
    await message.answer('Хорошо! Ты можешь вернуться в любое время.' + M_SEP, reply_markup=main_menu)
    dbworker.set_state(message.chat.id, config.State.MAIN_MENU.value)
