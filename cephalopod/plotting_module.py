from cephalopod import file_handler, file_chooser 
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import numpy as np

class plotter:

	def __init__(self, sources):

		self.sources = sources

	def plot_machine(self): 
		sources = self.sources		

		host = host_subplot(111, axes_class = AA.Axes)
		
		plt.subplots_adjust(right = 0.75)
		plt.xticks(fontsize = 16)
		plt.yticks(fontsize = 16) 

		host.set_yscale("log")

		host.set_xlabel(sources[0].data["x_unit"], fontsize = 25)
			
		for data_set in sources:
			x_val = data_set.data["x"]
			y_val = data_set.data["y"]

			x_unit = "$%s$" %data_set.data["x_unit"]
			y_unit = "$%s$" %data_set.data["y_unit"]

			host.set_ylabel(y_unit, fontsize  = 25)
			host.plot(x_val, y_val, label = data_set.data["sample_element"])
			plt.legend()

			if y_unit != sources[0].data["y_unit"]:
				par2 = host.twinx()
				par2.set_yscale("log")
				par2.set_ylabel(y_unit)

				offset = 60 
				new_fixed_axis = par2.get_grid_helper().new_fixed_axis
				par2.axis["right"] = new_fixed_axis(loc="right",
				                                    axes=par2,
				                                    offset=(offset, 0))
				par2.axis["right"].toggle(all = True)


		plt.show()
		

		"""
		else:

			data_set = data_sets[0]

			x_val = data_set["data"][0]
			y_val = data_set["data"][1]

			x_val = x_val.copy(order = "C")

			x_unit = data_set["x_unit"]
			y_unit = data_set["y_unit"]
		
			plt.semilogy(x_val, y_val, label = data_set["sample info"][2], nonposy = "clip")
			plt.xlabel(x_unit)
			plt.ylabel(y_unit)
			plt.legend()
			plt.show()
		"""




