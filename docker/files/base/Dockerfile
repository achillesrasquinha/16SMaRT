FROM  python:3.9

LABEL maintainer=achillesrasquinha@gmail.com

ENV TERM=xterm-256color \
    SRA_TOOLKIT_VERSION=3.0.0 \
    MOTHUR_VERSION=1.46.1 \
    VSEARCH_VERSION=2.18.0

RUN apt-get update && \
    # SRA Toolkit
    wget -nv https://ftp-trace.ncbi.nlm.nih.gov/sra/sdk/$SRA_TOOLKIT_VERSION/sratoolkit.$SRA_TOOLKIT_VERSION-ubuntu64.tar.gz -O $HOME/sra-toolkit.tar.gz && \
    tar xzvf $HOME/sra-toolkit.tar.gz -C $HOME && \
    cp -R $HOME/sratoolkit.$SRA_TOOLKIT_VERSION-ubuntu64/bin/* /usr/local/bin && \
    # SRA Toolkit configuration
    wget -nv https://raw.githubusercontent.com/ncbi/ncbi-vdb/2.11.2/libs/kfg/default.kfg -P $HOME/.ncbi && \
    export VDB_CONFIG=$HOME/.ncbi/default.kfg && \
    mkdir -p /usr/share/man/man1 && \
    apt-get install -y --no-install-recommends \
        openjdk-11-jre-headless \
        fastqc \
        r-base && \
    wget -nv https://github.com/mothur/mothur/releases/download/v${MOTHUR_VERSION}/Mothur.Ubuntu_20.zip -O $HOME/mothur.zip && \
    unzip $HOME/mothur.zip -d /mothur && \
    cp /mothur/mothur/mothur /usr/local/bin && \
    rm -rf $HOME/mothur* && \
    wget -nv https://github.com/torognes/vsearch/archive/v${VSEARCH_VERSION}.tar.gz -O $HOME/vsearch.tar.gz && \
    tar xzf $HOME/vsearch.tar.gz -C $HOME && \
    cd $HOME/vsearch-${VSEARCH_VERSION} && \
    ./autogen.sh && \
    ./configure CFLAGS="-O3" CXXFLAGS="-O3" && \
    make && \
    make install && \
    rm -rf \
        $HOME/sra-toolkit.tar.gz \
        $HOME/sratoolkit.$SRA_TOOLKIT_VERSION-ubuntu64 \
        $HOME/vsearch* \
        /var/lib/apt/lists/*