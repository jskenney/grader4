# Grader Base Image, this is what will be used to run the software

# Edit the dns settings if Academy settings cause issues with networking
# vim /etc/docker/daemon.json and ADD
#{
#    "dns": ["10.1.74.10"]
#}

# To build run (make sure your user is in the docker group)
# docker build -t cs-base .

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

# Install any needed packages specified in requirements.txt
#RUN pip3 install --trusted-host pypi.python.org --upgrade setuptools
#RUN pip3 install --trusted-host pypi.python.org -r python.requirements.txt

# Change the root permissions to user 666 (submit grader)
RUN chown -R 666 /root
