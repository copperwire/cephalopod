from setuptools import setup

setup(name = "octopus",
    version = "0.1a",
    description = "package to manage SIMS data remotely",
    url = "https://github.com/copperwire/octopus.git",
    author = "Robert Solli",
    author_email = "octopus.prey@gmail.com",
    license  ="MIT",
    packages = "octopus",
    install_requires = [
           "numpy",
           "bokeh"]
    zip_safe = False )
