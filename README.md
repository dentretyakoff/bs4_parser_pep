# Проект парсинга pep
Парсер документации PEP для Python.\
Используемые библиотеки:
```
- beautifulsoup4==4.9.3
- lxml==4.6.3
- prettytable==2.1.0
- requests-cache==1.0.0
- tqdm==4.61.0
```

## Установка и настройка
- Клонируйте репозиторий: `git clone git@github.com:dentretyakoff/bs4_parser_pep.git`
- Перейдите в директорию проекта: `cd ваш-репозиторий`
- Создайте и активируйте виртуальное окружение: `python3 -m venv venv && source venv/bin/activate`
- Установите зависимости: `pip install -r requirements.txt`

## Использование
Парсер имеет четыре режима работы:
- `whats-new` - cохраняет ссылки на статьи о наиболее важных изменениях между основными версиями Python.
- `latest-versions` - cохраняет ссылки на документацию основных версий Python.
- `download` - cкачивает документацию для актуальной версии Python.
- `pep` - одсчитывает количество PEP в каждом статусе и общее количество PEP.

Функции `whats-new`, `latest-versions` и `pep` могут принимать параметр `-o` или `--output` со значениями `{pretty,file}`:
- `-o pretty` - распечатает результат в терминал.
- `-o file` - сохранит файл с расширением `.csv` в каталог `./results/`.

Функция `download` сохраняет `.zip`-архив с документацией в каталог `./downloads/`.

Пример команды запуска:
```
python main.py whats-new -o pretty
```
Парсер сохраняет лог своей работы в каталог `./logs/`.

### Авторы
Команда Яндекс Практикум, [Денис Третьяков](https://github.com/dentretyakoff)
### Лицензия
[MIT License](https://opensource.org/licenses/MIT)