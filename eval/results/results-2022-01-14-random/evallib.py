#!/usr/bin/env python3
#
# a module that is a collection of various functionality for evaluation of experiments

import mizani.formatters as mizani
import pandas as pd
import plotnine as p9

# Read a file into a data frame
def read_file(filename):
    """Reads a CSV file into Panda's data frame"""
    df_loc = pd.read_csv(
        filename,
        sep=";",
        comment="#",
        na_values=['ERR', 'TO', 'MISSING'])
    return df_loc


# prints a scatter plot
def scatter_plot(df, xcol, ycol, domain, xname=None, yname=None, log=False, width=6, height=6, clamp=True, tickCount=5):
    assert len(domain) == 2

    POINT_SIZE = 1.0
    DASH_PATTERN = (0, (6, 2))

    if xname is None:
        xname = xcol
    if yname is None:
        yname = ycol

    # formatter for axes' labels
    ax_formatter = mizani.custom_format('{:n}')

    if clamp:  # clamp overflowing values if required
        df = df.copy(deep=True)
        df.loc[df[xcol] > domain[1], xcol] = domain[1]
        df.loc[df[ycol] > domain[1], ycol] = domain[1]

    # generate scatter plot
    scatter = p9.ggplot(df)
    scatter += p9.aes(x=xcol, y=ycol)
    scatter += p9.geom_point(size=POINT_SIZE, na_rm=True)
    scatter += p9.labs(x=xname, y=yname)

    # rug plots
    scatter += p9.geom_rug(na_rm=True, sides="tr", alpha=0.05)

    if log:  # log scale
        scatter += p9.scale_x_log10(limits=domain, labels=ax_formatter)
        scatter += p9.scale_y_log10(limits=domain, labels=ax_formatter)
    else:
        scatter += p9.scale_x_continuous(limits=domain, labels=ax_formatter)
        scatter += p9.scale_y_continuous(limits=domain, labels=ax_formatter)

    # scatter += p9.theme_xkcd()
    scatter += p9.theme_bw()
    scatter += p9.theme(panel_grid_major=p9.element_line(color='#666666', alpha=0.5))
    scatter += p9.theme(panel_grid_minor=p9.element_blank())
    scatter += p9.theme(figure_size=(width, height))
    scatter += p9.theme(text=p9.element_text(size=24, color="black"))

    # generate additional lines
    scatter += p9.geom_abline(intercept=0, slope=1, linetype=DASH_PATTERN)  # diagonal
    scatter += p9.geom_vline(xintercept=domain[1], linetype=DASH_PATTERN)  # vertical rule
    scatter += p9.geom_hline(yintercept=domain[1], linetype=DASH_PATTERN)  # horizontal rule

    res = scatter

    return res


# Print a matrix of plots
def matrix_plot(list_of_plots, cols):
    assert len(list_of_plots) > 0
    assert cols >= 0

    matrix_plot = None
    row = None
    for i in range(0, len(list_of_plots)):
        if i % cols == 0:  # starting a new row
            row = list_of_plots[i]
        else:
            row |= list_of_plots[i]

        if (i + 1) % cols == 0 or i + 1 == len(list_of_plots):  # last chart in a row
            if not matrix_plot:  # first row finished
                matrix_plot = row
            else:
                matrix_plot &= row

    return matrix_plot
