# Documentation

Python version = 3.6

Django version = 2.1


## Run project in local
### Backend
Install virtualenv and Virtualenvwrapper

```bash
$: python -m pip install --upgrade pip
$: pip Install VirtualEnv
$: pip install VirtualEnvWrapper-win
$: mkvirtualenv easywork.me -p=python3
$: workon easywork.me
```

### setup & install project

```bash
$: git clone git@gitlab.com:bmarketing/easywork.django.git
$: mkvirtualenv easywork
$: cd easywork.django
$: pip install -r requirements.txt
$: # https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient
$: wget https://download.lfd.uci.edu/pythonlibs/h2ufg7oq/mysqlclient-1.3.13-cp36-cp36m-win_amd64.whl
$: pip install mysqlclient-1.3.13-cp36-cp36m-win_amd64.whl
```

Create the local configuration file (local.py) from template

```bash
$: cp easywork/easywork/app/local_example.py easywork/easywork/app/local.py
```

Set settings variable

```bash
$:export DJANGO_SETTINGS_MODULE='easywork.app.settings'
```

Migrate DB and Run server
​    
```bash
$: cd easywork 
$: python manage.py makemigrations app
$: python manage.py migrate
$: python manage.py runserver 0.0.0.0:8000 --settings=easywork.app.settings
```


​    

### Frontend
Once we have installed everything and have the backend running

```bash
$: workon easywork
$: python manage.py runserver 0.0.0.0:8001 --settings=frontend.settings
```



Now, the frontend can be opened in the following url:
**http://lcoalhost:8001**

The backend is running here: **http://lcoalhost:8000**


## Superuser dashboard
Once the server is running, it's possible to open the CRUD dashboard.

First, it's necessary to create a superuser:

```bash
$: python mange.py createsuperuser
```

After that, it's possible to enter via the following url: **http://localhost:8000/admin**

## API documentation
The documentation is not detailed because we're not following standards and it's auto-generated.
​    **http://localhost:8000/docs**



## Navigate the project
We've 3 modules.
- API
- API documentation
 URL: http://localhost:8000/docs
    This documentation is not very complete because we had to hardcode the views to match the odl project API syntax.
    Ideally we'll migrate to ModelViews using DRF and update the frontend calls.
- Admin pannel

First, create an admin user

```bash
$: python manage.py createsuperuser
```

Now access viathe URL: http://localhost:8000/admin

## Unit tests

```bash
$: python manage.py test
```