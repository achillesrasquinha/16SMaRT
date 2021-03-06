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

CMD ["s3mart"]