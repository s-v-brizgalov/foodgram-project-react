![example workflow](https://github.com/s-v-brizgalov/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# Проект Foodgram, "Продуктовый помощник."

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/) [![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/) [![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/) [![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/) [![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/) [![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/) [![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/) [![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)

**Описание.**

Онлайн-сервис Foodgram и API для него.Имеется реализация CI/CD проекта.На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

  

**Доступный функционал.**

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

# Установка на удалённом сервере.

**Выполнить вход на удаленный сервер.**

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

# Примеры некоторых запросов API.

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

**Данные для входа в админку:**

- Электронная почта: foodgram@foodgram.ru
- password: 1q2w3e1q2w3e

**Проект доступен по адресу:**

- brizgalov.ru
