########################################################################################################################################################
# Author:   Kabir Singh
# Date:     29 November 2017
# Rev-Date: 19 November 2017
#
# Description: TODO
########################################################################################################################################################

import math
import argparse
from random import *

########################################################################################################################################################
# COMMAND LINE OPTIONS/ARGS
########################################################################################################################################################
parser = argparse.ArgumentParser(description="Simulate trials of probablistic reward task using Rutledge et al model for Momentary Subjective Well-Being",
                                  epilog=     "Please see [TODO github] for more detailed instructions")

#simulation variables
parser.add_argument("-n", action="store", dest="num_trials",  type=int,   default=64,   help="number of trials to run")
parser.add_argument("-d", action="store", dest="time_decay" , type=float, default=0.75, help="time decay constant (gamma)")
parser.add_argument("-g", action="store", dest="gamble_prob", type=float, default=0.5,  help="probability gamble is chosen in a trial")
parser.add_argument("-t", action="store", dest="sim_type",  type=str,   default="lab",   help="type of simulation: lab experiment(\"lab\"), smartphone app(\"app\"), sandbox")
parser.add_argument("-a", action="store", dest="attitude",  type=str,   default="r",   help="RPE calculation behavior, \'r\' for standard , \'o\' for optimist, \'p\' for pessimist")
parser.add_argument("-f", action="store", dest="FAVOR",  type=float,   default=1.0,   help="In sandbox EV calculation, the favorability factor applied to each past gamble")

#debugging variables
parser.add_argument("-v", action="store_true", dest="verbose_d", default=False,help="debugging verbose mode")

args = parser.parse_args()

########################################################################################################################################################
# Global Variables
########################################################################################################################################################

# "LAB" simulation weight set
l_weights  = [49, 11.41, 6.62, 14.69] # average from raw data
# "APP" simulation weight set
a_weights  = [49, 0.2, 0.1, 0.25]     # handpicked values, roughly
# "SANDBOX" simulation weight set
s_weights  = [49, 0.2, 0.1, 0.25]        # following ratio of lab-obtained data

# debugging flag
verbose = args.verbose_d 

########################################################################################################################################################
# Participant Instance
########################################################################################################################################################

class Participant:

    #############################################################################################
    # Member Variables + Init
    #############################################################################################
    def __init__(self, time_decay, gamble_prob, sim_type, attitude, favor):

        # aka forgetting factor, gamma
        self.time_decay  = time_decay
        # probability of selecting gamble for a trial in sim_1
        self.gamble_prob = gamble_prob
        # in sandbox_ev, favorability factor
        self.favor = favor

        # sandboxing allows for different functions to be subsituted for EV and RPE calcs
        # select EV calculation method 
        if sim_type == "lab" or sim_type == "app":
            self.get_expected_value = self.vanilla_ev
        else:
            self.get_expected_value = self.sandbox_ev

        # select RPE calculation method 
        if attitude == "optimistic":
            self.get_rpe = self.o_rpe
        elif attitude == "pessimist":
            self.get_rpe = self.p_rpe
        else:
            self.get_rpe = self.r_rpe

        # record of cr, ev, and rpe vals per trial
        self.trials    = {'CR': {}, 'EV': {}, 'RPE': {}} 
        
        # record of calculated happines val per trial
        self.happiness = [] 
        self.gambles   = []

    #############################################################################################
    # Trial Value Get/Set
    #############################################################################################

    def set_trial(self, index, cr, ev, rpe):
        self.trials['CR'][index] = cr
        self.trials['EV'][index] = ev 
        self.trials['RPE'][index] = rpe

    def get_trial(self, index):
        return (self.trials['CR'][index], self.trials['EV'][index], self.trials['RPE'][index])

    #############################################################################################
    # Expected Value Calculations
    #############################################################################################
    
    # simple, what paper alluded to having
    def vanilla_ev(self, index, positive_gamble, negative_gamble):
        return (positive_gamble + negative_gamble) / 2

    # my own concoction, definitely needs to be compared against real data
    def sandbox_ev(self, index, pos_gamble, neg_gamble):

        _sum = 0
        for i in range(0, len(self.gambles)):
            decay = pow(0.5, i + 1)
            _, gamble = self.gambles[i]
            _sum += (decay * gamble * self.favor)

        _sum += (pos_gamble + neg_gamble) / 2
        
        return _sum


    #############################################################################################
    # Reward Prediction Errors (RPE) Calculations
    #############################################################################################

    # "realist" rpe (this is the equation used in most computational models)
    def r_rpe(self, expected, actual):
        return (actual - expected)

    # "optimist" rpe
    def o_rpe(self, expected, actual):
        return (actual - (expected + (expected * 0.5)))

    # "pessimist" rpe
    def p_rpe(self, expected, actual):
        return (actual - (expected - (expected * 0.5)))

    #############################################################################################
    

########################################################################################################################################################
# Value Calculations
########################################################################################################################################################

# standard happiness calculation, added floor and ceiling
def calc_happiness_r(i, w, sum_cr, sum_ev, sum_rpe):

    h = w[0] + w[1] * sum_cr + w[2] * sum_ev + w[3] * sum_rpe

    if h > 100:
        return 100
    elif h < 0:
        return 0
    else:
        return h

########################################################################################################################################################
# Simulation + Aux Functions
########################################################################################################################################################

# sum previous trial contributions multiplied by appropriate time decay constant
def sum_w_decay(arr, max_index, decay):

    _sum = 0.0
    for i in range(1, max_index+1):
        tdecay = pow(decay, (max_index - i))
        trial = tdecay * arr[i]
        _sum += trial

        if verbose:
            print ("\t\ti={0}, td={1:.3f} , v={2:.5f}".format(i, tdecay, arr[i]))

    if verbose:
        print ("\t\tsum=", _sum)

    return _sum

###########################################################################

# return cr, neg_gamble, pos_gamble
def generate_task_values(trial_type, e_seed):

    hi  = uniform(e_seed * 0.5, e_seed * 1.5) 
    mid = (hi / 2) + uniform(e_seed * -0.2 , e_seed * 0.2)
    lo  = 0

    # loss trial
    if trial_type == 0: 
        return (mid * -1, hi * -1, lo)
    # mixed trial
    elif trial_type == 1:
        return (0, lo - mid, hi - mid)
    # gain trial
    elif trial_type == 2:
        return (mid, lo, hi)

###########################################################################

def run_simulation(p, num_trials, init_wallet, trial_seed, weights):

    w  = weights
    td = p.time_decay
    gp = p.gamble_prob

    wallet = init_wallet
    e_seed = trial_seed

    if verbose:
        print ("Gamble Probability: ", gp)
        print ("Time Decay: ", td)
        print ("-------------------------")
    else:
        print ("{0:.3f}, {1:.3f}, {2}".format(gp, td, num_trials))

    for i in range(1, num_trials+1):
        if verbose:
            print ("Trial #", i)

        (certain_value, pos_gamble, neg_gamble) = generate_task_values(randint(1,2), e_seed)

        # gamble or certain val?
        r = random()
        if r > gp:
            cr = certain_value
            ev  = 0.0
            rpe = 0.0
            wallet += cr

            if verbose:
                print ("\tchoosing cr: {0:.2f}".format(cr))

        else:
            cr  = 0.0
            ev = p.get_expected_value(i, pos_gamble, neg_gamble)
            if ( r > gp / 2) :
                rpe = p.get_rpe(ev, pos_gamble)
                wallet += pos_gamble

                if verbose:
                    print ("\tchoosing gamble: ({0:.2f}), {1:.2f}".format(pos_gamble, neg_gamble))
            else:
                rpe = p.get_rpe(ev, neg_gamble)
                wallet += neg_gamble

                if verbose:
                    print ("\tchoosing gamble: {0:.2f}, ({1:.2f})".format(pos_gamble, neg_gamble))

        if verbose:
            print ("\tSetting trial to: {0:.2f}, {1:.2f}, {2:.2f}".format(cr, ev, rpe))

        p.set_trial(i, cr, ev, rpe)

        happiness  = calc_happiness_r(i, w, sum_w_decay(p.trials['CR'], i, td), 
                                            sum_w_decay(p.trials['EV'], i, td),  
                                            sum_w_decay(p.trials['RPE'], i, td))

        if verbose:
            print ("\th = {0:.3f}".format(happiness))
        else:
            print("{0}, {1:.3f}, {2:.3f}, {3:.3f}, {4:.3f}, {5:.3f}".format(i, cr, ev, rpe, happiness, wallet))

        p.happiness.append(happiness)

########################################################################################################################################################

def run_simulation_sandbox(p, num_trials):

    td = p.time_decay
    gp = p.gamble_prob

    e_seed = 80
    wallet = 500.0

    if verbose:
        print ("Gamble Probability: ", gp)
        print ("Time Decay: ", td)
        print ("-------------------------")
    else:
        print ("{0:.3f}, {1:.3f}, {2}".format(gp, td, num_trials))

    for i in range(1, num_trials+1):
        if verbose:
            print ("Trial #", i)
        
        (certain_val, neg_gamble, pos_gamble) = generate_task_values(2, e_seed)
        ev = p.get_expected_value(i, pos_gamble, neg_gamble)

        if verbose:
            print ("choosing between cr={0:.3f} and ev={1:.3f}".format(certain_val, ev))

        if ev < certain_val:
            cr = certain_val
            ev = 0.0
            rpe = 0.0
            wallet += cr

            if verbose:
                print ("\tchoosing cr: {0:.2f}".format(cr))

        else:
            cr = 0.0
            r = random()
            if ( r > 0.5):
                rpe = p.get_rpe(ev, pos_gamble)
                wallet += pos_gamble
                p.gambles.append((i, pos_gamble))

                if verbose:
                    print ("\tchoosing gamble: ({0:.2f}), {1:.2f}".format(pos_gamble, neg_gamble))
            else:
                rpe = p.get_rpe(ev, neg_gamble)
                wallet += neg_gamble
                p.gambles.append((i, neg_gamble))

                if verbose:
                    print ("\tchoosing gamble: {0:.2f}, ({1:.2f})".format(pos_gamble, neg_gamble))

        if verbose:
            print ("\tSetting trial to: {0:.2f}, {1:.2f}, {2:.2f}".format(cr, ev, rpe))

        p.set_trial(i, cr, ev, rpe)

        happiness  = calc_happiness_r(i, s_weights, sum_w_decay(p.trials['CR'], i, td), 
                                                    sum_w_decay(p.trials['EV'], i, td),  
                                                    sum_w_decay(p.trials['RPE'], i, td))

        if verbose:
            print ("\th = {0:.3f}".format(happiness))
        else:
            print("{0}, {1:.3f}, {2:.3f}, {3:.3f}, {4:.3f}, {5:.3f}".format(i, cr, ev, rpe, happiness, wallet))

        p.happiness.append(happiness)


########################################################################################################################################################
# Main
########################################################################################################################################################

def main():

    # initialize a participant using command line arguments
    p = Participant(args.time_decay, args.gamble_prob, args.sim_type, args.attitude, args.favor)

    # run the appropriate simulation
    if args.sim_type == "lab":
        run_simulation(p, args.num_trials, 20.0, 1.5, l_weights)
    elif args.sim_type == "app":
        run_simulation(p, args.num_trials, 500.0, 80, a_weights)
    elif args.sim_type == "sandbox":
        run_simulation_sandbox(p, args.num_trials)

if __name__ == "__main__":
    main()
