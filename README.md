<div align="center">
  <img src=".github/assets/logo.png" height="128">
  <h1>
      s3mart
  </h1>
  <h4>A meta-analysis for meat across geographies.</h4>
</div>

<p align="center">
    <a href='https://github.com/achillesrasquinha/s3mart//actions?query=workflow:"Continuous Integration"'>
      <img src="https://img.shields.io/github/workflow/status/achillesrasquinha/s3mart/Continuous Integration?style=flat-square">
    </a>
    <a href="https://coveralls.io/github/achillesrasquinha/s3mart">
      <img src="https://img.shields.io/coveralls/github/achillesrasquinha/s3mart.svg?style=flat-square">
    </a>
    <a href="https://pypi.org/project/s3mart/">
      <img src="https://img.shields.io/pypi/v/s3mart.svg?style=flat-square">
    </a>
    <a href="https://pypi.org/project/s3mart/">
      <img src="https://img.shields.io/pypi/l/s3mart.svg?style=flat-square">
    </a>
    <a href="https://pypi.org/project/s3mart/">
		  <img src="https://img.shields.io/pypi/pyversions/s3mart.svg?style=flat-square">
	  </a>
    <a href="https://git.io/boilpy">
      <img src="https://img.shields.io/badge/made%20with-boilpy-red.svg?style=flat-square">
    </a>
</p>

### Table of Contents
* [Features](#features)
* [Quick Start](#quick-start)
* [Usage](#usage)
* [License](#license)

### Features
* Python 2.7+ and Python 3.4+ compatible.

### Quick Start

```shell
$ pip install s3mart
```

Check out [installation](docs/source/install.rst) for more details.

### Usage

#### Application Interface

```python
>>> import s3mart
```


#### Command-Line Interface

```console
$ s3mart
Usage: s3mart [OPTIONS] COMMAND [ARGS]...

  A meta-analysis for meat across geographies.

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  help     Show this message and exit.
  version  Show version and exit.
```


### Docker

Using `s3mart's` Docker Image can be done as follows:

```
$ docker run \
    --rm \
    -it \
    achillesrasquinha/s3mart \
      --verbose
```

### License

This repository has been released under the [MIT License](LICENSE).

---

<div align="center">
  Made with ❤️ using <a href="https://git.io/boilpy">boilpy</a>.
</div>