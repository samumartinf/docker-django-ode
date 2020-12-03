## How to use:
### For production
To run cd to the Docker-Django directory and run:
$ docker-compose -f docker-compose.prod.yml up -d --build
$ docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput


### For development
To run dev cd to the Docker-Django directory and run:
docker-compose up -d --build
docker-compose exec web python manage.py migrate --noinput


