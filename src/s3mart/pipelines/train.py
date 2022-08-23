from __future__ import absolute_import

from s3mart.__attr__ import __name__ as NAME
from s3mart.data import get_data_dir

def build_model():
    pass
    # do something ...

def train(data_dir = None, artifacts_dir = None, *args, **kwargs):
    data_dir = get_data_dir(NAME, data_dir)
    model    = build_model()
    # do something ...