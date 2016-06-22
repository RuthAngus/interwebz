from bokeh.io import vform
from bokeh.models import CustomJS, ColumnDataSource
from bokeh.models import Select, Button #, MultiSelect
from bokeh.plotting import Figure, output_file, save
# import pandas as pd

# Usage: import do_a_plot and feed it a table
# currently takes Pandas DataFrame as input; haven't tested
# other formats such as astropy tables

output_file("callback.html") # currently writes to a file
# should change to output JS and HTML strings to pass to template

def get_error_tuples(val,err,pos,alpha=0.6):
	# val: the coordinates on the axis with error bars (i.e., y coordinates if plotting y errs, etc)
	# err: the given error (assuming 1 sigma)
	# pos: the coordinates on the axis opposite the error bars (x coordinates if y errs, etc)
	err_width = [(i, j) for i, j in zip(x - xerr, x + xerr)]
	err_pos = [(i, i) for i in pos]
	#plot.multi_line(err_width, err_ypos, alpha=alpha)

def do_a_plot(table):
	column_list = list(table)
	table['blank_x'] = '' # add fake columns for plotting
	table['blank_y'] = ''
	table['blank_x_err'] = ''
	table['blank_y_err'] = ''
	source = ColumnDataSource(data=dict(table))

	plot = Figure(plot_width=500, plot_height=500)
	scatter = plot.scatter('blank_x', 'blank_y', source=source, _changing=True)
	# line = plot.line('blank_x', 'blank_y', source=source, visible=False, _changing=True)

	main_callback = CustomJS(args=dict(source=source,
		xaxis=plot.xaxis[0],
		yaxis=plot.yaxis[0]), code="""
	        var data = source.get('data');
	        var f = cb_obj.get('value');
	        var axis = cb_obj.get('title')[0].toLowerCase();
	        if (axis == 'x') {
	        	xaxis.set({"axis_label": f});
	        } else if (axis == 'y') {
	        	yaxis.set({"axis_label": f});
	        } else {
	        	return false;
	        }
	        blank_data = data['blank_' + axis];
	        for (i = 0; i < blank_data.length; i++) {
	            blank_data[i] = data[f][i];
	        }
	        source.trigger('change');
	    """)

	reverse_js = """
			var start = range.get("start");
			var end = range.get("end");
			range.set({"start": end, "end": start});
			return false;
		"""
	reverse_x_callback = CustomJS(args=dict(range=plot.x_range), code=reverse_js)
	reverse_y_callback = CustomJS(args=dict(range=plot.y_range), code=reverse_js)

	select_x = Select(title="X Options:", value=column_list[0], options=column_list, callback=main_callback)
	select_y = Select(title="Y Options:", value=column_list[0], options=column_list, callback=main_callback)
	reverse_x_button = Button(label="Reverse X range", type="success", callback=reverse_x_callback)
	reverse_y_button = Button(label="Reverse Y range", type="success", callback=reverse_y_callback)

	layout = vform(select_x, select_y, reverse_x_button, reverse_y_button, plot)

	save(layout)
