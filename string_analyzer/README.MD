# String Analyzer Service (Django)


## Setup


```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

####Visit
http://127.0.0.1:8000/strings

##Endpoints

POST /strings

GET /strings/{string_value}

GET /strings

GET /strings/filter-by-natural-language?query=...

DELETE /strings/{string_value}

##Notes

Uses SQLite by default

Natural language filter is rule-based (limited)