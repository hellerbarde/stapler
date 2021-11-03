FROM debian:bullseye-slim
MAINTAINER himself@derjohn.de
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install Packages
RUN apt-get update \
&& apt-get install -y \
  git \
  libffi-dev \
  libffi7 \
  rustc \
  python3-pip \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

RUN pip3 install poetry PyPDF2
RUN git clone https://github.com/hellerbarde/stapler.git /tmp/stapler
RUN cd /tmp/stapler \
&& poetry install \
&& poetry run tox -e py \
&& poetry build \
&& pip3 install dist/stapler-1.0.0.tar.gz

