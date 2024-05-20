---
title: "Containerization"
linkTitle: "Containerization"
weight: 5
date: 2021-12-17
description: >
  Policies and recommendations for  containerization 
---


## Building with `ko`

Prefer using [ko](https://github.com/google/ko) if you have simple Dockerfile and does not have
OS dependencies 

[thoughts about ko from Google](https://cloud.google.com/blog/topics/developers-practitioners/ship-your-go-applications-faster-cloud-run-ko)

How to run - ko publish will build container and push it to specified registry

{{% alert %}}
Please note that with ko it's not required to have Docker installed on machine
{{% /alert %}}

``` bash
export KO_DOCKER_REPO=gcr.io/${PROJECT_ID}
ko publish ./worker --tags ${TAG} -B
```

## Building with `Dockerfile`

Opinionated dockerfile example


 > All [Tini](https://github.com/krallin/tini) does is spawn a single child (Tini is meant to be run in a container), and wait for it to exit all the while reaping zombies and performing signal forwarding.

``` Dockerfile
FROM golang:1.17.3-alpine3.14 as base

ENV TINI_VERSION v0.19.0
ENV USER webhook
ENV UID 10001

RUN apk update && \
    apk add --no-cache \
        git \
        ca-certificates \
        tzdata && \
    update-ca-certificates

RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    "${USER}"

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini-static /usr/local/bin/tini

RUN chmod +x /usr/local/bin/tini

COPY --from=amd64/busybox:1.31.0 /bin/busybox /bin/busybox
COPY --from=amd64/busybox:1.31.0 /bin/busybox /bin/sh

WORKDIR /webhook

COPY . /webhook

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -o /go/bin/webhook \
    github.com/takeoff-com/webhook-provider/app/services/webhook-api && \
    rm /go/bin/webhook

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go get \
    github.com/go-delve/delve/cmd/dlv

RUN rm -rf /webhook

FROM base as builder

WORKDIR /webhook

COPY . /webhook

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
    go build -o /go/bin/webhook \
    github.com/takeoff-com/webhook-provider/app/services/webhook-api

FROM scratch as final

COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo
COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group
COPY --chown=webhook --from=builder /go/bin/webhook /bin/webhook
COPY --chown=webhook --from=builder /go/bin/dlv /bin/dlv
COPY --chown=webhook --from=builder /usr/local/bin/tini /bin/tini
COPY --chown=webhook --from=builder /webhook/app/services/webhook-api/docs/swagger.yaml ./app/services/webhook-api/docs/swagger.yaml
COPY --from=amd64/busybox:1.31.0 /bin/busybox /bin/busybox
COPY --from=amd64/busybox:1.31.0 /bin/busybox /bin/sh
RUN /bin/busybox --install -s /bin
RUN ln -fs /bin/busybox /bin/sh
COPY --from=builder /tmp /tmp

RUN chmod -R 0777 /tmp

USER webhook:webhook

EXPOSE 8080

ENTRYPOINT ["/bin/tini", "--", "/bin/webhook"]
```
