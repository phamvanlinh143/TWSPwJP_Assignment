from twsp_object import Window, Machine, Job, INF_TIME, TWSPwJP
import numpy as np
import copy
import json

def parse_dataset(json_path):
    with open(json_path,'r') as f:
        data = json.load(f)
    split_min = data['Splitmin']
    lst_jobs = []
    for job in data['Jobs']:
        job_obj = Job(process_time=job['Processing'], split_min=split_min, job_name=job['Name'])
        lst_jobs.append(job_obj)
    LPT_lst_job = sorted(lst_jobs, key=lambda x: x.process_time, reverse=True)
    SPT_lst_job = sorted(lst_jobs, key=lambda x: x.process_time, reverse=False)

    lst_machines = []
    for machine in data['Machines']:
        lst_window = []
        for idx, window in enumerate(machine['Windows']):
            if window['StartTime']+window['Capacity'] >= INF_TIME:
                window_obj = Window(index=idx+1, start_time=window['StartTime'], end_time=INF_TIME)
            else:
                window_obj = Window(index=idx+1, start_time=window['StartTime'], end_time=window['StartTime']+window['Capacity'])
            lst_window.append(window_obj)
        machine_obj = Machine(num_wins=len(lst_window), windows=lst_window, split_min=split_min, machine_name=machine['Name'])
        lst_machines.append(machine_obj)
    
    return split_min, lst_jobs, lst_machines

def run():
    # # -------------- initial data --------------
    # split_min = 3
    # J1 = Job(process_time=6, split_min=split_min, job_name="J1")
    # J2 = Job(process_time=7, split_min=split_min, job_name="J2")
    # J3 = Job(process_time=8, split_min=split_min, job_name="J3")
    # J4 = Job(process_time=5, split_min=split_min, job_name="J4")
    # J5 = Job(process_time=10, split_min=split_min, job_name="J5")
    # J6 = Job(process_time=4, split_min=split_min, job_name="J6")
    # lst_jobs = [J1, J2, J3, J4, J5, J6]
    # LPT_lst_job = sorted(lst_jobs, key=lambda x: x.process_time, reverse=True)
    # SPT_lst_job = sorted(lst_jobs, key=lambda x: x.process_time, reverse=False)
    #
    # W11 = Window(index=1, start_time=0, end_time=7)
    # W12 = Window(index=2, start_time=7, end_time=12)
    # W13 = Window(index=3, start_time=12, end_time=20)
    # W14 = Window(index=4, start_time=20, end_time=INF_TIME)
    # lst_window_m1 = [W11, W12, W13, W14]
    # M1 = Machine(num_wins=len(lst_window_m1), windows=lst_window_m1, split_min=split_min, machine_name="M1")
    #
    # W21 = Window(index=1, start_time=0, end_time=5)
    # W22 = Window(index=2, start_time=5, end_time=11)
    # W23 = Window(index=3, start_time=11, end_time=18)
    # W24 = Window(index=4, start_time=18, end_time=INF_TIME)
    # lst_window_m2 = [W21, W22, W23, W24]
    # M2 = Machine(num_wins=len(lst_window_m2), windows=lst_window_m2, split_min=split_min, machine_name="M2")
    # # -------------- end initial data --------------

    # -------------- initial data --------------
#     split_min = 3
#     J1 = Job(process_time=6, split_min=split_min, job_name="J1")
#     J2 = Job(process_time=7, split_min=split_min, job_name="J2")
#     J3 = Job(process_time=8, split_min=split_min, job_name="J3")
#     J4 = Job(process_time=5, split_min=split_min, job_name="J4")
#     J5 = Job(process_time=10, split_min=split_min, job_name="J5")
#     J6 = Job(process_time=4, split_min=split_min, job_name="J6")
#     lst_jobs = [J1, J2, J3, J4, J5, J6]
#     LPT_lst_job = sorted(lst_jobs, key=lambda x: x.process_time, reverse=True)
#     SPT_lst_job = sorted(lst_jobs, key=lambda x: x.process_time, reverse=False)

#     W11 = Window(index=1, start_time=0, end_time=7)
#     W12 = Window(index=2, start_time=7, end_time=12)
#     W13 = Window(index=3, start_time=12, end_time=20)
#     W14 = Window(index=4, start_time=20, end_time=INF_TIME)
#     lst_window_m1 = [W11, W12, W13, W14]
#     M1 = Machine(num_wins=len(lst_window_m1), windows=lst_window_m1, split_min=split_min, machine_name="M1")

#     W21 = Window(index=1, start_time=0, end_time=5)
#     W22 = Window(index=2, start_time=5, end_time=11)
#     W23 = Window(index=3, start_time=11, end_time=18)
#     W24 = Window(index=4, start_time=18, end_time=25)
#     W25 = Window(index=4, start_time=25, end_time=INF_TIME)
#     lst_window_m2 = [W21, W22, W23, W24, W25]
#     M2 = Machine(num_wins=len(lst_window_m2), windows=lst_window_m2, split_min=split_min, machine_name="M2")
    # -------------- end initial data --------------
    
    
    split_min, lst_jobs, lst_machines = parse_dataset('./dataset/DS0/input1.json')
    LPT_lst_job = sorted(lst_jobs, key=lambda x: x.process_time, reverse=True)
    SPT_lst_job = sorted(lst_jobs, key=lambda x: x.process_time, reverse=False)
    
    solver = TWSPwJP(jobs=lst_jobs, machines=lst_machines, split_min=split_min)

    solver.init_solution()
    cmax = max(job.completion_time for job in solver.jobs)
    print(f"Cmax = {cmax}")
    solver.reset()

    solver = TWSPwJP(jobs=LPT_lst_job, machines=lst_machines, split_min=split_min)
    solver.init_solution()
    cmax = max(job.completion_time for job in solver.jobs)
    print(f"LPT Cmax = {cmax}")
    solver.reset()

    solver = TWSPwJP(jobs=SPT_lst_job, machines=lst_machines, split_min=split_min)
    solver.init_solution()
    cmax = max(job.completion_time for job in solver.jobs)
    print(f"SPT Cmax = {cmax}")
    solver.reset()

    best_cmax = 100
    best_solver = None
    for _ in range(30):
        num_jobs = len(lst_jobs)
        rand_perm = np.random.permutation(num_jobs)
        rand_perm = rand_perm.tolist()
        new_lst_jobs = [lst_jobs[idx] for idx in rand_perm]
        solver = TWSPwJP(jobs=new_lst_jobs, machines=lst_machines, split_min=split_min)
        solver.init_solution()
        cmax = max(job.completion_time for job in solver.jobs)
        if cmax < best_cmax:
            best_solver = copy.deepcopy(solver)
            best_cmax = cmax
        print(f"Cmax = {cmax}")
        solver.reset()

    print(f"min cmax = {best_cmax}")
    for machine in best_solver.machines:
        print(machine.machine_name)
        for window in machine.windows:
            print(window)


if __name__ == '__main__':
    run()
