FROM certbot/certbot

RUN apt-get update && apt-get install -y cron

ARG DOMAIN_NAME

COPY certbot_cron /etc/cron.d/certbot_cron

CMD ["cron", "-f"]
