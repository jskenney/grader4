# Grader Base Image, this is what will be used to run the software

# Edit the dns settings if Academy settings cause issues with networking
# vim /etc/docker/daemon.json and ADD
#{
#    "dns": ["10.1.74.10"]
#}

# To build run (make sure your user is in the docker group)
# docker build -t cs-base .

# Use the base ubuntu image as a starting point
FROM ubuntu

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Hello!
MAINTAINER Jeff Kenney

# Set Environment variable
ENV DEBIAN_FRONTEND noninteractive

# Install any required Ubuntu Packages
RUN apt-get update
RUN apt-get -y install build-essential pkg-config libc6-dev libssl-dev libexpat1-dev yasm bison gdb autoconf automake cmake flex bison expat expect g++ ncurses-dev clang libreadline-dev libc++-dev valgrind libbsd-dev imagemagick enscript gnuplot libtool libedit-dev libbsd-dev libgmp3-dev zlib1g-dev libacl1-dev perl
RUN apt-get -y install python2.7-dev python3-dev python-setuptools python3-setuptools python-pip python3-pip python-dev python-nltk python-ply python-pyorbit python-telepathy python-vte python-numpy python-scipy python-matplotlib cython
RUN apt-get -y install curl unzip zip unrar tofrodos
RUN apt-get -y install g++ ncurses-dev gdb build-essential enscript gnuplot clang
RUN apt-get -y install openjdk-11-jre javahelp2
RUN apt-get -y install g++ ncurses-dev gdb build-essential enscript gnuplot clang racket gfortran nasm cython erlang gforth golang ghc ant ant-optional clisp clojure1.8 lua5.3 gobjc ruby jruby scala rustc rust-gdb
RUN apt-get -y install beef libicu-dev elixir coq coq-doc coq-theories gprolog gprolog-doc tk clang rustc rust-doc libpng-dev mono-complete haskell-platform haskell-platform-doc tcl ruby scala scala-doc gnat-8 gnat-8-doc gforth gfortran gfortran-doc
RUN apt-get -y install maven ant git emacs
RUN apt-get -y install libacl1-dev curl
RUN apt-get -y install graphviz
RUN apt-get -y install python3-lxml python-lxml
RUN apt-get -y install python-openssl python3-openssl
RUN apt-get clean

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r Docker.python
RUN pip3 install --trusted-host pypi.python.org -r Docker.python
