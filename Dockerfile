FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

# Create an empty folder on our docker image called /app
RUN mkdir /app
# We then change the default working directory to that /app we created
WORKDIR /app
# It then copies the app folder from our local machine into the app folder of our docker image
COPY ./app /app

RUN adduser -D user
USER user