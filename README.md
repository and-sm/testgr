# Testgr
Web service which provides all collected data from test executions, launched using nose2 and [nose2-rt](https://github.com/and-sm/nose2-rt) plugin.
# How it works
nose2 has several methods for providing details of test runs and tests before and after test execution. Testgr API collects all data produced by those methods and show it in user friendly manner.
Each nose2 execution generates a job object with list of tests. If some test is running, passed, failed or skipped - nose2-rt plugin sends updated data to Testgr and user can see test execution status in real-time.

### Main page of Testgr. 
In the current development phase it has two tables - "Job History" and "Running Jobs".

![Main page](https://i.imgur.com/fW1Jn4L.png)

### Job page. 
There you can observe status of your test execution. 

![Job page](https://i.imgur.com/Hdp9F05.png)

### Requirements:
**Testgr** was developed an tested using the following software:
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


