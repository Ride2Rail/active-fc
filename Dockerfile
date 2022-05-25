FROM python:3.8

ENV APP_NAME=active.py
COPY /code/"$APP_NAME" /code/"$APP_NAME"
COPY /code/active.conf /code/active.conf
COPY /code/utils_active.py /code/utils_active.py

WORKDIR /code


ENV FLASK_APP="$APP_NAME"
ENV FLASK_RUN_HOST=0.0.0.0

RUN pip3 install --no-cache-dir pip==22.1.1

COPY requirements.txt requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5005

CMD ["flask", "run"]
