# News API (Flask + PostgreSQL)

CRUD API для управления новостями с использованием Flask и PostgreSQL. Поддерживает создание, чтение, обновление и удаление новостей с тегами.

## Установка

### Требования

- Python 3.11+
- PostgreSQL 17+
- pip

### 1. Клонирование репозитория
```bash
git clone https://github.com/Ewgentor/news_backend.git
```
### 2. Настройка окружения
Создайте файл ```.env``` в корне проекта:
```
DATABASE_URL=postgresql://user:password@localhost/news_db
```
### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Инициализация базы данных
```bash
psql -c 'CREATE DATABASE news_db;'
```

## Использование

### Запуск сервера
```bash
flask run --host=127.0.0.1 --post=5000
```

## Примеры запросов (cURL)

### Создать новость
```bash
curl -X POST http://127.0.0.1:5000/news \
-H 'Content-Type: application/json' \
-d '{
    "title": "Заголовок новости",
    "text": "Текст новости",
    "img": "http://example_img.com",
    "tags": ["Тег1", "Тег2", "Тег3"]
}'
```
### Получить все новости

```bash
curl -X GET http://127.0.0.1:5000/news
```

### Обновить новость
```bash
curl -X PATCH http://127.0.0.1:5000/news \
-H 'Content-Type: application/json' \
-d '{
    "tags": ["Тег1", "Тег3"]
}'
```

## API Endpoints

| Метод  | Путь                      | Описание                             | Тело запроса (JSON)                                                           |
|--------|---------------------------|--------------------------------------|-------------------------------------------------------------------------------|
| GET    | `/news`                   | Получить все новости                 | Не требуется                                                                  |
| GET    | `/news/<int:id>`          | Получить новость по ID               | Не требуется                                                                  |
| POST   | `/news`                   | Создать новость                      | `{"title": "...", "text": "...", "img": "...","tags"["..."]`                  |
| PATCH  | `/news/<int:id>`          | Обновить новость                     | `{"title": "...", "text": "...", "img": "...","tags"["..."]` (можно частично) |
| DELETE | `/news/<int:id>`          | Удалить новость                      | Не требуется                                                                  |
| PATCH  | `/news/<int:id>/rollback` | Откатить последнее изменение новости | Не требуется                                                                  |


## Технологии
- **Python 3.11+**
- **Flask**
- **Flask-SQLAlchemy**
- **PostgreSQL**