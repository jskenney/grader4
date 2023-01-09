# Grader Base Image, this is what will be used to run the software

# Edit the dns settings if Academy settings cause issues with networking
# vim /etc/docker/daemon.json and ADD
#{
#    "dns": ["10.1.74.10"]
#}

# To build run (make sure your user is in the docker group)
# docker build -t cs-base .

# Use the base ubuntu image as a starting point
FROM ubuntu:20.04

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
RUN apt-get update && apt-get -y install autoconf \
  automake \
  bison \
  build-essential \
  clang \
  clisp \
  cmake \
  cppcheck \
  curl \
  cython \
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
  mysql-client \
  nasm \
  ncurses-dev \
  default-jre \
  perl \
  pkg-config \
  python3-matplotlib \
  python3-nltk \
  python3-numpy \
  python3-ply \
  python3-scipy \
  python3-mysqldb \
  python3-mysql.connector \
  python3-dev \
  python3-lxml \
  python3-openssl \
  python3-pip \
  python3-setuptools \
  python3-networkx \
  python3-pandas \
  racket \
  tofrodos \
  unrar \
  unzip \
  yasm \
  zip \
  zlib1g-dev \
  openjdk-11-jdk \
  valgrind \
  spim \
  wamerican \
  chezscheme \
  chezscheme9.5-doc \
  chezscheme9.5 \
  junit4 \
&& rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip3 install --trusted-host pypi.python.org --upgrade setuptools
RUN pip3 install --trusted-host pypi.python.org -r Docker.python
