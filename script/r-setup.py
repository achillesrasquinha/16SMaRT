# pylint: disable=E0602

import os.path as osp
import json
import sys

R_REPO = "https://cloud.r-project.org"

def install_r_packages(path_packages):
    path_packages = osp.abspath(path_packages)

    if osp.exists(path_packages):
        packages = {}

        with open(path_packages) as f:
            packages = json.load(f)
            
        if "dependencies" in packages:
            from rpy2.robjects.packages import importr

            utils = importr("utils")

            for name, version in packages["dependencies"].items():
                utils.install_packages(name, repos = R_REPO)

        if "biocDependencies" in packages:
            from rpy2.robjects.packages import importr
            from rpy2 import robjects as ro

            R = ro.r

            utils = importr("utils")
            utils.install_packages("BiocManager", repos = R_REPO)

            biocManager = importr("BiocManager")

            for name, version in packages["biocDependencies"].items():
                biocManager.install(name, ask = False)

if __name__ == "__main__":
    args = sys.argv[1:]
    
    install_r_packages(args[0])