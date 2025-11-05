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

**16SMaRT** is a comprehensive, production-ready bioinformatics analysis pipeline for 16S rRNA gene sequencing data. It provides a complete "one-click" solution for performing microbial community analysis of amplicon sequencing data, taking you from raw sequencing reads to publication-ready visualizations.

## What is 16SMaRT?

16SMaRT automates the entire workflow of 16S rRNA analysis, a fundamental technique for studying microbial communities without the need for culturing. The primary objective is to:
- Identify microbial taxa present in your samples
- Determine their relative abundances and proportions
- Compare microbial community composition across different samples
- Generate phylogenetic relationships and diversity metrics
- Produce interactive visualizations for downstream analysis

## Key Capabilities

- **Automated Data Retrieval**: Seamlessly downloads sequencing data from NCBI SRA using accession numbers
- **Quality Control**: Comprehensive quality assessment using FASTQC and MultiQC with detailed HTML reports
- **Intelligent Preprocessing**: Automated primer trimming, quality filtering, and sequence merging optimized for 16S data
- **Taxonomic Classification**: Leverages SILVA database for accurate taxonomic assignment (97% OTU clustering)
- **Phylogenetic Analysis**: Constructs phylogenetic trees showing evolutionary relationships
- **Diversity Analysis**: Calculates both alpha (within-sample) and beta (between-sample) diversity metrics
- **Interactive Visualizations**: Generates 6 types of publication-ready interactive HTML plots:
  - Taxonomic abundance bar charts
  - Alpha diversity metrics (Shannon, Simpson, Chao1, Observed OTUs)
  - Beta diversity ordination (PCoA with Bray-Curtis)
  - Rarefaction curves
  - Phylogenetic trees
  - Geographic distribution maps
- **Dual Analysis Mode**: Produces results for both raw and rarefied (normalized) data

## Supported Data Types

16SMaRT currently supports single-end or paired-end [Illumina](https://www.illumina.com/) MiSeq sequencing data with FASTQ format.

## Architecture

16SMaRT is written in Python using [boilpy's](https://github.com/achillesrasquinha/boilpy) data-pipeline boilerplate and integrates industry-standard bioinformatics tools:
- **mothur**: OTU clustering, alignment, and classification
- **SILVA**: Reference database for 16S rRNA sequences
- **R/phyloseq**: Statistical analysis and visualization
- **VSEARCH**: Chimera detection

The pipeline is built with parallel processing capabilities to maximize computational resources, making it blazingly fast even on local machines for moderate sample sizes. For large-scale studies, 16SMaRT can be deployed on High-Performance Computing (HPC) systems using [Singularity](#running-on-hpc-systems-using-singularity).

## Why Use Docker/Singularity?

16SMaRT orchestrates multiple bioinformatics tools with complex dependencies. Using containerization ensures:
- **One-click installation** with zero dependency conflicts
- **Perfect reproducibility** across different systems
- **Consistent results** regardless of your computing environment

</div>

## Table of Contents

* [Features](#features)
* [Pipeline Workflow](#pipeline-workflow)
* [Quick Start](#quick-start)
* [Input Format](#input-format)
* [Usage](#usage)
* [Output Files](#output-files)
* [Configuration](#configuration)
* [Support](#support)
* [Citation](#citation)
* [License](#license)

## Features

### Data Handling
* Supports single-end and paired-end [Illumina](https://www.illumina.com/) data
* Automatic download from NCBI SRA database
* CSV-based metadata input or directory of FASTQ files
* Configurable primer trimming with mismatch tolerance

### Quality Control & Preprocessing
* Per-sample quality assessment with [FASTQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
* Aggregated quality reports using [MultiQC](https://multiqc.info/)
* Intelligent sequence trimming and filtering using [mothur](https://mothur.org)
* Quality score filtering (default: average Q35)
* Ambiguous base removal
* Homopolymer filtering
* Chimera detection with VSEARCH

### Analysis Pipeline
* OTU clustering at 97% similarity (0.03 distance cutoff)
* Taxonomic classification using SILVA database (v132 default)
* Phylogenetic tree construction
* Alpha diversity metrics (Observed OTUs, Chao1, Shannon, Simpson)
* Beta diversity analysis (Bray-Curtis dissimilarity)
* Rarefaction analysis for sampling depth assessment
* Statistical analysis using [phyloseq](https://joey711.github.io/phyloseq/)

### Visualization
* 6 types of interactive HTML plots (Plotly-based)
* Dual analysis mode (raw + rarefied data)
* Geographic distribution mapping
* Customizable color schemes and layouts

### Performance & Deployment
* Multi-core parallel processing
* Optimized resource utilization
* [Docker](https://www.docker.com/) containerization for reproducibility
* [Singularity](https://singularity.hpcng.org/) support for HPC systems
* Configurable batch processing for large datasets

## Pipeline Workflow

16SMaRT executes a comprehensive seven-stage pipeline:

```
1. Input Parsing
   └─> Read CSV metadata or scan FASTQ directory

2. Data Retrieval
   └─> Download from NCBI SRA (if needed)
   └─> Validate FASTQ integrity

3. Quality Control
   └─> Run FASTQC on all samples
   └─> Generate MultiQC summary report

4. Sequence Trimming
   └─> Remove primers (if specified)
   └─> Filter by quality scores
   └─> Remove ambiguous bases and homopolymers
   └─> Merge paired-end reads (if applicable)

5. Sequence Merging
   └─> Combine all samples into master FASTA
   └─> Generate sample grouping metadata

6. Bioinformatics Processing
   └─> Align to SILVA reference
   └─> Remove chimeric sequences
   └─> Cluster into OTUs (97% similarity)
   └─> Classify taxonomy
   └─> Build phylogenetic tree

7. Analysis & Visualization
   └─> Calculate diversity metrics
   └─> Generate 6 interactive plots (raw + rarefied)
```

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

## Input Format

16SMaRT accepts input in two formats:

### Option 1: CSV Metadata File

Create a CSV file with the following columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `group` | Yes | Sample identifier | `Sample_A` |
| `sra` | Yes* | NCBI SRA accession number | `SRR9822494` |
| `layout` | Yes | Sequencing layout | `single` or `paired` |
| `primer_f` | No | Forward primer sequence | `AGAGTTTGATCCTGGCTCAG` |
| `primer_r` | No | Reverse primer sequence | `GGTTACCTTGTTACGACTT` |
| `trimmed` | No | Skip trimming if already done | `true` or `false` |
| `min_length` | No | Minimum sequence length | `240` |
| `max_length` | No | Maximum sequence length | `275` |
| `country` | No** | Geographic location | `Australia` |

\* If providing local FASTQ files instead of SRA accessions, place files in the data directory with naming: `{group}.fastq` (single-end) or `{group}_1.fastq` and `{group}_2.fastq` (paired-end)

\** Required for geographic distribution visualization

**Example CSV:**
```csv
group,sra,layout,primer_f,primer_r,trimmed,min_length,max_length,country
Sample_SK13,ERR3792283,paired,,,true,240,275,Australia
Sample_AH19,SRR9822494,single,AGAGTTTGATCCTGGCTCAG,GGTTACCTTGTTACGACTT,false,120,300,Greenland
Sample_Local,,paired,,,false,200,300,USA
```

### Option 2: FASTQ Directory

Simply place your FASTQ files in a directory with the naming convention:
- Single-end: `sample_name.fastq` or `sample_name.fastq.gz`
- Paired-end: `sample_name_1.fastq` and `sample_name_2.fastq` (or `.fastq.gz`)

16SMaRT will automatically detect and process all FASTQ files.

## Usage

### Basic Usage

```bash
# Using Docker
docker run --rm -it \
    -v "/path/to/data:/data" \
    -v "/path/to/config:/root/.config/s3mart" \
    -v "/path/to/workspace:/work" \
    ghcr.io/achillesrasquinha/s3mart \
    bpyutils --run-ml s3mart -p "data_dir=/data" --verbose
```

### Advanced Usage with Parameters

```bash
# Specify custom input CSV and configuration
docker run --rm -it \
    -v "/path/to/data:/data" \
    -v "/path/to/config:/root/.config/s3mart" \
    -v "/path/to/workspace:/work" \
    ghcr.io/achillesrasquinha/s3mart \
    bpyutils --run-ml s3mart \
        -p "data_dir=/data" \
        -p "input=/work/samples.csv" \
        -p "fastqc=true" \
        -p "multiqc=true" \
        -p "jobs=8" \
        --verbose
```

### Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data_dir` | string | - | Directory containing FASTQ files or where SRA files will be downloaded |
| `input` | string | - | Path to CSV metadata file or URL |
| `fastqc` | boolean | `true` | Run FASTQC quality control |
| `multiqc` | boolean | `true` | Generate MultiQC aggregated report |
| `jobs` | integer | CPU count | Number of parallel processes |
| `quality_average` | integer | `35` | Minimum average quality score |
| `maximum_ambiguity` | integer | `0` | Maximum ambiguous bases allowed |
| `maximum_homopolymers` | integer | `8` | Maximum homopolymer run length |
| `primer_difference` | integer | `5` | Allowed primer mismatches |
| `classification_cutoff` | integer | `80` | Taxonomy confidence threshold (%) |
| `silva_version` | integer | `132` | SILVA database version |
| `trim_chunks` | integer | `8` | Number of parallel trimming batches |

### Example Workflows

**1. Process samples from NCBI SRA:**
```bash
# Create input CSV with SRA accessions
cat > samples.csv << EOF
group,sra,layout,country
Soil_A,SRR9822494,paired,USA
Soil_B,SRR9822495,paired,USA
Water_A,SRR9822496,single,Canada
EOF

# Run pipeline
docker run --rm -it \
    -v "$PWD:/work" \
    ghcr.io/achillesrasquinha/s3mart \
    bpyutils --run-ml s3mart -p "input=/work/samples.csv" --verbose
```

**2. Process local FASTQ files:**
```bash
# Organize files
mkdir data
cp Sample_A_1.fastq Sample_A_2.fastq data/
cp Sample_B_1.fastq Sample_B_2.fastq data/

# Run pipeline
docker run --rm -it \
    -v "$PWD/data:/data" \
    ghcr.io/achillesrasquinha/s3mart \
    bpyutils --run-ml s3mart -p "data_dir=/data" --verbose
```

**3. Custom quality thresholds:**
```bash
docker run --rm -it \
    -v "$PWD/data:/data" \
    ghcr.io/achillesrasquinha/s3mart \
    bpyutils --run-ml s3mart \
        -p "data_dir=/data" \
        -p "quality_average=30" \
        -p "maximum_homopolymers=10" \
        -p "classification_cutoff=85" \
        --verbose
```

Check out the [docs](docs/source) page for more detailed usage instructions.

## Output Files

16SMaRT generates a comprehensive set of outputs organized in the working directory:

### Quality Control Reports
- `fastqc/` - Individual FASTQC reports for each sample (HTML + data)
- `multiqc_report.html` - Aggregated quality metrics across all samples

### Processed Sequences
- `trimmed/` - Quality-filtered and trimmed sequences per sample (FASTA format)
- `output.fasta` - Merged sequences from all samples
- `output.groups` - Sample grouping metadata

### OTU Analysis
- `output.shared` - OTU abundance table (samples × OTUs)
- `output.taxonomy` - Taxonomic classification for each OTU
- `output.tre` - Phylogenetic tree (Newick format)

### Interactive Visualizations (HTML)

All plots are generated in two versions (raw and rarefied):

1. **`plot_taxonomic_abundance_[raw|rarefied].html`**
   - Stacked bar charts showing relative abundance of taxa
   - Interactive: hover for exact percentages, click to hide/show taxa

2. **`plot_alpha_diversity_[raw|rarefied].html`**
   - Box plots of diversity metrics (Observed, Chao1, Shannon, Simpson)
   - Grouped by sample metadata

3. **`plot_beta_diversity_[raw|rarefied].html`**
   - Principal Coordinates Analysis (PCoA) ordination
   - Based on Bray-Curtis dissimilarity
   - Interactive: rotate 3D plot, hover for sample details

4. **`plot_rarefaction_[raw|rarefied].html`**
   - Rarefaction curves showing OTU accumulation vs. sequencing depth
   - Helps assess if sequencing depth is sufficient

5. **`plot_phylogenetic_tree_[raw|rarefied].html`**
   - Interactive phylogenetic tree with taxonomic annotations
   - Color-coded by taxonomic groups

6. **`plot_world_map_[raw|rarefied].html`**
   - Geographic distribution of samples on world map
   - Requires `country` column in input CSV

### Intermediate Files
- `*.logfile` - mothur processing logs
- `*.align` - Aligned sequences to SILVA reference
- `*.dist` - Distance matrices for OTU clustering

## Configuration

### Environment Variables

16SMaRT can be configured using environment variables with the `S3MART_` prefix:

```bash
export S3MART_QUALITY_AVERAGE=30
export S3MART_JOBS=16
export S3MART_SILVA_VERSION=138

docker run --rm -it \
    -e S3MART_QUALITY_AVERAGE \
    -e S3MART_JOBS \
    -e S3MART_SILVA_VERSION \
    -v "$PWD/data:/data" \
    ghcr.io/achillesrasquinha/s3mart \
    bpyutils --run-ml s3mart -p "data_dir=/data"
```

### Configuration File

You can also create a configuration file at `/root/.config/s3mart/config.yml`:

```yaml
quality_average: 35
maximum_ambiguity: 0
maximum_homopolymers: 8
primer_difference: 5
classification_cutoff: 80
cutoff_level: 0.03
silva_version: 132
jobs: 8
fastqc: true
multiqc: true
```

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