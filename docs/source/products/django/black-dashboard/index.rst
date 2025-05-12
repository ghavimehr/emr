:og:description: Django Black Dashboard - Open-Source Django Template 
:og:image: https://user-images.githubusercontent.com/51070104/196730732-dda1794b-93ce-48cb-bc5c-182411495512.png
:og:image:alt: Django Black Dashboard - Open-Source Django Template 

`Black Dashboard </product/black-dashboard/django/>`__
=============================================================

.. title:: Django Black Dashboard - Open-Source Django Template 
.. meta::
    :description: Open-Source Django Template crafted on top of Black Dashboard Design
    :keywords: django, starter, django template, black design, black dashboard, bootstrap dark-design

Free starter built on top of Bootstrap and Django with database, authentication, and Docker support. The Black Dashboard design is crafted by Creative-Tim using Bootstrap 5 Framework.

- 👉 `Django Black Dashboard </product/black-dashboard/django/>`__ - Product Page (contains download link)
- 👉 `Django Black Dashboard <https://django-black-dashboard.appseed-srv1.com>`__ - LIVE Demo
- 👉 `Get Support </ticket/create/>`__ via Email and Discord 

.. include::  /_templates/components/signin-invite.rst


Features
--------

- Simple, Easy-to-Extend codebase
- `Black Dashboard </docs/templates/bootstrap/black-dashboard.html>`__ Full Integration 
- Bootstrap 4 Styling 
- Session-based Authentication
- DB Persistence: SQLite (default), can be used with MySql, PgSql
- Docker 
- CI/CD integration for Render 

.. image:: https://user-images.githubusercontent.com/51070104/196730732-dda1794b-93ce-48cb-bc5c-182411495512.png
   :alt: Django Black Dashboard - Open-source Starter styled with Black Dashboard design 


Download Source Code 
--------------------

The product can be downloaded from the `official product page </product/black-dashboard/django/>`__ or directly from GitHub (public repository)

.. code-block:: shell

    git clone https://github.com/app-generator/django-black-dashboard.git
    cd django-black-dashboard

Once the source code is available in the local filesystem, the next step is to start it and use provided features. 


.. include::  /_templates/components/start-in-docker.rst


Codebase  
--------

The project is coded using a simple and intuitive structure presented below:

.. code-block:: bash
    :caption: Project Files

    < Project ROOT > 
        |
        |
        |-- core/                            
        |    |-- settings.py                  # Project Configuration  
        |    |-- urls.py                      # Project Routing
        |
        |-- home/
        |    |-- views.py                     # APP Views 
        |    |-- urls.py                      # APP Routing
        |    |-- models.py                    # APP Models 
        |    |-- tests.py                     # Tests  
        |    |-- templates/                   # Theme Customisation 
        |         |-- includes                # UI Components  
        |     
        |-- requirements.txt                  # Project Dependencies
        |
        |-- env.sample                        # ENV Configuration (default values)
        |-- manage.py                         # Start the app - Django default start script


Building the project
--------------------

It's best to use a Python Virtual Environment for installing the project dependencies. You can use the following
code to create the virtual environment

.. code-block:: bash

    virtualenv env

To activate the environment execute **env\Scripts\activate.bat** for Windows or **source env/bin/activate** on Linux-based operating systems. 

Having the `VENV` active, we can proceed and install the project dependencies:

.. code-block:: bash

    pip install -r requirements.txt

Core Dependencies
-----------------

The starter requires the following in order to be succesfully started: 

- Python 3.10 (or above)
- (Optional) Git command line - used by the versioning system 
- (Optional) MySql or PostgreSQL DB Servers 
  - if the default SQLite is not enough
- A modern code editor like VsCode or Sublime 

The python version can be easily check in the terminal by typing: 

.. code-block:: bash

    python --version
    Python 3.12.0

Environment Settings  
--------------------

The starter loads the environment variables from `.env` file. Here are the critical ones: 

- **DEBUG**: set by default to False (development mode)
- **SECRET_KEY**: a random value used by Django to secure sensitive information like passwords and cookie information 
- **Database** Credentials: `DB_ENGINE`, `DB_USERNAME`, `DB_PASS`, `DB_HOST`, `DB_PORT`, `DB_NAME`
    - if detected, the database is switched automatically from the default SQLite to the specified DBMS  

Setting up the Database
-----------------------

**By default**, the application **uses SQLite** for persistence. In order to use `MySql`/`PostgreSQL`, you'll need to install the Python driver(s):

.. code-block:: bash

    pip install mysqlclient # for MySql
    # OR 
    pip install psycopg2    # for PostgreSQL

To connect the application with your mySQL database, you'll need to fill in the credentials
int the `.env` file and run the migrations.

.. code-block:: text
    :caption: .env

    DB_ENGINE=mysql
    # OR 
    DB_ENGINE=postgresql

    # DB credentials below
    DB_HOST=localhost
    DB_NAME=<DB_NAME_HERE>
    DB_USERNAME=<DB_USER_HERE>
    DB_PASS=<DB_PASS_HERE>
    DB_PORT=3306

Use the following commands to seed your data:

.. code-block:: bash

    python manage.py makemigrations
    python manage.py migrate

Running the project
-------------------

You can run Rocket Django locally or deploy it on Render. If you want to run the server locally, you'll need to run the following command:

.. code-block:: bash

    python manage.py createsuperuser
    python manage.py runserver

Open `localhost` on your browser and you can interact with the application. 

.. _localhost: http://127.0.0.1:8000/

.. image:: https://user-images.githubusercontent.com/51070104/196730732-dda1794b-93ce-48cb-bc5c-182411495512.png
   :alt: Django Black Dashboard - Open-source Starter styled with Black Dashboard design 

.. include::  /_templates/components/django-create-users.rst

.. include::  /_templates/components/generator-django.rst
        
.. include::  /_templates/components/footer-links.rst
