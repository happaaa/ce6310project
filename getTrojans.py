import pandas as pd
from tqdm import tqdm
import argparse
import sys
from importlib import import_module

# COMPUTER CONTROL VALUES FROM DATA_OUT FILE
def getControl(INPUTS: list, WIRES: list,  num_samples: int, infile: str, outfile: str):
    tt = open(infile)
    control_vals = []
    for k in tqdm(range(len(INPUTS)), desc='Getting control values', ascii=False, ncols=100):
        control = [0 for i in WIRES]
        for index in range(0, num_samples):
            tt.read(len(INPUTS))
            line0 = tt.read(len(WIRES))
            if tt.read(1) != '\n':
                raise Exception("SOMETHING SPACED WRONG")
            tt.read(len(INPUTS))
            line1 = tt.read(len(WIRES))
            line0_val, line1_val = removexz(line0, line1)
            xor = bin(line0_val ^ line1_val)[2:].zfill(len(WIRES))
            xor = [int(k) for k in xor]
            control = [val + xor[index] for index, val in enumerate(control)]
            tt.read(1)
        control_vals.append(control)

    tt.close()
    control_df = pd.DataFrame(control_vals, index=INPUTS, columns=WIRES)
    control_df.to_csv(outfile)

# REMOVE UNKNOWN AND HIGH-IMPEDANCE VALUES FROM DATA_OUT LINES
def removexz(line0: str, line1: str):
    while 'x' in line0:
        loc = line0.find('x')
        if line1[loc] == 'x':
            line0 = line0[:loc] + '0' + line0[loc+1:]
            line1 = line1[:loc] + '0' + line1[loc+1:]
        elif line1[loc] == '0':
            line0 = line0[:loc] + '1' + line0[loc+1:]
        elif line1[loc] == '1':
            line0 = line0[:loc] + '0' + line0[loc+1:]
    while 'x' in line1:
        loc = line1.find('x')
        if line0[loc] == '0':
            line1 = line1[:loc] + '1' + line1[loc+1:]
        elif line0[loc] == '1':
            line1 = line1[:loc] + '0' + line1[loc+1:]
    while 'z' in line0:
        loc = line0.find('z')
        if line1[loc] == 'z':
            line0 = line0[:loc] + '0' + line0[loc+1:]
            line1 = line1[:loc] + '0' + line1[loc+1:]
        elif line1[loc] == '0':
            line0 = line0[:loc] + '1' + line0[loc+1:]
        elif line1[loc] == '1':
            line0 = line0[:loc] + '0' + line0[loc+1:]
    while 'z' in line1:
        loc = line1.find('z')
        if line0[loc] == '0':
            line1 = line1[:loc] + '1' + line1[loc+1:]
        elif line0[loc] == '1':
            line1 = line1[:loc] + '0' + line1[loc+1:]
    return int(line0, 2), int(line1, 2)

# PERFORM HEURISTICS ON CONTROL TABLE
def getHeuristic(WIRES: list, num_samples: int, inCSV: str, outCSV: str):
    control_heuristic = []
    control_df = pd.read_csv(inCSV, index_col=0)
    control_df = control_df.div(num_samples)
    for col in control_df:
        control_heuristic.append([control_df[control_df[col] != 0][col].mean(), control_df[control_df[col] != 0][col].median()])
    heuristic_df = pd.DataFrame(control_heuristic, index=WIRES, columns=['mean', 'median'])
    heuristic_df.to_csv(outCSV)

# MARK SUSPICIOUS WIRES FROM HEURISTIC TABLE
def markSusWires(inCSV: str, outCSV: str, threshold: float = 0.01):
    heuristic_df = pd.read_csv(inCSV, index_col=0)
    heuristic_df = heuristic_df.fillna(1).T
    sus_wires_mean = []
    sus_wires_median = []
    sus_wires_both = []
    for wire in heuristic_df:
        if (heuristic_df.loc['mean', wire] < threshold):
            sus_wires_mean.append(wire)
        if (heuristic_df.loc['median', wire] < threshold):
            sus_wires_median.append(wire)
        if (heuristic_df.loc['mean', wire] < threshold and heuristic_df.loc['median', wire] < threshold):
            sus_wires_both.append(wire)
    outfile = open(outCSV, 'w')
    outfile.write('SUSPICIOUS WIRES')
    outfile.write('\nMEAN,')
    [outfile.write(i + ',') for i in sus_wires_mean]
    outfile.write('\nMEDIAN,')
    [outfile.write(i + ',') for i in sus_wires_median]
    outfile.write('\nBOTH,')
    [outfile.write(i + ',') for i in sus_wires_both]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-benchmark', type=str, help='trusthub benchmark')
    parser.add_argument('-data', type=str, help='data_out file from verilog testbench')
    parser.add_argument('--manual_threshold', action='store_true', 
                        help='pause marking suspicious wires to determine threshold manually')
    parser.add_argument('-t', type=float, help='manual threshold setting')

    args = parser.parse_args()
    benchmark = args.benchmark
    data = args.data
    flag_threshold = args.manual_threshold
    threshold = args.t

    if benchmark is None:
        print("NO BENCHMARK NAME GIVEN")
        sys.exit()

    benchmark_module = 'netlists.' + benchmark + '_net'
    benchmark_module = import_module(benchmark_module)
    controlvals = 'postprocessing/' + benchmark + '_' + str(benchmark_module.NUM_SAMPLES) + 'control.csv'
    heuristics = 'postprocessing/' + benchmark + '_' + str(benchmark_module.NUM_SAMPLES) + 'heuristic.csv'
    sus_wires = 'postprocessing/' + benchmark + '_' + str(benchmark_module.NUM_SAMPLES) + 'marked.csv'

    if threshold is not None:
        markSusWires(heuristics, sus_wires, threshold)
        sys.exit()

    if data is None:
        print("NO DATA_OUT FILE GIVEN")
        sys.exit()
    

    getControl(benchmark_module.INPUTS, benchmark_module.WIRES, benchmark_module.NUM_SAMPLES, data, controlvals)
    getHeuristic(benchmark_module.WIRES, benchmark_module.NUM_SAMPLES, controlvals, heuristics)
    if not flag_threshold:
        markSusWires(heuristics, sus_wires)




    
