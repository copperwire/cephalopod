import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import numpy as np

class plotter:
	colors = ["b", "g", "r", "c", "m", "y", "k"]


	def __init__(self, sources):

		self.sources = sources
	
	def checkEqual2(self, iterator):
		return len(set(iterator)) <= 1

	def plot_machine(self): 
		sources = self.sources
		req_ax = self.checkEqual2([source.data["y_unit"] for source in sources])
		
		if  req_ax == False: 
			fig, ax1 = plt.subplots()

			ax1.set_yscale("log")

			ax2 = ax1.twinx()
			ax2.set_yscale("log")

			sc1 = sources[0].data

			x1 = sc1["x"]
			y1 = sc1["y"]
			el1 = sc1["sample_element"]
			xun1 = sc1["x_unit"]
			yun1 = r"%s" %sc1["y_unit"]

			ax1.plot(x1, y1, self.colors[0]+ "x-", label = el1)		
			ax1.set_xlabel(xun1)
			ax1.set_ylabel(yun1)
			
			source_diff = None

			for source, color in zip(sources[1:], self.colors[1:]):
	
				scn = source.data

				xn = scn["x"]
				yn = scn["y"]
				eln = scn["sample_element"]
				xunn = scn["x_unit"]
				yunn = scn["y_unit"]

				if yunn != yun1:
					ax2.plot(xn, yn, color+"o-", label = eln)
					source_diff = source
				else:
					ax1.plot(xn, yn, color+"x-", label = eln)

			ax2.set_ylabel(source_diff.data["y_unit"])
			ax2.legend(loc=0)


		else: 

			sc1 = sources[0].data

			fig, ax1 = plt.subplots()
			ax1.set_yscale("log")

			x1 = sc1["x"]
			y1 = sc1["y"]
			el1 = sc1["sample_element"]
			xun1 = sc1["x_unit"]
			yun1 = sc1["y_unit"]

			ax1.plot(x1, y1, "b-", label = el1)		
			ax1.set_xlabel(xun1)
			ax1.set_ylabel(yun1)
			
			for source, color in zip(sources[1:], self.colors[1:]):
	
				scn = source.data

				xn = scn["x"]
				yn = scn["y"]
				eln = scn["sample_element"]
				xunn = scn["x_unit"]
				yunn = scn["y_unit"]

				ax1.plot(xn, yn, color+"-", label = eln)

		plt.legend()
		plt.xticks(fontsize = 16)
		plt.yticks(fontsize = 16) 

		plt.show()
		
	def mass_plot(self):
		sources = self.sources


		host = host_subplot(111, axes_class = AA.Axes)
		plt.subplots_adjust(right = 0.75)
		host.set_yscale("log")

		hist = sources.data["top"]
		bin_edges = sources.data["edges"]

		host.set_xlabel(sources.data["x_unit"], fontsize = 25)


		y_unit = sources.data["y_unit"]

		host.set_ylabel(y_unit, fontsize = 25)
		host.bar(bin_edges[:-1], hist, width = 1)
		host.set_xlim(min(bin_edges), max(bin_edges))

		plt.xticks(fontsize = 16)
		plt.yticks(fontsize = 16) 

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




