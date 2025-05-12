:og:description: Django Material Kit PRO - OAuth, Extended User Profiles, Premium UI Kit for Django | App-Generator.dev
:og:image: https://github.com/user-attachments/assets/c7252fc8-25bf-4586-8e4e-d5b953c492f3
:og:image:alt: Premium Django project styled with Material Kit Design, a premium UI Kit Bootstrap design actively supported by Creative-Tim. 

`Material Kit PRO </product/material-kit-pro/django/>`__
===================================================================

.. title:: Django Material Kit PRO - OAuth, Extended User Profiles, Premium UI Kit for Django | App-Generator.dev
.. meta::
    :description: Premium Django project styled with Material Kit Design, a premium UI Kit Bootstrap design actively supported by Creative-Tim.
    :keywords: material kit, material design, django material premium starter, premium django starter, premium django template

Premium Django project styled with Material Kit Design, a premium UI Kit Bootstrap design actively supported by Creative-Tim. 
The product is designed to deliver the best possible user experience with highly customizable feature-rich pages.

- 👉 `Django Material Kit PRO </product/material-kit-pro/django/>`__ - Product Page (contains download link)
- 👉 `Django Material Kit PRO <https://django-mkit2-pro.onrender.com/>`__ - LIVE Demo
- 👉 `Get Support </ticket/create/>`__ via Email and Discord 

.. include::  /_templates/components/signin-invite.rst


Features
--------

- Simple, Easy-to-Extend Codebase
- Material Kit PRO Design - Full Integration 
- Bootstrap 5 Styling 
- Session-based Authentication
- Extended User Profiles
- OAuth for GitHub & Google
- DB Persistence: SQLite (default), can be used with MySql, PgSql
- Docker 
- CI/CD integration for Render 

.. image:: https://github.com/user-attachments/assets/c7252fc8-25bf-4586-8e4e-d5b953c492f3
   :alt: Django Material Kit PRO - Premium Django project styled with Material Kit Design, a premium UI Kit Bootstrap design actively supported by Creative-Tim.


.. include::  /_templates/components/django-prerequisites.rst

Download Source Code 
--------------------

Access the `product page </product/material-kit-pro/django/#pricing>`__ and complete the purchase. 
Unpack the ZIP archive and folow these steps:

.. code-block:: shell

    unzip django-material-kit-pro.zip
    cd django-material-kit-pro

Once the source code is unzipped, the next step is to start it and use provided features. 

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

You can run Django Material Kit locally or deploy it on Render. If you want to run the server locally, you'll need to run the following command:

.. code-block:: bash

    python manage.py createsuperuser
    python manage.py runserver

Open `localhost` on your browser and you can interact with the application. 

.. _localhost: http://127.0.0.1:8000/

.. image:: https://github.com/user-attachments/assets/c7252fc8-25bf-4586-8e4e-d5b953c492f3
   :alt: Django Material Kit PRO - Premium Django project styled with Material Kit Design, a premium UI Kit Bootstrap design actively supported by Creative-Tim.

.. include::  /_templates/components/footer-links.rst
