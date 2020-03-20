# Get the last version of nginx
FROM nginx

# Clean the default config and set a custom config
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx

# Add extra configs for the project
COPY no_ssl_config /etc/nginx/sites-enabled/