# импортируем встроенную библиотеку для логирования
import logging

# импортируем базовый класс ошибок библиотеки request
from requests import RequestException
# импортируем из файла exceptions наше кастомное исключение
from exceptions import ParserFindTagException


# в файле utils реализуем перехват ошибок
# наиболее часто встречающиеся ошибки при парсинге -
# ошибки при загрузке страницы
# ошибки при поиске нужного тега
# информация об ошибках  будет записываться в логи

# функция для перехвата ошибки при запросе к странице
# RequestException
# создаем функцию get_response
def get_response(session, url):
    """
    Функция, отвечающая за перехват ошибок при загрузке страницы.
    """
    # в блоке try мы пытаемся выполнить некоторые действия,
    # выполнение этих действий могут вызвать ошибки
    # из-за какого-нибудь исключения
    # с помощью метода get() делаем запрос к некоторому url
    # в объекте response будет храниться вся информация
    # ответа сервера на запрос
    # настраиваем кодировку и по итоам работы вернем response
    try:

        response = session.get(url)
        response.encoding = 'utf-8'
        return response

    # в блоке except мы пытаемся
    # перехватить эти ошибки как исключения
    # поэтому в блоке except указываем RequestException
    # параметр stack_info отвечает за вывод стека вызова функций
    # cтек вызова функций выглядит как полный трейсбек с сообщением об ошибке
    # но указывает не на саму ошибку, а на операцию логирования
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


# создаем новую функцию для перехвата ошибки поиска тега
# для этого у нас есть кастомное исключение
# на вход эта функция принимает три параметра
# soup - это может быть как страница целиком, так и отдельный тег
# tag - это название искомого тега
# attrs - опциональный параметр, словарь с аттрибутами для поиска
def find_tag(soup, tag, attrs=None):
    """
    Функция, отвечающая за перехват ошибок при поиске нужного тега.
    """
    # функция будет искать теги с аттрибутами, которые переданы при ее вызове
    # либо вообще с любыми аттрибутами(на что указывает пустой словарь)
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    # если тег не найдется, то программа завершит работу,
    # а в логи и терминал выведется сообщение об ошибке
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    # если тег будет найден, то он вернется по итогам выполнения программы
    return searched_tag

# после того, как функции, отвечающие за перехват ошибок при парсинге написаны
# их нужно импортировать в файл main.py
