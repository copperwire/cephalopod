import sys
import os 
import numpy as np


class file_handler:
	"""
	Public methods:

	__init__
	file_iteration
	data_conversion
	runtime 

	Class to get data from the SIMS output files. 
	The data is collected in groups by the delimiters in the data file, e.g. **** DATA START*** 
	contains all numerical data. Operations are then preformed to convert the data to human and 
	machine readable formats. 

	The class can easily be changed to take an arbitrary data file with a known delimiter between
	types of parameters. If there are several data sets, submit a list with strings denoting the 
	start of the dataset and the corresponding attribute of the class will be a dictionary with 
	the denoted rows as keys with substance as the first element and the x and y axis as the
	second and third element.  
	
	The class is initialized with the plotting module, if you wish to only use the file decoding 
	aspect please view the sample running in the docstring of the runtime method.
	"""

	def __init__(self, filename):
		"""Gets the filename from which the data is collected. """
		self.filename = filename 
		self.has_iterated = False

	def file_iteration(self, delim = "***"):
		"""
		Walks through the supplied data file and stores all lines in string format. The data is
		saved by assigning each set of rows to the corresponding delimiter. The delimiting value 
		(by default \" *** \") determines where the method separates the objects. Each part of the
		file can be accessed through 

		getattr(ClassInstance, File Partition)

		where File Partition is the string directly following the delimiter. 

		Method will be expanded to be more robust in taking delimiters with spaces adjacent 
		to the string following the delimiter. 

		"""
		self.has_iterated = True

		num_lines = sum(1 for line in open(self.filename))

		with open(self.filename) as self.file_object:
			line_indices = np.arange(0, num_lines, 1, dtype = int)

			data_type_indices = []
			lines = []

			for line, i in zip(self.file_object, line_indices):
				decoded = " ".join(line.split())
				lines.append(decoded)
				if line[:3] == delim:
					data_type_indices.append(i)

			self.attribute_names = []


			for index_of_data_type, i in zip(data_type_indices, np.arange(0, len(data_type_indices), 1,  dtype = int)): 
				attribute_name = str(lines[index_of_data_type][4:-4])

				self.attribute_names.append(attribute_name)
				try:
					a = setattr(self, attribute_name, lines[index_of_data_type + 1: data_type_indices[i + 1 ] - 1]) 
				except IndexError: 
					a = setattr(self, attribute_name, lines[index_of_data_type + 1: ])

		
	def data_conversion(self, data_name = "DATA START", key_row= [2, 3], nonposy = True, mass_spectra = False, SIMS_file = True):
		"""
		Strictly needs to be run after the file_iteration method.
		Formats the strings contained in the data_name attribute of the class to float.
		To accomodate log-plots the default is to make a correction to the y axis such that 
		non-positive and small numbers are set to 1. 

		Keyword arguments:
		data_name (string) = string following delimiter before the data set.
		key_row (list) = list with the rows in the data set which contains information about 
		the data

		returns dictionary with subdictionaries on the form:

                                
                    /->"Data"--> ("x", "y", "element", "x/y units")
		attribute--|
				    \->"gen_info" --> file_attribute(all general info about the sample not specific to element) 

		"""
		try:	
			data_set = getattr(self, data_name)
		
		except AttributeError:
			print("class has no attribute named %s. Trying to fix") %data_name
			if self.has_iterated:
				new_name = data_name.strip()
				try:
					data_set = getattr(self, new_name)
				except AttributeError:
					sys.exit("Unfixable:(")
			else: 
				self.file_iteration()
				try:
					data_set = getattr(self, data_name)
					print("fix'd. Don't thank me or anything. I'm just a program")
				except AttributeError:
					sys.exit("Unfixable:(")

		self.substances = data_set[key_row[0]].split(" ")
		units = data_set[key_row[1]].split(" ")

		x = []
		for line in data_set[key_row[1] + 1:] :
			dat = line.split(" ")
			a = [float(c) for c in dat]
			y = []

			"""
			Making the arrays log-friendly by adding 1 to all zero or less than one elements. 
			"""

			y.append(a[0])
			if nonposy:
				for i in range(1, len(a)):
					if i % 2 == 1:
						if a[i] < 1:
							a[i] = a[i] + 1
						else: 
							a[i] = a[i]
					else:
						a[i] = a[i]
			x.append(a)

		reshaping = np.shape(x)
		u = np.reshape(x, (reshaping[0], reshaping[1]))

		variables_per_substance = len(x[0])/len(self.substances)

		gen_info = {}

		for attribute in self.attribute_names:
			"""
			Shold implement conversion to one string with float argument appended as dictionary,
			maybe? 
			"""	
			value = getattr(self, attribute)
			value = [line.split(" ") for line in value]
			gen_info[attribute] = value


		if SIMS_file: 
			data = self.SIMS_data_sort(u, x, units, mass_spectra)
		else:
			data = self.data_sort()

		if not mass_spectra:
			key_func = lambda data: self.isotope_number(data["sample_element"])
			y = dict(data = sorted(data, key = key_func), gen_info = gen_info)

		else:
			y = dict(data = data, gen_info = gen_info)
		
		return y

	def SIMS_data_sort(self, u, x, units,  mass_spectra):
		data = []
		for name, number in zip(self.substances, np.arange(0, len(x[0]), 2, dtype = int)):

			if len(units) != len(u[0]):
				if u[0][number] < 1e-1:
					units.pop(number)
				else:
					units.pop(number+1)

			if not mass_spectra:
				data.append({"x": np.array(u[:,number]), "y": np.array(u[:,number + 1]), 
				"element": [name for i in range(len(np.array(u[:,number + 1])))],
				"x_unit": units[number],
				"y_unit": units[number + 1],
				"sample_element": name})
			else:
				data.append({"x": np.array(u[:,number]), "y": np.array(u[:,number + 1]), 
				"x_unit": units[number],
				"y_unit": units[number + 1]})

		return data

	def data_sort(self):
		return []

	def runtime(self, delim = "***", data_name = "DATA START", key_row= [2, 3], mass_spectra = False):
		"""
		Runs the file iterator and data conversion and returns a touple of the names of the analyzed 
		elements and dictionaries containing all data 
		"""
		self.file_iteration(delim);
		x = self.data_conversion(data_name, key_row, True, mass_spectra);
		return  x

	def isotope_number(self, string):
		try:
			is_num = int(string[:3])
		except ValueError:
			try:
				is_num = int(string[:2])
			except ValueError:
				is_num = int(string[:1])

		return is_num
