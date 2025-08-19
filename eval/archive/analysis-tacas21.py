#!/usr/bin/env python3

# PREAMBLE
import pandas as pd
import re as re
import tabulate as tab
import plotnine as p9
import math
import mizani.formatters as mizani


FILE_INPUT = "results.csv"
#FILE_INPUT = "results/results-2020-09-06/random-all-to300-merged.csv"

# in seconds
TIMEOUT = 300
TIMEOUT_VAL = TIMEOUT * 1.1
TIME_MIN = 0.01

# For reading in files
def read_file(filename):
   """Reads a CSV file into Panda's data frame"""
   df = pd.read_csv(
          filename,
          sep=";",
          comment="#",
          na_values=['ERR','TO', 'MISSING'])
   return df

# For printing scatter plots

def scatter_plot(df, xcol, ycol, domain, xname=None, yname=None, log=False, width=6, height=6, clamp=True, tickCount=5):
    assert len(domain) == 2

    POINT_SIZE=0.5
    DASH_PATTERN=(0, (3,1))

    if xname == None:
      xname = xcol
    if yname == None:
      yname = ycol

    # formater for axes' labels
    ax_formatter = mizani.custom_format('{:n}')

    if clamp: # clamp overflowing values if required
      df = df.copy(deep=True)
      df.loc[df[xcol] > domain[1], xcol] = domain[1]
      df.loc[df[ycol] > domain[1], ycol] = domain[1]


    # generate scatter plot
    scatter  = p9.ggplot(df)
    scatter += p9.aes(x=xcol, y=ycol)
    scatter += p9.geom_point(size=POINT_SIZE, na_rm=True)
    scatter += p9.labs(x=xname, y=yname)

    if log: # log scale
      scatter += p9.scale_x_log10(limits=domain, labels=ax_formatter)
      scatter += p9.scale_y_log10(limits=domain, labels=ax_formatter)
    else:
      scatter += p9.scale_x_continuous(limits=domain, labels=ax_formatter)
      scatter += p9.scale_y_continuous(limits=domain, labels=ax_formatter)

    #scatter += p9.theme_xkcd()
    scatter += p9.theme_bw()
    scatter += p9.theme(panel_grid_major=p9.element_line(color='#666666', alpha=0.5))
    scatter += p9.theme(figure_size=(width, height))

    # generate additional lines
    scatter += p9.geom_abline(intercept=0, slope=1, linetype=DASH_PATTERN)  # diagonal
    scatter += p9.geom_vline(xintercept=domain[1], linetype=DASH_PATTERN)   # vertical rule
    scatter += p9.geom_hline(yintercept=domain[1], linetype=DASH_PATTERN)   # horizontal rule

    res = scatter

    return res


# Print a matrix of plots
def matrix_plot(list_of_plots, cols):
  assert len(list_of_plots) > 0
  assert cols >= 0

  matrix_plot = None
  row = None
  for i in range(0, len(list_of_plots)):
    if i % cols == 0:   # starting a new row
      row = list_of_plots[i]
    else:
      row |= list_of_plots[i]

    if (i+1) % cols == 0 or i + 1 == len(list_of_plots): # last chart in a row
      if not matrix_plot:   # first row finished
        matrix_plot = row
      else:
        matrix_plot &= row

  return matrix_plot

#############################################################################
############################## ENTRY POINT ##################################
#############################################################################
df = read_file(FILE_INPUT)

print(f"# of automata: {len(df)}")

# some sanitization
# remove automata with trivial language
df = df[df['ranker-maxr-Transitions'] != 0]
df = df[df['ranker-maxr-autfilt-States'] != 1]

print(f'# of automata after sanitization: {len(df)}')
print("\n\n")

summary_states = dict()
for col in df.columns:
  if re.search('-States$', col) or re.search('-runtime$', col):
    summary_states[col] = dict()
    summary_states[col]['max'] = df[col].max()
    summary_states[col]['min'] = df[col].min()
    summary_states[col]['mean'] = df[col].mean()
    summary_states[col]['median'] = df[col].median()
    summary_states[col]['std'] = df[col].std()
    summary_states[col]['timeouts'] = df[col].isna().sum()

df_summary_states = pd.DataFrame(summary_states).transpose()


################  states of complements ##################
interesting = ["ranker-maxr-nopost",
               "ranker-rrestr-nopost",
               "schewe",
               "ranker-maxr-autfilt",
               "ranker-maxr-bo-autfilt",
               "piterman-autfilt",
               "safra-autfilt",
               "spot-autfilt",
               "fribourg-autfilt",
               "seminator-autfilt",
               "roll-autfilt",
               ]

tab_interesting = []
for i in interesting:
  row = df_summary_states.loc[i+'-States']
  row_dict = dict(row)
  row_dict.update({'name':i})
  tab_interesting.append([row_dict['name'],
                          # row_dict['min'],
                          row_dict['max'],
                          row_dict['mean'],
                          row_dict['median'],
                          row_dict['std'],
                          row_dict['timeouts']])

# headers = ["name", "min", "max", "mean", "median", "std. dev", "timeouts"]
headers = ["method", "max", "mean", "median", "std. dev", "timeouts"]
print("######################################################################")
print("####                        Table 1 (left)                        ####")
print("######################################################################")
print(tab.tabulate(tab_interesting, headers=headers, tablefmt="github"))
print("\n\n")

#################### runtimes of complementation ##################
interesting = ["ranker-maxr",
               "ranker-maxr-bo",
               "piterman",
               "safra",
               "spot",
               "fribourg",
               "seminator",
               "roll",
               ]

tab_interesting = []
for i in interesting:
  row = df_summary_states.loc[i+'-runtime']
  row_dict = dict(row)
  row_dict.update({'name':i})
  tab_interesting.append([row_dict['name'],
                          # row_dict['min'],
                          # row_dict['max'],
                          row_dict['mean'],
                          row_dict['median'],
                          row_dict['std'],
                          # row_dict['timeouts'],
                          ])

headers = ["method", "mean", "median", "std. dev"]
# headers = ["method", "min", "max", "mean", "median", "std. dev", "timeouts"]
print("######################################################################")
print("####                           Table 2                            ####")
print("######################################################################")
print(tab.tabulate(tab_interesting, headers=headers, tablefmt="github"))
print("\n\n")

# min and max states
states_min = 1
states_max = df_summary_states['max'].max()
states_timeout = states_max * 1.1

# sanitizing NAs
for col in df.columns:
  if re.search('-States$', col):
    df[col].fillna(states_timeout, inplace=True)
    df[col].replace(0, states_min, inplace=True)   # to remove 0 (in case of log graph)

  if re.search('-runtime$', col):
    df[col].fillna(TIMEOUT_VAL, inplace=True)
    df.loc[df[col] < TIME_MIN, col] = TIME_MIN   # to remove 0 (in case of log graph)

# print("States min: {}".format(states_min))
# print("States max: {}".format(states_max))


# comparing wins/loses
compare_methods = [("ranker-maxr-nopost-States", "ranker-rrestr-nopost-States"),
                   ("ranker-maxr-nopost-States", "schewe-States"),
                   ("ranker-maxr-autfilt-States", "piterman-autfilt-States"),
                   ("ranker-maxr-autfilt-States", "safra-autfilt-States"),
                   ("ranker-maxr-autfilt-States", "spot-autfilt-States"),
                   ("ranker-maxr-autfilt-States", "fribourg-autfilt-States"),
                   ("ranker-maxr-autfilt-States", "seminator-autfilt-States"),
                   ("ranker-maxr-autfilt-States", "roll-autfilt-States"),
                  ]

tab_wins = []
for left, right in compare_methods:
  left_over_right = df[df[left] < df[right]]
  right_timeouts = left_over_right[left_over_right[right] == states_timeout]

  right_over_left = df[df[left] > df[right]]
  left_timeouts = right_over_left[right_over_left[left] == states_timeout]

  tab_wins.append([right, len(left_over_right), len(right_timeouts), len(right_over_left), len(left_timeouts)])

headers_wins = ["methods", "wins", "wins-timeouts", "loses", "loses-timeouts"]
print("######################################################################")
print("####                        Table 1 (right)                       ####")
print("######################################################################")
print(tab.tabulate(tab_wins, headers=headers_wins, tablefmt="github"))
print("\n\n")


print("##############    other claimed results    ###############")

############# the best solution ##########
df['other_min'] = df[['safra-autfilt-States','piterman-autfilt-States', 'spot-autfilt-States', 'fribourg-autfilt-States', 'seminator-autfilt-States', 'roll-autfilt-States']].min(axis=1)

ranker_best = df[df['ranker-maxr-autfilt-States'] < df['other_min']]
ranker_not_best = df[df['ranker-maxr-autfilt-States'] > df['other_min']]

num_ranker_not_strictly_best = len(df) - len(ranker_not_best)
num_ranker_not_strictly_best_percent = "{:.1f}".format(num_ranker_not_strictly_best / len(df) * 100)
num_ranker_strictly_best = len(ranker_best)
num_ranker_strictly_best_percent = "{:.1f}".format(num_ranker_strictly_best / len(df) * 100)
print(f"ranker non-strictly best: {num_ranker_not_strictly_best} (= {num_ranker_not_strictly_best_percent} %)")
print(f"ranker stricly best: {num_ranker_strictly_best} (= {num_ranker_strictly_best_percent} %)")
# print(f"ranker not best = {len(ranker_not_best)}")

###########   BackOff   ################
backoff = df[df["ranker-maxr-bo-Engine"].str.contains("GOAL", na=False)]
print(f"backoff executions: {len(backoff)}")


to_cmp2 = [{'x':"ranker-maxr-nopost", 'y':"ranker-rrestr-nopost", 'xname':'Ranker-MaxR', 'yname':'Ranker-RRestr', 'filename': "fig_1a"},
           {'x':"ranker-maxr-nopost", 'y':"schewe", 'xname': "Ranker-MaxR", 'yname': "Schewe-RedAvgOut", 'filename': "fig_1b"},
           {'x':"ranker-maxr-autfilt", 'y':"seminator-autfilt", 'xname': "Ranker-MaxR+PP", 'yname': "Seminator 2+PP", 'max': 10000, 'tickCount': 3, 'filename': "fig_2a"},
           {'x':"ranker-maxr-autfilt", 'y':"piterman-autfilt", 'xname': "Ranker-MaxR+PP", 'yname': "Piterman+PP", 'max': 10000, 'tickCount': 3, 'filename': "fig_2b"},
           {'x':"ranker-maxr-autfilt", 'y':"fribourg-autfilt", 'xname': "Ranker-MaxR+PP", 'yname': "Fribourg+PP", 'max': 10000, 'tickCount': 3, 'filename': "fig_2c"},
           {'x':"ranker-maxr-autfilt", 'y':"roll-autfilt", 'xname': "Ranker-MaxR+PP", 'yname': "ROLL+PP", 'max': 10000, 'tickCount': 3, 'filename': "fig_2d"},
          ]

# add fields where not present
for params in to_cmp2:
  if 'xname' not in params:
    params['xname'] = None
  if 'yname' not in params:
    params['yname'] = None
  if 'max' not in params:
    params['max'] = states_timeout
  if 'tickCount' not in params:
    params['tickCount'] = 5

size = 8
plot_list = [(params['x'], params['y'], params['filename'], scatter_plot(df,
                                 xcol=params['x'] + '-States', ycol=params['y'] + '-States',
                                 xname=params['xname'], yname=params['yname'],
                                 domain=[states_min, params['max']],
                                 tickCount=params['tickCount'],
                                 log=True, width=size, height=size)) for params in to_cmp2]

print("\n\n")
print("Generating plots...")
for x, y, filename, plot in plot_list:
  filename = f"plots/{filename}.pdf"
  print(f"plotting x: {x}, y: {y}... saving to {filename}")
  #plot.save(filename, scale_factor=2)
  plot.save(filename)
  print(plot)
