# Pull base image
FROM python:3.6

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV SECRET_KEY changemeonprod

# Set work directory
WORKDIR /code

# Install dependencies
RUN pip install --upgrade pip
RUN pip install django==2.1.3
RUN pip install django-anymail==4.3
RUN pip install channels==2.1.5
RUN pip install channels-redis==2.3.1
RUN pip install gunicorn==19.9.0
RUN pip install requests==2.20.0

# Copy project
COPY . /code/
