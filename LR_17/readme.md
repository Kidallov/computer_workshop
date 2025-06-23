
# Отчет по лабораторной работе № 17
## «Настройка проекта калькулятора с помощью Poetry»

### Цель работы
Научиться создавать и настраивать проект на Python с использованием менеджера зависимостей Poetry. Настроить разные окружения (dev и prod), установить зависимости, запускать тесты и основную программу в разных средах. Выполнить анализ деревьев зависимостей.

---

## Шаг 1: Инициализация проекта с Poetry

### Команда:
```bash
poetry init
```

### Итоговый файл `pyproject.toml`:
```toml
[tool.poetry]
name = "calculator"
version = "0.1.0"
description = "CLI калькулятор с логированием и табличным выводом"
authors = ["Кидалов Александр"]
readme = "README.md"
packages = [{ include = "src" }]

[tool.poetry.dependencies]
python = "^3.11"
tabulate = "^0.9"
pdoc = "^14.4"

[tool.poetry.group.dev.dependencies]
pytest = "^8.2"
black = "^24.4"
pylint = "^3.2"
ipdb = "^0.13"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

---

## Шаг 2: Установка зависимостей

### В dev-среде:
```bash
poetry install
```

### В prod-среде:
```bash
poetry install --no-dev
```

---

## Шаг 3: Запуск тестов и приложения

### Запуск тестов в dev:
```bash
poetry run pytest
```

### Запуск приложения в prod:
```bash
poetry run python main.py
poetry run pdoc src --output-dir docs
```

---

## Шаг 4: Анализ зависимостей

### Общее дерево зависимостей:
```bash
poetry show --tree
```

### Только продакшн зависимости:
```bash
poetry show --only main --tree
```

### Только dev-зависимости:
```bash
poetry show --only dev --tree
```

**Вывод**: dev-окружение содержит инструменты тестирования, отладки и форматирования, а prod — только необходимые библиотеки для запуска.

---

## Заключение

В ходе работы был сконфигурирован проект с использованием Poetry. Настроены два окружения (prod и dev), установлены зависимости, выполнен запуск автотестов и основной программы, сформирована документация и произведен анализ зависимостей.
