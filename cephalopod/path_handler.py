import tkinter
from tkinter import filedialog

def file_chooser():
	files = filedialog.askopenfilenames(title='Choose files')
	if len(files) == 1:
		files = files[0]
	return files

def directory_chooser():
	directory = filedialog.askdirectory(title = "Choose directory")
	return directory