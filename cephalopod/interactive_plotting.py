from bokeh.models import HoverTool, TapTool, BoxZoomTool, BoxSelectTool, PreviewSaveTool, ResetTool
from bokeh.models.widgets import Panel, Tabs, TextInput, RadioGroup, Button
from bokeh.models.sources import ColumnDataSource
from bokeh.io import output_file, show, vform, hplot
from bokeh.palettes import Spectral11, RdPu9, Oranges9
from bokeh.plotting import figure, output_server, curdoc
from bokeh.client import push_session
from bokeh.models import Range1d, LogAxis, LinearAxis
from .path_handler import directory_chooser
from .plotting_module import plotter
import threading
import sys

#figure = Figure

import matplotlib.pyplot as plt

import os
import random
import numpy as np 

from tkinter import  Tk, filedialog
from cephalopod import file_handler

class interactive_plotting:

	def __init__(self, filenames = None, tk_root_obj = None, debug = False):

		if filenames is not None:
			self.filenames = filenames
		else: 
			self.get_files(tk_root_obj)

		if not isinstance(self.filenames, (list, np.ndarray, tuple, set, str)):
			self.filenames = [self.filenames]

		if not self.filenames:
			raise TypeError("Filnames can't be an empty list or empty object of type %s" %type(self.filenames)) 

		self.debug = debug
		if debug:
			self.debug_file_setup()

		self.source_line= []
		self.figure_data = []

		self.attribute_ids = []
		self.tentacle()


	def tentacle(self):
		self.plotting()

	def debug_file_setup(self):
		self.debug_file = open("debug_output.txt", "w")
		self.debug_file.write("Initialized debug file")
		self.debug_file.close()

	def get_files(self, tk_root):
		if tk_root is not None:
			print("""If you want to pass  files directly do it by interactive_plotting(filenames = list) """)
			root = tk_root
			files = filedialog.askopenfilenames(parent=tk_root,title='Choose files')
			root.quit()
			self.filenames = files
		else:
			print("""If you want to pass  files directly do it by interactive_plotting(filenames = list) """)
			root = Tk()
			root.files = filedialog.askopenfilenames(title='Choose files')
			self.filenames = root.files
			root.withdraw()


	def data_generation (self, filename):
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
		class_instance = file_handler(filename)
		class_instance.file_iteration()

		if "ITO" in filename:
			data_sets = class_instance.data_conversion(mass_spectra = True)
		else:
			data_sets = class_instance.data_conversion()


		return data_sets


	def __version__(self):
		print("Version 0.15a0 ")
		return

	def plotting(self):

		if self.debug:
			self.debug_file = open("debug_output.txt", "w")
			self.debug_file.write("Initialized plotting subroutine")
			self.debug_file.close()

		TOOLS="pan,wheel_zoom,box_zoom,reset,hover,previewsave"

		tab_plots = []
		self.all_elements = []
		self.elements_comparison = []

		for filename in self.filenames:
	
			data_dict = self.data_generation(filename)
			self.data_test(data_dict)

			name_check = data_dict["gen_info"]["DATA FILES"]
			attr_id = name_check[1][4][:-3] + "_" + name_check[2][2]
			self.attribute_ids.append(attr_id)

			attr_extra_y_ranges = False
			attr_extra_x_ranges = False

			local_source_line = []

			"""
			create plots for each datafile and put them in a tab.
			"""

			y_axis_units = [x["y_unit"] for x in data_dict["data"]]
			x_axis_units = [x["x_unit"] for x in data_dict["data"]]

			figure_obj = figure(plot_width = 1000, plot_height = 800, y_axis_type = "log",
			title = attr_id, tools = TOOLS)
			#figure_obj.axes.major_label_text_font_size("12pt")
			#figure_obj.major_label_text_font_size("12pt")

			self.figure_data.append((figure_obj, data_dict))
		
			figure_obj.yaxis.axis_label = y_axis_units[0]
			figure_obj.xaxis.axis_label = x_axis_units[0]

			if not all(x == y_axis_units[0] for x in y_axis_units):
				for unit, dataset in zip(y_axis_units, data_dict["data"]): 
					if not unit == y_axis_units[0]:
						
						extra_y_ranges_exists = attr_extra_y_ranges
						extra_y_ranges_exists = True

						if self.debug:
							self.debug_file = open("debug_output.txt", "w")
							self.debug_file.write("Added extra y-axis for file_id: %s, element: %s | New length %g" 
								%(attr_id, dataset["sample_element"], len(figure_obj.yaxis)))
							self.debug_file.close()

						figure_obj.extra_y_ranges =  {"foo": Range1d(start = np.amin(dataset["y"]),
						end = np.amax(dataset["y"]))}
						figure_obj.add_layout(LogAxis(y_range_name = "foo", axis_label = unit), "right")
						break

			if not all(x == x_axis_units[0] for x in x_axis_units):
				for unit, dataset in zip(x_axis_units, data_dict["data"]): 
					if not unit == x_axis_units[0]:
						
						extra_x_ranges_exists = attr_extra_x_ranges
						extra_x_ranges_exists = True
						
						if self.debug:
							self.debug_file = open("debug_output.txt", "w")
							self.debug_file.write("Added extra x-axis for file_id: %s, element: %s. | New length %g" 
								%(attr_id, dataset["sample_element"], len(figure_obj.yaxis)))
							self.debug_file.close()
			
						figure_obj.extra_x_ranges =  {"bar": Range1d(start = np.amin(dataset["x"]),
						end = np.amax(dataset["x"]))}
						figure_obj.add_layout(LinearAxis(x_range_name = "bar", axis_label = unit), "above")
						break

			figure_obj.xaxis.axis_label = x_axis_units[0]
			colour_list = Spectral11 + RdPu9 + Oranges9
			colour_indices = [0, 2, 8, 10, 12, 14, 20, 22, 1, 3, 9, 11, 13, 15]


			list_of_elements = []
			source_list = []
			line_list = []

			for dataset, color_index in zip(data_dict["data"], colour_indices):

				self.all_elements.append(dataset["sample_element"]) #strip isotope number 
				color = colour_list[color_index]

				source = ColumnDataSource(data = dataset) #Datastructure for source of plotting

				self.source_test(source)

				list_of_elements.append(dataset["sample_element"])
				line_glyph = figure_obj.line("x", "y", source = source, 
							line_width = 2,
							line_color = color, 
							legend = dataset["sample_element"])

				if self.debug:
					self.debug_file = open("debug_output.txt", "w")
					self.debug_file.write("Create line object on figure %s  at %s" %(id(figure_obj), id(line_glyph)))
					self.debug_file.close()

				line_list.append(line_glyph)
				source_list.append(source)

			local_source_line.append([[source, line] for source, line in zip(source_list, line_list)])
			self.source_line.append(local_source_line)

			#Calculations on the dataset
			text_input_rsf = TextInput(value = "default", title = "RSF or SF (at/cm^3): ")
			do_integral_button = Button(label = "Calibration integral")
			smoothing_button = Button(label = "smth selct elem")
			matplot_button = Button(label = "Create matplotlib fig")

			text_input_sputter = TextInput(value = "default", title = "Sputter speed: number unit")
			text_input_crater_depth = TextInput(value = "default", title = "Depth of crater in: number unit")
			


			radio_group = RadioGroup(labels = list_of_elements, active=0)


			text_input_xval_integral = TextInput(value = "0", title = "x-delimiter ")
			text_input_dose = TextInput(value = "0", title = "Dose[cm^-2] ")

			#Save files for later use
			save_flexDPE_button = Button(label = "Save element for FlexPDE")
			save_all_flexDPE_button = Button(label = "Save all elements for FlexPDE")
			save_textfile_button = Button(label = "Sava Data in textfile")

			#Pointers to methods on click / change handlers
			radio_group.on_change("active", lambda attr, old, new: None)

			matplot_button.on_click(lambda source_list = source_list:
										self.matplotlib_export(source_list))
			
			do_integral_button.on_click(lambda 
											source_list = source_list, 
											line_list = line_list, 
											source_line = self.source_line,
											figure_data = self.figure_data,
											radio = radio_group,
											x_box = text_input_xval_integral, 
											dose = text_input_dose,
											extra_y_ranges = attr_extra_y_ranges: 
										self.integrate(source_list, line_list, source_line, figure_data, radio, x_box, dose, extra_y_ranges))

			smoothing_button.on_click(lambda 
										source_list = source_list,
										radio = radio_group, 
										data_dict = data_dict,
										x_box = text_input_xval_integral: 
									self.smoothing(source_list, data_dict, radio, x_box) )

			save_flexDPE_button.on_click(lambda 
											source_list = source_list,
											attrname = attr_id,
											radio = radio_group: 
										self.write_to_flexPDE(source_list, attrname, radio))

			save_all_flexDPE_button.on_click(lambda 
												source_list = source_list, 
												attrname = attr_id,
												radio = radio_group:
												self.write_all_to_flexPDE(source_list, attrname, radio))

			save_textfile_button.on_click(lambda 
											data_dict = data_dict, 
											source_list = source_list,
											attrname = attr_id,
											radio = radio_group:
											self.write_new_datafile(data_dict, source_list, attrname,radio))


			text_input_rsf.on_change("value", lambda attr, old, new, 
												radio = radio_group, 
												data_dict = data_dict,
												figure = figure_obj,
												source_list = source_list,
												text_input = text_input_rsf, 
												which = "rsf":
												self.update_data(data_dict, source_list, figure, radio, text_input, new, which))


			text_input_sputter.on_change("value", lambda attr, old, new, 
													radio = radio_group, 
													data_dict = data_dict,
													figure = figure_obj,
													source_list = source_list, 
													text_input = text_input_sputter,
													which = "sputter":
													self.update_data(data_dict, source_list, figure, radio, text_input, new, which))

			text_input_crater_depth.on_change("value", lambda attr, old, new, 
														radio = radio_group, 
														data_dict = data_dict,
														source_list = source_list,
														figure = figure_obj,
														text_input = text_input_crater_depth, 
														which = "crater_depth":
														self.update_data(data_dict, source_list, figure, radio, text_input, new, which))


			#Initialization of actual plotting. 
			tab_plots.append(Panel(child = hplot(figure_obj, 
										   vform(radio_group, save_flexDPE_button, save_all_flexDPE_button, save_textfile_button, matplot_button), 
										   vform(text_input_rsf, smoothing_button, text_input_sputter, text_input_crater_depth),
										   vform(text_input_xval_integral, text_input_dose, do_integral_button)),
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

			figure_obj = figure(plot_width = 1000, plot_height = 800, y_axis_type = "log", title = comparison_element, tools = TOOLS)
			#figure_obj.xaxis.major_label_text_font_size("12pt")
			#figure_obj.yaxis.major_label_text_font_size("12pt")
			
			y_axis_units = []
			x_axis_units = []

			comparison_datasets = []

			for data_dict_iter in self.column(self.figure_data, 1):

				for dataset in data_dict_iter["data"]:

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

			for data_dict, source_line_nested, attr_id, color_index  in zip(self.column(self.figure_data, 1), self.source_line,  self.attribute_ids,  colour_indices):

				for dataset, source_lis_coup, in zip(data_dict["data"], source_line_nested[0]):
					
					source_local = source_lis_coup[0]
					self.source_test(source_local)
					self.source_dataset_test(source_local, dataset)

					if dataset["sample_element"] == comparison_element:
						color = colour_list[color_index]

						"""
						Logic that ensures that plots get put with correspoinding axes. 
						"""
						if dataset["x_unit"] != x_axis_units[-1] or dataset["y_unit"] != y_axis_units[-1]:

							if dataset["x_unit"] != x_axis_units[-1] and dataset["y_unit"] != y_axis_units[-1]:
								name_check = data_dict["gen_info"]["DATA FILES"]
								attr_id = name_check[1][4][:-3] + "_" + name_check[2][2]

								figure_obj.line("x", "y", source = source_local,
								line_width = 2, 
								line_color = color, 
								legend = attr_id,
								x_range_name = "bar", 
								y_range_name = "foo")

							elif dataset["x_unit"] != x_axis_units[-1]:

								figure_obj.line("x", "y", source = source_local,
								line_width = 2, 
								line_color = color, 
								legend = attr_id, 
								x_range_name = "bar")

							else: 

								figure_obj.line("x", "y", source = source_local,
								line_width = 2, 
								line_color = color, 
								legend = attr_id, 
								y_range_name = "foo")

						else: 
							figure_obj.line("x", "y", source = source_local,
							line_width = 2, 
							line_color = color, 
							legend = attr_id)

			tab_plots.append(Panel(child = figure_obj, title = comparison_element))	


		tabs = Tabs(tabs = tab_plots)
		#curdoc().add_root(tabs)
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
		return

	def matplotlib_export(self, sources_list):
		inst = plotter(sources_list)
		inst.plot_machine()

	def integrate(self, source_list, line_list, source_line, figure_data, radio, x_box, dose, extra_y_ranges):
		"""
		Preforms a trapezoid integration over the x axis converted to cm on the selected element. 
		The calculated integral is used to find  the SF value: SF = dose/integral in the case of 
		distance on the x axis. 

		This integral is then applied automatically to all lines corresponing to this element
		"""
		element = radio.labels[radio.active]

		for source, line in zip(source_list, line_list):
			if source.data["sample_element"] == element:
				source_local = source
				line_obj = line

		lower_xlim = float(x_box.value)
		dose = float(dose.value)
		if dose == 0:
			return 

		x = np.array(source_local.data["x"])*1e-4
		y = np.array(source_local.data["y"])

		x_change = x[x>lower_xlim]
		y_change = y[len(y)-len(x_change):]

		integral = np.trapz(y_change, x = x_change)
		
		SF = dose/(integral)

		####
		#### IF TIME DO CALCULATION WITH DATA CYCLES AND SR
		
		for fig_data, source_line_nest, i in zip(figure_data, source_line, range(len(figure_data))):
			for source_line_item, j in zip(source_line_nest[0], range(len(source_line_nest))):
				self.source_test(source_line_item[0])

				if source_line_item[0].data["sample_element"] == element:
					source_local = source_line_item[0]
					line_obj = source_line_item[1]

					figure_obj = fig_data[0]  
					data_dict = fig_data[1] 
				else:
					continue
				
				for dataset in data_dict["data"]:
					if dataset["sample_element"] == element:

						dataset["y_unit"] = "C[at/cm^3]"
						found = False

						for line in data_dict["gen_info"]["CALIBRATION PARAMETERS"]:
							if element in line:
								found = True

							#should check of existing RSF and divide y by that number before applying new one.
							if "RSF" in line and found:
								line.append("%1.3e" %SF) 
								break

						y_s = np.array(source_local.data["y"])
						new_y = y_s * SF
						dataset["y"] = new_y

						source_local.data = dataset

						if not extra_y_ranges:
							print("extra_y_ranges didn't exist and I'm making a plot")

							figure_obj.extra_y_ranges =  {"second_y": Range1d(start = np.amin(dataset["y"]),
							end = np.amax(dataset["y"]))}
							
							figure_obj.add_layout(LogAxis(y_range_name = "second_y", axis_label = dataset["y_unit"]), "right")
							
							line_obj.glyph.line_alpha = 0
							line_obj.data_source = ColumnDataSource()

							new_line_obj = figure_obj.line("x", "y", source = source_local, line_width = 2, 
									line_color = line_obj.glyph.line_color, 
									legend = dataset["sample_element"], 
									name = dataset["sample_element"],
									y_range_name = "second_y")

							source_line[i][j][1] = new_line_obj

							if self.debug:
								self.debug_file = open("debug_output.txt", "w")
								self.debug_file.write("Added new y-axis for element: %s in integrate \n" %(dataset["sample_element"]))
								self.debug_file.close()

						elif extra_y_ranges:
							if self.debug:
								self.debug_file = open("debug_output.txt", "w")
								self.debug_file.write("Found more than one yaxis on file_id %s, element %s \n" 
									%(attr_id, dataset["sample_element"]))
								self.debug_file.close()

							line_obj = figure_obj.line("x", "y", source = source_local, line_width = 2, 
									line_color = line_obj.glyph.line_color, 
									legend = dataset["sample_element"], 
									name = dataset["sample_element"],
									y_range_name = "foo"
									)

			return

	def write_to_flexPDE(self, source_list, attrname, radio):
		element = radio.labels[radio.active]

		for source in source_list:
			if source.data["sample_element"] == element:
				source_local = source

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

		if self.debug:
				self.debug_file = open("debug_output.txt", "w")
				self.debug_file.write("SUCCESS: wrote to flexPDE file for file_id : %s, element: %s \n" %(attrname, element))
				self.debug_file.close()
		return

	def write_all_to_flexPDE(self, source_list, attrname, radio):
		path_to_flex = directory_chooser()
		
		for element in radio.labels:
			
			for source in source_list:
				if source.data["sample_element"] == element:
					source_local = source
	
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

		if self.debug:
				self.debug_file = open("debug_output.txt", "w")
				self.debug_file.write("SUCCESS: wrote all elements to flexPDE file for file_id : %s \n" %attrname)		
				self.debug_file.close()
		return
	
	def write_new_datafile(self, data_dict, source_list, attrname, radio):
		direct = directory_chooser()
		filename = direct+"/"+"pd_"+attrname+".dp_rpc_apc"
		file_object = open(filename, "w+")
		if self.debug:
			debug_file = open("debug_output.txt", "w")

		for source in source_list:
			debug_file.write(str(source.data["sample_element"]+ " ")) 
			debug_file.write(str(radio.labels[0]) + "\n")

			if source.data["sample_element"] == radio.labels[0]:
				source_local = source

		debug_file.close()
		iter_over = len(np.array(source_local.data["y"]))

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
			file_object.write("%s                                   "%element)
		file_object.write("\n")

		dataset = data_dict["data"]

		for i in range(len(radio.labels)):
			file_object.write("Time    %s       %s       " %(dataset[i]["x_unit"], dataset[i]["y_unit"])) 

		file_object.write("\n")

		for i in range(iter_over):

			for source_local in source_list:

				x = source_local.data["x"]
				y = source_local.data["y"]
				
				if source_local.data["x_unit"] == "Time":
					file_object.write("%1.5e            %1.5e     "%(x[i], y[i]))
				else:
					file_object.write("        %1.5e    %1.5e     "%(x[i], y[i])) 
		
			file_object.write("\n")
		

		file_object.write("\n")
		file_object.write("*** DATA END ***")
		file_object.close()

	def smoothing(self, source_list, data_dict, radio, x_box):
		"""
		Preforms exponential smoothing on the selected curve. The parameter alpha
		determines how fast the function "forgets" the previous results. This value should be exposed to the user
		"""
		element = radio.labels[radio.active]

		lower_xdelim = float(x_box.value)

		for source, dataset in zip(source_list, data_dict["data"]):
			if source.data["sample_element"] == element:
				source_local = source
				dataset = dataset

			try:
				print(source.data["sample_element"], element)
			except UnboundLocalError: 
				print(source.data["sample_element"], element)
				return
			"""
			elif source == source_list[-1]:
				if self.debug:
					self.debug_file = open("debug_output.txt", "w")
					self.debug_file.write("Didn't find the correct source in smoothing function with element: %s and source elements:%s" 
										%(element, [data.data["sample_element"] for data in source_list]))
					self.debug_file.close()
				return
			"""
		
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

		dataset["y"] = adj_ema
		source_local.data = dataset


	def estimate_RSF(self, attrname, radio):
		ion_pot = np.loadtxt("/home/solli/Documents/octopus/RSF_estimation/ionization_potentials.txt")
		ion_pot = np.reshape(ion_pot, (np.shape(ion_pot)[1], np.shape(ion_pot)[0]))

		
	def update_data(self, data_dict, source_list, figure, radio, text_input, new, which):
		element = radio.labels[radio.active]

		if which == "rsf":
			try:
				RSF = float(new)
			except ValueError:
				RSF = 1.
				#text_input.value = "ERROR: PLEASE INPUT NUMBER"

			for source in source_list:
				if source.data["sample_element"] == element:
					source_local = source

			x = np.array(source_local.data["x"])
			y = np.array(source_local.data["y"])

			y = RSF*y
			
			# DOES NOT WORK
			text_input = TextInput(value = "%.2e" %RSF, title = "RSF (at/cm^3): ")
			######

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
			for dataset in data_dict["data"]:
				if element == dataset["sample_element"]:
					dataset["y_unit"] = "C[at/cm^3]"
					found = False

					for line in data_dict["gen_info"]["CALIBRATION PARAMETERS"]:
						if element in line:
							found = True

						if "RSF" in line and found:
							dataset["y"] = y
							source_local.data = dataset
							line.append("%1.3e" %RSF) 
							break
			for source in source_list:
				print(dataset["sample_element"])
			return
		
		elif which == "sputter" or which == "crater_depth":
			"""
			Should create new axis and push to active session to replace the plot? 
			Or simply append new x-axis? Need to identify if there exists a second x-axis allready
			"""
			sputter_speed = None
			unit = None
			x = None

			for source, dataset in zip(source_list, data_dict["data"]):
				source_local = source

				if which == "sputter":
					try:
						sputter_speed, unit = new.split(" ")
						sputter_speed = float(sputter_speed) 
						sputter_speed, unit, x = self.depth_convert(dataset, source_local, sputter_speed, unit)

					except ValueError:
						print("Value Error, please input valid float and string")
						return

				elif which == "crater_depth":
					try: 
						crater_depth, unit = new.split(" ")
						crater_depth = float(crater_depth)
						sputter_speed, unit, x = self.depth_convert(dataset, source_local,  crater_depth, unit, True)
					except ValueError:
						print("Value Error, please input valid float and string")
						return

			if "No" in data_dict["gen_info"]["ACQUISITION PARAMETERS"][5]: 

				data_dict["gen_info"]["ACQUISITION PARAMETERS"][5] = "Crater Depth Measurement     Yes" 
				if "nm" in unit:
					data_dict["gen_info"]["ACQUISITION PARAMETERS"][6].append(str(sputter_speed * x[-1]))
					for value in data_dict["data"]:
						value["x_unit"] = "Depth[nm]"

				elif "um" in unit:
					data_dict["gen_info"]["ACQUISITION PARAMETERS"][6].append(str(sputter_speed * x[-1]*1e-3))
					for value in data_dict["data"]:
						value["x_unit"] = "Depth[um]"

			figure.xaxis.axis_label = "Depth "+ "[" + unit + "]"


	def depth_convert(self, dataset,  source_local, float_obj, unit, crater_depth_isfloat = False):

		x_arr_convert = source_local.data["x"]
	
		if crater_depth_isfloat:
			sputter_speed = float_obj / x_arr_convert[-1]
		else: 
			sputter_speed = float_obj
			if "/s" in unit:
				unit = unit[:2]

		x = np.array(source_local.data["x"])
		y = np.array(source_local.data["y"])

		x = x*sputter_speed

		dataset["x"] = x
		source_local.data = dataset
			
		return sputter_speed, unit, x

	def column(self, matrix, i):
		return [row[i] for row in matrix]

	def source_dataset_test(self, source, dataset):
		assert isinstance(source, ColumnDataSource)
		assert isinstance(dataset, dict)

		x_s = source.data["x"]
		y_s = source.data["y"]

		x_d = dataset["x"]
		y_d = dataset["y"]

		assert len(x_s) == len(x_d)
		assert len(y_s) == len(y_d)

		assert np.allclose(x_s, x_d)
		assert np.allclose(y_s, y_d)

	def source_test(self, source):
		try:
			assert isinstance(source, ColumnDataSource)
		except AssertionError:
			sys.exit("Exiting from unittest(source) - was not ColumnDatasource object but %s" %str(type(source)))
		x = source.data["x"]
		y = source.data["y"]

		assert x is not None
		assert y is not None

		assert len(x) is not 0
		assert len(y) is not 0

	def data_test(self, data):
		assert "data" in data.keys()
		assert "gen_info" in data.keys()

		for dataset in data["data"]:
			assert len(dataset["x"]) is not 0
			assert len(dataset["y"]) is not 0
