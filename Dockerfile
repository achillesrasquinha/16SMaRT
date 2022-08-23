

FROM  python:3.7-alpine

ARG DEVELOPMENT=false

LABEL maintainer=achillesrasquinha@gmail.com

ENV S3MART_PATH=/usr/local/src/s3mart

RUN apk add --no-cache \
        bash \
        git \
    && mkdir -p $S3MART_PATH

COPY . $S3MART_PATH
COPY ./docker/entrypoint.sh /entrypoint
RUN sed -i 's/\r//' /entrypoint \
	&& chmod +x /entrypoint

WORKDIR $S3MART_PATH

RUN if [[ "${DEVELOPMENT}" ]]; then \
        pip install -r ./requirements-dev.txt; \
        python setup.py develop; \
    else \
        pip install -r ./requirements.txt; \
        python setup.py install; \
    fi

ENTRYPOINT ["/entrypoint"]

CMD ["s3mart"]