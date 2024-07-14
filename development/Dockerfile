FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ARG NETBOX_VERSION

RUN apt-get update \
    && apt-get install -y --no-install-recommends git postgresql-client libpq-dev gcc build-essential \
    && pip install --upgrade pip

# Install NetBox
RUN mkdir -p /opt/netbox \
    && git clone --single-branch --branch=${NETBOX_VERSION} https://github.com/netbox-community/netbox.git /opt/netbox/ \
    && pip install -r /opt/netbox/requirements.txt

# Install Netbox Plugin
COPY . /plugin/netbox_config_diff
RUN pip install --editable /plugin/netbox_config_diff[test]

WORKDIR /opt/netbox/netbox/
