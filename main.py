from twsp_object import Window, Machine, Job, INF_TIME, TWSPwJP

def run():
    split_min = 3
    J1 = Job(process_time=6, split_min=split_min)
    J2 = Job(process_time=7, split_min=split_min)
    J3 = Job(process_time=8, split_min=split_min)
    J4 = Job(process_time=5, split_min=split_min)
    J5 = Job(process_time=10, split_min=split_min)
    J6 = Job(process_time=4, split_min=split_min)
    lst_jobs = [J1, J2, J3, J4, J5, J6]
    LPT_lst_job = sorted(lst_jobs, key=lambda x: x.process_time, reverse=True)
    SPT_lst_job = sorted(lst_jobs, key=lambda x: x.process_time, reverse=False)


    W11 = Window(index=1, start_time=0, end_time=7)
    W12 = Window(index=2, start_time=7, end_time=12)
    W13 = Window(index=3, start_time=12, end_time=20)
    W14 = Window(index=4, start_time=20, end_time=INF_TIME)
    lst_window_m1 = [W11, W12, W13, W14]

    M1 = Machine(num_wins=len(lst_window_m1), windows=lst_window_m1, split_min=split_min)

    W21 = Window(index=1, start_time=0, end_time=5)
    W22 = Window(index=2, start_time=5, end_time=11)
    W23 = Window(index=3, start_time=11, end_time=18)
    W24 = Window(index=4, start_time=18, end_time=INF_TIME)
    lst_window_m2 = [W21, W22, W23, W24]

    M2 = Machine(num_wins=len(lst_window_m2), windows=lst_window_m2, split_min=split_min)

    solver = TWSPwJP(jobs=lst_jobs, machines=[M1, M2], split_min=split_min)

    solver.init_solution()
    cmax = 0
    for machine in solver.machines:
        for window in machine.windows:
            if window.pivot_time > cmax:
                cmax = window.pivot_time
    print(f"Cmax = {cmax}")
    solver.reset()

    solver = TWSPwJP(jobs=LPT_lst_job, machines=[M1, M2], split_min=split_min)
    solver.init_solution()
    cmax = 0
    for machine in solver.machines:
        for window in machine.windows:
            if window.pivot_time > cmax:
                cmax = window.pivot_time
    print(f"LPT Cmax = {cmax}")
    solver.reset()

    solver = TWSPwJP(jobs=SPT_lst_job, machines=[M1, M2], split_min=split_min)
    solver.init_solution()
    cmax = 0
    for machine in solver.machines:
        for window in machine.windows:
            if window.pivot_time > cmax:
                cmax = window.pivot_time
    print(f"SPT Cmax = {cmax}")
    solver.reset()

if __name__ == '__main__':
    run()
