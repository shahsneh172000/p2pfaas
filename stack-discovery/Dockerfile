# FROM golang:1.17.6-alpine3.15 as build
FROM --platform=linux/arm64 golang:1.17.6-alpine3.15 as build
LABEL stage=builder

RUN apk update && apk add build-base

WORKDIR /go
COPY . .

# build
RUN cd src/discovery && go build -o ../../discovery

FROM alpine:3.15.0

LABEL org.label-schema.license="MIT" \
    org.label-schema.vcs-url="https://gitlab.com/p2p-faas/stack-discovery" \
    org.label-schema.vcs-type="Git" \
    org.label-schema.name="p2p-fog/discovery" \
    org.label-schema.vendor="gabrielepmattia" \
    org.label-schema.docker.schema-version="1.0"

WORKDIR /home/app
COPY --from=build /go/discovery .

RUN mkdir -p /data

# set permissions
# RUN addgroup -S app && adduser -S -g app app
# RUN chown -R app:app ./
# USER app

EXPOSE 19000

CMD ["./discovery"]