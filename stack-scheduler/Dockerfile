# FROM golang:1.18.0-alpine3.15 as build
FROM --platform=linux/arm64 golang:1.18.0-alpine3.15 as build
LABEL stage=builder

# RUN apk update && apk add curl git
RUN apk update && apk add git

WORKDIR /go
COPY . .

# write commit version
RUN sed -i "s/\"xxx\"/$(git log --format=\"%H\" -n 1)/" src/scheduler/config/config.go

# build
RUN cd src/scheduler && go build -o ../../scheduler

FROM alpine:3.15.0

WORKDIR /home/app
COPY --from=build /go/scheduler .

RUN mkdir -p /data

# set permissions
# RUN addgroup -S app && adduser -S -g app app
# RUN chown -R app:app ./
# USER app

EXPOSE 18080
# pprof
# EXPOSE 16060 

CMD ["./scheduler"]
