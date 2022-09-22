FROM ghcr.io/achillesrasquinha/s3mart:base

ARG DEVELOPMENT=false

ENV S3MART_PATH=/s3mart \
    WORKSPACEDIR=/work

WORKDIR $S3MART_PATH

COPY ./docker/entrypoint.sh /entrypoint.sh

RUN python /r-setup.py /Rpackages.json

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . $S3MART_PATH

RUN cd $S3MART_PATH && \
    if [[ "${DEVELOPMENT}" ]]; then \
        pip install -r ./requirements-dev.txt; \
        python setup.py develop; \
    else \
        pip install -r ./requirements.txt; \
        python setup.py install; \
    fi 

WORKDIR $WORKSPACEDIR

ENTRYPOINT ["/entrypoint.sh"]

CMD ["s3mart"]