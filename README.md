# Testgr
Web service which provides monitoring and data store for nose2 or Pytest tests execution results.
# How it works
nose2 and Pytest frameworks have several methods for providing details of test runs and tests before and after test execution. To connect **Testgr** and these frameworks - you need to use [**nose2-rt**](https://github.com/and-sm/nose2rt) or [**pytest-rt**](https://github.com/and-sm/pytest-rt) plugins (depending on your framework).
 **Testgr** service collects all data produced by plugins and store it in the database.
If some test is in running, passed, failed or skipped state - plugin will send updated data to **Testgr** and user will see test execution status in real-time.

### Main page of Testgr. 

![Main page](https://i.lensdump.com/i/WzoouF.png)

### Job page. 
There you can review status of your finished or live test execution. 

**Job in progress status:**
![Job page](https://i.lensdump.com/i/iAbfNC.png)

**Finished job:**
![Finished_job](https://i.lensdump.com/i/WzonOT.png)

### Example of finished test:
![Failed test](https://i.lensdump.com/i/iAbUW5.png)

### Search:
![Search](https://i.lensdump.com/i/WzoMZ7.png)


### Requirements:
**Testgr** was developed an tested using the following software:
* Python 3.7
* Django 2.2
* Redis 4
* SQLite and MySQL 5.7
* Docker
* docker-compose

### API plugins setup
Depending on your test framework (nose2 or pytest) you can choose [**nose2-rt**](https://github.com/and-sm/nose2rt) or [**pytest-rt**](https://github.com/and-sm/pytest-rt).


### Deploy
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




