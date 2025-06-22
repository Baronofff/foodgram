Foodgram - Продуктовый помощник

Описание:
Онлайн-платформа для публикации кулинарных рецептов с возможностью формирования списка покупок.

Основной функционал:
- Публикация и редактирование рецептов
- Добавление рецептов в избранное
- Подписка на авторов
- Формирование списка покупок (с экспортом в PDF)
- Поиск рецептов по тегам и ингредиентам

Технологический стек:
[Backend] Python 3.9 + Django 3.2 + DRF
[Frontend] React.js
[База данных] PostgreSQL
[Инфраструктура] Docker + Nginx + Gunicorn
[CI/CD] GitHub Actions

Установка:
1. git clone https://github.com/baronofff/foodgram.git
2. cd foodgram
3. docker-compose up --build

Доступ после запуска:
- Сайт: http://localhost
- API: http://localhost/api/docs/
- Админка: http://localhost/admin
(логин: admin, пароль: admin)

Для production-развертывания:
1. Настроить .env файл
2. Запустить docker-compose -f docker-compose.production.yml up -d
3. Применить миграции: docker-compose exec backend python manage.py migrate