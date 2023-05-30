# Проект парсинга

## Функции, которые выполняет парсер

> Собирает ссылки на статьи о нововведениях в Python, позволяет переходить по ним и забирать информацию об авторах и редакторах статей;
> Собирает информацию о версиях Python;
> Скачивает архив с актуальной документацией Python;
> Собирает данные обо всех PEP документах, сравнивает статусы и записывает их в файл;


## Технологии проекта

- Python — высокоуровневый язык программирования;
- bs4 - библиотека для парсинга;
- Pretty Table - библиотека для удобного отображения табличных данных;
- argparse - библиотека для парсинга аргументов командной строки;
- requests-cache - библиотека для кэширования HTTP-ответов и их локального сохранения;
- tqdm - библиотека для реализации прогресс-бара;
- logging - модуль стандартной библиотеки Python для работы с логами;
- csv - библиотека для работы с файлами в формате csv в Python


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/elenashovtyuk/bs4_parser_pep.git
```

```
cd bs4_parser_pep
```

Cоздать виртуальное окружение:

```
python3 -m venv venv
```

Активировать виртуальное окружение

```
source venv/bin/activate
```

Обновить менеджер пакетов pip

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

## Примеры команд

Создаст csv файл с таблицей из двух колонок: «Статус» и «Количество»:

```
python main.py pep -o file или python main.py pep --output file
```

Выводит таблицу с тремя колонками в теримнал: "Ссылка на документацию", "Версия", "Статус":

```
python main.py latest-versions -o pretty
```

Выводит ссылки на нововведения в python:

```
python main.py whats-new
```
