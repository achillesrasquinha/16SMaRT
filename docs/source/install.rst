.. _install:

### Installation

#### Installation via pip

The recommended way to install **s3mart** is via `pip`.

```shell
$ pip install s3mart
```

For instructions on installing python and pip see “The Hitchhiker’s Guide to Python” 
[Installation Guides](https://docs.python-guide.org/starting/installation/).

#### Building from source

`16SMaRT` is actively developed on [https://github.com](https://github.com/achillesrasquinha/16SMaRT)
and is always avaliable.

You can clone the base repository with git as follows:

```shell
$ git clone https://github.com/achillesrasquinha/16SMaRT
```

Optionally, you could download the tarball or zipball as follows:

##### For Linux Users

```shell
$ curl -OL https://github.com/achillesrasquinha/tarball/16SMaRT
```

##### For Windows Users

```shell
$ curl -OL https://github.com/achillesrasquinha/zipball/16SMaRT
```

Install necessary dependencies

```shell
$ cd s3mart
$ pip install -r requirements.txt
```

Then, go ahead and install s3mart in your site-packages as follows:

```shell
$ python setup.py install
```

Check to see if you've installed s3mart correctly.

```shell
$ s3mart --help
```