#!/usr/bin/env python3

# PREAMBLE
import altair as alt
import pandas as pd
import re as re
import tabulate as tab

FILE_INPUT = "results.csv"

# in seconds
TIMEOUT = 300
TIMEOUT_VAL = TIMEOUT * 1.1
TIME_MIN = 0.01

# do not care about the limit
alt.data_transformers.disable_max_rows()

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
def scatter_plot(df, xcol, ycol, domain, xname=None, yname=None, log=False, width=600, height=600, tickCount=5):
    assert len(domain) == 2

    if xname == None:
      xname = xcol
    if yname == None:
      yname = ycol

    plot_type = "log" if log else "linear"
    scatter = alt.Chart(df).mark_point(size=10, filled=True).encode(
       x=alt.X(xcol + ':Q', axis=alt.Axis(title=xname, tickCount=tickCount), scale=alt.Scale(type=plot_type, base=10, domain=domain, clamp=True)),
       y=alt.Y(ycol + ':Q', axis=alt.Axis(title=yname, tickCount=tickCount), scale=alt.Scale(type=plot_type, base=10, domain=domain, clamp=True))
       )

    rules = (alt.Chart(pd.DataFrame({'y': [domain[1]]})).mark_rule(strokeDash=[3,1]).encode(y='y') +
             alt.Chart(pd.DataFrame({'x': [domain[1]]})).mark_rule(strokeDash=[3,1]).encode(x='x'))

    diag = alt.Chart(pd.DataFrame({'x': domain, 'y': domain})).mark_line(color='black', strokeDash=[3,1], size=1).encode(x='x', y='y')

    res = scatter + rules + diag
    res = res.properties(
        width=width, height=height
        )

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
df = df[df['ranker-Transitions'] != 0]
df = df[df['ranker-autfilt-States'] != 1]

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
interesting = ["ranker-nopost",
               "ranker-tight-nopost",
               "schewe",
               "ranker-autfilt",
               "ranker-composition-autfilt",
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
interesting = ["ranker",
               "ranker-composition",
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
compare_methods = [("ranker-nopost-States", "ranker-tight-nopost-States"),
                   ("ranker-nopost-States", "schewe-States"),
                   ("ranker-autfilt-States", "piterman-autfilt-States"),
                   ("ranker-autfilt-States", "safra-autfilt-States"),
                   ("ranker-autfilt-States", "spot-autfilt-States"),
                   ("ranker-autfilt-States", "fribourg-autfilt-States"),
                   ("ranker-autfilt-States", "seminator-autfilt-States"),
                   ("ranker-autfilt-States", "roll-autfilt-States"),
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

ranker_best = df[df['ranker-autfilt-States'] < df['other_min']]
ranker_not_best = df[df['ranker-autfilt-States'] > df['other_min']]

num_ranker_not_strictly_best = len(df) - len(ranker_not_best)
num_ranker_not_strictly_best_percent = "{:.1f}".format(num_ranker_not_strictly_best / len(df) * 100)
num_ranker_strictly_best = len(ranker_best)
num_ranker_strictly_best_percent = "{:.1f}".format(num_ranker_strictly_best / len(df) * 100)
print(f"ranker non-strictly best: {num_ranker_not_strictly_best} (= {num_ranker_not_strictly_best_percent} %)")
print(f"ranker stricly best: {num_ranker_strictly_best} (= {num_ranker_strictly_best_percent} %)")
# print(f"ranker not best = {len(ranker_not_best)}")

###########   BackOff   ################
backoff = df[df["ranker-composition-Engine"].str.contains("GOAL", na=False)]
print(f"backoff executions: {len(backoff)}")



to_cmp = [
  ('ranker', 'seminator'),
  ('ranker', 'safra'),
#  ('ranker', 'goal-default'),            # -- this is Piterman
  ('ranker', 'piterman'),
  ('ranker', 'schewe'),
  ('ranker', 'fribourg'),
  ('ranker', 'spot'),
  ('ranker', 'roll'),
  ('ranker', 'ranker-tight'),
]

to_cmp2 = [{'x':"ranker-nopost", 'y':"ranker-tight-nopost", 'xname':'Ranker-MaxR', 'yname':'Ranker-RRestr', 'filename': "fig_1a"},
           {'x':"ranker-nopost", 'y':"schewe", 'xname': "Ranker-MaxR", 'yname': "Schewe-RedAvgOut", 'filename': "fig_1b"},
           {'x':"ranker-autfilt", 'y':"seminator-autfilt", 'xname': "Ranker-MaxR+PP", 'yname': "Seminator 2+PP", 'max': 10000, 'tickCount': 3, 'filename': "fig_2a"},
           {'x':"ranker-autfilt", 'y':"piterman-autfilt", 'xname': "Ranker-MaxR+PP", 'yname': "Piterman+PP", 'max': 10000, 'tickCount': 3, 'filename': "fig_2b"},
           {'x':"ranker-autfilt", 'y':"fribourg-autfilt", 'xname': "Ranker-MaxR+PP", 'yname': "Fribourg+PP", 'max': 10000, 'tickCount': 3, 'filename': "fig_2c"},
           {'x':"ranker-autfilt", 'y':"roll-autfilt", 'xname': "Ranker-MaxR+PP", 'yname': "ROLL+PP", 'max': 10000, 'tickCount': 3, 'filename': "fig_2d"},
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

size = 400
plot_list = [(params['x'], params['y'], params['filename'], scatter_plot(df,
                                 xcol=params['x'] + '-States', ycol=params['y'] + '-States',
                                 xname=params['xname'], yname=params['yname'],
                                 domain=[states_min, params['max']],
                                 tickCount=params['tickCount'],
                                 log=True, width=size, height=size)) for params in to_cmp2]

print("\n\n")
print("Generating plots...")
for x, y, filename, plot in plot_list:
  filename = f"plots/{filename}.png"
  print(f"plotting x: {x}, y: {y}... saving to {filename}")
  plot.save(filename, scale_factor=2)
