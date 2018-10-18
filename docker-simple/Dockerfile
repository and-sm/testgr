# Pull base image
FROM python:3.6

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code

# Install dependencies
RUN pip install --upgrade pip
RUN pip install django==2.1.2
RUN pip install channels==2.1.3
RUN pip install channels-redis==2.3.0

# Copy project
COPY . /code/
