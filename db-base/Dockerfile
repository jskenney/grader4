# Grader Database Base Docker Image, this is what will be used to run the software

# BASE_CONFIG = {
#                'db-base':
#                          {'INSTANCES': 1,
#                           'DOCKER_CPUS': '121-122',
#                           'DOCKER_MEM_LIMIT': '16g',
#                           'USER': 0,
#                           'CAP_DROP': [],
#                           'CAP_ADD': [],
#                           'xxxTMPFS': {'/var/lib/mysql':'size=1G'}
#                          }
#               }

# Use the base ubuntu image as a starting point
FROM cs-base

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Hello!
MAINTAINER Jeff Kenney

# Set Environment variable
ENV DEBIAN_FRONTEND noninteractive

# Connect to the Patching Server for faster downloads
RUN echo "Acquire::http::Proxy \"http://apt.cs.usna.edu:3142\";" | tee /etc/apt/apt.conf.d/00aptproxy

# Install any required Ubuntu Packages
RUN apt-get update && apt-get -y install \
  r-base \
  r-base-dev \
  r-cran-rmysql \
  mysql-server \
&& rm -rf /var/lib/apt/lists/*

RUN service mysql start && mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -u root mysql && echo 'sql_mode = "STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION"' | tee -a /etc/mysql/mysql.conf.d/mysqld.cnf && echo "default-time-zone='US/Eastern'" | tee -a /etc/mysql/mysql.conf.d/mysqld.cnf && mysql -u root mysql -e "CREATE USER 'demo'@'%' IDENTIFIED BY 'demopw';" && mysql -u root mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'demo'@'%' WITH GRANT OPTION;" && mysql -u root mysql -e "CREATE DATABASE demo;"

RUN locale-gen en_US && update-locale LANG=en_US

RUN echo 'sql_mode = "STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION"' | tee -a /etc/mysql/mysql.conf.d/mysqld.cnf
RUN echo "default-storage-engine = InnoDB"     | tee -a /etc/mysql/mysql.conf.d/mysqld.cnf
RUN echo "innodb_checksum_algorithm = crc32"   | tee -a /etc/mysql/mysql.conf.d/mysqld.cnf
RUN echo "log_bin_trust_function_creators = 1" | tee -a /etc/mysql/mysql.conf.d/mysqld.cnf

# Change the root permissions to user 666 (submit grader)
RUN chown -R 666 /root
