# Django Simple Social Network
___

1. [Project objective](#project-objective)
2. [Realization](#realization)
   + [Technical part](#technical-part)
   + [Business tasks](#business-tasks)
3. [Project structure](#project-structure)
4. [Description of environment variables](#description-of-environment-variables)
5. [Launch](#launch)
   + [Requirements](#requirements)
   + [Start local development server](#start-local-development-server)
   + [Start in docker](#start-in-docker)
6. [Licensing](#licensing)
___


## Project objective
Just a social network backend that can 
serve as a framework for building more complex 
social network systems.


## Realization
___

### Technical part
* The application is implemented using [Django Rest Framework](#https://www.django-rest-framework.org/).
* PostgreSQL is used for data storage.
* JWT is used for authorization.
* Sending emails with SMTP.
* The application is containerized using Docker.
* The CI process is configured for the web application, namely the assembly, testing and evaluation of the test coverage.

### Business tasks
* Registration by username with confirmation of the email address.
* The ability to write posts to each registered user.
* The user can like the post. The author of the post will receive a system notification.
* The user can comment on posts. The author of the post will receive a system notification.
* The user can subscribe to a specific author. His posts will be the first in the search results. 
* Notifications about new subscribers and new posts from the author.


## Project structure
___
- `db` - Database configuration for Docker.
- `nginx` - NGINX configuration for Docker.
- `src` - Web-application.
  - `blog` - Everything related to posts, likes and subscribers.
  - `common` - Common overlay over the django rest framework for convenient operation.
  - `notifications` - Notification module for processing and displaying notifications.
  - `test_coverage` - Configuration and test coverage data.
  - `users` - User module, working with personal data, authorization and registration.
  - `.coveragerc` - Common configuration file for test coverage.
  - `.env.example` - Example of environment variables.
  - `.env.tests.template` - Template for generating environment variables in testing.
  - `entrypoint.sh` - Script for launching a web application in Docker.
  - `requirements.tests.txt` - Additional dependencies for testing the web application.
  - `requirements.txt` - Main dependencies of the web application.
  - `test.sh` - Test startup script.


## Description of environment variables
___
* `SECRET_KEY` - The django app secret key.
* `DEBUG` - Debug mode (0 or 1).
* `DB_NAME` - Database name.
* `DB_USER` - Database user.
* `DB_PASSWORD` - Password for database user.
* `DB_HOST` - Host on which the database is running.
* `DB_PORT` - Port on which the database is running.
* `JWT_ALGORITHM` - The algorithm from the PyJWT library which will be used to perform .
  signing/verification operations on tokens.
* `JWT_SIGNING_KEY` - The signing key that is used to sign the content of generated tokens.
* `PASSWORD_RESET_TIMEOUT` - Timeout for reset password.
* `CONFIRM_EMAIL_TIMEOUT` - Timeout for email confirmation.
* `PUBLIC_HOST` - Public host (client host).
* `EMAIL_HOST` - Host on which SMTP server is running.
* `EMAIL_PORT` - Port on which SMTP server is running.
* `EMAIL_HOST_USER` - SMTP server user.
* `EMAIL_HOST_PASSWORD` - Password for SMTP server user.
* `EMAIL_USE_TLS` - Whether to use a TLS (secure) connection when talking to the SMTP server.
* `EMAIL_USE_SSL` - Whether to use an implicit TLS (secure) connection when talking to the SMTP server.
* `DEFAULT_FROM_EMAIL` - Default email address for automated correspondence from the site.


## Launch
___

### Requirements
* Installed Python version `3.10` or higher.
* Installed packages:
  * `docker`
  * `docker-compose`


### Start local development server
1. Create a PostgreSQL database to use in the web application.
2. Create a `src/.env` file and specify environment variables by example `src/.env.example`.
3. Run `python3 --version` and make sure you have python version `3.10` or higher.
4. `python3 -m venv venv` - Creating a virtual python environment in the venv folder .
5. `source venv/bin/activate` - Activate the virtual environment.
6. `pip3 install -r requirements.txt` - Installing dependencies.
7. You are already to start!
   Run following command
  ```shell
  python manage.py runserver 0.0.0.0:8000
  ```
  Your local development server start on [http://0.0.0.0:8000](http://0.0.0.0:8000)


### Start in docker
1. Create a `src/.env` file and specify environment variables by example `src/.env.example`
2. Create a `db/.env` file and specify environment variables by example `db/.env.example`
3. You are already to start! 
Run following command
```shell
docker-compose up -d --build
```


## Licensing
___
See [LICENSE](LICENSE)
