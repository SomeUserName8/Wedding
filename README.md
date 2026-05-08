# Wedding Guest KMeans Seating

Скрипт читает CSV гостей, применяет взвешенные признаки (`age`, `side`, `alcohol`) и с помощью `KMeans` рекомендует рассадку по столам.

## Что настраивается

В файле `seat_recommender.py` есть две глобальные переменные:

- `TABLE_COUNT` - количество столов.
- `MAX_GUESTS_PER_TABLE` - максимальное количество гостей за столом.

Перед запуском поменяйте их под вашу рассадку.

## Подготовка окружения (venv)

В корне проекта:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Запуск

```bash
python3 seat_recommender.py
```

## Входные данные

По умолчанию используется файл:

- `guests.csv`

Ожидаемые колонки:

- `id`
- `age`
- `side` (`Невеста` или `Жених`)
- `alcohol` (`TRUE` или `FALSE`)
- `age_weight`, `side_weight`, `alcohol_weight` (поддерживается формат `0,4`)

## Результат

- Создается файл `seating_recommendations.csv` с колонкой `recommended_table`.

## Возможные ошибки

Скрипт валидирует:

- `TABLE_COUNT > 0`
- `MAX_GUESTS_PER_TABLE > 0`
- `TABLE_COUNT * MAX_GUESTS_PER_TABLE >= количество гостей`
- корректность обязательных колонок и формата значений.
