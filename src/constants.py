from pathlib import Path

# DOWNLOADS_URL = 'https://docs.python.org/3/download.html'
# WHATS_NEW_URL = 'https://docs.python.org/3/whatsnew/'
MAIN_DOC_URL = 'https://docs.python.org/3/'
# константа, где будет храниться путь до директории с текущим файлом.
# Path(__file__) - абсолютный путь до текущего файла;
# parent - директория, где лежит файл
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
# добавим новую константу для адреса с PEP документацией
PEP_URL = 'https://peps.python.org/'

EXPECTED_STATUS = {
    'A': ['Active', 'Accepted'],
    'D': ['Deferred'],
    'F': ['Final'],
    'P': ['Provisional'],
    'R': ['Rejected'],
    'S': ['Superseded'],
    'W': ['Withdrawn'],
    '': ['Draft', 'Active'],
}
