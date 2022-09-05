# Foodgram

![Foodgram workflow](https://github.com/PVchuchkov/foodgram-project-react/actions/workflows/main.yml/badge.svg)  


# Foodgram
Foodgram  - проект для публикации рецептов. Авторизованные пользователи
могут подписываться на понравившихся авторов, добавлять рецепты в избранное,
в покупки, скачать список покупок ингредиентов для добавленных в покупки
рецептов.

## Запуск проекта
* Установите docker на сервер:
sudo apt install docker.io 
* Установите docker-compose на сервер:

sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

* Отредактируйте файл infra/nginx.conf и в строке server_name впишите свой IP
* Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на сервер:

* впишитеи в .env файл ни сервере или в в secrets проэкта на github 
в случае workflow:
    ```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    SECRET_KEY=<секретный ключ проекта django>
    
    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя от DockerHub>
    
    SECRET_KEY=<секретный ключ проекта django>
    
    HOST=<IP сервера>
    USER=<username для сервера>
    SSH_KEY=<ваш SSH ключ сервера>
    
    PASSPHRASE=<пароль для ключа, если он установлен>
    
    TELEGRAM_TO=<ID чата>
    TELEGRAM_TOKEN=<токен вашего бота>
  

* После успешной сборки на сервере выполните команды (только после первого деплоя):
    
    - Выполните миграции:
    sudo docker-compose exec backend python manage.py migrate
    
    - Соберите статику:
    sudo docker-compose exec backend python manage.py collectstatic
    
    - Создать суперпользователя:
    sudo docker-compose exec backend python manage.py createsuperuser
                                                                          
### Адрес документации
  http://158.160.5.77/api/docs/     
  
### адрес в интернете

  Проект запущен по адресу http:/158.160.5.77//

Логин-пароль админа

root
sotnichenko.danik@yandex.ru


Автор проекта: Сотниченко Даниил. sotnichenko.danik@mail.ru


