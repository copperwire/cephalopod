import tkinter
from tkinter import filedialog


def file_chooser():
	root = tkinter.Tk()
	files = filedialog.askopenfilenames(parent=root,title='Choose files')
	if len(files) == 1:
		files = files[0]
	root.quit()
	return files