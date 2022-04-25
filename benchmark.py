import re
import os

def print_test_result(filename):
    print('#'*20 + filename + '#'*20)
    file = open(filename, "r")
    lines = file.readlines()

    float_number = r'(\d+).(\d+)(e-\d+)?'
    algo_names = ["FCFS", "Tabu Search", "Hill climbing", "Beam search"]

    count = 0
    elapsed_times = [[]]
    lower_bounds = []
    cmaxs = [[]]
    for line in lines:
        if re.search('Lower Bound', line):
            lb = int(re.search(r'\d+', line).group())
            lower_bounds.append(lb)
        elif re.search('Cmax', line):
            cmax = int(re.search(r'\d+', line).group())
            if len(cmaxs[-1]) == 4:
                cmaxs.append([])
            cmaxs[-1].append(cmax)
        elif re.search('elapsed', line, re.IGNORECASE):
            if len(elapsed_times[-1]) == 4:
                elapsed_times.append([])
            time = float(re.search(float_number, line).group())
            elapsed_times[-1].append(time)

    times = [0.0]*4
    print("Time")
    for e in elapsed_times:
        for i, d in enumerate(e):
            times[i] += d

    for i, time in enumerate(times):
        print(f"{algo_names[i]:14}: {(str(time / len(lower_bounds)).replace('.', ','))}")
    print()

    print()
    print("#MIN")
    sharp_min = [0]*4
    for e in cmaxs:
        min_cmax = min(e)
        for i, d in enumerate(e):
            if d == min_cmax:
                sharp_min[i] += 1

    for i, v in enumerate(sharp_min):
        print(f"{algo_names[i]:14}: {v}")

    print()
    print("%LB")
    percent_lb = [0.0]*4
    for i, e in enumerate(cmaxs):
        for j, d in enumerate(e):
            lb = (d - lower_bounds[i]) / lower_bounds[i]
            percent_lb[j] += lb

    for i, e in enumerate(percent_lb):
        print(f"{algo_names[i]:14}: {str(e / len(lower_bounds)).replace('.', ',')}")
    print()

if __name__ == '__main__':
    for name in os.listdir('./'):
        if re.search(".txt", name):
            print(name)
            print_test_result(name)
