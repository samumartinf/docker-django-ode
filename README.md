## How to use:
### For production
Run the follwing in your Docker-Django directory:
'''docker-compose -f docker-compose.prod.yml down -v
$ docker-compose -f docker-compose.prod.yml up -d --build
$ docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput'''


### For development
'''
docker-compose up -d --build
docker-compose exec web python manage.py migrate --noinput

'''

