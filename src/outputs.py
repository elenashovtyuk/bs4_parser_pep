import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT


# Функция контроля вывода результатов парсинга
# определяет - в каком виде данные будут выведены

# eсли вместе с опциональным аргументом -o или --output
# будет указано pretty
# например python main.py whats-new -o pretty
# то данные будут выведены в терминал в виде таблицы

# если вместе с аргументом будет указан file
# то результаты будут выведены в файл

# если же аргумент --output не будет указан, то
# данные по умолчаанию будут выведены в терминал построчно

def control_output(results, cli_args):
    output = cli_args.output
    if output == 'pretty':
        # вывод данных в PrettyTable c помощью функции pretty_output
        pretty_output(results)
    elif output == 'file':
        # вывод данных в csv с помощью функции file_output
        file_output(results, cli_args)
    else:
        # вывод данных по умолчанию - в терминал построчно()
        # с помощью функции default_output(по умолчанию)
        default_output(results)


# вывод данных по умолчанию - построчно
def default_output(results):
    # Печатаем список results построчно.
    for row in results:
        print(*row)


# вывод данных парсинга в виде таблицы
def pretty_output(results):
    # Инициализируем объект PrettyTable.
    table = PrettyTable()
    # В качестве заголовков устанавливаем первый элемент списка.
    table.field_names = results[0]
    # Выравниваем всю таблицу по левому краю.
    table.align = 'l'
    # Добавляем все строки, начиная со второй (с индексом 1).
    table.add_rows(results[1:])
    # Печатаем таблицу.
    print(table)


# создание директории с результатами парсинга
def file_output(results, cli_args):
    # сформируем новый путь до директории results
    results_dir = BASE_DIR / 'results'
    # создадим директорию results_dir
    results_dir.mkdir(exist_ok=True)
    # получаем режим работы парсера из аргументов  командной строки
    parser_mode = cli_args.mode
    # получаем текущую дату и время
    now = dt.datetime.now()
    # сохраняем текущую дату и время в указанном формате
    # результат будет выглядеть так 2021-06-18_07-40-41
    now_formatted = now.strftime(DATETIME_FORMAT)
    # собираем имя файла из полученных переменных:
    # "режим работы программы" + "дата и время записи" + "формат"
    file_name = f'{parser_mode}_{now_formatted}.csv'
    # получаем абсолютный путь к файлу с результатами
    file_path = results_dir / file_name
    # Через контекстный менеджер открываем файл по сформированному ранее пути
    # в режиме записи 'w', в нужной кодировке utf-8.
    with open(file_path, 'w', encoding='utf-8') as f:
        # Создаём «объект записи» writer.
        writer = csv.writer(f, dialect='unix')
        # Передаём в метод writerows список с результатами парсинга.
        writer.writerows(results)

    # добавим логи в функцию file_output
    logging.info(f'Файл с результатами был сохранен: {file_path}')
