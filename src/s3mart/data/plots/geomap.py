import rpy2.robjects as ro
from   rpy2.robjects.lib import ggplot2 as gg

from bpyutils.util.types import lmap

R = ro.r

def plot(*args, **kwargs):
    data  = kwargs.get("data")
    file_ = kwargs.get("file_", "output.png")

    countries = lmap(lambda x: x["country"], data)

    map_world = gg.map_data("world")
    map_data  = gg.map_data("world", region = countries)

    gp    = gg.ggplot(map_world)
    pp    = (gp
        + gg.aes_string(x = "long", y = "lat", group = "group")
        + gg.geom_polygon(fill = "lightgray", colour = "white")
        + gg.geom_polygon(
            data    = map_data,
            mapping = gg.aes_string(x = "long", y = "lat", fill = "region")
        )
        + gg.theme_void()
        + gg.theme(legend_position = "none")
    )

    pp.plot()

    R("dev.copy(png, '%s')" % file_)