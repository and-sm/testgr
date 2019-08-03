# Pull base image
FROM python:3.7.3

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV SECRET_KEY changemeonprod

# Set work directory
WORKDIR /code

# Install dependencies
RUN pip install --upgrade pip
RUN pip install django==2.2.1
RUN pip install django-anymail==6.0.1
RUN pip install channels==2.2.0
RUN pip install channels-redis==2.4.0
RUN pip install gunicorn==19.9.0
RUN pip install requests==2.22.0
RUN pip install mysqlclient==1.4.2.post1
RUN pip install redis==3.2.1
RUN pip install djangorestframework==3.10.2

# Copy project
COPY . /code/
