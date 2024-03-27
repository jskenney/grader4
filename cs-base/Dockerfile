# Grader Base Image, this is what will be used to run the software

# Edit the dns settings if Academy settings cause issues with networking
# vim /etc/docker/daemon.json and ADD
#{
#    "dns": ["10.1.74.10"]
#}

# To build run (make sure your user is in the docker group)
# docker build -t cs-base .

# Use the base ubuntu image as a starting point
FROM ubuntu:22.04

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
  software-properties-common \
  autoconf \
  automake \
  bison \
  build-essential \
  clang \
  clang-15 \
  clisp \
  cmake \
  cppcheck \
  curl \
  cython3 \
  expat \
  expect \
  flex \
  g++ \
  gcc-multilib \
  libbsd-dev \
  libcairo2-dev \
  libc++-dev \
  libc6-dev \
  libedit-dev \
  libexpat1-dev \
  libgmp3-dev \
  libgtk-3-dev \
  libicu-dev \
  liblzo2-dev \
  libpng-dev \
  libreadline-dev \
  libssl-dev \
  libtool \
  libxml2-dev \
  llvm \
  llvm-15 \
  locales \
  mysql-client \
  nasm \
  ncurses-dev \
  default-jre \
  perl \
  pkg-config \
  r-base \
  r-base-dev \
  r-cran-rmysql \
  python3-mysqldb \
  python3-mysql.connector \
  python3-dev \
  python3-graphviz \
  python3-pip \
  python3-openssl \
  python3-setuptools \
  racket \
  tofrodos \
  unrar \
  unzip \
  yasm \
  zip \
  zlib1g-dev \
  openjdk-11-jdk \
  openjdk-17-jdk \
  maven \
  valgrind \
  spim \
  wamerican \
  chezscheme \
  chezscheme-doc \
  junit4 \
&& rm -rf /var/lib/apt/lists/*

RUN locale-gen en_US && update-locale LANG=en_US

# Apparently we need to worry about certs now
RUN echo "Options = UnsafeLegacyRenegotiation" | tee -a /etc/ssl/openssl.cnf
RUN curl -k http://apt.cs.usna.edu/ssl/install-ssl-system-docker.sh -o /tmp/install-ssl-system-docker.sh && bash /tmp/install-ssl-system-docker.sh

# For Dan's Class
RUN apt-add-repository -y ppa:deadsnakes/ppa && apt-get update && apt-get -y install python3.11 python3.11-venv python3.12 python3.12-venv

# Install any needed packages specified in requirements.txt
RUN pip3 install --trusted-host pypi.python.org --upgrade setuptools
RUN pip3 install --trusted-host pypi.python.org -r python.requirements.txt

# Install software for maven
RUN bash make_m2.sh

# Change the root permissions to user 666 (submit grader)
RUN chown -R 666 /root

# Add user submit with homedir /root and uid 666
RUN useradd -d /root -s /bin/bash -u 666 submit
