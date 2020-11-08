# py-algo-complex
Algorithm Complexity Checker

## How to install scripts on your host
The easiest way is to clone the GitHub repository and build virtual environment for launching the script:
```
cd <some directory on your choice>
git clone https://github.com/jraska1/py-algo-complex.git
cd py-algo-complex
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## General overview of script features
To launch the script, you have to activate the venv and run it as python script.
For options overview, use -h or --help option as follows:

```
(.venv) [raska@localhost py-algo-complex]$ python main.py -h
Usage: main.py [OPTIONS] SRC

  Algorithm Complexity Checker - tool for estimating complexity of software,
  computing regression parameters and predicting execution time.

  Produced by:   DSW - Dwarf Software Workshop

  Licence:       Apache Licence, version 2.0

Options:
  -x, --x-value INTEGER   Independent variable to predict execution time
  --sample-count INTEGER  Number of samples used for data normalization
                          [default: 100]

  --delimiter TEXT        Field delimiter character  [default:  ]
  -v, --verbose           To be more verbose
  -h, --help              Show this message and exit.
```

## Expected data format
As a source data the scripts expects pair of values, where:
- the first number (obviously integer) represents size of data sample used for testing
- the second number (obviously float) represent measured execution time 

There is one such data source I used for developing script:
```
(.venv) [raska@localhost py-algo-complex]$ cat data/data10.txt 
10 384.8
30 486.4
50 876.6
70 1142.2
90 1861.0
100 2239.5
300 21175.3
500 58231.4
700 115257.1
900 191215.3
```
In this data set the execution time is provided in milliseconds. 
 
 
 ## Simple script use-case
 I am using data10.txt file as a data source for analyzing complexity 
 and predicting execution time for sample size = 5000.
```
(.venv) [raska@localhost py-algo-complex]$ cat data/data10.txt | python main.py -x 5000 -
Algorithm Complexity Estimation: O(n^2)
Regression Function: 23.023251 + 0.235607 * x^2
Predicted Execution Time: 5890202.553507
```
As you can see, estimated algorithm complexity is O(x^2) and predicted execution time for sample size 5000 
is about 5 890 seconds.
  