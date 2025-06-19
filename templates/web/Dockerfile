# Usamos una imagen base con PHP y Apache
FROM php:8.4-apache

# Habilitamos los módulos necesarios
RUN a2enmod rewrite ssl

# Instalamos extensiones de PHP necesarias
RUN docker-php-ext-install mysqli pdo pdo_mysql

# Copiamos la aplicación al contenedor
COPY . /var/www/html/

# Copiamos la configuración SSL (sin habilitar aún)
COPY ./default-ssl.conf /etc/apache2/sites-available/default-ssl.conf

# Activamos el sitio SSL pero no recargamos Apache todavía
RUN a2ensite default-ssl.conf

# Copiamos el entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponemos los puertos
EXPOSE 80 443

# Usamos el script como punto de entrada
ENTRYPOINT ["/entrypoint.sh"]
