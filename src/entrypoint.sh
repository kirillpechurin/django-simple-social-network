set -e

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py setup_system

gunicorn --reload config.wsgi:application --bind 0.0.0.0:8000 --log-level info