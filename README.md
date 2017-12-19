#How to Use Simulation Software

##Requirements
	The model was implemented in Python 3.6.3 and uses the Numpy and MatPlotLib (which requires TK) libraries. It is suggested that before running the simulation code, one assures that your device is running Python 3+ and have the required libraries installed. If you are running on MacOS or Linux/GNU, you can simply install them via the appropriate pip command:

> # pip install [library name]

To check whether or not you need to update your instance of Python, please run:

> python --version

##Running the Simulation
To run the simulation, please run:

> python simulation.py [flags] 

The flags that are available to use at the time of the paper submission are:

-t[ lab | app | sandbox] : the type of trial to be run
-n [INTEGER] : the number of trials to run the simulation for
-d [FLOAT]: time decay constant/forgetting factor/gamma (between 0.0 and 1.0)
-g [FLOAT]: gambling probability in lab/app simulations
-a [optimist | realist | pessimist ] : RPE calculation type
-f [FLOAT] : In sandbox EV calculation, the favorability factor applied to each past gamble
-v : verbose, debugging flag, produces a lot of output
-h, --help : display these options

ex:
> python simulation.py -t lab -n 256 -g 0.6 -d 0.44 

The output of the program is formatted as such:
GAMBLE_PROB, TIME_DECAY, NUM_TRIALS, SIMULATION_TYPE
1, CERTAIN_VAL_1, EXPECTED_VAL_1, RPE_1, H_1, EARNINGS_1
2, CERTAIN_VAL_2, EXPECTED_VAL_2, RPE_2, H_2, EARNINGS_2
…
N, CERTAIN_VAL_N, EXPECTED_VAL_N, RPE_N, H_N, EARNINGS_N

It is recommended that you send the output to file, using “>”,  so that they can be used later:

> python simulation.py -t app -n 75 > results.csv

##Visualizing Simulation Output
Also included is a simple plotting tool that will display the results of a non-verbose output (no “-v” flag). To use, simply type:

> python plotter.py [name_of_results_file]

