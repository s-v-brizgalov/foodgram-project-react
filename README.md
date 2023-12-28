
# Проект Foodgram, "Продуктовый помощник"

<p><a href="https://www.python.org/" rel="nofollow"><img src="https://camo.githubusercontent.com/938bc97e6c0351babffcd724243f78c6654833e451efc6ce3f5d66a635727a9c/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d507974686f6e2d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d507974686f6e" alt="Python" data-canonical-src="https://img.shields.io/badge/-Python-464646??style=flat-square&amp;logo=Python" style="max-width:100%;"></a>
<a href="https://www.djangoproject.com/" rel="nofollow"><img src="https://camo.githubusercontent.com/99e48bebd1b4c03828d16f8625f34439aa7d298ea573dd4e209ea593a769bd06/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d446a616e676f2d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d446a616e676f" alt="Django" data-canonical-src="https://img.shields.io/badge/-Django-464646??style=flat-square&amp;logo=Django" style="max-width:100%;"></a>
<a href="https://www.docker.com/" rel="nofollow"><img src="https://camo.githubusercontent.com/038c45c7c5f0059723bba28b5b77bd9ac7994c8da774814c8fcb620f4bc61b35/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d646f636b65722d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d646f636b6572" alt="docker" data-canonical-src="https://img.shields.io/badge/-docker-464646??style=flat-square&amp;logo=docker" style="max-width:100%;"></a>
<a href="https://www.postgresql.org/" rel="nofollow"><img src="https://camo.githubusercontent.com/18b5ef277b89701f948c212d45d3460070037bda9712fe5f1e64315811356ea2/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d506f737467726553514c2d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d506f737467726553514c" alt="PostgreSQL" data-canonical-src="https://img.shields.io/badge/-PostgreSQL-464646??style=flat-square&amp;logo=PostgreSQL" style="max-width:100%;"></a>
<a href="https://www.sqlite.org/index.html" rel="nofollow"><img src="https://camo.githubusercontent.com/2c46c2b57530e634094dcb5ca341adbd8cc101300fd0968991b2a2700f1ac318/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d53514c6974652d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d53514c697465" alt="SQLite" data-canonical-src="https://img.shields.io/badge/-SQLite-464646??style=flat-square&amp;logo=SQLite" style="max-width:100%;"></a>
<a href="https://github.com/"><img src="https://camo.githubusercontent.com/ca897bbf26e1c6429197c0c0f53e16f1625eaa99d0bc8caa4934c4b12ece45a1/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d4769744875622d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d476974487562" alt="GitHub" data-canonical-src="https://img.shields.io/badge/-GitHub-464646??style=flat-square&amp;logo=GitHub" style="max-width:100%;"></a>
<a href="https://github.com/features/actions"><img src="https://camo.githubusercontent.com/b70fe9e64e76d385b8cae9b6366dfba69af953e85d16cf43bb1f9d46fefb1621/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d476974487562253230416374696f6e732d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d476974487562253230616374696f6e73" alt="GitHub%20Actions" data-canonical-src="https://img.shields.io/badge/-GitHub%20Actions-464646??style=flat-square&amp;logo=GitHub%20actions" style="max-width:100%;"></a>
<a href="https://nginx.org/ru/" rel="nofollow"><img src="https://camo.githubusercontent.com/b9f9edede39c7f898e25e81ce431f7c4b8d0b375c05768fd6916e599fcba219f/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f2d4e47494e582d3436343634363f3f7374796c653d666c61742d737175617265266c6f676f3d4e47494e58" alt="NGINX" data-canonical-src="https://img.shields.io/badge/-NGINX-464646??style=flat-square&amp;logo=NGINX" style="max-width:100%;"></a></p>

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

**Данные для входа в админку:**

- Электронная почта: foodgram@foodgram.ru
- Логин: foodgramuser
- Имя: foodgramuser
- Фамилия: foodgramuser
- password: 1q2w3e1q2w3e

**Адрес:**

- brizgalov.ru
