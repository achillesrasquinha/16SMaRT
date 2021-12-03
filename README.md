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

**16SMaRT** is a bioinformatics analysis pipeline for 16s rRNA gene sequencing data. **16SMaRT** is a "one-click" solution towards performing microbial community analysis of amplicon sequencing data. **16SMaRT** aims to be your go-to solution for your next microbiome/metagenomics project. The primary objective of **16SMaRT** analysis is to determine what genes are present and in what proportions in comparision across a range of samples. It currently supports single-end or paired-end [Illumina](https://www.illumina.com/) MiSeq data.

## Table of Contents

* [Features](#features)
* [Quick Start](#quick-start)
* [Usage](#usage)
  * [Input Data](#input-data)
    * [CSV DataSheet](#csv-datasheet)
  * [Quality Control](#quality-control)
* [Support](#support)
* [References](#references)
* [Citation](#citation)
* [License](#license)

## Features

* Supports single-end and paired-end [Illumina](https://www.illumina.com/) data.
* Quality Control using [FASTQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) and [MultiQC](https://multiqc.info/).
* Trimming using [mothur](https://mothur.org).
* Multi-Processing.
* [Docker](https://www.docker.com/) + [Singularity](https://singularity.hpcng.org/) support.

## Quick Start

### Using [Docker](https://www.docker.com/)

You can run **16SMaRT** by simply running the following command:

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
    docker://ghcr.io/achillesrasquinha/s3mart \
    bpyutils --run-ml s3mart -p "data_dir=/data" --verbose
```

## Usage

### Input Data

The input data can be passed to **16SMaRT** in two different ways using the `input` argument, either:

* a comma-seperated datasheet containing [NCBI SRA](https://www.ncbi.nlm.nih.gov/sra) IDs (or a URL to a CSV file).
* a directory containing a list of FASTQ files.

#### CSV DataSheet

The CSV DataSheet must be of the following format.

| Column       | Description |
|--------------|-------------|
| `group`      | A group of FASTQ files (or a study).
| `sra`        | [NCBI SRA](https://www.ncbi.nlm.nih.gov/sra) ID
| `layout`     | Single-End or Paired-End Sequence (values: `single`, `paired`)
| `primer_f`   | Forward Primer
| `primer_r`   | Reverse Primer
| `trimmed`    | whether this sequence has already been trimmed or not. (values: `true`, `false`)
| `min_length` | start length used to screen a sequence.
| `max_length` | end length used to screen a sequence.

Take a look at a [sample.csv](https://github.com/achillesrasquinha/16SMaRT/blob/develop/src/s3mart/data/sample.csv) used in our sample pipeline.

![](docs/source/_static/sample-datasheet.png)

You can then provide the parameter as follows:

```
input=/work/input.csv
```

or 

```
input="<YOUR_URL_TO_CSV_FILE>"
```

### Quality Control

**16SMaRT** uses [FASTQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) and [MultiQC](https://multiqc.info/) for Quality Control. By default, this is done right after reading FASTQ files.

Quality Control can be disabled by simply providing the parameter as follows:

```
fastqc=False; multiqc=False
```

## Support

Have any queries? Post an issue on the [GitHub Issue Tracker](https://github.com/achillesrasquinha/16SMaRT/issues).

## References

1. Schloss, Patrick D., et al. “Introducing Mothur: Open-Source, Platform-Independent, Community-Supported Software for Describing and Comparing Microbial Communities.” Applied and Environmental Microbiology, vol. 75, no. 23, Dec. 2009, pp. 7537–41. journals.asm.org (Atypon), https://doi.org/10.1128/AEM.01541-09.

## Citation

If you use this software in your work, please cite it using the following:

> Furbeck, R., & Rasquinha, A. (2021). 16SMaRT - 16s rRNA Sequencing Meta-analysis Reconstruction Tool. (Version 0.1.0) [Computer software]. [https://github.com/achillesrasquinha/16SMaRT](https://github.com/achillesrasquinha/16SMaRT)

## License

This repository has been released under the [MIT License](LICENSE).

---

<div align="center">
  Made with ❤️ using <a href="https://git.io/boilpy">boilpy</a>.
</div>