import pandas as pd
from bokeh_plot import do_a_plot

tab = pd.read_csv('../uncrowded_everything_all_clipped.csv')

do_a_plot(tab)