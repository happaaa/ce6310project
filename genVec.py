from random import randint
from math import log2
import sys
import argparse

benchmark_dict = {  's15850': 88, 
                    's35932': 136,
                    's38417': 129,
                    's38584': 139,
                 }

# GENERATE VECTOR FILE OF RANDOM COMBINATIONS OF INPUTS
def genVec(num_inputs: int, num_samples: int, benchmark: str):
    if log2(num_samples) >= num_inputs:
        raise Exception("ERROR: NUM OF SAMPLES EXCEEDS POSSIBLE NUMBER OF INPUT COMBINATIONS")

    outfile = 'vectorfiles/' + benchmark + '_' + str(num_samples) + 'samples.vec'
    vec = open(outfile, 'w')
    for i in range(num_inputs):
        prev_combinations = set()
        rand0 = '0'.zfill(num_inputs)
        for j in range(num_samples):
            while rand0 in prev_combinations:
                # roll until new combination
                rand_int = randint(0, 2 ** num_inputs)
                randint_bin = bin(rand_int).split('b')[1].zfill(num_inputs)
                rand0 = randint_bin[:i] + '0' + randint_bin[i + 1:]
            # append new combination to list
            prev_combinations.add(rand0)
            rand1 = rand0[:i] + '1' + rand0[i + 1:]
            vec.write(rand0 + '\n')
            vec.write(rand1 + '\n')
    vec.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-benchmark', type=str, help='trusthub benchmark')
    parser.add_argument('-num_samples', type=int, help='amount of random samples of truth table to sample')

    args = parser.parse_args()
    benchmark = args.benchmark
    num_samples = args.num_samples

    if benchmark is None or num_samples is None:
        print("NO BENCHMARK OR NUMBER OF SAMPLES GIVEN")
        sys.exit()

    if (benchmark not in benchmark_dict.keys()):
        num_inputs = input("Enter number of inputs in benchmark: ")
        benchmark_dict[benchmark] = int(num_inputs)

    genVec(benchmark_dict[benchmark], num_samples, benchmark)