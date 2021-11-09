FROM  python:3.9

LABEL maintainer=achillesrasquinha@gmail.com

ENV TERM=xterm-256color \
    SRA_TOOLKIT_VERSION=2.9.6 \
    VSEARCH_VERSION=2.18.0 \
    GEOMEAT_PATH=/usr/local/src/geomeat

RUN apt-get --allow-releaseinfo-change update && \
    # SRA Toolkit
    wget -nv https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/$SRA_TOOLKIT_VERSION/sratoolkit.$SRA_TOOLKIT_VERSION-ubuntu64.tar.gz -O $HOME/sra-toolkit.tar.gz && \
    tar xzvf $HOME/sra-toolkit.tar.gz -C $HOME && \
    cp -R $HOME/sratoolkit.$SRA_TOOLKIT_VERSION-ubuntu64/bin/* /usr/local/bin && \
    # SRA Toolkit configuration
    wget -nv https://raw.githubusercontent.com/ncbi/ncbi-vdb/master/libs/kfg/default.kfg -P $HOME/.ncbi && \
    export VDB_CONFIG=$HOME/.ncbi/default.kfg && \
    # FastQC
    mkdir -p /usr/share/man/man1 && \
    apt-get install -y --no-install-recommends \
        openjdk-11-jre-headless \
        fastqc \
        mothur && \
    wget -nv https://github.com/torognes/vsearch/archive/v${VSEARCH_VERSION}.tar.gz -O $HOME/vsearch.tar.gz && \
    tar xzf $HOME/vsearch.tar.gz -C $HOME && \
    cd $HOME/vsearch-${VSEARCH_VERSION} && \
    ./autogen.sh && \
    ./configure CFLAGS="-O3" CXXFLAGS="-O3" && \
    make && \
    make install && \
    mkdir -p $GEOMEAT_PATH && \
    rm -rf \
        $HOME/sra-toolkit.tar.gz \
        $HOME/sratoolkit.$SRA_TOOLKIT_VERSION-ubuntu64 \
        $HOME/vsearch*

COPY ./docker/entrypoint.sh /entrypoint.sh

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY . $GEOMEAT_PATH

WORKDIR $GEOMEAT_PATH

RUN pip install -r /requirements.txt && \
    python setup.py install

ENTRYPOINT ["/entrypoint.sh"]

CMD ["geomeat"]