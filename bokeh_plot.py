#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bokeh.io import vform
from bokeh.models import CustomJS, ColumnDataSource
from bokeh.models import Select, Button, Slider, HBox, VBoxForm
from bokeh.plotting import Figure, output_file, save
from bokeh.embed import components
from bokeh.io import curdoc

import shutil

# Usage: import do_a_plot and feed it a table
# currently takes Pandas DataFrame as input; haven't tested
# other formats such as astropy tables

# output_file("templates/callback.html") # currently writes to a file
# should change to output JS and HTML strings to pass to template

def get_error_tuples(val,err,pos,alpha=0.6):
	# val: the coordinates on the axis with error bars (i.e., y coordinates if plotting y errs, etc)
	# err: the given error (assuming 1 sigma)
	# pos: the coordinates on the axis opposite the error bars (x coordinates if y errs, etc)
	err_width = [(i, j) for i, j in zip(x - xerr, x + xerr)]
	err_pos = [(i, i) for i in pos]
	#plot.multi_line(err_width, err_ypos, alpha=alpha)

def do_a_plot(table):
	#print table.columns
	table.columns = [c.strip() for c in table.columns]
	#df.columns = ['a', 'b']
	column_list = list(table)
	#print column_list
	#print table[column_list[0]]
	marker_size = 5
	alpha = 0.9
	table['blank_x'] = '' # add fake columns for plotting
	table['blank_y'] = ''
	table['marker_size'] = marker_size
	table['alpha'] = alpha
	#table['blank_x_err'] = ''
	#table['blank_y_err'] = ''
	source = ColumnDataSource(data=dict(table))

	plot = Figure(plot_width=600, plot_height=600)
	scatter = plot.scatter('blank_x', 'blank_y', size='marker_size', line_alpha='alpha', fill_alpha='alpha',
		source=source, _changing=True)
	scatter.glyph._changing = True
	# line = plot.line('blank_x', 'blank_y', source=source, visible=False, _changing=True)

	main_callback = CustomJS(args=dict(source=source,
		xaxis=plot.xaxis[0],
		yaxis=plot.yaxis[0]), code="""
	        var data = source.get('data');
	        var f = cb_obj.get('value').trim();
	        console.log(f);
	        // for(var propertyName in data) {
			// 	console.log('name ' + propertyName + ', name_stripped ' + propertyName.trim());
			// }
	        var axis = cb_obj.get('title')[0].toLowerCase();
	        // console.log(axis);
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

	slider_js = """
			var property = cb_obj.get('title');
			var propname;
			if (property.search('Size') != -1) {
				propname = 'marker_size';
			} else if (property.search('Transparency') != -1) {
				propname = 'alpha';
			} else {
				return false;
			}
	        var val = cb_obj.get('value');
	        marker_prop = source.get('data')[propname];
	        for (i = 0; i < marker_prop.length; i++) {
	            marker_prop[i] = val;
	        }
	        source.trigger('change');
	    """

	reverse_js = """
			var start = range.get("start");
			var end = range.get("end");
			range.set({"start": end, "end": start});
			return false;
		"""
	reverse_x_callback = CustomJS(args=dict(range=plot.x_range), code=reverse_js)
	reverse_y_callback = CustomJS(args=dict(range=plot.y_range), code=reverse_js)
	marker_callback = CustomJS(args=dict(source=source), code=slider_js)
	alpha_callback = CustomJS(args=dict(source=source), code=slider_js)

	select_x = Select(title="X Options:", value=column_list[0], options=column_list, callback=main_callback)
	select_y = Select(title="Y Options:", value=column_list[0], options=column_list, callback=main_callback)
	# select_c = Select(title="Color Weight:", value=column_list[0], options=column_list, callback=main_callback)	
	slider_marker = Slider(title="Marker Size", start=1, end=30, value=marker_size, step=1, callback=marker_callback)
	slider_alpha = Slider(title="Marker Transparency", start=0, end=1,
		value=alpha, step=0.05, callback=alpha_callback)
	reverse_x_button = Button(label="Reverse X range", type="success", callback=reverse_x_callback)
	reverse_y_button = Button(label="Reverse Y range", type="success", callback=reverse_y_callback)

	# layout = vform(select_x, select_y, reverse_x_button, reverse_y_button, plot)
	
	controls = [select_x, select_y, slider_marker, slider_alpha, reverse_x_button, reverse_y_button]
	inputs = HBox(VBoxForm(*controls))
	layout = HBox(inputs, plot)
	curdoc().add_root(layout)

	output_file('bokeh_plot.html') # currently writes to a file
	save(curdoc())
	shutil.copy('bokeh_plot.html', 'templates/')

	script, div = components(layout)
	return script, div
