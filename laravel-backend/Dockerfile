FROM php:8.2-fpm-alpine

WORKDIR /var/www/html

# Install PHP dependencies and extensions
RUN apk add --no-cache \
    nginx \
    mysql-client \
    git \
    curl \
    supervisor \
    nodejs \
    npm \
    && docker-php-ext-install pdo_mysql opcache \
    && docker-php-ext-enable opcache

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

COPY . .

RUN composer install --no-dev --optimize-autoloader

# Setup Nginx
COPY docker/nginx/default.conf /etc/nginx/http.d/default.conf

# Setup Supervisor to run PHP-FPM and Nginx
COPY docker/supervisor/conf.d/supervisord.conf /etc/supervisord.conf

# Give correct permissions for storage directory
RUN chown -R www-data:www-data storage bootstrap/cache \
    && chmod -R 775 storage bootstrap/cache

EXPOSE 80

CMD ["supervisord", "-c", "/etc/supervisord.conf"]
