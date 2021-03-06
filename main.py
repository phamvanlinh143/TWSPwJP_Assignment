import os
import sys
import time
import argparse

from typing import List
from pathlib import Path
from utils import load_json_data, visualize
from twsp_object import TWSPwJP
from twsp_object import Job, Window, Machine, INF_TIME


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
    split_min, lst_jobs, lst_machines = parse_dataset(file)
    for job in lst_jobs:
        print(job)
    for machine in lst_machines:
        print(machine)

    input_name = Path(file).stem
    print("=" * 80)
    solver = TWSPwJP(jobs=lst_jobs, machines=lst_machines, split_min=split_min)
    print(f"Lower Bound = {solver.LB}")

    print("=" * 80)
    start_time = time.time()
    solver.solve()
    print(f"elapsed time: {time.time() - start_time}")
    print(solver.solution_info())
    print(f"FCFS Cmax = {solver.cmax}")
    visualize(solver.machines, lst_jobs, image_name=f'{input_name}', prefix="FCFS")
    solver.reset()
    print("=" * 80)
    solver.tabu_search(limit_time=30, tabu_size=4096)
    print(f"Tabu Search Cmax = {solver.cmax}")
    visualize(solver.machines, lst_jobs, image_name=f'{input_name}', prefix="Tabu")
    print("=" * 80)
    solver.reset()
    solver.hill_climbing(limit_time=30)
    print(f"Hill Climbing Cmax = {solver.cmax}")
    visualize(solver.machines, lst_jobs, image_name=f'{input_name}', prefix="Hill")
    print("=" * 80)
    solver.reset()
    solver.local_beam_search(limit_time=30, beam_width=5)
    visualize(solver.machines, lst_jobs, image_name=f'{input_name}', prefix="Beam")
    print(f"Local Beam Search Cmax = {solver.cmax}")
    print("=" * 80)
    solver.reset()


def get_files(dirname: str) -> List[str]:
    res = []
    for name in os.listdir(dirname):
        f = os.path.join(dirname, name)
        if os.path.isfile(f):
            res.append(f)
        else:
            res += get_files(f)
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, help='data_path', default='dataset/DS1/10_2_3/input_10_2_3_5.json')
    args = parser.parse_args()
    # run('dataset/DS0/input1.json')
    # run('dataset/DS0/input2.json')
    # run('dataset/DS0/input3.json')
    # dirs = ['dataset/DS1/10_2_3',
    #         'dataset/DS1/10_3_3',
    #         'dataset/DS1/10_4_3',
    #         'dataset/DS1/20_2_3',
    #         'dataset/DS1/20_3_3',
    #         'dataset/DS1/20_4_3',
    #         'dataset/DS1/30_2_3',
    #         'dataset/DS1/30_3_3',
    #         'dataset/DS1/30_4_3', ]
    # for dir in dirs:
    #     for name in os.listdir(dir):
    #         f = os.path.join(dir, name)
    #         if os.path.isfile(f):
    #             run(f)

    run(args.data_path)


if __name__ == '__main__':
    main()
