# Testgr
Web service which provides access to Pytest and nose2 test executions data, in connection with [nose2-rt](https://github.com/and-sm/nose2-rt) and [pytest-rt](https://github.com/and-sm/pytest-rt) plugins.
# How it works
nose2 and Pytest have several methods for providing details of test runs and tests before and after test execution. Testgr API collects all data produced by nose2-rt or pytest-rt plugins and show it in user friendly manner.
Each test execution generates a job object with list of tests. If some test is running, passed, failed or skipped - plugins will send updated data to Testgr and user can see test execution status in real-time.

### Main page of Testgr. 
In the current development phase it has two tables - "Last 10 jobs" and "Running jobs".

![Main page](https://i.imgur.com/sR3SMxF.png)

### Job page. 
There you can observe status of your test execution. 

![Job page](https://i.imgur.com/Rlhrep5.png)

### Example of failed test:
![Failed test](https://i.imgur.com/Whr8kVG.png)

### Example of passed test:
![Passed test](https://i.imgur.com/6hg3tzQ.png)

### Job history:
![Job history](https://i.imgur.com/0hg7Rh8.png)
### Requirements:
**Testgr** was developed an tested using the following software:
* Python 3.6.5
* Django 2.1.2
* Redis 4
* SQLite and MySQL 5.7.23
* Docker
* docker-compose

### HowTo deploy
Docker stack is build on the next components:
* Nginx as reverse proxy
* Gunicorn
* Daphne
* Redis

You can set up **Testgr** rapidly using docker-compose:
```
git clone https://github.com/and-sm/testgr.git
cd testgr
docker-compose up -d --build
```
Open **Testgr** by using http://127.0.0.1 address.

Stop **Testgr**:
```
docker-compose down
```

Start **Testgr** again:
```
docker-compose up -d
```

Also basic setup can be found in the "docker-simple" folder. It will deploy Django's runserver only.

### nose2-rt setup

In nose2.cfg find **[rt]** section and configure "endpoint" setting

Example: 
```
[unittest]
plugins = nose2.plugins.nose2-rt.rt

[rt]
endpoint = http://127.0.0.1/loader
show_errors = True
```

### pytest-rt setup

In conftest.py enable following settings:
```
pytest_plugins = "pytest_rt"
endpoint = "http://127.0.0.1/loader"
show_errors = True
```
