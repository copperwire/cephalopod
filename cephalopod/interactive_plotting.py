from bokeh.models import HoverTool, TapTool, BoxZoomTool, BoxSelectTool, PreviewSaveTool, ResetTool
from bokeh.models.widgets import Panel, Tabs, TextInput, RadioGroup, Button
from bokeh.models.sources import ColumnDataSource
from bokeh.io import output_file, show, vform, hplot
from bokeh.palettes import Spectral11, RdPu9, Oranges9
from bokeh.plotting import figure, output_server, curdoc
from bokeh.client import push_session
from bokeh.models import Range1d, LogAxis, LinearAxis
from .path_handler import directory_chooser

import os
import random
import numpy as np 

import tkinter
from tkinter import filedialog

from cephalopod import file_handler

class interactive_plotting:

	def __init__(self, filenames = None):

		if filenames is not None:
			self.filenames = filenames
		else: 
			print("""If you want to pass  files directly do it by interactive_plotting(filenames = list) """)
			root = tkinter.Tk()
			files = filedialog.askopenfilenames(parent=root,title='Choose files')
			root.quit()
			self.filenames = files

		self.generation = False

		if not isinstance(self.filenames, (list, np.ndarray, tuple, set, str)):
			self.filenames = [self.filenames]

		if not self.filenames:
			raise TypeError("Filnames can't be an empty list or empty object of type %s" %type(self.filenames)) 

		self.tentacle()


	def tentacle(self):
		self.data_generation()
		self.plotting()

	def data_generation (self):
		"""
		Evaluates all files supplied to class and sets the filename and sample id as attributes containing the list 
		of data sets from each file. e.g.:

		filename = 151118h.dp
		sample id = 600c

		then the attribute "151118h_600c" exists as a variable in the class. The attribute is a list of dictionaries
		with keys such that for each index of  the attribute:

		151118h_600c[i] for i in [number of files]:
			data = 2 x n nested list where data[0] contains all data points corresponding to the key \" x_unit \"
			x_unit = string with physical unit of data[0]
			y_unit = string with physical unit of data[1]
			sample info = nested list containing sample id, original filename, sample code etc.
			sample_element = name of the element measured by the SIMS process  		 
		"""

		self.generation = True
		self.attribute_ids = []

		for filename in self.filenames:

			class_instance = file_handler(filename)
			class_instance.file_iteration()
			data_sets = class_instance.data_conversion()

			name_check = data_sets["gen_info"]["DATA FILES"]

			attr_id = name_check[1][4][:-3] + "_" + name_check[2][2]

			self.attribute_ids.append(attr_id)
			setattr(self, attr_id, data_sets)

	def version(self):
		print("Version 0.14a1 ")

	def plotting(self):

		#Tools = [hover, TapTool(), BoxZoomTool(), BoxSelectTool(), PreviewSaveTool(), ResetTool()]
		TOOLS="crosshair,pan,wheel_zoom,box_zoom,reset,hover,previewsave"


		tab_plots = []
		#output_file("test.html")
		self.all_elements = []
		self.elements_comparison = []

		for attr_id, i in zip(self.attribute_ids, range(len(self.attribute_ids))):
			
			"""
			create plots for each datafile and put them in a tab.
			"""
			data_dict = getattr(self, attr_id)

			y_axis_units = [x["y_unit"] for x in data_dict["data"].values()]
			x_axis_units = [x["x_unit"] for x in data_dict["data"].values()]

			figure_obj = figure(plot_width = 1000, plot_height = 800, y_axis_type = "log",
			title = attr_id, tools = TOOLS)
			#figure_obj.axes.major_label_text_font_size("12pt")
			#figure_obj.major_label_text_font_size("12pt")
			
			setattr(self, attr_id+"_"+"figure_obj",figure_obj)

			figure_obj.yaxis.axis_label = y_axis_units[0]
			figure_obj.xaxis.axis_label = x_axis_units[0]

			if not all(x == y_axis_units[0] for x in y_axis_units):
				for unit, dataset in zip(y_axis_units, data_dict["data"].values()): 
					if not unit == y_axis_units[0]:
						figure_obj.extra_y_ranges =  {"foo": Range1d(start = np.amin(dataset["y"]),
						end = np.amax(dataset["y"]))}
						figure_obj.add_layout(LogAxis(y_range_name = "foo", axis_label = unit), "right")
						break

			if not all(x == x_axis_units[0] for x in x_axis_units):
				for unit, dataset in zip(x_axis_units, data_dict["data"].values()): 
					if not unit == x_axis_units[0]:
						figure_obj.extra_x_ranges =  {"bar": Range1d(start = np.amin(dataset["x"]),
						end = np.amax(dataset["x"]))}
						figure_obj.add_layout(LinearAxis(x_range_name = "bar", axis_label = unit), "above")
						break



			figure_obj.xaxis.axis_label = x_axis_units[0]
			colour_list = Spectral11 + RdPu9 + Oranges9
			colour_indices = [0, 2, 8, 10, 12, 14, 20, 22, 1, 3, 9, 11, 13, 15]

			list_of_elements = []

			for dataset, color_index in zip(data_dict["data"].values(), colour_indices):

				self.all_elements.append(dataset["sample_element"]) #strip isotope number 
				color = colour_list[color_index]

				source = ColumnDataSource(data = dataset) #Datastructure for source of plotting

				setattr(self, attr_id+"_"+dataset["sample_element"]+"_source", source) #Source element generalized for all plotting				


				list_of_elements.append(dataset["sample_element"])

				figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample_element"]
								+"_source"), line_width = 2, line_color = color, 
								legend = dataset["sample_element"], name = dataset["sample_element"],
								 )

			hover = figure_obj.select_one(HoverTool).tooltips = [("element", "@element"), ("(x,y)", "($x, $y)")]

			radio_group = RadioGroup(labels = list_of_elements, active=0)

			"""
			Need to fetch default variables from input file and replace DEFAULT

			Block of code produces the layout of buttons and callbacks
			"""

			
			#Calculations on the dataset
			text_input_rsf = TextInput(value = "default", title = "RSF (at/cm^3): ")
			do_integral_button = Button(label = "Calibration Integral")
			smoothing_button = Button(label = "smth selct elem")

			text_input_sputter = TextInput(value = "default", title = "Sputter speed: float unit")
			text_input_crater_depth = TextInput(value = "default", title = "Depth of crater in: float")
			

			radio_group.on_change("active", lambda attr, old, new: None)

			text_input_xval_integral = TextInput(value = "0", title = "x-delimiter ")
			text_input_yval_integral = TextInput(value = "0", title = "y-delimiter ")

			#Save files for later use
			save_flexDPE_button = Button(label = "Save element for FlexPDE")
			save_all_flexDPE_button = Button(label = "Save all elements for FlexPDE")
			save_textfile_button = Button(label = "Sava Data in textfile")


			#Pointers to methods on click / change handlers
			do_integral_button.on_click(lambda identity = self.attribute_ids[i], radio = radio_group, 
										x_box = text_input_xval_integral, y_box = text_input_yval_integral: 
										self.integrate(identity, radio, x_box, y_box))

			smoothing_button.on_click(lambda identity = self.attribute_ids[i], radio = radio_group, 
										x_box = text_input_xval_integral, y_box = text_input_yval_integral: 
									self.smoothing(identity, radio, x_box, y_box) )

			save_flexDPE_button.on_click(lambda identity = self.attribute_ids[i], radio = radio_group: 
										self.write_to_flexPDE(identity, radio))

			save_all_flexDPE_button.on_click(lambda identity = self.attribute_ids[i], radio = radio_group:
											self.write_all_to_flexPDE(identity, radio))

			save_textfile_button.on_click(lambda identity = self.attribute_ids[i], radio = radio_group:
											self.write_new_datafile(identity, radio))


			text_input_rsf.on_change("value", lambda attr, old, new, radio = radio_group, 
								identity = self.attribute_ids[i], text_input = text_input_rsf, which = "rsf":
								self.update_data(identity, radio, text_input, new, which))


			text_input_sputter.on_change("value", lambda attr, old, new, radio = radio_group, 
								identity = self.attribute_ids[i], text_input = text_input_sputter, which = "sputter":
								self.update_data(identity, radio, text_input, new, which))

			text_input_crater_depth.on_change("value", lambda attr, old, new, radio = radio_group, 
								identity = self.attribute_ids[i], text_input = text_input_crater_depth, which = "crater_depth":
								self.update_data(identity, radio, text_input, new, which))


			#Initialization of actual plotting. 
			tab_plots.append(Panel(child = hplot(figure_obj, 
										   vform(radio_group, save_flexDPE_button, save_all_flexDPE_button, save_textfile_button), 
										   vform(text_input_rsf, smoothing_button, text_input_sputter, text_input_crater_depth),
										   vform(text_input_xval_integral, text_input_yval_integral, do_integral_button)),
										   title = attr_id))


		"""
		Check to see if one or more element exists in the samples and creat a comparison plot for each 
		of those elements.
		"""
		
		for element in self.all_elements:
			checkers = list(self.all_elements)
			checkers.remove(element)
			if element in checkers and not element in self.elements_comparison:
				self.elements_comparison.append(element)

		"""create plots for each element that is to be compared """
	
		for comparison_element in self.elements_comparison: 

			colour_list = Spectral11 + RdPu9 + Oranges9
			colour_indices = [0, 2, 8, 10, 12, 14, 20, 22, 1, 3, 9, 11, 13, 15]
			figure_obj = figure(plot_width = 1000, plot_height = 800, y_axis_type = "log", title = comparison_element, tools = TOOLS)
			#figure_obj.xaxis.major_label_text_font_size("12pt")
			#figure_obj.yaxis.major_label_text_font_size("12pt")
			

			y_axis_units = []
			x_axis_units = []

			comparison_datasets = []


			for attr_id, color_index in zip(self.attribute_ids, colour_indices):

				data_dict = getattr(self, attr_id)

				for dataset in data_dict["data"].values():

					if dataset["sample_element"] == comparison_element:
						comparison_datasets.append(dataset)
						y_axis_units.append(dataset["y_unit"])
						x_axis_units.append(dataset["x_unit"])

			figure_obj.xaxis.axis_label = comparison_datasets[-1]["x_unit"]
			figure_obj.yaxis.axis_label = comparison_datasets[-1]["y_unit"]

			if not all(x == y_axis_units[-1] for x in y_axis_units):
				for unit, data in zip(y_axis_units, comparison_datasets): 
					if not unit == y_axis_units[-1]:
						figure_obj.extra_y_ranges =  {"foo": Range1d(start = np.amin(data["y"]),
						end = np.amax(data["y"]))}
						figure_obj.add_layout(LogAxis(y_range_name = "foo", axis_label = unit), "right")
						break

			if not all(x == x_axis_units[-1] for x in x_axis_units):
				for unit, data in zip(x_axis_units, comparison_datasets): 
					if not unit == x_axis_units[-1]:
						figure_obj.extra_x_ranges =  {"bar": Range1d(start = np.amin(data["x"]),
						end = np.amax(data["x"]))}
						figure_obj.add_layout(LinearAxis(x_range_name = "bar", axis_label = unit), "above")
						break


			for attr_id, color_index in zip(self.attribute_ids, colour_indices):

				data_dict = getattr(self, attr_id)

				for dataset in data_dict["data"].values():

					if dataset["sample_element"] == comparison_element:
						color = colour_list[color_index]

						"""
						Logic that ensures that plots get put with correspoinding axes. 
						"""
						if dataset["x_unit"] != x_axis_units[-1] or dataset["y_unit"] != y_axis_units[-1]:

							if dataset["x_unit"] != x_axis_units[-1] and dataset["y_unit"] != y_axis_units[-1]:

								figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample_element"]+"_source"), line_width = 2, 
								line_color = color, legend = attr_id, x_range_name = "bar", y_range_name = "foo")

							elif dataset["x_unit"] != x_axis_units[-1]:

								figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample_element"]+"_source"), line_width = 2, 
								line_color = color, legend = attr_id, x_range_name = "bar")

							else: 

								figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample_element"]+"_source"), line_width = 2, 
								line_color = color, legend = attr_id, y_range_name = "foo")

						else: 
							figure_obj.line("x", "y", source = getattr(self, attr_id+"_"+dataset["sample_element"]+"_source"), line_width = 2, 
							line_color = color, legend = attr_id)
						


			tab_plots.append(Panel(child = figure_obj, title = comparison_element))	

		tabs = Tabs(tabs = tab_plots)

		session = push_session(curdoc())
		session.show()
		session.loop_until_closed()

	def raw_data(self):

		if self.generation:
			y = {}
			for name in self.attribute_ids:
				y[name] = getattr(self, name)
			return y	
		else:
			self.data_generation()
			self.raw_data()

	def integrate(self,  attrname, radio, x_box, y_box):

		element = radio.labels[radio.active]
		source_local = getattr(self, attrname+"_"+element+"_source") 

		lower_xlim = float(x_box.value)
		lower_ylim = float(y_box.value)

		x = np.array(source_local.data["x"])
		y = np.array(source_local.data["y"])

		x_change = x[x>lower_xlim]*1e-4 
		y_change = y[len(y)-len(x_change):]

		integral = np.trapz(y_change, x = x_change)

		comparsion = np.sum(y) * x[-1]*1e-4

		print(integral, comparsion)

	def write_to_flexPDE(self, attrname, radio):
		element = radio.labels[radio.active]

		source_local = getattr(self, attrname+"_"+element+"_source")  #attr_id+"_"+dataset["sample_element"]+"_source"

		x = np.array(source_local.data["x"])
		y = np.array(source_local.data["y"])

		path_to_flex = directory_chooser()
		write_to_filename = path_to_flex+"/"+attrname+ "_"+element+".txt"

		file_object = open(write_to_filename, "w+")

		file_object.write("X %i \n" %len(x)) 
		
		for item in x: 
			file_object.write("%1.3f " %item) 

		file_object.write("\nData {u} \n")

		for item in y: 
			file_object.write("%1.1e " %item) 

		file_object.close()

	def write_all_to_flexPDE(self, attrname, radio):
		path_to_flex = directory_chooser()
		
		for element in radio.labels:
		
			source_local = getattr(self, attrname+"_"+element+"_source")  #attr_id+"_"+dataset["sample_element"]+"_source"

			x = np.array(source_local.data["x"])
			y = np.array(source_local.data["y"])
			write_to_filename = path_to_flex+"/"+attrname+ "_"+element+".txt"

			file_object = open(write_to_filename, "w+")

			file_object.write("X %i \n" %len(x)) 
			
			for item in x: 
				file_object.write("%1.3f " %item) 

			file_object.write("\nData {u} \n")

			for item in y: 
				file_object.write("%1.1e " %item) 

			file_object.close()

	
	def write_new_datafile(self, attrname, radio):
		data_dict = getattr(self, attrname)
		direct = directory_chooser()
		filename = direct+"/"+"pd_"+attrname+".dp_rpc_apc"
		file_object = open(filename, "w+")

		source_local_len = getattr(self, attrname+"_"+radio.labels[radio.active]+"_source")
		iter_over = len(np.array(source_local_len.data["y"]))

		for  delim, attr in data_dict["gen_info"].items():
			if delim == "DATA START" or delim =="DATA END":
				continue	
			file_object.write("*** "+delim+" ***")
			file_object.write("\n")
			for list_obj in attr:
				for word in list_obj:
					file_object.write(str(word) + " ")
				file_object.write("\n")	
			file_object.write("\n")			

		file_object.write("*** DATA START ***\n")
		file_object.write("\n")
		file_object.write(attrname[:attrname.find("_")]+"\n")

		for element in radio.labels:
			file_object.write("%s                                     "%element)
		file_object.write("\n")

		dataset = data_dict["data"]

		for key in radio.labels:
			file_object.write("Time    %s       %s       " %(dataset[key]["x_unit"], dataset[key]["y_unit"])) 

		file_object.write("\n")

		for i in range(iter_over):

			for place in radio.labels:
				source_local = getattr(self, attrname+"_"+place+"_source")
				x = source_local.data["x"]
				y = source_local.data["y"]
				
				if dataset[place]["x_unit"] == "Time":
					file_object.write("%1.5e            %1.5e      "%(x[i], y[i]))
				else:
					file_object.write("        %1.5e    %1.5e      "%(x[i], y[i])) 
			
			file_object.write("\n")
		file_object.write("\n")
		file_object.write("*** DATA END ***")
		file_object.close()

	def smoothing(self, attrname, radio, x_box, y_box):
		element = radio.labels[radio.active]

		lower_xdelim = float(x_box.value)
		lower_ydelim = float(y_box.value)

		source_local = getattr(self, attrname+"_"+element+"_source")  #attr_id+"_"+dataset["sample_element"]+"_source"

		x = np.array(source_local.data["x"])
		y = np.array(source_local.data["y"])
		
		zero = 0

		if lower_xdelim != 0:
			i = 0
			for value in x:
				if value > lower_xdelim:
					zero = i
					break
				i += 1

		#Maybe user should define the alpha? 
		alpha = 0.5 #some number between 0 and 1, needs be adjusted

		s1 = y[zero]
		ema = np.zeros(len(y[zero:]))
		ema[0] = s1
		j = 1
		
		for val in y[zero+1:]:
			ema[j] = alpha * val + (1-alpha) * ema[j-1]
			j += 1 

		adj_ema = np.append(y[:zero], ema)

		source_local.data = dict(x = x, y = adj_ema, element = [element for i in range(len(x))])


	def estimate_RSF(self, attrname, radio):
		ion_pot = np.loadtxt("/home/solli/Documents/octopus/RSF_estimation/ionization_potentials.txt")
		ion_pot = np.reshape(ion_pot, (np.shape(ion_pot)[1], np.shape(ion_pot)[0]))

		
	def update_data(self, attrname, radio, text_input, new, which):

		if which == "rsf":
			element = radio.labels[radio.active]
			
			try:
				RSF = float(new)
			except ValueError:
				RSF = 1.
				#text_input.value = "ERROR: PLEASE INPUT NUMBER"

			source_local = getattr(self, attrname+"_"+element+"_source")  #attr_id+"_"+dataset["sample_element"]+"_source"

			x = np.array(source_local.data["x"])
			y = np.array(source_local.data["y"])

			y = RSF*y
			
			# DOES NOT WORK
			text_input = TextInput(value = "%.2e" %13331, title = "RSF (at/cm^3): ")
			######

			data_dict = getattr(self, attrname)

			for dataset in data_dict["data"].values():
				if element in dataset["sample_element"]:
					dataset["y_unit"] = "C[at/cm^3]"

					for line in data_dict["gen_info"]["CALIBRATION PARAMETERS"]:
						if "RSF" in line:
							line.append("%1.3e" %RSF) 
							break
	
			"""
			#include snippet to update axis:
			#useless without being able to change the figure.line glyph that hosts the line for which the RSF
			#is being calculated

			figure_obj = getattr(attr_id+"_"+"figure_obj")

			if len(figure_obj.yaxis) == 1:
				figure_obj.extra_y_ranges =  {"foo": Range1d(start = np.amin(data["data"]["y"]),
				end = np.amax(data["data"]["y"]))}
				figure_obj.add_layout(LogAxis(y_range_name = "foo", axis_label = "C[cm^-3]"), "right")
			"""

			source_local.data = dict(x = x, y = y, element = [element for i in range(len(x))]) 
		
		elif which == "sputter" or which == "crater_depth":
			"""
			Should create new axis and push to active session to replace the plot? 
			Or simply append new x-axis? Need to identify if there exists a second x-axis allready
			"""

			if which == "sputter":
				try:
					sputter_speed, unit = new.split()
					sputter_speed = float(sputter_speed) 
				except ValueError:
					return

			elif which == "crater_depth":
				try: 
					crater_depth, unit = new.split()
					sputter_speed = float(crater_depth) / x[-1]

				except ValueError:
					return

			figure_obj = getattr(self, attrname+"_"+"figure_obj")

			data = getattr(self, attrname)

			if not "No" in data["gen_info"]["ACQUISITION PARAMETERS"][5]: 

				data["gen_info"]["ACQUISITION PARAMETERS"][5] = "Crater Depth Measurement        Yes" 
				if unit == "nm":
					data["gen_info"]["ACQUISITION PARAMETERS"][6].append(str(sputter_speed * x[-1]))
					for value in data["data"].values():
						value["x_unit"] = "Depth[nm]"

				elif unit == "um":
					data["gen_info"]["ACQUISITION PARAMETERS"][6].append(str(sputter_speed * x[-1]*1e-3))
					for value in data["data"].values():
						value["x_unit"] = "Depth[um]"

				for element in radio.labels: 
					source_local = getattr(self, attrname+"_"+element+"_source")  #attr_id+"_"+dataset["sample_element"]+"_source"
					x = np.array(source_local.data["x"])
					y = np.array(source_local.data["y"])

					x = x*sputter_speed
				
					source_local.data = dict(x = x, y = y) 
					figure_obj.xaxis.axis_label = "Depth " + " " + "[" + unit + "]"
