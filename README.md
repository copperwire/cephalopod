# octopus
Package for treating sims data remotely. 


The package is installed by `pip install cephalopod` or from conda by `conda install -c https://conda.anaconda.org/copperwire cephalopod`.
If cloned from git install by running the following command  in your terminal `python setup.py install`, to build in dev-mode run `pip install . -e`

Use of the module is done either by grabbing raw data from `file_handler` as such:

```python
from cephalopod import file_handler, file_chooser

file = file_chooser() #string from dialogue

a = file_handler(file)
x = file_handler.runtime() 
```

from the docstring x is a dictionary  with subdictionaries on the form:
```                                
            /->"Data"--> name -->("x", "y", "element", "x/y units")
attribute--|
		    \->"gen_info" --> file_attribute(all general info about the sample not specific to element) 
```
Where quoted strings are pre-set keys and all other keys are defined iteratively and is available by iteration over the dictionary or inferred from the strings contained in the DELIMITER as set in the function (see docstring on `file_handler.data_conversion`). 

To run the module with graphical output see below for an example:

In your terminal run the command `bokeh serve` to initialize the server. Default hosted on local port 5006.

```python
from cephalopod import interactive_plotting as ip

ip()
```

**GUI**

* FlexPDE
  * Either save one or all elements as FlexPDE friendly files in a supplied folder

* RSF
  * Provide a number corresponding to a Sensitivity Factor  (SF) or a Relative Sensitivity Factor (RSF) which is applied to the signal

* Save Datafile
  * Saves datafile in an almost identical shape to the original file in a supplied directory

* Smooth select element
  * Calculates a  moving exponential average on the element selected. Set x-limit do change where the smoothing is applied.

* Calculate SF value 
  * Using a set dose and x-limit computes the sensitivity factor by the discrete time integral over the impurity element's signal.
