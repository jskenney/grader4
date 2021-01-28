# Grader Base Image, this is what will be used to run the software

# Edit the dns settings if Academy settings cause issues with networking
# vim /etc/docker/daemon.json and ADD
#{
#    "dns": ["10.1.74.10"]
#}

# To build run (make sure your user is in the docker group)
# docker build -t cs-base .

# Use the base ubuntu image as a starting point
FROM ubuntu:18.04

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Hello!
MAINTAINER Jeff Kenney

# Set Environment variable
ENV DEBIAN_FRONTEND noninteractive

# Install any required Ubuntu Packages
#   mono-complete \
#   mono-devel \
#coq \
#coq-theories \
#  beef \
#  clojure1.8 \
#   elixir \
#gtk-sharp2 \
#erlang \
#gforth \
#gfortran \
#ghc \
#gnat-8 \
#gobjc \
#golang \
#gprolog \
#graphviz \
#haskell-platform \
#javahelp2 \
#jruby \
#libavcodec-dev \
#libcanberra-gtk-module \
#libgl1-mesa-dev \
#libqt4-dev \
#lua5.3 \
#maven \
#mpi \
#mpich \
#mysql-client-5.7 \
#php \
#php-mysqlnd \
#php7.2-cli \
#php7.2-sqlite3 \
#racket \
#ruby \
#rust-gdb \
#rustc \
#scala \
#scamper \
#scapy \
#socat \
#sqlite3 \
#traceroute \
#libmpich-dev \
#libmpich12 \
#ant \
#ant-optional \
#  enscript \
#  gdb \
#libsqlite3-dev \
#valgrind \
#  libacl1-dev \
#  libfdk-aac-dev \
#  python-pyorbit \
#python3-mysql.connector \
#python3-mysqldb \
#python-mysql.connector \
#python-mysqldb \
#  python-telepathy \
#  python-vte \
#  git \
#  gnuplot \
#  imagemagick \

RUN apt-get update && apt-get -y install autoconf \
  automake \
  bison \
  build-essential \
  clang \
  clisp \
  cmake \
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
  nasm \
  ncurses-dev \
  default-jre \
  perl \
  pkg-config \
  python-dev \
  python-lxml \
  python-matplotlib \
  python-nltk \
  python-numpy \
  python-openssl \
  python-pip \
  python-ply \
  python-scipy \
  python-setuptools \
  python-mysqldb \
  python-mysql.connector \
  python2.7-dev \
  python3-mysqldb \
  python3-mysql.connector \
  python3-dev \
  python3-lxml \
  python3-openssl \
  python3-pip \
  python3-setuptools \
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
&& rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r Docker.python
RUN pip3 install --trusted-host pypi.python.org -r Docker.python
