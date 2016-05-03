from tkinter import filedialog, Tk

def file_chooser():
	root = Tk()
	root.files = filedialog.askopenfilenames(title='Choose files')
	if len(files) == 1:
		files = files[0]
	root.withdraw()
	return root.files

def directory_chooser():
	root = Tk()
	root.directory = filedialog.askdirectory(title = "Choose directory")
	root.withdraw()
	return root.directory