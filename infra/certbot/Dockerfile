FROM certbot/certbot

ARG DOMAIN_NAME

COPY certbot_renew.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/certbot_renew.sh

RUN echo "0 0 1 */2 * /usr/local/bin/certbot_renew.sh" | crontab -
