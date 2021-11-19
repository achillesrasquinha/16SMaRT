<div align="center">
  <img src=".github/assets/logo.png" height="200">
  <h1>
      16SMaRT
  </h1>
  <h4>16s rRNA Sequencing Meta-analysis Reconstruction Tool.</h4>
</div>

<p align="center">
    <a href='https://github.com/achillesrasquinha/16SMaRT/actions?query=workflow:"Continuous Integration"'>
      <img src="https://img.shields.io/github/workflow/status/achillesrasquinha/16SMaRT/Continuous Integration?style=flat-square">
    </a>
    <a href="https://coveralls.io/github/achillesrasquinha/16SMaRT">
      <img src="https://img.shields.io/coveralls/github/achillesrasquinha/16SMaRT.svg?style=flat-square">
    </a>
    <a href="https://git.io/boilpy">
      <img src="https://img.shields.io/badge/made%20with-boilpy-red.svg?style=flat-square">
    </a>
</p>

*16SMaRT* is a bioinformatics analysis pipeline for 16s rRNA gene sequencing data. It currently supports single-end or paired-end [Illumina](https://www.illumina.com/) data.

### Table of Contents
---------------------

* [Features](#features)
* [Quick Start](#quick-start)
* [Usage](#usage)
* [License](#license)

### Features
------------

* Supports single-end and paired-end [Illumina](https://www.illumina.com/) data.
* Quality Control using [FASTQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/).
* [Docker](https://www.docker.com/) + [Singularity](https://singularity.hpcng.org/) support.

### Quick Start
---------------

#### Using [Docker](https://www.docker.com/)

You can run *16SMaRT* by simply running the following command:

```
docker run \
    --rm -it \
    -v "<HOST_MACHINE_PATH_DATA>:/data" \
    -v "<HOST_MACHINE_PATH_CONFIG>:/root/.config/s3mart \
    ghcr.io/achillesrasquinha/16SMaRT \
    bpyutils --run-ml s3mart -p "data_dir=/data" --verbose
```

where `<HOST_MACHINE_PATH_DATA>` is the path to your host machine to store pipeline data and `<HOST_MACHINE_PATH_CONFIG>` is the path to store 16SMaRT configuration and intermediate data.

#### Running on HPC systems using [Singularity](https://singularity.hpcng.org/)

Singularity is the most widely used container system for HPC (High-Performance Computing) systems. In order to run your analysis on an HPC system, simply run the following command.

```
singularity run \
    --home $HOME \
    --cleanenv \
    -B <HOST_MACHINE_PATH_DATA>:/data \
    -B <HOST_MACHINE_PATH_CONFIG>:/root/.config/s3mart \
    docker://ghcr.io/achillesrasquinha/16SMaRT \
    bpyutils --run-ml s3mart -p "data_dir=/data" --verbose
```

### Usage
---------

### License
-----------

This repository has been released under the [MIT License](LICENSE).

---

<div align="center">
  Made with ❤️ using <a href="https://git.io/boilpy">boilpy</a>.
</div>