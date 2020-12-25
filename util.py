import dbworker
import config
import os
from aiogram import types
import pylatex as pyl
import datetime
import em_config
import string
import random


class Button(config.Enum):
    B_HELLO = 'Привет'
    B_HELLO_VANDA = 'Привет, Эмили'
    B_YES = 'Да'
    B_NO = 'Нет'
    B_TO_MAIN_MENU = 'В главное меню'
    B_BACK = '<< Назад'

    B_MENU_EMOTIONS = 'Отметить эмоцию'
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
    E_SURPRISE = 'Удивление'
    E_INTEREST = 'Интерес'
    E_SHAME = 'Стыд'

    B_STAT_WEEK = 'За последнюю неделю'
    B_STAT_MONTH = 'С начала месяца'
    B_DONT_WANT = 'Не хочу'


hello = types.ReplyKeyboardMarkup(resize_keyboard=True)
hello.row(Button.B_HELLO_VANDA.value)

yes_or_no = types.ReplyKeyboardMarkup(resize_keyboard=True)
yes_or_no.row(Button.B_YES.value, Button.B_NO.value)

to_main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
to_main_menu.row(Button.B_TO_MAIN_MENU.value)

back_or_to_main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
back_or_to_main_menu.row(Button.B_BACK.value, Button.B_TO_MAIN_MENU.value)

main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row(Button.B_MENU_EMOTIONS.value, Button.B_MENU_ABOUT.value)
main_menu.row(Button.B_MENU_STAT.value, Button.B_MENU_SETTINGS.value)

settings = types.ReplyKeyboardMarkup(resize_keyboard=True)
settings.row(Button.B_SETTINGS_TIME_ZONE.value)
settings.row(Button.B_SETTINGS_NOTIFICATIONS_CHANGE.value)
settings.row(Button.B_SETTINGS_NOTIFICATION_REMOVE.value)
settings.row(Button.B_TO_MAIN_MENU.value)

emotions_groups = types.ReplyKeyboardMarkup(resize_keyboard=True)
emotions_groups.row(Button.E_ANGER.value, Button.E_FEAR.value, Button.E_SHAME.value)
emotions_groups.row(Button.E_SADNESS.value, Button.E_JOY.value)
emotions_groups.row(Button.E_SURPRISE.value, Button.E_INTEREST.value)
emotions_groups.row(Button.B_TO_MAIN_MENU.value)

stat_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
stat_menu.row(Button.B_STAT_WEEK.value, Button.B_STAT_MONTH.value)
stat_menu.row(Button.B_TO_MAIN_MENU.value)

dont_want = types.ReplyKeyboardMarkup(resize_keyboard=True)
dont_want.row(Button.B_DONT_WANT.value)

M_NL = '\n\n'
M_WS = ' '
M_COLON = ':'

S_TIME = 3


async def move_to_state(message, state, markup, answer):
    await message.answer(answer, reply_markup=markup)
    dbworker.set_state(message.chat.id, state.value)


async def move_to_state_md(message, state, markup, answer):
    await message.answer(answer, reply_markup=markup, parse_mode='Markdown')
    dbworker.set_state(message.chat.id, state.value)


def get_hour(hours, delta, sign):
    return (24 + hours + delta * (1 if sign == '+' else -1)) % 24


def get_zero_d(number):
    return '0' + str(number) if number < 10 else str(number)


def reformat_date(date):
    return get_zero_d(date.day) + '.' + get_zero_d(date.month) + '.' + str(date.year)


def get_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def generate_pdf(title, subtitle, records, tz, filename, months):
    doc = pyl.Document(page_numbers=False, documentclass='article', document_options=['12pt'], lmodern=False)
    doc.packages.append(pyl.Package('babel', options=['english', 'russian']))
    doc.packages.append(pyl.Package('geometry', options=['left=1cm', 'right=1.5cm', 'top=0.3cm', 'bottom=1.2cm']))
    doc.packages.append(pyl.Package('tikz'))
    doc.packages.append(pyl.Package('enumitem'))

    doc.append(pyl.NoEscape(r'\definecolor{Color}{rgb}{0.45, 0.76, 0.98}'))
    doc.append(pyl.NoEscape(r'\setlist{nolistsep, itemsep=0.5cm,parsep=0.5pt}'))

    title = pyl.NoEscape(
        r'\normalsize {\large \textbf{' + pyl.utils.bold(title) + r'}}\\ \vspace{0.5\baselineskip}' + subtitle)
    doc.preamble.append(pyl.Command('title', title))
    doc.preamble.append(pyl.Command('date', pyl.NoEscape('')))
    doc.append(pyl.NoEscape(r'\maketitle'))

    doc.append(pyl.Command('vspace', pyl.NoEscape(r'-3\baselineskip')))
    doc.append(pyl.NoEscape(r'\renewcommand\labelitemi{}'))

    line_s = pyl.NoEscape(
        r'\begin{tikzpicture}[baseline]\shade[left color=Color!50!white, right color=white] rectangle (\textwidth,2pt);\node[inner sep=0pt,text ragged,anchor=south west,text depth=.5ex,text height=1.5ex] at (1pt,2pt) {\large ')
    line_e = pyl.NoEscape('};\end{tikzpicture}\n')
    with doc.create(pyl.Itemize()) as itemize:
        l_date = datetime.datetime(1000, 1, 1).date()
        for record in records:
            time = record['timestamp'] + datetime.timedelta(hours=tz)
            rnote = config.decode(record['note'])
            note = r'\\' + pyl.utils.escape_latex(rnote) if len(rnote) > 0 else ''
            date = ''
            if time.date() != l_date:
                date = line_s + r'{' + str(time.day) + ' ' + months[time.month - 1] + r'}' + line_e
                l_date = time.date()
            tex_item = pyl.NoEscape(date + get_zero_d(time.hour) + M_COLON + get_zero_d(time.minute) + r'$\ \cdot \ $' +
                                    pyl.utils.bold(em_config.match(record['emotion'])) + note)
            itemize.add_item(tex_item)
    doc.generate_pdf(filename, clean=True)
