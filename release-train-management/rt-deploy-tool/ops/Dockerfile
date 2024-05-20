# Please keep up to date with the new-version of Golang docker for builder
FROM golang:1.17.1-buster as base

#------------------------------
# artifact builder stage
#------------------------------
FROM base AS builder
WORKDIR /app

COPY go.mod ./
COPY go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -a -o deploy ./rt-deploy-tool/app

#------------------------------
# generate clean, final image for end users
#------------------------------
FROM gcr.io/distroless/base-debian10 as final
COPY --from=builder /app .

USER nonroot:nonroot

# executable
ENTRYPOINT [ "./deploy" ]
# arguments that can be overridden
# CMD [ "3", "300" ]