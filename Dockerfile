FROM python:3.9
RUN apt-get update && apt-get -y install cron
WORKDIR /app
COPY crontab /etc/cron.d/crontab
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY main.py /app/main.py
RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

# run crond as main process of container
CMD ["cron", "-f"]