import random
import string
import datetime
import pickle
import vk_api
from vk_api import VkUpload
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
import requests
import re
import xlrd
import PIL.Image as Image
import os
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from copy import deepcopy as copy

page = requests.get("https://www.mirea.ru/schedule/")
soup = BeautifulSoup(page.text, "html.parser")
result = re.findall(r"htt.+x", str(soup.find('div', {'class': 'rasspisanie'}). \
                                   find(string='Институт информационных технологий'). \
                                   find_parent('div').find_parent('div').findAll("a")))
accept = 0
url1 = []
ogr = 0
weather_access = 0
groups_list = []
groups = {}
professors = {}
count_pages = 0
prof_access = 0
x = []
y1 = []
y2 = []
y3 = []
week_days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]


def update():
    """
        Обновление данных расписания
        Функция не имеет параметров
    """
    count = 1
    for x in result:
        if 1:
            with open('file' + str(count) + '.xlsx', 'wb') as file1:
                resp = requests.get(x)
                file1.write(resp.content)
                count += 1
    file1.close()


def replace_none(data):  # замена None на ''
    """
        Замена символов для считывания файлов
        :param data - словарь с данными
    """
    for k, v in data.items() if isinstance(data, dict) else enumerate(data):
        if v is None:
            data[k] = {'subject': '', 'lesson_type': '', 'lecturer': '', 'classroom': '', 'url': ''}
        elif isinstance(v, (dict, list)):
            replace_none(v)


if datetime.datetime.now().weekday() == 0:  # Если понедельник, то данные обновляются
    update()
for i in range(3):      # Заполнение списков
    book = xlrd.open_workbook("file{}.xlsx".format(i + 1))
    sheet = book.sheet_by_index(0)
    num_cols = sheet.ncols
    num_rows = sheet.nrows
    for col_index in range(num_cols):
        group_cell = str(sheet.cell(1, col_index).value)
        if "БО" in group_cell or "-18" in group_cell or "-17" in group_cell or "-19" in group_cell:
            groups_list.append(group_cell)
            week = {"понедельник": None, "вторник": None, "среда": None, "четверг": None, "пятница": None,
                    "суббота": None}
            for k in range(6):
                day = [[], [], [], [], [], []]
                for i in range(6):
                    for j in range(2):
                        subject = sheet.cell(3 + j + i * 2 + k * 12, col_index).value   # заполнение groups
                        lesson_type = sheet.cell(3 + j + i * 2 + k * 12, col_index + 1).value
                        lecturer = sheet.cell(3 + j + i * 2 + k * 12, col_index + 2).value
                        classroom = sheet.cell(3 + j + i * 2 + k * 12, col_index + 3).value
                        url = sheet.cell(3 + j + i * 2 + k * 12, col_index + 4).value
                        lesson = {"subject": subject, "lesson_type": lesson_type, "lecturer": lecturer, # заполнение professors
                                  "classroom": classroom, "url": url}
                        day[i].append(lesson)
                        professors_list = lecturer.split('\n')
                        subject_list = subject.split('\n')
                        pr_lesson = copy(lesson)
                        pr_lesson.pop('lecturer')
                        pr_lesson['group'] = group_cell

                        for h in range(len(professors_list)):
                            if len(subject_list) > h:
                                pr_lesson['subject'] = subject_list[h]
                            if professors_list[h] not in professors:
                                day1 = [[None] * 2, [None] * 2, [None] * 2, [None] * 2, [None] * 2, [None] * 2]
                                week1 = {'понедельник': copy(day1), 'вторник': copy(day1), 'среда': copy(day1),
                                         'четверг': copy(day1),
                                         'пятница': copy(day1), 'суббота': copy(day1)}
                                professors.update({professors_list[h]: week1})
                            professors[professors_list[h]][week_days[k]][i][j] = lesson
                week[week_days[k]] = day
            groups.update({group_cell: week})

    """
        ВАЖНО!
        Запуск сессии, передача токена. Для работоспособности бота необходимо вписать токен в поле снизу. Получить токен можно, \
        сгенерировав его в сообществе Вконтакте и вписав в поле ниже.
        Подробнее по ссылке:
        https://vk.com/dev/bots_docs
    """

print('ready')
replace_none(professors)
vk_session = vk_api.VkApi(token='dba28ffac316eabeb7bc1e13ea9d65a3ab4a150621bb0eb9275421240c68b45c57cccafc2a406986a8a95')  # токен сюда
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)


def error():
    """
        Показывает сообщение с ошибкой. Говорит про отсутствие заданной команды
    """
    vk.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        message='Я не знаю такой команды. Попробуйте что-нибудь другое'.format(event.text)
    )


def coronavirus():
    """
        Считывает данные с сайта со статистикой по коронавирусу и выводит его в качестве графика в ответном сообщении.
    """
    page = requests.get('https://coronavirusstat.ru/country/russia/')
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.findAll('table')[0]
    data = {}
    count_days = table.find('tbody').findAll('tr')
    for row in count_days:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        active = re.findall(r'\d*\.\d+|\d+', cols[0])
        cured = re.findall(r'\d*\.\d+|\d+', cols[1])
        dead = re.findall(r'\d*\.\d+|\d+', cols[2])
        cases = re.findall(r'\d*\.\d+|\d+', cols[3])
        print(active)
        print(cured)
        print(dead)
        print(cases)
        print('\n\n')
        date = str(row.find('th').contents[0])
        stat = {'1': int(active[0]), '2': int(active[1]), '3': int(cured[0]), '4': int(cured[1]),
                '5': int(dead[0]), '6': int(dead[1]), '7': int(cases[0]), '8': int(cases[1])}
        data.update({date: stat})
    print(data)
    dates = list(data.keys())
    for date in dates:
        x.insert(0, data[date])
        y1.insert(0, data[date]['1'])
        y2.insert(0, data[date]['3'])
        y3.insert(0, data[date]['5'])
    fig, ax = plt.subplots()
    ax.stackplot(dates, y1, y2, y3, labels=['Активных', 'Вылечено', 'Умерло'])
    ax.legend(loc='upper left')
    plt.title('Россия- статистика.  Коронавирус')
    fig.autofmt_xdate()
    page = requests.get('https://coronavirusstat.ru/country/russia/')
    soup = BeautifulSoup(page.text, 'html.parser')
    this_day = soup.find('h6').find('strong').contents[0]
    if not os.path.exists('coronavirus/'):
        os.makedirs('coronavirus/')
    fig.savefig('coronavirus/covid.png')
    upload = VkUpload(vk_session)
    attachments = []
    """
        ВАЖНО!
        Для отображения картинки коронавируса в боте необходимо указать собственный текущий адрес её хранения.
        Данный адрес предоставлен как пример для его указания.
        Выпилить в случае несовместимости с жизнью.
    """
    photo = upload.photo_messages(photos='C:/Users/leone/PycharmProjects/testproject1/coronavirus/covid.png')[0]
    attachments.append('photo{}_{}'.format(photo['owner_id'], photo['id']))
    vk.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        attachment=','.join(attachments),
        message='По состоянию на {}\nСлучаев: {} (+{} за сегодня)\nАктивных: {} (+{} за сегодня)\nВылечено: {} ' \
                '(+{} за сегодня)\nУмерло: {} (+{} за сегодня)'.format(
            this_day, data[dates[0]]["7"], data[dates[9]]["8"], data[dates[0]]["1"], data[dates[0]]["2"],
            data[dates[0]]["3"], data[dates[0]]["4"], data[dates[0]]["5"], data[dates[0]]["6"],
        ))


def found():
    """
        Данная функция находит расписание определённого преподавателя из университета, при необходимости предлагая выбрать
        его из нескольких возможных вариантов. Функция позволяет показать расписание преподавателя на сегодня, на завтра,
        на эту или следующую неделю
    """
    professor = event.text.split()[1]
    professors_list = [key for key, value in professors.items() if key.startswith(professor)]
    print(professors_list)
    if len(professors_list) > 1:
        keyboard = VkKeyboard(one_time=True)
        for p in professors_list:
            keyboard.add_button(p, color=VkKeyboardColor.PRIMARY)
        vk.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message='Выберите преподавателя'
        )
        prof_access = 1
    elif len(professors_list) == 1:
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('На сегодня', color=VkKeyboardColor.POSITIVE)
        keyboard.add_button('На завтра', color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button('На эту неделю', color=VkKeyboardColor.PRIMARY)
        keyboard.add_button('На следующую неделю', color=VkKeyboardColor.PRIMARY)
        professor = professors_list[0]
        vk.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
            message='Показать расписание преподавателя {}...'.format(professors_list[0])
        )
        prof_access = 1
        accept = 1
    else:
        vk.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            message='Такого преподавателя не нашлось'
        )


def start():
    """
        Начальное сообщение с отображением и описанием всех функций бота в едином сообщении
    """
    vk.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        message='Здравствуйте! Вы можете вписать номер своей группы(формат "ИКБО-06-19"), чтобы я запомнила '
                'вашу группу. Также вы можете воспользоваться одной из команд ниже:\n'
                '-Фамилия преподавателя(формат "Найти Иванов"), чтобы узнать его расписание.\n'
                '-Слово "Погода", чтобы узнать прогноз\n'
                '-Слово "Коронавирус", чтобы узнать статистику коронавируса на ближайшие 10 дней\n'
                '-Слово "Бот", показать расписание\n -Слово "Бот" + день недели(формат "Бот понедельник", '
                'чтобы показать расписание на этот день(сначала введите вашу группу)\n'
                '-Словa "Бот" + группа(формат "Бот ИНБО-01-19", чтобы показать расписание этой группы\n'
                '-Слова "Бот" + день недели + группа(формат "Бот вторник ИКБО-10-18", чтобы показать расписание'
                ' этой группы на этот день\n'
                'Успехов)'
    )


def testweather(count_pages):
    """
        Позволяет показать текущую погоду сейчас, либо погоду на ближайшие 5 дней при выборе соответствующего варианта.
        :param dice - счётчик страниц для формирования погоды на несколько дней
    """
    if re.match("^СЕЙЧАС", event.text, re.IGNORECASE):
        path_val = requests.get('http://api.openweathermap.org/data/2.5/weather?q=moscow&appid'
                                '=8ffb0255da9e43f05a700252453058bf&units=metric')
        info = path_val.json()
    if re.match("^СЕГОДНЯ|^ЗАВТРА|^НА 5 ДНЕЙ", event.text, re.IGNORECASE):
        path_val = requests.get('http://api.openweathermap.org/data/2.5/forecast?q=moscow&appid'
                                '=8ffb0255da9e43f05a700252453058bf&units=metric')
        info1 = path_val.json()
        if re.match("^СЕГОДНЯ", event.text, re.IGNORECASE):
            time_right_now = str('20\d\d-20-\d\d \d\d:\d\d:\d\d')
        elif re.match("^ЗАВТРА", event.text, re.IGNORECASE):
            time_right_now = str('20\d\d-20-\d\d \d\d:\d\d:\d\d')
        elif re.match("^НА 5 ДНЕЙ", event.text, re.IGNORECASE):
            time_right_now = str('20\d\d-\d\d-\d\d 12:\d\d:\d\d')

        else:
            pass
    upload = VkUpload(vk_session)
    attachments = []
    pattern = "https://openweathermap.org/img/wn/{}@2x.png"
    if re.match("^СЕЙЧАС", event.text, re.IGNORECASE):
        url = pattern.format(str(info["weather"][0]["icon"]))
        image = requests.get(url, stream=True)
        if re.match("^2\d\d", str(info["weather"][0]["id"])):
            weather_type = t_weather['1']
        elif re.match("^3\d\d", str(info["weather"][0]["id"])):
            weather_type = t_weather['2']
        elif re.match("^5\d\d", str(info["weather"][0]["id"])):
            weather_type = t_weather['3']
        elif re.match("^6\d\d", str(info["weather"][0]["id"])):
            weather_type = t_weather['4']
        elif re.match("^7\d\d", str(info["weather"][0]["id"])):
            weather_type = t_weather['5']
        elif re.match("^800", str(info["weather"][0]["id"])):
            weather_type = t_weather['6']
        else:
            weather_type = t_weather['7']
        if re.findall("^[0-1]$", str(info["wind"]["speed"])):
            wind_speed = t_speed['1']
        elif re.findall("^[2-6]$", str(info["wind"]["speed"])):
            wind_speed = t_speed['2']
        elif re.findall("^[7-9]$|1[0-4]$", str(info["wind"]["speed"])):
            wind_speed = t_speed['3']
        elif re.findall("1[5-9]$", str(info["wind"]["speed"])):
            wind_speed = t_speed['4']
        elif re.findall("2[0-5]$", str(info["wind"]["speed"])):
            wind_speed = t_speed['5']
        elif re.findall("2[6-9]$|3[0-2]$", str(info["wind"]["speed"])):
            wind_speed = t_speed['6']
        else:
            wind_speed = t_speed['7']
        photo = upload.photo_messages(photos=image.raw)[0]
        attachments.append('photo{}_{}'.format(photo['owner_id'], photo['id']))
        vk.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            attachment=','.join(attachments),
            message='Сейчас погода в Москве просто блеск: \n' + weather_type +
                    '\nТемпература сейчас ' + str(info["main"]["temp_min"]) + ' - ' + str(
                info["main"]["temp_max"]) + ' С'
                                            '\nВлажность: ' + str(
                info["main"]["humidity"]) + '\nДавление сейчас: ' + str(int(float(info["main"]["pressure"]) *
                                                                            0.750063755419211)) + ' мм.рт.ст. \n ' +
                    'Ветер: ' + \
                    str(t_wind[round(float(info["wind"]["deg"]) / 45) % 8]) +
                    ', силой: ' + str(
                info["wind"]["speed"]) + ', то есть ' + wind_speed + '\n'
        )
        weather_access = 0
    else:
        message_wind = ''
        for i in range(39):
            if re.search(time_right_now, info1['list'][i]['dt_txt']):
                if re.match("^2\d\d", str(info1['list'][i]["weather"][0]["id"])):
                    weather_type = t_weather['1']
                elif re.match("^3\d\d", str(info1['list'][i]["weather"][0]["id"])):
                    weather_type = t_weather['2']
                elif re.match("^5\d\d", str(info1['list'][i]["weather"][0]["id"])):
                    weather_type = t_weather['3']
                elif re.match("^6\d\d", str(info1['list'][i]["weather"][0]["id"])):
                    weather_type = t_weather['4']
                elif re.match("^7\d\d", str(info1['list'][i]["weather"][0]["id"])):
                    weather_type = t_weather['5']
                elif re.match("^800", str(info1['list'][i]["weather"][0]["id"])):
                    weather_type = t_weather['6']
                else:
                    weather_type = t_weather['7']
                if re.match("^[0-1].\w+$", str(info1['list'][i]["wind"]["speed"])):
                    wind_speed = t_speed['1']
                elif re.match("^[2-6].\w+$", str(info1['list'][i]["wind"]["speed"])):
                    wind_speed = t_speed['2']
                elif re.match("^[7-9].\w+$|^1[0-4].\w+$", str(info1['list'][i]["wind"]["speed"])):
                    wind_speed = t_speed['3']
                elif re.match("^1[5-9].\w+$", str(info1['list'][i]["wind"]["speed"])):
                    wind_speed = t_speed['4']
                elif re.match("^2[0-5].\w+$", str(info1['list'][i]["wind"]["speed"])):
                    wind_speed = t_speed['5']
                elif re.match("^2[6-9].\w+$|^3[0-2].\w+$", str(info1['list'][i]["wind"]["speed"])):
                    wind_speed = t_speed['6']
                else:
                    wind_speed = t_speed['7']
                """
                ВАЖНО!
                Для отображения картинок погоды в боте необходимо указать собственный текущий адрес их хранения.
                Данный адрес предоставлен как пример для его указания.
                Выпилить в случае несовместимости с жизнью.
                """
                url1.append('C:/Users/leone/PycharmProjects/testproject1/weather/icons/' + '{}.png'.format(str(
                    info1['list'][i]["weather"][0]["icon"])))
                count_pages += 1
                message_wind += str(count_pages) + ') Погода на ' + str(
                    info1['list'][i]['dt_txt']) + ' : \n' + weather_type + \
                                '\nТемпература: ' + str(info1['list'][i]["main"]["temp_min"]) + '- ' + str(
                    info1['list'][i]["main"]["temp_max"]) \
                                + ' С\nВлажность: ' + str(
                    info1['list'][i]["main"]["humidity"]) + '\nДавление: ' + \
                                str(int(float(info1['list'][i]["main"][
                                                  "pressure"]) * 0.750063755419211)) + ' мм.рт.ст. \n ' + 'Ветер: ' + \
                                str(t_wind[
                                        round(float(info1['list'][i]["wind"]["deg"]) / 45) % 8]) + ', силой: ' + \
                                str(info1['list'][i]["wind"]["speed"]) + ', то есть ' + wind_speed + '\n'
        weather_access = 0
        new_image = Image.new("RGBA", (count_pages * 50, 50))
        c = 0
        for i in url1:
            img2 = Image.open(i)
            new_image.paste(img2, (c, 0))
            c += 50
        image_name = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        path_image = "C:/Users/leone/PycharmProjects/testproject1/weather/brush/{}.png".format(image_name)
        new_image.save(path_image)
        photo = upload.photo_messages(photos=path_image)[0]
        attachments.append('photo{}_{}'.format(photo['owner_id'], photo['id']))
        vk.messages.send(
            user_id=event.user_id,
            attachment=','.join(attachments),
            random_id=get_random_id(),
            message=message_wind
        )
        count_pages = 0
        url1.clear()


def week():
    """
        Показать текущую неделю и определить её чётность.
    """
    if datetime.datetime.now().isocalendar()[1] % 2 == 0:
        chet = "чётная"
    else:
        chet = "нечётная"
    vk.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        message="Cейчас идёт " + str(datetime.datetime.now().isocalendar()[1] - 6) + " неделя\n" + "Она " + chet
    )


def weather():
    """
        Определить желаемый пользователем тип погоды, а также ввести основные варианты понятий и обозначений для более наглядного
        описания погодных условий.
    """
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('сейчас', color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button('на 5 дней', color=VkKeyboardColor.POSITIVE)
    weather_access = 1
    t_weather = {'1': "Гроза", '2': "Изморось", '3': "Дождь", '4': "Снег", '5': "Туман", '6': "Чистое небо",
                 '7': "Облачно", }
    t_wind = ['северный', 'северо-восточный', 'восточный', 'юго-восточный', 'южный', 'юго-западный', 'западный',
              'северо-западный']
    t_speed = {'1': "штиль", '2': "слабый", '3': "сильный", '4': "очень сильный", '5': "шторм",
               '6': "сильный шторм",
               '7': "ураган"}
    vk.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message='Показываю погоду в Москве...'
    )
    return t_weather, t_wind, t_speed


def found_prof():
    """
        Показать меню для выбора желатемого формата расписания преподавателя.
    """
    professor = str(event.text)
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('На сегодня', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('На завтра', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('На эту неделю', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('На следующую неделю', color=VkKeyboardColor.PRIMARY)
    vk.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
        message='Показать расписание преподавателя {}...'.format(professor)
    )
    return professor


def schtudile(accept):
    """
        Показать расписание группы при условии наличия заданной группы. Показать меню функций для выбора формата расписания занятий
        :param accept - проверка на наличие ранее заданной группы
    """
    if accept == 0:
        vk.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            message='Пожалуйста, сперва задайте свою группу(формат "ИНБО-10-19"), чтобы '
                    'продолжить'.format(event.text)
        )
    else:
        u_day = week_days[datetime.datetime.now().weekday()]
        u_week = datetime.datetime.now().isocalendar()[1] % 2
        if re.match("^НА СЛЕДУЮЩУЮ НЕДЕЛЮ", event.text, re.IGNORECASE):
            u_week += 1
        if re.match("^КАКАЯ ГРУППА?", event.text, re.IGNORECASE):
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message="Показываю расписание группы"
            )
        outer = ""
        if prof_access == 0:
            u_gr = pickle.loads(gr)[0].upper()
            for j in range(6):
                outer = outer + "\n Показываю расписание на " + week_days[j] + ": \n"
                for i in range(6):
                    outer = outer + str((i + 1)) + ") " + str(
                        groups[u_gr][week_days[j]][i][u_week - 1].get("subject")) + ", " + str(
                        groups[u_gr][week_days[j]][i][u_week - 1].get("lecturer")) + ", " + str(
                        groups[u_gr][week_days[j]][i][u_week - 1].get("url")) + "\n"
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message=outer
            )
        else:
            for j in range(6):
                outer = outer + "\n Показываю расписание на " + week_days[j] + ": \n"
                for i in range(6):
                    outer = outer + str((i + 1)) + ") " + str(
                        professors[str(professor)][str(week_days[j])][i][u_week - 1].get(
                            "subject")) + ", " + str(
                        professors[professor][week_days[j]][i][u_week - 1].get("lesson_type")) + ", " + str(
                        professors[professor][week_days[j]][i][u_week - 1].get("url")) + "\n"
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message=outer
            )


def schtudile_now(accept, prof_access):
    """
        Показать текущее расписание группы (на сегодня или завтра) при условии наличия заданной группы.
        :param accept - проверка на наличие ранее заданной группы
        :param prof_access - проверка на отсутствие поиска преподавателя
    """
    global ogr
    if accept == 0:
        vk.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            message='Пожалуйста, сперва задайте свою группу(формат "ИНБО-10-19"), чтобы '
                    'продолжить'.format(event.text)
        )
    else:
        u_day = week_days[datetime.datetime.now().weekday()]
        u_week = datetime.datetime.now().isocalendar()[1] % 2
        if re.match("^НА ЗАВТРА", event.text, re.IGNORECASE):
            try:
                u_day = week_days[datetime.datetime.now().weekday() + 1]
            except:
                pass
        outer = ""
        if prof_access == 0:
            for i in range(6):
                if ogr == 0:
                    u_gr = pickle.loads(gr)[0].upper()
                else:
                    u_gr = pickle.loads(gr1)[0].upper()
                    ogr = 0
                outer = outer + str((i + 1)) + ") " + str(
                    groups[u_gr][u_day][i][u_week].get("subject")) + ", " + str(
                    groups[u_gr][u_day][i][u_week].get("lecturer")) + ", " + str(
                    groups[u_gr][u_day][i][u_week].get("url")) + "\n"
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message=outer
            )
        else:
            for i in range(6):
                outer = outer + str((i + 1)) + ") " + str(
                    professors[str(professor)][str(u_day)][i][u_week - 1].get("subject")) + ", " + str(
                    professors[professor][u_day][i][u_week - 1].get("lesson_type")) + ", " + str(
                    professors[professor][u_day][i][u_week - 1].get("url")) + "\n"
            vk.messages.send(
                user_id=event.user_id,
                random_id=get_random_id(),
                message=outer
            )
            prof_access = 0
            accept -= 1


def my_group(accept):
    """
        Определение текущей группы учащегося
        :param accept - проверка на наличие ранее заданной группы

    """
    if accept != 0:
        your_gr = []
    your_gr = [event.text]
    gr = pickle.dumps(your_gr)
    vk.messages.send(
        user_id=event.user_id,
        random_id=get_random_id(),
        message='Теперь буду помнить, что вы из группы {}. '
                'Когда-нибудь обязательно встретимся!'.format(event.text)
    )
    accept += 1  # переделать доступ
    return gr, accept


def name_group(accept):
    """
        Определение конкретной группы для разового поиска её расписания
        :param accept - проверка на наличие ранее заданной группы

    """
    global ogr
    if accept != 0:
        your_gr = []
    ch_group = re.findall('[А-Я]{2}БО-[0-9]{2}-[0-9]{2}', event.text, re.IGNORECASE)[0]
    ch_gr = [ch_group]
    gr1 = pickle.dumps(ch_gr)
    accept += 1
    ogr += 1
    vk.messages.send(
        keyboard=keyboard.get_keyboard(),
        user_id=event.user_id,
        random_id=get_random_id(),
        message='Вы хотите узнать расписание группы ' + str(ch_group) + " : \n"
    )
    return gr1


def stud_mes():
    """
        Отображение сообщения расписания конкретной группы

    """
    vk.messages.send(
        keyboard=keyboard.get_keyboard(),
        user_id=event.user_id,
        random_id=get_random_id(),
        message='Вы хотите узнать расписание …'
    )


def bot_func():
    """
        Выполнение технических функций бота

    """
    if accept == 1:
        u_gr = pickle.loads(gr)[0].upper()
    if re.search("[А-Я]{2}БО-[0-9]{2}-[0-9]{2}", event.text, re.IGNORECASE):
        u_gr = re.findall("[А-Я]{2}БО-[0-9]{2}-[0-9]{2}$", event.text, re.IGNORECASE)[0].upper()
        mas = 1
    if accept == 0:
        vk.messages.send(
            user_id=event.user_id,
            random_id=get_random_id(),
            message='Пожалуйста, сперва задайте свою группу(формат "ИНБО-10-19"), чтобы '
                    'продолжить'.format(event.text)
        )
    else:
        for i in range(6):
            if re.findall("\w+", event.text, re.IGNORECASE)[1] == week_days[i]:
                outer = ""
                u_day = week_days[i]
                u_week = datetime.datetime.now().isocalendar()[1] % 2
                for i in range(6):
                    outer = outer + str((i + 1)) + ") " + str(
                        groups[u_gr][u_day][i][u_week].get("subject")) + ", " + str(
                        groups[u_gr][u_day][i][u_week].get("lecturer")) + ", " + str(
                        groups[u_gr][u_day][i][u_week].get("url")) + "\n"
                vk.messages.send(
                    keyboard=keyboard.get_keyboard(),
                    user_id=event.user_id,
                    random_id=get_random_id(),
                    message=outer
                )
                mas = 0
                break

for event in longpoll.listen():  # команды
    """
        Циклический слушатель команд для корректной работы бота
    """
    if event.type == VkEventType.MESSAGE_NEW and event.text and event.to_me:
        if re.match("НАЧАТЬ", event.text, re.IGNORECASE):
            start()
        elif re.match("^БОТ$|^БОТ [А-Я]{2}БО-[0-9]{2}-[0-9]{2}", event.text, re.IGNORECASE):
            keyboard = VkKeyboard(one_time=True)
            keyboard.add_button('на сегодня', color=VkKeyboardColor.POSITIVE)
            keyboard.add_button('на завтра', color=VkKeyboardColor.NEGATIVE)
            keyboard.add_line()
            keyboard.add_button('на эту неделю', color=VkKeyboardColor.PRIMARY)
            keyboard.add_button('на следующую неделю', color=VkKeyboardColor.PRIMARY)
            keyboard.add_line()
            keyboard.add_button('какая неделя?', color=VkKeyboardColor.DEFAULT)
            keyboard.add_button('какая группа?', color=VkKeyboardColor.DEFAULT)

            if re.search("[А-Я]{2}БО-[0-9]{2}-[0-9]{2}", event.text, re.IGNORECASE):
                gr1 = name_group(accept)
            else:
                stud_mes()
        elif re.match("^БОТ \w+$|^БОТ \w+ [А-Я]{2}БО-[0-9]{2}-[0-9]{2}", event.text, re.IGNORECASE):
            bot_func()
        elif re.match("[А-Я]{2}БО-[0-9]{2}-[0-9]{2}", event.text, re.IGNORECASE):
            gr, accept = my_group(accept)
        elif re.match("^НА СЕГОДНЯ|^НА ЗАВТРА", event.text, re.IGNORECASE):
                schtudile_now(accept, prof_access)
        elif re.match("^НА ЭТУ НЕДЕЛЮ|^НА СЛЕДУЮЩУЮ НЕДЕЛЮ|^КАКАЯ ГРУППА?", event.text, re.IGNORECASE):
                schtudile(accept)
                prof_access = 0
                accept -= 1
        elif re.match("^КАКАЯ НЕДЕЛЯ?", event.text, re.IGNORECASE):
            week()
        elif re.match("^НАЙТИ \w+$", event.text, re.IGNORECASE):
            found()
        elif re.match("^\w+ \w.\w.", event.text, re.IGNORECASE) and prof_access == 1:
            professor = found_prof()
            prof_access = 1
            accept += 1
        elif re.match("^ПОГОДА", event.text, re.IGNORECASE):
            t_weather, t_wind, t_speed = weather()
            weather_access = 1
        elif re.match("^СЕЙЧАС|^СЕГОДНЯ|^ЗАВТРА|^НА 5 ДНЕЙ", event.text, re.IGNORECASE) and weather_access == 1:
            testweather(count_pages)
            weather_access = 0
        elif re.match("^КОРОНАВИРУС", event.text, re.IGNORECASE):
            coronavirus()
        else:
            error()
