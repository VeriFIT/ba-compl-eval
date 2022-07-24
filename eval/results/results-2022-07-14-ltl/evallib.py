#!/usr/bin/env python3
#
# a module that is a collection of various functionality for evaluation of experiments

import datetime
import mizani.formatters as mizani
import pandas as pd
import plotnine as p9
import re as re

# Read a file into a data frame
def read_file(filename):
    """Reads a CSV file into Panda's data frame"""
    df_loc = pd.read_csv(
        filename,
        sep=";",
        comment="#",
        na_values=['ERR', 'TO', 'MISSING'])
    return df_loc

# A generic scatter plot command that can print several data frames into one scatterplot
def scatter_plot_n(dfs, xcol, ycol, domain, colors, xname=None, yname=None, log=False, width=6, height=6, clamp=True, tickCount=5):
    assert len(domain) == 2
    assert len(dfs) == len(colors)

    POINT_SIZE = 1.5
    DASH_PATTERN = (0, (6, 2))

    if xname is None:
        xname = xcol
    if yname is None:
        yname = ycol

    # formatter for axes' labels
    ax_formatter = mizani.custom_format('{:n}')

    if clamp:  # clamp overflowing values if required
        new_df_list = list()
        for df in dfs:
            new_df = df.copy(deep=True)
            new_df.loc[new_df[xcol] > domain[1], xcol] = domain[1]
            new_df.loc[new_df[ycol] > domain[1], ycol] = domain[1]

            new_df_list.append(new_df)

        dfs = new_df_list

    # generate scatter plot
    scatter = p9.ggplot()
    scatter += p9.aes(x=xcol, y=ycol)
    for (df, color) in zip(dfs, colors):
        scatter += p9.geom_point(size=POINT_SIZE, na_rm=True, data=df, color=color, alpha=0.5)
        scatter += p9.geom_rug(na_rm=True, sides="tr", data=df, color=color, alpha=0.05)
    scatter += p9.labs(x=xname, y=yname)

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


# prints a scatter plot for one data set
def scatter_plot(df, **kwargs):
    return scatter_plot_n(dfs=[df], colors=["black"], **kwargs)


# scatter plot for one data set with some parameters for Buchi evaluation
def scatplot(df, params):
    size = 8
    if 'xname' not in params:
        params['xname'] = None
    if 'yname' not in params:
        params['yname'] = None
    if 'max' not in params:
        params['max'] = 10000
    if 'tickCount' not in params:
        params['tickCount'] = 5
    if 'filename' not in params:
        params['filename'] = "fig_" + params['x'] + "_vs_" + params['y']

    pl = scatter_plot(df,
                      xcol=params['x'] + '-States',
                      ycol=params['y'] + '-States',
                      xname=params['xname'], yname=params['yname'],
                      domain=[1, params['max']],
                      tickCount=params['tickCount'],
                      log=True, width=size, height=size)

    if 'save' in params and params['save'] == True:
        pl.save(filename=params['filename'], dpi=1000)

    return pl


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


# Connect a DF with results to DF with classification of inputs
def connect_with_classification(df, clas_file):
    df_clas = read_file(clas_file)
    df = pd.merge(df, df_clas, on='name')
    return df


# prints results of classification
def print_classification(df):
    df_empty = df[df['empty'] == 1]
    df_deterministic = df[df['deterministic'] == 1]
    df_deterministic_weak = df[(df['deterministic'] == 1) & (df['weak'] == 1)]
    df_inherently_weak = df[df['inherently weak'] == 1]
    df_semi_deterministic = df[df['semi deterministic'] == 1]
    df_terminal = df[df['terminal'] == 1]
    df_unambiguous = df[df['unambiguous'] == 1]
    df_weak = df[df['weak'] == 1]
    df_very_weak = df[df['very weak'] == 1]
    df_elevator = df[df['elevator'] == 1]
    df_elevator_not_semi = df[(df['elevator'] == 1) & (df['semi deterministic'] == 0)]

    print(f"! Classification of input automata")
    print(f"!   # empty: {len(df_empty)}")
    print(f"!   # deterministic: {len(df_deterministic)}")
    print(f"!   # deterministic weak: {len(df_deterministic_weak)}")
    print(f"!   # inherently weak: {len(df_inherently_weak)}")
    print(f"!   # semi-deterministic: {len(df_semi_deterministic)}")
    print(f"!   # terminal: {len(df_terminal)}")
    print(f"!   # unambiguous: {len(df_unambiguous)}")
    print(f"!   # weak: {len(df_weak)}")
    print(f"!   # very weak: {len(df_very_weak)}")
    print(f"!   # elevator: {len(df_elevator)}")
    print(f"!   # elevator not semi-deterministic: {len(df_elevator_not_semi)}")


# computes summary statistics
def summary_stats(df):
    summary = dict()
    for col in df.columns:
        if re.search('-States$', col) or re.search('-runtime$', col):
            summary[col] = dict()
            summary[col]['max'] = df[col].max()
            summary[col]['min'] = df[col].min()
            summary[col]['mean'] = df[col].mean()
            summary[col]['median'] = df[col].median()
            summary[col]['std'] = df[col].std()
            summary[col]['timeouts'] = df[col].isna().sum()
    return pd.DataFrame(summary).transpose()


# table to LaTeX file
def table_to_file(table, headers, out_file):
    with open(f"plots/{out_file}.tex", mode='w') as fl:
        print(tab.tabulate(table, headers=headers, tablefmt="latex"), file=fl)


# load results
def load_results(filename):
    df = read_file(filename)

    print(f"! Loaded results")
    print(f"!   file:  {filename}")
    print(f"!   time:  {datetime.datetime.now()}")
    print(f"!   # of automata: {len(df)}")
    return df


# loads a file with the classification
def load_results_classification(results, classification):
    df = load_results(results)
    df = connect_with_classification(df, classification)
    return df


# remove automata of a particular kind (e.g. inherently weak, etc.)
def remove_aut(df, kind):
    before = len(df)
    df = df[df[kind] == 0]
    after = len(df)
    print(f"! removed {before-after} automata of the type \"{kind}\"")
    return df


# get rid of timeouts and 0 states and give them some value
def sanitize_results(df, df_summary_states, timeout):
    # min and max states
    states_min = 1
    states_max = df_summary_states['max'].max()
    states_timeout = states_max * 1.1
    time_min = 0.01

    # sanitizing NAs
    for col in df.columns:
        if re.search('-States$', col):
            df[col].fillna(states_timeout, inplace=True)
            df[col].replace(0, states_min, inplace=True)  # to remove 0 (in case of log graph)

        if re.search('-runtime$', col):
            df[col].fillna(timeout, inplace=True)
            df.loc[df[col] < time_min, col] = time_min  # to remove 0 (in case of log graph)

    return df
