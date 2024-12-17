FROM ubuntu:latest
LABEL authors="rodin"

ENTRYPOINT ["top", "-b"]