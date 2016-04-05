from setuptools import setup

setup(name = "cephalopod",
    version = "0.14a1",
    description = "package to manage SIMS data remotely",
    url = "https://github.com/copperwire/cephalopod.git",
    download_url = "https://github.com/copperwire/cephalopod/tarball/0.14a0",
    author = "Robert Solli",
    author_email = "octopus.prey@gmail.com",
    license  ="MIT",
    packages = ["cephalopod"],
    install_requires = [
           "numpy",
           "bokeh"],
    zip_safe = False )
