import rpy2.robjects as ro

R = ro.r

def save_plot(ggplot, *args, **kwargs):
    target_file = kwargs.get("target_file")
    
    ggplot.plot()
    
    R("dev.copy(png, '%s')" % target_file)