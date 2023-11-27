# main.py
import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, MAIN_PEP_URL
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    """Сохраняет ссылки на статьи о наиболее важных
    изменениях между основными версиями Python.
    """
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    soup = BeautifulSoup(response.text, features='lxml')

    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})

    sections_by_python = div_with_ul.find_all('li',
                                              attrs={'class': 'toctree-l1'})

    result = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        session = requests_cache.CachedSession()
        response = get_response(session, version_link)
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        result.append((version_link, h1.text, dl_text))

    return result


def latest_versions(session):
    """Сохраняет ссылки на документацию основных версий Python."""
    response = get_response(session, MAIN_DOC_URL)
    soup = BeautifulSoup(response.text, features='lxml')

    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')

    result = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match:
            version = text_match.group('version')
            status = text_match.group('status')
        else:
            version = a_tag.text
            status = ''
        result.append((link, version, status))

    return result


def download(session):
    """Скачивает документацию для актуальной версии Python."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(table_tag, 'a',
                          {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    """Подсчитывает количество PEP в каждом статусе и общее количество PEP."""
    response = get_response(session, MAIN_PEP_URL)
    soup = BeautifulSoup(response.text, features='lxml')

    tables_by_category = find_tag(soup, 'section',
                                  attrs={'id': 'index-by-category'}
                                  ).find_all('tbody')
    rows_from_all_tables = []
    for table in tables_by_category:
        rows_from_all_tables.extend(table.find_all('tr'))

    result = [('Статус', 'Количество')]
    count_pep_per_status = {}
    mismatched_statuses = []
    for row in rows_from_all_tables:
        pep_a_tag = find_tag(row, 'a')
        href = pep_a_tag['href']
        pep_link = urljoin(MAIN_PEP_URL, href)
        session = requests_cache.CachedSession()
        response = get_response(session, pep_link)
        soup = BeautifulSoup(response.text, features='lxml')
        status_in_table = EXPECTED_STATUS.get(find_tag(row, 'td').text[1:2])
        dl_in_card = find_tag(soup, 'dl')
        status_in_card = find_tag(dl_in_card, 'abbr').text
        count_pep_per_status.setdefault(status_in_card, 0)
        count_pep_per_status[status_in_card] += 1

        if status_in_card not in status_in_table:
            mismatched_statuses.append((pep_link, status_in_card,
                                        status_in_table))
    if mismatched_statuses:
        logging.warning('Несовпадающие статусы:')
        for miss in mismatched_statuses:
            link, received, expected = miss
            logging.warning(link)
            logging.warning(f'Статус в карточке: {received}')
            logging.warning(f'Ожидаемые статусы: {expected}')

    result.extend([(k, v) for k, v in count_pep_per_status.items()])
    result.append(('Total', sum(count_pep_per_status.values())))

    return result


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
