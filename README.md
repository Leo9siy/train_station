## TRAIN STATION API PROJECT

## This project ll help u with Your Train Station

## TECNOLOGIES
- Python 3.13
- Django 5.1.6
- DRF 5.5

## Setup

```bash
git clone https://github.com/Leo9siy/train_station.git
cd train_station
python -m venv .venv
.venv\Scripts\activate

SET DJANGO_SECRET_KEY=<Your secred key>
SET POSTGRES_DB=<Your DB Name>
SET POSTGRES_USER=<Your DB user>
SET POSTGRES_HOST=<Your DB Host>
SET POSTGRES_PASSWORD=<Your DB Password>

pip install -r requirements.txt
python manage.pu migrate
python manage.py runserver
```

## Before start

1. Create superuser with custom Email and Password
```
python manage.py createsuperuser
```
2. Login at https://127.0.0.1/api/v1/user/login

3. Read more about This API at https://127.0.0.1/api/doc/swagger/

## To test use
```bash
python manage.py test
```

## Run with Docker

docker-compose build
docker-compose up

## Getting Access

create user /api/v1/user/register
get token /api/v1/user/login/

## FEATURES
1. JWT authentication
2. More User Groups
3. More custom permissions
