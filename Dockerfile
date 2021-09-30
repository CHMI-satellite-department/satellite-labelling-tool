# syntax=docker/dockerfile:1
FROM python:3.8-slim

WORKDIR /app

# --- setup proxy
ARG HTTP_PROXY
ARG HTTPS_PROXY

RUN test -z $HTTP_PROXY || echo 'Acquire::http::Proxy "'${HTTP_PROXY}'";' >> /etc/apt/apt.conf && \
    test -z $HTTPS_PROXY || echo 'Acquire::https::Proxy "'${HTTPS_PROXY}'";' >> /etc/apt/apt.conf

# --- install environment
RUN apt-get update && apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

# invalidate docker cache from here if a unique --build-arg CACHE_DATE is used
# Ex: docker build --build-arg CACHE_DATE=$(date +%Y-%m-%d:%H:%M:%S) ...
ARG CACHE_DATE=not_a_date

RUN pip3 install --no-cache-dir -r requirements.txt

# --- switch user
RUN groupadd -r slt && \
    useradd -rm -g slt slt && \
    chown slt:slt -R /app

USER slt

# --- install application
COPY --chown=slt:slt . ./slt/
RUN chmod +x ./slt/bin/*
ENV PATH="/app/slt/bin:${PATH}"
ENV PYTHONPATH="/app/slt:${PYTHONPATH}"

# --- setup entrypoint
ENTRYPOINT ["/app/slt/bin/slt"]
