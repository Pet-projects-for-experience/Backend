FROM certbot/certbot

ARG DOMAIN_NAME

COPY fullchain.pem letsencrypt/live/${DOMAIN_NAME}/fullchain.pem

COPY privkey.pem letsencrypt/live/${DOMAIN_NAME}/privkey.pem
