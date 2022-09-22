FROM ghcr.io/achillesrasquinha/s3mart:base

ARG DEVELOPMENT=false

ENV S3MART_PATH=/s3mart \
    WORKSPACEDIR=/work

SHELL ["/bin/bash", "-c"]

WORKDIR $S3MART_PATH

COPY ./docker/entrypoint.sh /entrypoint.sh

COPY ./Rpackages.json /Rpackages.json
RUN python /r-setup.py /Rpackages.json

COPY ./requirements-dev.txt /requirements-dev.txt
COPY ./requirements.txt /requirements.txt

RUN if [[ "${DEVELOPMENT}" ]]; then \
        pip install -r /requirements-dev.txt; \
    else \
        pip install -r /requirements.txt; \
    fi

COPY . $S3MART_PATH

RUN cd $S3MART_PATH && \
    if [[ "${DEVELOPMENT}" ]]; then \
        python setup.py develop; \
    else \
        python setup.py install; \
    fi 

WORKDIR $WORKSPACEDIR

ENTRYPOINT ["/entrypoint.sh"]

CMD ["s3mart"]