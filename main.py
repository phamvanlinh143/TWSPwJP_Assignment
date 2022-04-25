from twsp_object import TWSPwJP
from twsp_object import Job, Window, Machine, INF_TIME
import os
import sys
import time
from utils import load_json_data, visualize

out = sys.stdout

def parse_dataset(json_path):
    data = load_json_data(json_path)

    split_min = data['Splitmin']
    lst_jobs = []
    for job in data['Jobs']:
        job_obj = Job(process_time=job['Processing'], split_min=split_min, job_name=job['Name'])
        lst_jobs.append(job_obj)

    lst_machines = []
    for machine in data['Machines']:
        lst_window = []
        for idx, window in enumerate(machine['Windows']):
            if window['StartTime'] + window['Capacity'] >= INF_TIME:
                window_obj = Window(index=idx + 1, start_time=window['StartTime'], end_time=INF_TIME)
            else:
                window_obj = Window(index=idx + 1, start_time=window['StartTime'],
                                    end_time=window['StartTime'] + window['Capacity'])
            lst_window.append(window_obj)
        machine_obj = Machine(num_wins=len(lst_window), windows=lst_window, split_min=split_min,
                              machine_name=machine['Name'])
        lst_machines.append(machine_obj)

    return split_min, lst_jobs, lst_machines


def run(file: str):
    with open(file.split('/')[-2] + ".txt", 'a') as f:
        sys.stdout = f
        split_min, lst_jobs, lst_machines = parse_dataset(file)
        for job in lst_jobs:
            print(job)
        for machine in lst_machines:
            print(machine)

        solver = TWSPwJP(jobs=lst_jobs, machines=lst_machines, split_min=split_min)
        print(f"Lower Bound = {solver.LB}")

        start_time = time.time()
        solver.solve()
        print(f"Elapsed time: {time.time() - start_time}")
        print(f"FCFS Cmax = {solver.cmax}")
        solver.reset()
        print("=" * 80)
        solver.tabu_search(limit_time=30, tabu_size=4096)
        print(f"Tabu Search Cmax = {solver.cmax}")
        solver.reset()
        print("=" * 80)
        solver.hill_climbing(limit_time=60)
        print(f"Hill Climbing Cmax = {solver.cmax}")
        solver.reset()
        print("=" * 80)
        solver.local_beam_search(limit_time=60, beam_width=5)
        print(f"Local Beam Search Cmax = {solver.cmax}")
        print("=" * 80)
        for machine in solver.machines:
            print(machine.machine_name)
            for window in machine.windows:
                print(window)
        visualize(solver.machines, lst_jobs, image_name='input_10_2_3_5')
        solver.reset()
        sys.stdout = out

def get_files(dirname: str) -> list[str]:
    res = []
    for name in os.listdir(dirname):
        f = os.path.join(dirname, name)
        if os.path.isfile(f):
            res.append(f)
        else:
            res += get_files(f)
    return res

def main():
    # run('dataset/DS0/input1.json')
    # run('dataset/DS0/input2.json')
    # run('dataset/DS0/input3.json')
    dirs = ['dataset/DS1/10_2_3',
    'dataset/DS1/10_3_3',
    'dataset/DS1/10_4_3',
    'dataset/DS1/20_2_3',
    'dataset/DS1/20_3_3',
    'dataset/DS1/20_4_3',
    'dataset/DS1/30_2_3',
    'dataset/DS1/30_3_3',
    'dataset/DS1/30_4_3',]
    for dir in dirs:
        for name in os.listdir(dir):
            f = os.path.join(dir, name)
            if os.path.isfile(f):
                run(f)

if __name__ == '__main__':
    main()
