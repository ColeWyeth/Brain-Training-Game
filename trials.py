import numpy as np
import sys 
from select import select 
from os import path, system, chdir
import random
from collections import defaultdict

register = np.zeros(26)
register_names = [chr(ord('A') + i) for i in range(26)]

session_results = defaultdict(list)

def set_register(new_vals):
    for i, v in enumerate(new_vals):
        register[i] = v 

class Query:
    def __init__(self, ind):
        self.ind = ind 

    def ask(self, timeout):
        print("Enter the value of " + register_names[self.ind] + ":")
        rlist, _, _ = select([sys.stdin], [], [], timeout)
        if rlist:
            answer = int(sys.stdin.readline())
            return (answer == register[self.ind])
        else:
            return(False)

class Command:
    def __init__(self):
        self.string_rep = '\n'
    def GetString(self):
        return self.string_rep 
    def Execute(self):
        pass 

class AddTo(Command):
    def __init__(self, ind, add):
        self.ind = ind
        self.add = add
        self.string_rep = "Add " + str(add) + " to register " + register_names[ind] + '\n'

    def Execute(self):
        register[self.ind] += self.add 

class AddInto(Command):
    def __init__(self, ind1, ind2):
        self.ind1 = ind1
        self.ind2 = ind2 
        self.string_rep = "Add " + register_names[ind1] + " into " + register_names[ind2]

    def Execute(self):
        register[self.ind2] += register[self.ind1]
    
class MultBy(Command):
    def __init__(self, ind1, ind2):
        self.ind1 = ind1 
        self.ind2 = ind2 
        self.string_rep = "Multiply " + register_names[ind2] + " by " + register_names[ind1]

    def Execute(self):
        register[self.ind2] *= register[self.ind1]

class SetTo(Command):
    def __init__(self, ind, new_val):
        self.ind = ind 
        self.new_val = new_val 
        self.string_rep = "Set " + register_names[ind] + " to " + str(new_val)

    def Execute(self):
        register[self.ind] = self.new_val 

# a round executes a sequence of Commands and Queries with a fixed time limit  
class Round:
    def __init__(self, sequence, timeout):
        self.seq = sequence 
        self.timeout = timeout 
    def run(self):
        print("You will have " + str(self.timeout) + " seconds to give each answer." )
        for step in self.seq:
            if isinstance(step, Command):
                print(step.GetString())
                step.Execute()
            else:
                if step.ask(self.timeout):
                    system("clear")
                    print("Correct")
                else:
                    print("Failed")
                    return(False)
        return(True)
        
class Trial:
    def __init__(self, level):
        self.level = level 
        self.ind_range = range(min(level+1, 26))

        self.rounds = []
        greatest_time = 10 - 2*(level//10)

        for i in range(5):
            self.rounds.append(self.generate_round(max(2, greatest_time - i)))
    
    def generate_round(self, timeout):
        """ Generate a round at the level of difficulty with the given timeout. 
            The round will be returned. This is a helper function for running 
            the trial. 
        """
        sequence = []
        for i in range(5 + self.level):
            ind1 = random.choice(self.ind_range)
            ind2 = random.choice(self.ind_range)
            num = random.choice(range(10 + 10*self.level))
            next_command = np.random.choice(
                [AddTo(ind1, num), AddInto(ind1, ind2), MultBy(ind1, ind2), SetTo(ind1, num)],
                p=[0.4, 0.1, 0.1, 0.4], # Upweight nonzero initialization, reduce repeated squaring.
                )
            next_query = Query(random.choice(self.ind_range))
            sequence.append(next_command)
            sequence.append(next_query)

        return Round(sequence, timeout)

    def run(self):
        for i, round in enumerate(self.rounds):
            print("Round " + str(i) + " beginning.")
            if self.level >= 10:
                set_register(np.ones(26) * self.level)
                print("All registers have been initialized to " + str(self.level))
            if not round.run():
                print("Failed round " + str(i))
                session_results[self.level].append(i)
                return(False)
            print("Round " + str(i) + " passed.")
            print()
            set_register(np.zeros(26))
        session_results[self.level].append(i+1)
        print("Trial passed!")
        return(True)


def main():
    global register 

    # so we can access level.txt even if it's not in the current working directory
    chdir("/home/cwyeth/Brain-Training-Game") 
    
    while True:
        level = 0 
        if path.exists('level.txt'):
            levelfile = open('level.txt', 'r')
            level = int(levelfile.read())
            levelfile.close()
        else:
            levelfile = open('level.txt', 'w')
            levelfile.write('0')
            levelfile.close()

        trial = Trial(level)
        if trial.run():
            levelfile = open('level.txt', 'w')
            levelfile.write(str(level + 1))
            levelfile.close 
        else:
            print("You lose. Your level has not increased.")

        go_on = input("Continue (y/n): ")

        if not go_on == 'y':
            break

        set_register(np.zeros(26))

    print("Session results:")
    result_list = [(k,session_results[k]) for k in session_results.keys()]
    result_list.sort(key=lambda x: x[0])
    for level, results in result_list:
        print(f"LEVEL {level}: {results}")
    print("Session ended")


    # add1 = AddTo(0, 10)
    # q1 = Query(0)
    # add2 = AddTo(1, 5)
    # q2 = Query(0)
    # add3 = AddTo(0, 1)
    # q3 = Query(1)
    # r1 = Round([add1, q1, add2, q2, add3, q3], 1)
    # r1.run()

if __name__ == "__main__":
    main()
    