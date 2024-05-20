FROM python:3.10.6-slim

LABEL description "Release Qualification Tools"
ARG GH_PAT

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/root/.local/bin:/root/google-cloud-sdk/bin:$PATH"

COPY . /rq

RUN pip install -U pip \
    && apt-get update \
    && apt install -y --no-install-recommends vim curl netcat git \
    && curl -sSL https://install.python-poetry.org | python - --version 1.7.1 \
    && cd /rq \
    && echo 'echo $GH_PAT' > ~/.git-askpass && chmod +x ~/.git-askpass\
    && git config --global core.askPass ~/.git-askpass \
    && git config --global url."https://token@github.com/".insteadOf "https://github.com/" \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi && \
    GHCLI_VERSION=$(curl -sX GET "https://api.github.com/repos/cli/cli/releases" \
      | awk '/tag_name/{print $4;exit}' FS='[""]' | awk '{print substr($1,2); }') && \
    curl -o \
        /tmp/ghcli.tar.gz -L \
        "https://github.com/cli/cli/releases/download/v${GHCLI_VERSION}/gh_${GHCLI_VERSION}_linux_amd64.tar.gz" && \
    tar -C /usr/bin --strip-components=2 -zxf /tmp/ghcli.tar.gz gh_${GHCLI_VERSION}_linux_amd64/bin/gh && \
    rm -rf ~/.askpass

COPY certs/letsencrypt-stg-root-x1.crt /usr/local/share/ca-certificates/letsencrypt-stg-root-x1.crt
COPY certs/letsencrypt-stg-root-x2.crt /usr/local/share/ca-certificates/letsencrypt-stg-root-x2.crt

RUN update-ca-certificates

RUN curl -sSL https://sdk.cloud.google.com | /bin/bash

WORKDIR /rq

# keep running
ENTRYPOINT ["tail", "-f", "/dev/null"]

