from typing import List, Union, Optional
from dto import DTO
import numpy as np
from utils import get_all_sub_jobs

INF_TIME = 2000


class Window(DTO):
    def __init__(self, index: int, start_time: int, end_time: int):
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.pivot_time = self.start_time
        self.list_sub_jobs = []

    @property
    def remain_size(self):
        return self.end_time - self.pivot_time

    @property
    def idle_time(self):
        return self.remain_size

    @property
    def processed_time(self):
        return self.pivot_time - self.start_time

    def check_insert_job(self, job):
        return job.p_time < self.remain_size

    def insert_job(self, job):
        job_time = job.p_time
        assert job_time <= self.remain_size
        self.pivot_time = self.pivot_time + job_time
        self.list_sub_jobs.append(job)


class Machine(DTO):
    def __init__(self, num_wins: int, windows: List[Window], split_min: int):
        self.num_wins = num_wins
        self.windows = windows
        self.split_min = split_min

    def get_processed_time(self):
        return sum(window.processed_time for window in self.windows)


class SubJob(DTO):
    def __init__(self, p_time, status: bool = False, owner: Machine = None):
        self.p_time = p_time
        self.status = status
        self.owner = owner


class Job(DTO):
    def __init__(self, process_time: int, split_min: int, owner: Machine = None):
        self.process_time = process_time
        self.split_min = split_min
        self.owner = owner

        # processing
        self.start_time = 0
        self.end_time = self.process_time
        self.pivot_time = self.start_time

        self.sub_jobs = []

    @property
    def remain_time(self):
        return self.end_time - self.pivot_time

    @property
    def splited_job(self):
        return len(self.sub_jobs) > 1

    @property
    def completion_time(self):
        # TODO
        return 0

    def create_sub_job(self, p_time, machine):
        assert p_time <= self.remain_time
        sub_job = SubJob(p_time=p_time, owner=None)
        self.pivot_time = self.pivot_time + p_time
        self.sub_jobs.append(sub_job)
        return sub_job

    def all_sub_jobs_generator(self):
        self._all_subjobs = []
        all_sub_jobs = get_all_sub_jobs(self.process_time, self.split_min)
        for comb_jobs in all_sub_jobs:
            sub_job_ins = []
            for sub_job_time in comb_jobs:
                sub_job_ins.append(SubJob(p_time=sub_job_time))
            self._all_subjobs.append(sub_job_ins)


class TWSPwJP(DTO):
    def __init__(self, jobs: List[Job], machines: List[Machine], split_min: int):
        self.jobs = jobs
        self.machines = machines
        self.split_min = split_min
        self.cmax = -1

    @property
    def num_jobs(self):
        return len(self.jobs)

    @property
    def num_machines(self):
        return len(self.machines)

    def get_machine_has_ready(self, job: Job):
        # return with condition:
        # 1. machine has executed the job
        # 2. machine in machines with completion time is minimum
        lst_processed_time = [machine.get_processed_time() for machine in self.machines]
        min_idx = np.argmin(np.array(lst_processed_time)).item()
        return self.machines[min_idx]

    def init_solution(self):
        # Assignment Algorithm
        for job in self.jobs:
            machine = self.get_machine_has_ready(job)
            lst_windows = machine.windows
            for window in lst_windows:
                if job.remain_time >= self.split_min and window.remain_size >= self.split_min:
                    if job.remain_time <= window.remain_size:
                        # Assign job Ji with the size job.remain_time into current window
                        sub_job = job.create_sub_job(job.remain_time, machine)
                        window.insert_job(sub_job)
                    else:
                        if job.remain_time - window.remain_size >= self.split_min:
                            # Assign job Ji with the size window.remain_size into current window
                            sub_job = job.create_sub_job(window.remain_size, machine)
                            window.insert_job(sub_job)
                        elif job.remain_time - self.split_min >= self.split_min:
                            # Assign job Ji with the size (job.remain_time - self.split_min) into current window
                            sub_job = job.create_sub_job(job.remain_time - self.split_min, machine)
                            window.insert_job(sub_job)
