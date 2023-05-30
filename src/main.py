import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm
# импортируем функции, которые отвечают за конфигурации
# аргументов командной строки и логов
from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, MAIN_DOC_URL, PEP_URL, EXPECTED_STATUS
from outputs import control_output
# импортируем из файла utils.py функций, которые реализуют перехват
# ошибок и запись в логи. И заменяем часть кода, отвечающего за
# за загрузку страницы и поиск  нужных тегов
# на вызов этих двух функций
from utils import get_response, find_tag


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    # session = requests_cache.CachedSession()
    # response = session.get(whats_new_url)
    # response.encoding = 'utf-8'

    # заменим код загрузки и установки кодировки на вызов функции
    # get_response
    # (она реализует перехват ошибок при загрузке страницы и запись в логи)
    response = get_response(session, whats_new_url)
    # если основная страница не загрузится, то программа закончит работу
    if response is None:
        return None
    # создаем "суп", из которого потом будем "доставать"
    # информацию по нужным тегам
    soup = BeautifulSoup(response.text, features='lxml')

    # main_div = soup.find('section', attrs={'id': 'what-s-new-in-python'})
    # заменим вышестоящую строку main_div на следующее
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})

    # div_with_ul = main_div.find('div', attrs={'class': 'toctree-wrapper'})
    # заменим вышестоящую строку на следующее
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})

    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        # session = requests_cache.CachedSession()
        # response = session.get(version_link)
        # response.encoding = 'utf-8'

        # заменим код загрузки страницы и установки кодировки
        # на вызов функции get_response()
        response = get_response(session, version_link)
        # если страница не загрузится, то программа перейдет к следующей ссылке
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        # h1 = soup.find('h1')
        # dl = soup.find('dl')
        # также заменим в этих строках метод find на функцию
        # find_tag
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))

    # for row in results:
    #     print(*row)
    return results


def latest_versions(session):
    # session = requests_cache.CachedSession()
    # response = session.get(MAIN_DOC_URL)
    # response.encoding = 'utf-8'

    # опять заменим код загрузки страницы и установки кодировки
    # на вызов функции get_response
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    # используем функцию find_tag,
    # которая перехватывает ошибки при поиске нужных тегов
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results
    # for row in results:
    #     print(*row)


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    # session = requests_cache.CachedSession()
    # response = session.get(downloads_url)
    # response.encoding = 'utf-8'

    # опять заменим код загрузки страницы и установки кодировки
    # на вызов функции get_response()
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    # добавим логи для функции download()
    logging.info(f'Архив был загружен и сохранен: {archive_path}')


# добавим новую функцию
# для парсинга PEP-документации
def pep(session):
    # вызов функции get_response
    response = get_response(session, PEP_URL)

    if response is None:
        return None

    # создаем "суп"
    soup = BeautifulSoup(response.text, features='lxml')
    # сначала "достаем из супа" тег <section> c аттрибутом id = numerical-index
    section_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    # затем из этой секции "достаем" тег <tbody>
    tbody_tag = find_tag(section_tag, 'tbody')
    # внутри тега <tbody> находятся теги <tr>
    # каждый тег <tr> представляет собой контейнер для строк в таблице
    # сначала нам нужно достать все эти строки
    tr_tags = tbody_tag.find_all('tr')

    # в переменной status_sum сохраняем кол-во PEP в каждом статусе
    # в виде {Статус: Количество PEP в этом статусе}
    status_sum = {}
    # в переменной total_peps сохраняем общее кол-во документов PEP
    total_peps = 0

    results = [('Статус', 'Количество')]

    # далее для каждой строки
    for tr_tag in tr_tags:
        # нам нужно достать первый элемент <td>,
        # где находится аббревиатура, отвечающая за тип и статус документа PEP
        # <td> - это ячейки в каждой строке таблицы
        td_tag = find_tag(tr_tag, 'td')
        # теперь нам нужно достать именно статус из td
        # используем срез для того, чтобы из строки из 1 или 2 символов
        # достать символ, отвечающий за статус(от индекса 1 и до конца)
        # т.о. в переменной preview_status сохранен
        # статус документа из общей таблицы PEP
        preview_status = td_tag.text[1:]

        # далее нам нужно достать ссылку на конкретный PEP-документ
        # ссылка на него хранится в следующем теге <td>
        # поэтому можем использовать метод find
        # который найдет первый указанный элемент в коде
        # достаем тег <a> из тега
        a_tag = find_tag(tr_tag, 'a')
        # а уже из тега <a> достаем href - относительную ссылку на документ
        href = a_tag['href']
        # далее нужно работать со ссылкой на каждый конкретный документ
        # в таблице. Для этого нам нужна полная ссылка на документ
        # для этого используем функцию urljoin
        # из стандартной библиотеки urllib
        # в итоге объединяем адрес страницы с документами PEP и
        # относительную ссылку
        # на конкретный документ и получаем корректную ссылку
        link_on_pep = urljoin(PEP_URL, href)
        # теперь по этому адресу нужно сделать запрос
        response = get_response(session, link_on_pep)

        if response is None:
            return None

        # дальше уже инспектируем страницу с каждым конкретным документом PEP
        # "создаем суп" и "достаем" из него нужные элементы
        soup = BeautifulSoup(response.text, features='lxml')
        # нам нужно "достать из супа" статус для конкретно этого документа PEP
        # сначала достаем тег <section>
        # pep_tag_section =
        # find_tag(soup, 'section', {'id': 'pep-tag-section'})
        # далее из этого тега нужно достать все теги <dt>
        # этот тег по сути представляет собой ключ в паре "ключ-значение"
        dt_tags = soup.find_all('dt')

        # далее проходимся циклом по всем тегам dt
        for dt_tag in dt_tags:
            # как только в одном из тегом встречается Status
            if dt_tag.text == 'Status:':
                # сначала добавим в общее кол-во документов PEP +1
                total_peps += 1
                # берем следующий тег(тег <dd>, по сути это значение в паре
                # "ключ-значение"). В этом теге будет нужная информация
                #  о статусе документа
                status = dt_tag.find_next_sibling().string

                # если статус, который встретился уже есть в словаре,
                # то к кол-ву PEP с таким статусом прибавляем еще 1
                if status in status_sum:
                    status_sum[status] += 1

                # если же пока PEP с таким статусом не встречались
                # то присваиваем ключу с этим статусом
                # значение(кол-во PEP с таким статусом) 1
                if status not in status_sum:
                    status_sum[status] = 1

                if status not in EXPECTED_STATUS[preview_status]:
                    error_message = (
                        'Несовпадающие статусы:\n'
                        f'{link_on_pep}\n'
                        'Статус в карточке: {status}\n'
                        'Ожидаемые статусы: {EXPECTED_STATUS[preview_status]}'
                    )
                    logging.warning(error_message)
    # для каждого статуса в словаре status_sum
    for status in status_sum:
        # добавляем в cписок results статус и кол-во PEP-документов
        # с этим статусом
        results.append((status, status_sum[status]))
    # после добавления всех статусов в самом конце добавляем
    # общее кол-во всех PEP-документов
    results.append(('Total', total_peps))
    return results


# возможные режимы работы парсера - 4 функции, объединенные в одну программу
MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


# в функции main() мы поэтапно выполняем следующее:

# создаем парсер(используя для этого функцию
# из файла configs для настройки парсера)
# у парсера есть один обязательный и два опциональных аргумента

# далее выполняем парсинг строки в терминале -
# получаем аргументы командной строки

# Получаем из аргументов командной строки аргумент режима работы парсера

# в переменной result сохраняем результат вызова той или иной функции(
# в зависимости от указанного в командной строке режима парсера)

# если в итоге работы программы в определенном режиме
# были получены определенные результаты
#  то далее передаем эти результаты вместе
# с аргументами командной строки в функцию вывода

# также весь сопровождается логированием:
# о начале работы парсера, о получении аргументов командной строки,
#  о окончании работы парсера
def main():
    # добавим (запустим) функцию с конфигурацией логов
    configure_logging()
    # отмечаем в логах момент запуска программы
    logging.info('Парсер запущен')

    # Конфигурация парсера аргументов командной строки —
    # передача в функцию допустимых вариантов выбора.
    # для настройки парсера берется функция configure_argument_parser
    # импортированная из файла с настройками - configs.py
    # на вход этой функции подается множество возможных значений
    # ключей из словаря MODE_TO_FUNCTION
    # которые определяют режим работы парсера
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    # Считывание аргументов из командной строки.
    args = arg_parser.parse_args()

    # логируем (отмечаем в логах) аргументы командной строки
    logging.info(f'Аргументы командной строки: {args}')

    # Создание кеширующей сессии.
    session = requests_cache.CachedSession()
    # Если был передан ключ '--clear-cache', то args.clear_cache == True.
    if args.clear_cache:
        # Очистка кеша.
        session.cache.clear()
    # Получение из аргументов командной строки нужного режима работы.
    parser_mode = args.mode
    # Поиск и вызов нужной функции по ключу словаря.
    results = MODE_TO_FUNCTION[parser_mode](session)

    # Если из функции вернулись какие-то результаты,
    if results is not None:
        # передаём их в функцию вывода вместе с аргументами командной строки.
        control_output(results, args)

    # логируем завершение работы парсера
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
