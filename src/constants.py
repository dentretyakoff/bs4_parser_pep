# constants.py
from pathlib import Path


MAIN_DOC_URL = 'https://docs.python.org/3/'
MAIN_PEP_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'  # Формат даты в имени csv файлов.
LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'  # Формат даты для логов.
MAX_SIZE = 1_048_576  # Максимальный размер лог-файла.
LOG_COUNT = 5  # Количество лог-файлов.
EXPECTED_STATUS = {
        '': ('Active', 'Draft'),
        'A': ('Accepted', 'Active'),
        'D': 'Deferred',
        'F': 'Final',
        'P': 'Provisional',
        'R': 'Rejected',
        'S': 'Superseded',
        'W': 'Withdrawn'}
