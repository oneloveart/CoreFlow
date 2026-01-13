# TimeSaver — Bootstrap full project v2

Includes: CRUD, exports (CSV & PDF with summary + basic chart), unit tests.

Run:
1. pip install -r requirements.txt
2. python manage.py makemigrations
3. python manage.py migrate
4. python manage.py createsuperuser
5. python manage.py loaddata demo_data.json (optional)
6. python manage.py runserver

Run tests:
python manage.py test
