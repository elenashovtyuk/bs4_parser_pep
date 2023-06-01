import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from exceptions import ParserFindListOfVersionsException
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    """
    Парсер, который собирает информацию о нововведениях в Python.
    """
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    """
    Парсер, который собирает информацию о версиях Python.
    """
    response = get_response(session, MAIN_DOC_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        error_msg = f'Не найден список с версиями Python {a_tags}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindListOfVersionsException(error_msg)

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        version, status = text_match.groups() if text_match else a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    """
    Парсер, который скачивает архив актуальной документации Python.
    """
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
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

    logging.info(f'Архив был загружен и сохранен: {archive_path}')


def pep(session):
    """
    Парсер, который собирает данные обо всех PEP документах,
    сравнивает статусы и записывает их в файл.
    """
    response = get_response(session, PEP_URL)
    soup = BeautifulSoup(response.text, features='lxml')
    section_tag = find_tag(soup, 'section', attrs={'id': 'numerical-index'})
    tbody_tag = find_tag(section_tag, 'tbody')
    tr_tags = tbody_tag.find_all('tr')

    total_peps = 0
    results = [('Статус', 'Количество')]

    for tr_tag in tr_tags:
        td_tag = find_tag(tr_tag, 'td')
        preview_status = td_tag.text[1:]

        a_tag = find_tag(tr_tag, 'a')
        href = a_tag['href']
        link_on_pep = urljoin(PEP_URL, href)
        response = get_response(session, link_on_pep)
        if response is None:
            return None
        soup = BeautifulSoup(response.text, features='lxml')
        dt_tags = soup.find_all('dt')

        for dt_tag in dt_tags:
            if dt_tag.text == 'Status:':
                total_peps += 1
                status = dt_tag.find_next_sibling().string
                status_sum = defaultdict(int=1)
                status_sum[status] += 1
                if status not in EXPECTED_STATUS[preview_status]:
                    error_message = (
                        'Несовпадающие статусы:\n'
                        f'{link_on_pep}\n'
                        'Статус в карточке: {status}\n'
                        'Ожидаемые статусы: {EXPECTED_STATUS[preview_status]}'
                    )
                    logging.warning(error_message)
    for status in status_sum:
        results.append((status, status_sum[status]))
    results.append(('Total', total_peps))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except Exception:
        logging.exception('Ошибка при выполнении парсинга.', stack_info=True)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
