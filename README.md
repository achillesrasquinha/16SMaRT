<div align="center">
  <img src=".github/assets/logo.png" height="200">
  <h1>
      16SMaRT
  </h1>
  <h4>16s rRNA Sequencing Meta-analysis Reconstruction Tool.</h4>
</div>

<p align="center">
    <a href='https://github.com/achillesrasquinha/16SMaRT/actions?query=workflow:"Model CI"'>
      <img src="https://img.shields.io/github/workflow/status/achillesrasquinha/16SMaRT/Model CI?style=flat-square">
    </a>
    <a href='https://github.com/achillesrasquinha/16SMaRT/actions?query=workflow:"Docker"'>
      <img src="https://img.shields.io/github/workflow/status/achillesrasquinha/16SMaRT/Docker?style=flat-square&label=docker">
    </a>
    <a href="https://git.io/boilpy">
      <img src="https://img.shields.io/badge/made%20with-boilpy-red.svg?style=flat-square">
    </a>
</p>

<div align="justify">

**16SMaRT** is a bioinformatics analysis pipeline for 16s rRNA gene sequencing data. 16SMaRT is a "one-click" solution towards performing microbial community analysis of amplicon sequencing data. 16SMaRT aims to be your go-to solution for your next microbiome/metagenomics project. The primary objective of 16SMaRT analysis is to determine what genes are present and in what proportions in comparison across a range of samples. It currently supports single-end or paired-end [Illumina](https://www.illumina.com/) MiSeq data.

16SMaRT is written in Python using [boilpy's](https://github.com/achillesrasquinha/boilpy) data-pipeline boilerplate. 
16SMaRT is built on top of a considerable amount of dependencies and hence, the recommended way to install it is by using [docker](#using-docker) thus making installation in "one-click" and perfectly reproducible results. 16SMaRT is built with considering maximizing computation resources in mind thereby making it blazingly fast even on a local machine for a decent amount of samples. For a large number of studies, it is recommended to run 16SMaRT on a High-Performance Computing system using [singularity](#running-on-hpc-systems-using-singularity).

</div>

## Table of Contents

* [Features](#features)
* [Quick Start](#quick-start)
* [Usage](#usage)
* [Support](#support)
* [Citation](#citation)
* [License](#license)

## Features

* Supports single-end and paired-end [Illumina](https://www.illumina.com/) data.
* Quality Control using [FASTQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) and [MultiQC](https://multiqc.info/).
* Trimming using [mothur](https://mothur.org).
* Analysis using [phyloseq](https://joey711.github.io/phyloseq/).
* Multi-Processing.
* [Docker](https://www.docker.com/) + [Singularity](https://singularity.hpcng.org/) support.

## Quick Start

### Using [Docker](https://www.docker.com/)

First, install docker onto your system (can be followed via [docker's documentation](https://docs.docker.com/engine/install)).

Then, you can run simply run 16SMaRT by the following command:

```
docker run \
    --rm -it \
    -v "<HOST_MACHINE_PATH_DATA>:/data" \
    -v "<HOST_MACHINE_PATH_CONFIG>:/root/.config/s3mart \
    -v "<HOST_MACHINE_PATH_WORKSPACE>:/work \
    ghcr.io/achillesrasquinha/s3mart \
    bpyutils --run-ml s3mart -p "data_dir=/data" --verbose
```

where `<HOST_MACHINE_PATH_DATA>` is the path to your host machine to store pipeline data and `<HOST_MACHINE_PATH_CONFIG>` is the path to store 16SMaRT configuration and intermediate data. `<HOST_MACHINE_PATH_WORKSPACE>` is a workspace directory for you to store your files that can be used by 16SMaRT (e.g. input files).

### Running on HPC systems using [Singularity](https://singularity.hpcng.org/)

Singularity is the most widely used container system for HPC (High-Performance Computing) systems. In order to run your analysis on an HPC system, simply run the following command.

```
singularity run \
    --home $HOME \
    --cleanenv \
    -B <HOST_MACHINE_PATH_DATA>:/data \
    -B <HOST_MACHINE_PATH_CONFIG>:/root/.config/s3mart \
    -B <HOST_MACHINE_PATH_WORKSPACE>:/work \
    oras://ghcr.io/achillesrasquinha/s3mart:singularity \
    bpyutils --run-ml s3mart -p "data_dir=/data" --verbose
```

## Usage

### Basic Usage

* [**`input`**]()

    *Path to input CSV file, data directory of FASTQ files, URL to CSV file.*

* [**`fastqc`**]()

    *Run FASTQC after downloading SRAs.* (boolean, default - `True`)

* [**`multiqc`**]()

    *Run MultiQC after performing FASTQC.* (boolean, default - `True`)


Check out the [docs](docs/source) page to understand how to use this pipeline.

## Support

Have any queries? Post an issue on the [GitHub Issue Tracker](https://github.com/achillesrasquinha/16SMaRT/issues).

## Citation

If you use this software in your work, please cite it using the following:

> Furbeck, R., & Rasquinha, A. (2021). 16SMaRT - 16s rRNA Sequencing Meta-analysis Reconstruction Tool. (Version 0.1.0) [Computer software]. [https://github.com/achillesrasquinha/16SMaRT](https://github.com/achillesrasquinha/16SMaRT)

A comprehensive list of references for the tools used is listed [here](REFERENCES.md).

## License

This repository has been released under the [MIT License](LICENSE).

---

<div align="center">
  Made with ❤️ using <a href="https://git.io/boilpy">boilpy</a>.
</div>