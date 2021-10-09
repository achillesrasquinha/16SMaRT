import os.path as osp
import csv

from geomeat.config import PATH
from bpyutils.util.system import ShellEnvironment

def get_data():
    path_data = osp.join(PATH["DATA"], "data.csv")
    
    with open(path_data) as f:
        data  = csv.reader(f)

        with ShellEnvironment() as shell:
            for row in data:
                print(row)