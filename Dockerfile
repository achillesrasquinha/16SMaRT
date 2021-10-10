FROM  python:3.9

LABEL maintainer=achillesrasquinha@gmail.com

ENV SRA_TOOLKIT_VERSION=2.9.6 \
    GEOMEAT_PATH=/usr/local/src/geomeat

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        bash \
        git && \
    mkdir -p $GEOMEAT_PATH && \
    # SRA Toolkit configuration
    wget -nv https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/$SRA_TOOLKIT_VERSION/sratoolkit.$SRA_TOOLKIT_VERSION-ubuntu64.tar.gz -O $HOME/sra-toolkit.tar.gz && \
    tar xzvf $HOME/sra-toolkit.tar.gz -C $HOME && \
    cp -R $HOME/sratoolkit.$SRA_TOOLKIT_VERSION-ubuntu64/bin/* /usr/local/bin && \
    # SRA Toolkit configuration
    wget -nv https://raw.githubusercontent.com/ncbi/ncbi-vdb/master/libs/kfg/default.kfg -P $HOME/.ncbi && \
    export VDB_CONFIG=$HOME/.ncbi/default.kfg && \
    # FastQC
    apt-get install -y --no-install-recommends fastqc && \
    rm -rf \
        $HOME/sra-toolkit.tar.gz \
        $HOME/sratoolkit.$SRA_TOOLKIT_VERSION-ubuntu64

COPY . $GEOMEAT_PATH
COPY ./docker/entrypoint.sh /entrypoint.sh

WORKDIR $GEOMEAT_PATH

RUN pip install -r ./requirements.txt && \
    python setup.py install    

ENTRYPOINT ["/entrypoint.sh"]

CMD ["geomeat"]