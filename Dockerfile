<<<<<<< HEAD
<<<<<<< HEAD
FROM ghcr.io/achillesrasquinha/s3mart:base

ENV S3MART_PATH=/usr/local/src/s3mart \
    WORKSPACEDIR=/work

WORKDIR $S3MART_PATH

COPY ./docker/entrypoint.sh /entrypoint.sh

COPY ./Rpackages.json /Rpackages.json
COPY ./script/r-setup.py /r-setup.py
RUN pip install rpy2 && \
    python /r-setup.py /Rpackages.json

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . $S3MART_PATH

RUN cd $S3MART_PATH && \
    pip install -r /requirements.txt && \
    python setup.py install 

WORKDIR $WORKSPACEDIR

ENTRYPOINT ["/entrypoint.sh"]
=======
=======
>>>>>>> template/master


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
<<<<<<< HEAD
>>>>>>> template/master
=======
>>>>>>> template/master

CMD ["s3mart"]