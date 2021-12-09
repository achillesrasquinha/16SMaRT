from Bio import Phylo

from bpyutils.util._csv import read as read_csv
from bpyutils._compat import iteritems

_PHYLO_FORMAT = "newick"

def patch_tree_file(tree_file, list_file, target_file):
    lookup = { }
    data   = read_csv(list_file, delimiter = "\t")

    data   = data[0]

    for key, value in iteritems(data):
        if key.startswith("Otu"):
            values = value.split(",")
            for val in values:
                lookup[val] = key

    tree = next(Phylo.parse(tree_file, _PHYLO_FORMAT))
    for terminal in tree.get_terminals():
        if terminal.name in lookup:
            terminal.name = lookup[terminal.name]

    Phylo.write(tree, target_file, _PHYLO_FORMAT)