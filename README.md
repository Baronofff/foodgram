## 🚀 Быстрый старт (локальная установка)

### 1. Клонирование репозитория
```bash
git clone https://github.com/baronofff/foodgram.git
```
cd foodgram
2. Установка Docker
Mac: Docker Desktop for Mac

Windows: Docker Desktop for Windows

Docker Compose устанавливается автоматически с Docker Desktop

3. Запуск проекта
bash
docker-compose up --build
4. Доступ к приложению
Фронтенд: http://localhost

API документация: http://localhost/api/docs/

Админ-панель: http://localhost/admin

5. Остановка приложения
bash
docker-compose down
⚙️ Наполнение базы данных
После первого запуска выполните:

bash
# Применение миграций
docker-compose exec foodgram_backend python manage.py migrate

# Создание суперпользователя (опционально)
docker-compose exec foodgram_backend python manage.py createsuperuser

# Загрузка тестовых данных (опционально)
docker-compose exec foodgram_backend python manage.py loaddata fixtures/ingredients.json
🌐 Развертывание на сервере
Подготовка сервера
Подключитесь к серверу:

bash
ssh <username>@<host>
Установите Docker и Docker Compose (инструкции выше)

Настройте файлы:

bash
scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
Создайте .env файл с переменными:

env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<имя_базы_данных>
DB_USER=<пользователь_бд>
DB_PASSWORD=<пароль>
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<секретный_ключ_django>
Запуск на сервере
bash
# Сборка и запуск контейнеров
sudo docker-compose up -d --build

# Сборка статических файлов
sudo docker-compose exec backend python manage.py collectstatic --noinput

# Применение миграций
sudo docker-compose exec backend python manage.py migrate --noinput
🔧 Технологический стек
Backend: Django + Django REST Framework

База данных: PostgreSQL

Веб-сервер: Nginx + Gunicorn

Контейнеризация: Docker

Документация API: Swagger/OpenAPI

CI/CD: GitHub Actions

# 🤖 Настройка CI/CD (GitHub Actions)

Добавьте в Secrets репозитория (Settings → Secrets → Actions):


SECRET_KEY	Секретный ключ Django

DOCKER_USERNAME	Логин Docker Hub

DOCKER_PASSWORD	Пароль Docker Hub

HOST	Публичный IP сервера

USER	Имя пользователя на сервере

SSH_KEY	Приватный SSH-ключ

DB_ENGINE	django.db.backends.postgresql

POSTGRES_DB	Имя базы данных PostgreSQL

POSTGRES_USER	Пользователь БД PostgreSQL

POSTGRES_PASSWORD	Пароль пользователя БД

DB_HOST	Хост БД (db)

DB_PORT	Порт БД (5432)

TELEGRAM_TOKEN	Токен Telegram-бота

TELEGRAM_TO	ID Telegram-аккаунта для уведомлений

🌍 Демо-доступ
Сайт: 

Админ-панель:

Логин: 

Пароль: 

👨‍💻 Автор
Баронов Евгений
=======
# Проект Foodgram
