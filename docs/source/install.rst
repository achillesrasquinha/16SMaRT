.. _install:

### Installation

#### Installation via pip

The recommended way to install **geomeat** is via `pip`.

```shell
$ pip install geomeat
```

For instructions on installing python and pip see “The Hitchhiker’s Guide to Python” 
[Installation Guides](https://docs.python-guide.org/starting/installation/).

#### Building from source

`geomeat` is actively developed on [https://github.com](https://github.com/achillesrasquinha/geomeat)
and is always avaliable.

You can clone the base repository with git as follows:

```shell
$ git clone https://github.com/achillesrasquinha/geomeat
```

Optionally, you could download the tarball or zipball as follows:

##### For Linux Users

```shell
$ curl -OL https://github.com/achillesrasquinha/tarball/geomeat
```

##### For Windows Users

```shell
$ curl -OL https://github.com/achillesrasquinha/zipball/geomeat
```

Install necessary dependencies

```shell
$ cd geomeat
$ pip install -r requirements.txt
```

Then, go ahead and install geomeat in your site-packages as follows:

```shell
$ python setup.py install
```

Check to see if you’ve installed geomeat correctly.

```shell
$ geomeat --help
```