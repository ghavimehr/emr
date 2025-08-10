EMR – Electronic Medical Records System
Based on [AppGenerator](https://app-generator.dev/)


This project transforms a generic web dashboard template into a functional Electronic Medical Records (EMR) system. It is designed to replace inefficient paper-based patient charts (notably common in Iran’s healthcare) with digital records. By digitizing medical data, it addresses issues like illegible handwriting, missing files, and high paper costs . The EMR stores structured patient data (demographics, vitals, medical history, lab results, etc.) and standardizes it using modern healthcare data standards, enabling better analytics. The motivation is to streamline record-keeping, improve data quality, and support advanced research and AI-driven analyses of patient data in a healthcare context.

Features
 • Structured Patient Records: Store detailed, structured data for each patient (e.g. personal info, vitals, diagnoses, treatment notes) instead of paper charts.
 • Standardized Metrics: Convert qualitative health information into quantitative metrics. For example, it can compute clinical scores (BMI, risk scores, etc.) and encode conditions using accepted medical standards (ICD codes, questionnaire scores), enabling consistent reporting.
 • Data Analytics & AI/ML Support: The backend includes Python data science libraries (pandas, etc.), so records can be easily exported or analyzed with AI/ML tools. This makes it suitable for healthcare analytics and research.
 • Web-Based Dashboard: A responsive HTML/JavaScript frontend (using React/webpack and Tailwind CSS) provides a user-friendly interface for clinicians to enter and view records.
 • Multi-language Support: The system includes localization (e.g. Persian/Farsi support) to accommodate local language needs.
 • Authentication & Security: Uses Django’s authentication (via django-allauth) and best practices (HTTPS-ready, user sessions, etc.) to protect patient data.
 • Modular Design: Built with Django and REST APIs, making it extensible (e.g. adding new medical modules or analyses).

These capabilities replace paper workflows, reducing waste (e.g. printing costs) and errors , and lay groundwork for future AI-enhanced tools.

Technologies Used
 • Backend: Python 3.12 with Django 4.2 (https://www.djangoproject.com/) and Django REST Framework for API services. Key libraries include Django-AllAuth (authentication), Celery with Redis for background tasks, Gunicorn as WSGI server, and Waitress/uvicorn support  .
 • Database: PostgreSQL (primary) and MySQL support (via mysqlclient, mysql-connector-python) for data storage (configured through environment). Database migrations use Django’s ORM.
 • Frontend: JavaScript, HTML, and CSS. The UI is built with React (managed via webpack) and styled with Tailwind CSS. Frontend assets are compiled/bundled by webpack/yarn (see package.json, webpack.config.js, tailwind.config.js).
 • Dev Tools: Docker for containerization (app image based on nikolaik/python-nodejs:python3.12-nodejs22-slim ), docker-compose for orchestration (services for Django, Celery, Redis, Postgres). Babel and Webpack for transpiling, and ESLint/Prettier for code style (black, etc.).
 • Languages: The codebase is primarily in Python (≈48%) with HTML and JavaScript for front-end .
 • Infrastructure: Nginx configuration (in nginx/), Gunicorn configuration (gunicorn-cfg.py), and other production scripts (Dockerfiles, render.yaml).
 • Documentation: Sphinx is used for project docs (see docs/), supporting Markdown and reStructuredText.

This mix of tools (Python/Django backend with a Node.js-based frontend build) leverages modern web and data technologies to deliver a full-stack EMR solution.

Installation and Setup Instructions
 1. Clone the repository:

git clone https://github.com/ghavimehr/emr.git
cd emr
2. Prepare environment:
 • Copy the sample environment file and fill in secrets (database credentials, Django secret key, etc.):

cp env.sample .env


 • Set values for DB_NAME, DB_USERNAME, DB_PASS, DJANGO_SECRET_KEY, etc., in .env.

 3. Install backend dependencies:
Ensure you have Python 3.12+ and pip installed. In the project root:



python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

This installs Django, DRF, Celery, Redis client, Pandas, and all Python packages listed in requirements.txt .

 4. Install frontend dependencies:
Ensure you have Node.js (>= v16) and Yarn or npm. Then in the project root:

yarn install    # or: npm install
yarn build      # builds the frontend assets

(Yarn commands rely on the package.json, webpack.config.js, and tailwind.config.js provided.)

 5. Initialize the database:
Create and migrate the database:

python manage.py makemigrations
python manage.py migrate

Optionally, create a superuser:

python manage.py createsuperuser


 6. Collect static files:

python manage.py collectstatic --noinput


 7. Run the development server:

python manage.py runserver

This starts Django’s local server (by default on http://127.0.0.1:8000). You can now log in to the admin or access the app UI.

Required packages/software: Python 3.12, Node.js (with Yarn), PostgreSQL (or another DB), Redis (for Celery), and Docker (optional for containerized setup). All Python dependencies are listed in requirements.txt , and Node dependencies in package.json.

For a one-step setup, use Docker Compose (see Deployment section below).

Deployment
 • Docker: The project includes Dockerfiles (Dockerfile.app, Dockerfile.celery, etc.) and docker-compose.yml for production. In Docker mode, it builds a container for the Django app, a Celery worker, Redis, and Postgres. To deploy via Docker:

docker-compose up -d --build

This builds images and runs all services (app on port 5005, celery on 5007, docs on 5006). Postgres is set up as appseed-db (with credentials from .env), and Redis as appseed-redis  .

 • Cloud/Server: For production, a Linux server with Docker or Python support is needed. Ensure ports (e.g., 5005) are open or proxied via Nginx. Configure environment variables securely (in a real deployment, use protected secrets). The render.yaml file suggests deployment on Render or similar platforms.
 • Additional Services: A production deployment requires a managed PostgreSQL database (or equivalent) and Redis. SSL certificates for HTTPS should be added (using Nginx or a cloud load balancer).

Project Status

Warning: This project is under active development. The current version (v0.0.63) is a proof of concept. Key functionality (data entry forms, analytics tools) may be incomplete. Additional setup is required before it can be production-ready:
 • Migrations & Data: Database schemas may still evolve.
 • Dependencies: You may need to install extra packages as features expand.
 • Testing: Rigorous testing (unit tests, user testing) is ongoing.
 • Configuration: The developer must adjust environment settings (.env), update Docker configs, and secure the app for deployment.

Developers should treat this as a work-in-progress. Contributions and improvements are encouraged to reach a stable release.

Contributing

Contributions are welcome! If you have ideas (new features, bug fixes), feel free to fork the repo and submit a pull request. Please ensure code follows the existing style and include tests where applicable. You can also open issues on GitHub to report bugs or request enhancements.


## LICENSE

[@EULA](./LICENSE.md)

<br />

---

Crafted and actively supported by [AppSeed](https://appseed.us/) - *<support@appseed.us>*
