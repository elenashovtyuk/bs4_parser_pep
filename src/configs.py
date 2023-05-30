import argparse
# импорт модуля для работы с логами
import logging
# импорт хэндлера с ротацией логов
from logging.handlers import RotatingFileHandler

# добавим новый импорт-импортируем константу BASE_DIR из файла constants.py
from constants import BASE_DIR

# описание формата логов
# Время записи - Уровень сообщения - Сообщение
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
# указываем формат времени
DT_FORMAT = '%d.%m.%Y %H:%M:%S'
# конфигурация аргументов командной строки


def configure_argument_parser(available_modes):
    # создаем парсер - экземпляр класса ArgumentParser
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    # далее добавляем аргументы - обязательные(mode - режим работы парсера)
    # и опциональные(--clear-cache, --output)

    # добавим обязательный аргумент - режим работы парсера
    parser.add_argument(
        # наименование обязательного позиционного аргумента
        'mode',
        # параметр choice указывает, что у данного аргумента
        # есть некоторое множество возможных значений для выбора
        # это множество возможных значений подается на вход функции
        choices=available_modes,
        # добавим хэндлер для аргумента - параметр help
        # теперь при запуске программы с аргументом -h или --help
        # будет выводиться вспомогательная справочная информация об аргументе
        help='Режимы работы парсера'
    )

    # добавим опциональный аргумент
    # отвечает за очистку кэша -
    # если этот аргумент есть среди считанных из командной строки,
    # то выполняется очистка кэша
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    # Новый аргумент --output вместо аргумента pretty
    parser.add_argument(
        '-o',
        '--output',
        choices=('pretty', 'file'),
        help='Дополнительные способы вывода данных'
    )
    return parser


# функция, которая отвечает за конфигурацию логов
# здесь находится код, который отвечает за логирование
# во всем проекте - т.е. логирование настраиваем глобально.
def configure_logging():
    # сформируем путь до директории logs
    log_dir = BASE_DIR / 'logs'
    # создадим директорию для хранения логов
    log_dir.mkdir(exist_ok=True)
    # получение абсолютного пути до файла с логами
    log_file = log_dir / 'parser.log'

    # инициализация хэндлера с ротацией логов
    # хэндлер - обработчик логов, переданных в логгер
    # максимальный объем одного файла - десять в шестой степени байт (10**6),
    # максимальное кол-во файлов с логами - 5
    rotating_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 ** 6,
        backupCount=5
    )

    # базовая настройка логирования basicConfig
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,

        # уровень записи логов
        level=logging.INFO,

        # вывод логов в терминал
        # rotating_file на основе RotatingFileHandler
        # следит за объемом и кол-вом лог-файлов
        # StreamHandler отправляет записи в стандартные потоки,
        # такие как sys.stdout или sys.stder
        # с помощью этого хэндлера логи будут выводиться в терминал
        handlers=(rotating_handler, logging.StreamHandler())
    )

# после того, как функция с конфигурацией логирования написана
# нужно подключить ее к основному файлу  main.py
