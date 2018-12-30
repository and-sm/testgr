# Testgr
Web service which provides a monitoring and data store for nose2 or Pytest tests execution results.
# How it works
nose2 and Pytest have several methods for providing details of test runs and tests before and after test execution. **Testgr** service collects all data produced by nose2-rt or pytest-rt plugins and store it in the database.
If some test is running, passed, failed or skipped - plugin will send updated data to **Testgr** and user will see test execution status in real-time.

### Main page of Testgr. 

![Main page](https://i.imgur.com/S3oZKlw.png)

### Job page. 
There you can review status of your finished or live test execution. 

**Job in progress status:**
![Job page](https://i.imgur.com/gVfTZWW.png)

**Finished job:**
![Finished_job](https://i.imgur.com/QyVvzjn.png)

### Example of failed test:
![Failed test](https://i.imgur.com/Whr8kVG.png)

### Example of passed test:
![Passed test](https://i.imgur.com/6hg3tzQ.png)

### Search:
![Search](https://i.imgur.com/cOFdWjX.png)

### Job history:
![Job History](https://i.imgur.com/ba01FKI.png)

### Requirements:
**Testgr** was developed an tested using the following software:
* Python 3.6.5
* Django 2.1+
* Redis 4
* SQLite and MySQL 5.7.23
* Docker
* docker-compose

### HowTo deploy
Docker stack components:
* Nginx as reverse proxy
* Gunicorn
* Daphne
* Redis

You can set up **Testgr** rapidly using docker-compose:
```
git clone https://github.com/and-sm/testgr.git
cd testgr
```
Set up email configuration in **conf.env** file. Docker-compose stack use Mailgun as default backend. 
Configure **testgr/settings.py** file if more advanced email setup, MySQL or time settings needed.
```
docker-compose up -d --build
```
Open **Testgr** by using http://127.0.0.1 address.

How to stop **Testgr**:
```
docker-compose down
```

How to start **Testgr** again:
```
docker-compose up -d
```

### API plugins setup
Depending on your test framework (nose2 or pytest) you can choose [**nose2-rt**](https://github.com/and-sm/nose2rt) or [**pytest-rt**](https://github.com/and-sm/pytest-rt).
