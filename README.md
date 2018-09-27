# Testgr
Web service which provides access to Pytest and nose2 test executions data, in connection with [nose2-rt](https://github.com/and-sm/nose2-rt) and [pytest-rt](https://github.com/and-sm/pytest-rt) plugins.
# How it works
nose2 and Pytest have several methods for providing details of test runs and tests before and after test execution. Testgr API collects all data produced by nose2-rt or pytest-rt plugins and show it in user friendly manner.
Each test execution generates a job object with list of tests. If some test is running, passed, failed or skipped - plugins will send updated data to Testgr and user can see test execution status in real-time.

### Main page of Testgr. 
In the current development phase it has two tables - "Last 10 jobs" and "Running jobs".

![Main page](https://i.imgur.com/THA0YOG.png)

### Job page. 
There you can observe status of your test execution. 

![Job page](https://i.imgur.com/lzPGk3V.png)

### Example of failed test:
![Failed test](https://i.imgur.com/Whr8kVG.png)

### Example of passed test:
![Passed test](https://i.imgur.com/6hg3tzQ.png)
### Requirements:
**Testgr** was developed an tested using the following software:
* Python 3.6.5
* Django 2.1.1
* MySQL 5.7.23

### Initial setup
1. Make folder for **Testgr**.
2. Download sources from GitHub and unpack inside the previously created folder.
3. [Configure](https://docs.djangoproject.com/en/2.1/topics/install/) Django and make migrations.

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
