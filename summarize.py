"""

Evan Caplinger, (c)2025

Sept. 2025

Description: This code looks at the output from a slurm batch job output file and generates a .csv of runtime or other metrics for the run.

Inputs:
    filename        the name of the output file we read from
    indirect        choose the type of indirect sum we want to read. expect 'indirect_sum' or 'indirect_sum_seed'
    trial           choose the indirect sum trial we want. must be an integer that is found in the output file
    transformation  if you want to calculate a statistic other than runtime, state that here. accepts 'runtime', 'mflops_per_s', 'avg_latency', 'bandwidth', 'pct_bandwidth'
    average         set this flag if you want to also calculate the average of all problem sizes

Outputs: a .csv file with filename <original_filename>_<indirect>_<trial>_<transformation>.csv

Dependencies: argparse

"""

import re
import argparse
import os

PEAK_FLOPS = 3.92e10
PEAK_BANDWIDTH = 2.048e11

TRANSFORM_LUT = {
    'runtime':      lambda n, t: t,
    'mflops':       lambda n, t: 2 * n * n / (t * 1000000),
    'bandwidth':    lambda n, t: (8 * (n * (2 + 2 * n)) / t) / 1e9,
    'pct_bandwidth':lambda n, t: 100 * ((8 * (n * (2 + 2 * n)) / t) / PEAK_BANDWIDTH),
    'avg_latency':  lambda n, t: t / (n * (2 + 2 * n))
}

P_SIZES = [1, 4, 16, 64]

parser = argparse.ArgumentParser(prog='summarize.py')
parser.add_argument('filename')
# parser.add_argument('indirect')
# parser.add_argument('trial')
parser.add_argument('-t', '--transformation', default='runtime')
parser.add_argument('-a', '--average', action='store_true')
args = parser.parse_args()
fn = args.filename

if args.transformation not in TRANSFORM_LUT.keys() \
        and args.transformation != 'speedup':
    raise Exception('not a recognized transformation')

with open(fn, 'r') as f:
    lines = f.readlines()

problems = []
lastmatch = 0
for i, l in enumerate(lines):
    m = re.search('Description:\s+(.+)\.', l)
    if m:
        if i != 0:
            problems.append(lines[lastmatch:i])
        lastmatch = i
problems.append(lines[lastmatch:len(lines)])

data = {}
ns = []

p_counter = 0

for i, p in enumerate(problems):
    print(p[0])
    m = re.search('Description:\s+(.+)\.', p[0])    # get impl
    print(m[1])
    if m:
        desc = m[1]
        if desc == 'OpenMP dgemv':
            desc = f'{desc}; P={P_SIZES[p_counter]}'
            p_counter += 1
        elif 'Vectorized' in desc:
            desc = 'Vectorized dgemv'
        elif 'Basic' in desc:
            desc = 'Basic dgemv'
        
        # if desc not in data.keys():
        #     data[desc] = {}                             # add impl to list "categories"
        for l in p[1:]:
            v = re.search('Problem size N\=(\d+) took (\d+\.\d+) seconds', l)
            if v:
                n = int(v[1])
                t = float(v[2])
                if not desc in data.keys():
                    data[desc] = {}
                if not n in ns:
                    ns.append(n)
                if args.transformation == 'speedup':
                    if desc == 'Basic dgemv':
                        data[desc][n] = t
                    else:
                        data[desc][n] = data['Basic dgemv'][n] / t
                else:
                    data[desc][n] = TRANSFORM_LUT[args.transformation](n, t)
    
    else:
        print('uh oh something went really wrong')
        exit()


to_write = []
to_write.append('Implementation,' + ','.join([f'{i}' for i in sorted(ns)]) + '\n')
for k in sorted(data.keys()):
    v = data[k]
    to_write.append(f'{k},' + ','.join([f'{v[i]}' for i in sorted(ns)]) + '\n')

fn_out = fn.split('.')[0] + f'_{args.transformation}.csv'
with open(fn_out, 'w+') as f:
    f.writelines(to_write)