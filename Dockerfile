FROM python:3.11.0-bullseye

ARG ARG_ENC_KEY
ARG ARG_AWS_DYNAMO_ACCESS_KEY_ID
ARG ARG_AWS_DYNAMO_SECRET_ACCESS_KEY
ARG ARG_SVC_UN
ARG ARG_SVC_PW

ENV AWS_DEFAULT_REGION="us-west-2"

ENV ENC_KEY=$ARG_ENC_KEY
ENV AWS_DYNAMO_ACCESS_KEY_ID=$ARG_AWS_DYNAMO_ACCESS_KEY_ID
ENV AWS_DYNAMO_SECRET_ACCESS_KEY=$ARG_AWS_DYNAMO_SECRET_ACCESS_KEY
ENV SVC_UN=$ARG_SVC_UN
ENV SVC_PW=$ARG_SVC_PW

WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY ./app /code/app
COPY ./sql /code/sql

# 
#CMD ["hypercorn", "app.main:app", "--bind", "0.0.0.0:443"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]