import os.path as osp

from s3mart.config  import PATH
from s3mart import __name__ as NAME

from bpyutils.util._csv    import read as read_csv
from bpyutils.util.array   import group_by
from bpyutils.util.ml      import get_data_dir
from bpyutils.util.string  import check_url, safe_decode
from bpyutils.util.system  import write
from bpyutils import log, request as req

logger = log.get_logger(name = NAME)

CACHE  = PATH["CACHE"]

def get_input_data(input = None, data_dir = None, *args, **kwargs):
    data_dir = get_data_dir(NAME, data_dir)

    if input:
        if check_url(input, raise_err = False):
            response = req.get(input)
            response.raise_for_status()

            content = response.content

            input = osp.join(data_dir, "input.csv")
            write(input, safe_decode(content))
        
        input = osp.abspath(input)

        if osp.isdir(input):
            data_dir = input
    else:
        input = osp.join(PATH["DATA"], "sample.csv")

    groups = {}

    if osp.isfile(input):
        data   = read_csv(input)
        groups = group_by(data, "group")

    return data_dir, groups