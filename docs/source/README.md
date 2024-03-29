# Introduction

<div align="justify">

The unseen microbial world impacts us every day. From causing to preventing disease, spoiling or flavouring food, or helping ruminant animals digest grass. Bacteria are an important part of the world around us and understanding the various types and behaviors can overall improve our food and medical systems. A vast majority of environmental microbiologists claim that only less than 2% of all bacteria in the environment can be cultured within laboratory conditions. Such a vast divide of being unable to culture a vast majority of bacteria in the environment might be due to lack of culturing techniques, need for specific nutrients that are unable to produce within laboratory conditions, or dependence on interactions with other bacteria in order to live and grow. Thus, many bacteria get missed in traditional petri plate-based studies.

***Metagenomics*** is the study of genetic material (or genomes) extracted directly from all environmental samples. Such studies are in contrast with a traditional reduction-based approach in microbiology wherein a specific strain in consideration is isolated, purified and eventually its genome sequenced. Metagenomics helps us understand the ecology of the bacteria living within it, analyse them in their natural state and finally, understand the importance in human as well as animal health.

**16s rRNA** is the most common structural-based metagenomics experiment one can conduct for an observed community of bacteria. 16s rRNA-based experiments helps one perform a general survey of ***"what kinds of bacteria are available within the community and by how many?"***. One of the key advantage of considering a 16s rRNA-based experiment is that such a region is universally conserved amongst almost all bacteria yet has enough variability to distinguish various populations across various samples. One can think of it like a "fingerprint" for microbes.

<div align="center">

| Molecule of a 30S Subunit from thermus thermophilus | 16S ribosomal RNA |
|---------------------------------------|-------------------|
| ![](_static/thermus-thermophilus.gif) | <img src="_static/16S-rRNA.png" height="320"/> |

***Source:*** [Wikipedia](https://en.wikipedia.org/wiki/Thermus_thermophilus)

</div>

</div>

# Table of Contents

* [Input Data](#input-data)
    * [CSV DataSheet](#csv-datasheet)
* [Quality Control](#quality-control)
* [Preprocessing](#preprocessing)
* [Diversity Analysis](#diversity-analysis)
    * [Abundance](#abundance)
    * [Alpha Diversity](#alpha-diversity)
    * [Beta Diversity](#beta-diversity)

# Input Data

The input data can be passed to **16SMaRT** in two different ways using the `input` argument, either:

* a comma-seperated datasheet containing [NCBI SRA](https://www.ncbi.nlm.nih.gov/sra) IDs (or a URL to a CSV file).
* a directory containing a list of FASTQ files.

## CSV DataSheet

The CSV DataSheet must be of the following format.

| Column               | Description |
|----------------------|-------------|
| [**`group`**]()      | A group of FASTQ files (or a study).
| [**`sra`**]()        | [NCBI SRA](https://www.ncbi.nlm.nih.gov/sra) ID
| [**`layout`**]()     | Single-End or Paired-End Sequence (values: `single`, `paired`)
| [**`primer_f`**]()   | Forward Primer
| [**`primer_r`**]()   | Reverse Primer
| [**`trimmed`**]()    | whether this sequence has already been trimmed or not. (values: `true`, `false`)
| [**`min_length`**]() | start length used to screen a sequence.
| [**`max_length`**]() | end length used to screen a sequence.

For example, take a look at a [sample.csv](https://github.com/achillesrasquinha/16SMaRT/blob/develop/src/s3mart/data/sample.csv) used in our sample pipeline. You can then provide the parameter as follows:

```
input="/work/input.csv|<YOUR_URL_TO_CSV_FILE>"
```

Each SRA ID is then fetched and the FASTQ files are saved onto disk within your data directory.

# Quality Control

<div align="justify">

**16SMaRT** uses [FASTQC](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/) and [MultiQC](https://multiqc.info/) for Quality Control. By default, this is done right after reading FASTQ files. The output results of FASTQC for each FASTQ file can be obtained within the `<data_dir>/fastqc` whereas the MultiQC report can be obtained at `<data_dir>/multiqc_report.html` file.

</div>

Quality Control can be disabled by simply providing the parameter as follows:

```
fastqc=False; multiqc=False
```

# Preprocessing

| Key | Type  | Default 
|-----|-------|--------
| [**`trim_chunks`**]()           | integer | Number of group configurations to run parallely during trimming (default - 8).
| [**`quality_average`**]()       | integer | Calculate the average quality score for each sequence and remove those that have an average below the value provided. (default - 35)
| [**`maximum_ambiguity`**]()     | integer | mothur's [maxambig](https://mothur.org/wiki/trim.seqs/#maxambig) parameter called during [trim.seqs](https://mothur.org/wiki/trim.seqs) (default - 0).
| [**`maximum_homopolymers`**]()  | integer | mothur's [maxhomop](https://mothur.org/wiki/trim.seqs/#maxhomop) parameter called during [trim.seqs](https://mothur.org/wiki/trim.seqs) (default - 8).
| [**`primer_difference`**]()     | integer | mothur's [pdiffs](https://mothur.org/wiki/trim.seqs/#bdiffs--pdiffs--ldiffs--sdiffs--tdiffs) parameter called during [trim.seqs](https://mothur.org/wiki/trim.seqs) (default - 5).
| [**`classification_cutoff`**]() | integer | mothur's [pdiffs](https://mothur.org/wiki/classify.seqs/#cutoff) parameter called during [trim.seqs](https://mothur.org/wiki/classify.seqs) (default - 80).
| [**`cutoff_level`**]()          | float   | The cutoff parameter allows you to specify a consensus confidence threshold for your taxonomy (default - 0.03).
| [**`filter_taxonomy`**]()       | array   | Taxonomy to be removed (default - `["chloroplast", "mitochondria", "archaea", "eukaryota", "unknown"]`).
| [**`taxonomy_level`**]()        | integer | mothur's [taxlevel](https://mothur.org/wiki/merge.otus/#taxlevel) parameter called during [trim.seqs](https://mothur.org/wiki/merge.otus) (default - 6).
| [**`silva_pcr_start`**]()       | integer | Start length when performing a PCR over SILVA DB.
| [**`silva_pcr_end`**]()         | integer | End length when performing a PCR over SILVA DB.
| [**`silva_version`**]()         | string  | SILVA Version to be downloaded. Available versions are listed [here](https://mothur.org/wiki/silva_reference_files/) (default - 132).
| [**`minimal_output`**]()        | boolean | A minimal output optimizes the entire pipeline to utilize minimal disk resources (i.e., all intermediate resources will be deleted) (default - False).
| [**`jobs`**]()                  | integer | Number of jobs to use while performing a pipeline run. (default - number of CPUs)

# Diversity Analysis

## Abundance Chart

<div align="center">

| Raw Data | Rarified Data |
|----------|---------------|
| <img src="_static/plots/abundance_bar.png" height="500"/> | <img src="_static/plots/abundance_bar-resampled.png" height="500"/> |

</div>

## Alpha Diversity

<div align="justify">

Alpha diversity is a metric that describes the diversity or *richness* of the bacterial community of a sample. These indices approximate the number of different species or operational taxonomic units (OTUs) present. Alpha diversity can be estimated in a variety of ways, this pipeline considers Observed, Chao1, ACE, Shannon, Simpson, Inverse-Simpson and Fisher estimates. Each of these metrics has different assumptions or weaknesses, so all of them have been considered. For example, Observed metrics simply use the raw observed counts tabulated from rarified or non-rarefied sequence data whereas the Chao1 primarily considers total “richness” of the various species, the number of “rare” taxa only occurring once or twice and assumes a Poisson distribution. Bacterial communities do generally follow this distribution, as there are many “rare” taxa in nature, so this metric is often preferred in microbial community analysis as it addresses potential skew. Shannon metrics provide additional information, as they consider both “richness” and “evenness”, the proportion of each species compared to the total number of species.

</div>

<div align="center">

| Raw Data | Rarified Data |
|----------|---------------|
| <img src="_static/plots/alpha_diversity.png" height="420"/> | <img src="_static/plots/alpha_diversity-resampled.png" height="420"/> |

</div>

## Beta Diversity

<div align="justify">

Beta diversity estimates give researchers a methodology to describe differences between samples in microbial communities across samples, or how “related” one community is to another. “Relatedness” can be described using information from phylogenetic distances, individual taxa occurrence rate, or both. Currently, this pipeline utilizes Bray-Curtis ordination. This methodology is commonly used in ecology studies and utilizes only the abundances of each species across the samples to calculate their dissimilarity. It does not require phylogenetic distances that may take valuable computational storage space/processing time to generate. Future optimization will consider the Weighted UniFrac distance, a similarity index that does use the phylogeny “weighed” by occurrence rate.

</div>

<div align="center">

| Raw Data | Rarified Data |
|----------|---------------|
| <img src="_static/plots/beta_diversity.png" height="420"/> | <img src="_static/plots/beta_diversity-resampled.png" height="420"/> |

</div>