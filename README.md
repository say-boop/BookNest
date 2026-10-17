# 📚 BookNest

Простой REST API для ведения списка книг: можно добавлять книги, отмечать статус (хочу прочитать, читаю, прочитал), ставить оценку, искать и сортировать.

## ✨ Возможности

- **CRUD книг**: создание, чтение, обновление, удаление.
- **Статусы**: `want_to_read` (хочу прочитать), `reading` (читаю), `read` (прочитал).
- **Оценка**: от 1 до 10 (опционально).
- **Фильтрация**: по статусу (`?status=read`).
- **Поиск**: по названию и автору (`?search=толстой`).
- **Сортировка**: по дате добавления или рейтингу (`?sort=rating&order=desc`).

## 🛠 Стек

- **Python** 3.12
- **FastAPI**
- **SQLAlchemy 2.0** (async)
- **SQLite** (aiosqlite)
- **Alembic** (миграции)
- **Pydantic v2**
- **Poetry** (управление зависимостями)

## 🚀 Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/say-boop/BookNest.git
cd BookNest
```

### 2. Установить зависимости

```bash
poetry install
```

### 3. Создать .env

Скопируй `.env.example` в `.env`:

```bash
cp .env.example .env
```

### 4. Применить миграции

```bash
poetry run alembic upgrade head
```

### 5. Запустить сервер

```bash
poetry run uvicorn app.main:app --reload
```

### 6. Открыть документацию

Перейти по адресу: [клик](http://localhost:8000/docs)


## 📡 API Endpoints

| Метод  | Путь                         | Описание |
|--------|------------------------------|----------|
| GET    | `/books`                     | Список книг (с фильтрацией, поиском, сортировкой) |
| POST   | `/books`                     | Создать книгу |
| GET    | `/books/{book_id}`           | Получить книгу по ID |
| PATCH  | `/books/{book_id}`           | Обновить книгу |
| PATCH  | `/books/{book_id}/rating`    | Поставить оценку (1-10) |
| DELETE | `/books/{book_id}`           | Удалить книгу |


## Параметры `GET /books`

| Параметрд  | Тип      | Допустимые значения               | Описание |
|------------|----------|-----------------------------------|----------|
| `status`   | string   | `want_to_read`, `reading`, `read` | Фильтр по статусу |
| `search`   | string   | любая строка                      | Поиск по названию и автору |
| `sort`     | string   | `created_at`, `rating`            | Поле для сортировки |
| `order`    | string   | `asc`, `desc`                     | Направление сортировки |


## 📂 Структура проекта

```text
BookNest/
├── app/
│   ├── core/              # Конфиг, БД, исключения, enum'ы
│   ├── features/
│   │   └── books/         # Фича "книги"
│   │       ├── models.py      # SQLAlchemy-модель
│   │       ├── schemas.py     # Pydantic-схемы
│   │       ├── repository.py  # Работа с БД
│   │       ├── service.py     # Бизнес-логика
│   │       └── router.py      # HTTP-эндпоинты
│   └── main.py            # Точка входа
├── migrations/            # Alembic-миграции
├── scripts/               # Seed-скрипты
├── .env.example
├── pyproject.toml
└── README.md
```