FROM  python:3.9

LABEL maintainer=achillesrasquinha@gmail.com

ENV GEOMEAT_PATH=/usr/local/src/geomeat

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        bash \
        git && \
    mkdir -p $GEOMEAT_PATH

COPY . $GEOMEAT_PATH
COPY ./docker/entrypoint.sh /entrypoint.sh

RUN pip install $GEOMEAT_PATH

WORKDIR $GEOMEAT_PATH

ENTRYPOINT ["/entrypoint.sh"]

CMD ["geomeat"]