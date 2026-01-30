Please kindly install 
1. python -m venv venv
2. venv\Scripts\activate (For Windows) or venv/bin/activate (For Mac/Linux)
3. pip install django
4. Run Server From Terminal Command - python manage.py runserver


# Prothom-e ekta folder banai
mkdir my_blog_project
cd my_blog_project

# Virtual environment create kora (venv holo environment er naam)
python -m venv venv

# Virtual environment activate kora
# Windows er jonno:
venv\Scripts\activate
# Mac/Linux er jonno:
source venv/bin/activate



# Django install kora
pip install django

# Install check korar jonno (optional)
django-admin --version




# 'core' name-e project start kora (dot (.) dile current folder-e file gula thakbe)
django-admin startproject core .

# 'posts' name-e ekta app create kora
python manage.py startapp posts


# Model e kono change korle migration file banate hoy
python manage.py makemigrations

# Migration file gulo database-e apply kora (SQLite table create hobe eikhane)
python manage.py migrate



# Admin account create kora
python manage.py createsuperuser

# Project run kora
python manage.py runserver



file stracture must be 
my_blog_project/

venv/ (Environment files)

core/ (Project settings)

posts/ (App logic, models, views)

db.sqlite3 (Database file)

manage.py