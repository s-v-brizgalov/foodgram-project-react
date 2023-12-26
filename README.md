
# Проект Foodgram, "Продуктовый помощник"

***Python Django Фреймворк Django REST PostgreSQL Nginx gunicorn docker GitHub***

![example workflow](https://github.com/s-v-brizgalov/foodgram-project-react/actions/workflows/main.yml/badge.svg)

**Описание**

Онлайн-сервис Foodgram и API для него.Имеется реализация CI/CD проекта.На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

  

**Доступный функционал**

Аутентификация реализована с помощью стандартного модуля DRF - Authtoken.

У неаутентифицированных пользователей доступ к API только на уровне чтения.

Создание объектов разрешено только аутентифицированным пользователям.На прочий фунционал наложено ограничение в виде административных ролей и авторства.

**Управление пользователями.**

Возможность получения подробной информации о себе и ее редактирование.

Возможность подписаться на других пользователей и отписаться от них.

Получение списка всех тегов и ингредиентов.

Получение списка всех рецептов, их добавление.Получение, обновление и удаление конкретного рецепта.

Возможность добавить рецепт в избранное.

Возможность добавить рецепт в список покупок.

Возможность скачать список покупок в PDF формате.

  

# Технологи:

- Python 3.7
- Django 3.2.15
- Django Rest Framework 3.12.4
- Authtoken
- Docker
- Docker-создавать
- PostgreSQL
- Gunicorn
- Nginx

**Действия на GitHub**

Выделенный сервер Linux Ubuntu 22.04 с публичным IP

Локальный запуск проекта

Склонировать репозиторий:

git clone <название репозитория>

< cd название репозитория>

**Cоздать и активировать виртуальное окружение:**

  

**Команда для установки виртуального окружения на Mac или Linux:**

  

- python3 -m supports env

- source env/bin/activate

**Команда для Windows:**

  

- python -m venv venv

- source venv/Scripts/activate

**Перейти в директорию infra:**

- cd infra

**Создать файл .env по образцу:**

- .env.example

**Выполнить команду для доступа к документации:**

docker creation

**Установить зависимости из файла requirements.txt:**

  

- cd..

- cd backend

- pip install -r requirements.txt

**Выполните миграции**

- python manage.py migrate

**Заполнить базу тестовыми данными об ингредиентах:**

  

- python manage.py load_ingredients

**Создать суперпользователя, если необходимо:**

  - python manage.py createsuperuser


**Запустить локальный сервер:**

- python manage.py runserver

# Установка на удалённом сервере

**Выполнить вход на удаленный сервер**

**Установить docker:**

- sudo apt update 
- sudo apt install curl 
- curl -fSL https://get.docker.com -o get-docker.sh 
- sudo sh ./get-docker.sh 
- sudo apt-get install docker-compose-plugin

  

**Находясь локально в директории , скопировать файлы docker-compose.yml и nginx.conf на удаленный сервер:**

- scp docker-compose.yml <имя пользователя>@<хост>:/home/<имя пользователя>/

- scp nginx.conf <имя пользователя>@<хост>:/home/<имя пользователя>/

**Для правильной работы workflow необходимо добавить в Secrets данного репозитория на GitHub переменные окружения:**
- Переменные PostgreSQL, ключ проекта Django и их значения по-умолчанию можно взять из файла .env.example, затем установить свои.

  

- DOCKER_USERNAME=<имя пользователя DockerHub>

- DOCKER_PASSWORD=<пароль от DockerHub>

  

- USER=<username  для  подключения  к  удаленному  серверу>

- HOST=<ip  сервера>

- PASSPHRASE=<пароль для сервера, если он установлен>

- SSH_KEY=<ваш приватный SSH-ключ (для получения команда: cat ~/.ssh/id_rsa)>

  

- TELEGRAM_TO=<id  вашего  Телеграм-аккаунта>

- TELEGRAM_TOKEN=<токен вашего бота>

**Workflow проекта запускается при выполнении команды git push**

- tests: проверка кода на соответствие PEP8.

- build_and_push_to_docker_hub: сборка и размещение образа проекта на DockerHub.

- deploy: автоматический деплой на боевой сервер и запуск проекта.

- send_massage: отправка уведомления пользователю в Телеграм.

**После успешного результата работы workflow зайдите на боевой сервер**

**Примените миграции:**

- sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate

**Подгружаем статику:**

- sudo docker-compose exec backend python manage.py collectstatic --no-input

**Заполните базу тестовыми данными об ингредиентах:**

- sudo docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients

**Создайте суперпользователя:**

- sudo docker compose -f docker-compose.production.yml  exec -it backend python manage.py createsuperuser

# Примеры некоторых запросов API

**Регистрация пользователя:**

  

- POST / api/users/

**Получение данных своей учетной записи:**

  

- GET / api/users/me/

**Добавление подписки:**

  

- POST / api/users/ id/ subscribe/


**Обновление рецепта:**

   - PATCH /api/recipes/id/

**Удаление рецепта из избранного:**

   - DELETE /api/recipes/id/favorite/

**Получение списка ингредиентов:**

   - GET /api/ingredients/

**Скачать список покупок:**

   - GET /api/recipes/download_shopping_cart/

**Автор бэкэнда:**

- Сергей Бризгалов

**Данные пользователя**

Электронная почта: foodgram@foodgram.ru
Логин: foodgramuser
Имя: foodgramuser
Фамилия: foodgramuser
password: 1q2w3e1q2w3e
