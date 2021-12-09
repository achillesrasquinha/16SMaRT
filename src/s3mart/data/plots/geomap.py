import rpy2.robjects as ro
from rpy2.robjects.lib import ggplot2 as gg

from bpyutils.util.types import lmap

from s3mart.data.plots.util import save_plot

R = ro.r

def plot(*args, **kwargs):
    data  = kwargs.get("data")

    countries = lmap(lambda x: x["country"], data)

    map_world = gg.map_data("world")
    map_data  = gg.map_data("world", region = countries)

    gp    = gg.ggplot(map_world)
    pp    = (gp
        # + R.geom_sf()
        + gg.aes_string(x = "long", y = "lat", group = "group")
        + gg.geom_polygon(fill = "lightgray", colour = "white")
        + gg.geom_polygon(
            data    = map_data,
            mapping = gg.aes_string(x = "long", y = "lat", fill = "region")
        )
        + gg.theme_void()
        + gg.theme(legend_position = "none")
    )

    save_plot(pp, plot_kwargs = { },
        *args, **kwargs)