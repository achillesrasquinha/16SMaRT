from __future__ import absolute_import

<<<<<<< HEAD
from s3mart.data.get_data import get_data_dir
=======
from s3mart.__attr__ import __name__ as NAME
from s3mart.data import get_data_dir
>>>>>>> template/master

def build_model():
    pass
    # do something ...

def train(data_dir = None, artifacts_dir = None, *args, **kwargs):
<<<<<<< HEAD
    data_dir = get_data_dir(data_dir)
=======
    data_dir = get_data_dir(NAME, data_dir)
>>>>>>> template/master
    model    = build_model()
    # do something ...