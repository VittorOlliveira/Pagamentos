# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.6

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

# create root directory for our project in the container
RUN mkdir /api_pagamentos

# Set the working directory to /api_pagamentos
WORKDIR /api_pagamentos

# Copy the current directory contents into the container at /api_pagamentos
ADD . /api_pagamentos/

# Install any needed packages specified in requirements.txt
RUN apt-get update
RUN pip install -r requirements.txt


# port where the Django app runs  
EXPOSE 8000  

# start server  
CMD python manage.py runserver 0.0.0.0:8000