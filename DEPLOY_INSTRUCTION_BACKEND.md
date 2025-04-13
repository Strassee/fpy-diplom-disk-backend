# Инструкция по развертыванию приложения (Backend)

1. Разверните сервер с Linux (например Ubuntu 24.04.2 LTS)
2. Создайте на рабочем компьютере ключ для подключения к серверу по SSH, команда: ssh-keygen
3. Добавьте публичный ключ id_rsa.pub из домашней директории ~/.ssh/ на сервер
4. Подключитесь к серверу - команда "ssh admin@ip_адрес сервера"
5. Создайте нового пользователя, например admin, назначьте его администратором и переключитесь на него: adduser admin, usermod admin -aG sudo, su admin
7. Обновите репозиторий sudo apt update
8.  Установите необходимые пакеты для развертывания приложения: sudo apt install python3-venv python3-pip postgresql nginx git
9.  Cоздайте папку проекта в домашней директории (команда mkdir) и скопируйте проект с Github в папку проекта командой: git clone ссылка_на_репозиторий_github
10. Создайте базу данных для приложения, для этого:
    - Переключитесь на пользователя postgres: sudo su postgres
    - Зайдите в postgres: psql
    - Задайте пароль для пользователя postgres: ALTER USER postgres WITH PASSWORD 'Пароль';
    - Создайте базу данных: CREATE DATABASE Название_базы_данных;
    - Проверьте, что базаданных создалась (в списке должно быть ее имя): SELECT datname FROM pg_database;
    - Выйдите из postgres и из пользователя postgres: \q, exit
11.   Скопируйте и переименуйте файл /disk/.env.template в /disk/.env и настройте в нем параметры приложения:
    - SECRET_KEY=сгенерируйте секретный ключ для приложения Django (сайт https://djecrety.ir/)
    - DEBUG=отключите режим отладки для Production mode (False)
    - MEDIA_ROOT=задайте имя директории-хранилища
    - DATABASES_ENGINE=django.db.backends.postgresql
    - DATABASES_NAME=Имя базы данных
    - DATABASES_USER=Имя пользователя базы данных
    - DATABASES_PASSWORD=Пароль пользователя базы данных
    - DATABASES_HOST='127.0.0.1'
    - DATABASES_PORT='5432'
    - STATIC_FOLDER='static'
    - ALLOWED_HOSTS=127.0.0.1,localhost,перечислите разрешенные хосты для приложения, включая доменные имена
    - CSRF_TRUSTED_ORIGINS=http://127.0.0.1:3000,http://localhost:3000,перечислите доверенные хосты для приложения, включая доменные имена
    - ADMIN_USERNAME=задайте логин первого суперпользователя
    - ADMIN_PASSWORD=задайте пароль первого суперпользователя
    - ADMIN_EMAIL=задайте e-mail первого суперпользователя
12. Перейдите в корень папки проекта и создайте виртуальное окружение: python3 -m venv .venv
13. Активируйте виртуальное окружение: source .venv/bin/activate
14. Установите необходимые модули для проекта в виртуальное окружение: pip install -r requirements.txt
15. Подготовьте миграции и примените их к базе данных: python manage.py makemigrations, python manage.py migrate
16. Проверьте работоспособность приложения в режиме разработки: python manage.py runserver 0.0.0.0:8000
17. Перейдите в корневую папку проекта, где находится файл wsgi.py, и проверьте работу gunicorn командой: gunicorn disk.wsgi -b 0.0.0.0:8000
18. Настройте работу gunicorn как службы сервера, для этого создайте файл sudo nano /etc/systemd/system/gunicorn.service со следующим содержимым:

    [Unit]
    Description=gunicorn service
    After=network.target

    [Service]
    User=имя_пользователя_системы
    Group=группа_пользователя_системы
    WorkingDirectory=/путь_до_корня_проекта
    ExecStart=/путь_до_корня_проекта/.venv/bin/gunicorn \
              --access-logfile - \
              --workers=3 \
              --bind unix:/путь_до_корня_проекта/disk/gunicorn.sock \
              disk.wsgi:application

    [Install]
    WantedBy=multi-user.target

19. Стартуйте службу gunicorn.service, добавьте ее в автозагрузку и проверьте статус: sudo systemctl start gunicorn, sudo systemctl enable gunicorn, sudo systemctl status gunicorn
20. Настройте статику в Django-приложении: 
    - в settings.py в блоке 'INSTALLED_APPS' проверьте наличие/добавьте 'django.contrib.staticfiles'
    - в settings.py проверьте наличие/добавьте переменную STATIC_URL - название папки, в которую собирается статика, задайте ей значение f'/{env('STATIC_FOLDER')}/', где env('STATIC_FOLDER') - переменная окружения из файла .env
    - в settings.py проверьте наличие/добавьте переменную STATIC_ROOT, задайте ей значение os.path.join(BASE_DIR, env('STATIC_FOLDER'))
    - соберите статику командой python manage.py collectstatic
21. Настройте веб-сервер Nginx:
    - создайте файл настроек сайта командой sudo nano /etc/nginx/sites-available/disk
    - задайте в нем следующие настройки: 
      server {
        listen 8000;
        server_name ip_адрес_или_доменное_имя_сервера;

        location /static/ {
            root путь_до_корня_проекта_где_находится_папка_static;
        }

        location / {
            include proxy_params;
            proxy_pass http://unix:путь_до_корня_проекта/disk/gunicorn.sock;
        }
      }
    - включите сайт командой: sudo ln -s /etc/nginx/sites-available/disk /etc/nginx/sites-enabled/disk
    - Для корректного разрешения прав и подключения Nginx к gunicorn.sock в файле конфигурации Nginx /etc/nginx/nginx.conf в строке 'user' вместо пользователя www-data напишите имя своего текущего пользователя: sudo nano /etc/nginx/nginx.conf
    - В этом же файле настроек /etc/nginx/nginx.conf, необхожимо отключить проверку размера тела запроса с клиента, для возможности отправки на сервер больших файлов. Добавьте в конец блока http {} файла конфигурации строчку: client_max_body_size 0;
    - на фаерволле разрешите полные права для Nginx: sudo ufw allow 'Nginx Full'
    - для обновления рабочей конфигурации перезапустите веб-сервер Nginx: sudo systemctl reload nginx или sudo nginx -s reload
22. проверьте работоспособность бэкэнда, - перейдите в браузер и попробуйте открыть страницу: http://ip_адрес_или_доменное_имя_сервера:8000/ Должно отобразиться 'Not Found. The requested resource was not found on this server' Если ответ другой, проверьте все ли Вы сделали согласно этой инструкции.
23. Если страница открылась, перейдите к разворачиванию фронтэнда на сервере. Инструкция по разворачиванию находится в файле DEPLOY_INSTRUCTION_FRONTEND.md в корне проекта фронтэнда.
