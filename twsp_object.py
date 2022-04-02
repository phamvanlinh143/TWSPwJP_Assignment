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
        self.assigned_jobs = []

    @property
    def remain_size(self):
        return self.end_time - self.pivot_time

    @property
    def idle_time(self):
        return self.remain_size

    @property
    def processed_time(self):
        return self.pivot_time - self.start_time

    def valid_insert_job(self, job):
        return job.p_time <= self.remain_size

    def insert_job(self, job):
        assert self.valid_insert_job(job)
        self.pivot_time = self.pivot_time + job.p_time
        self.assigned_jobs.append(job)

    def reset(self):
        self.assigned_jobs.clear()
        self.pivot_time = self.start_time


class Machine(DTO):
    def __init__(self, num_wins: int, windows: List[Window], split_min: int, machine_name: str):
        self.num_wins = num_wins
        self.windows = windows
        self.split_min = split_min
        self.machine_name = machine_name

    def get_processed_time(self):
        # Viết lại hàm này, hơi sai sai
        return sum(window.processed_time for window in self.windows)

    def get_processed_time_v2(self):
        # Viết hàm ưu tiên trả về khi một window còn dư nhiều hơn split_time
        processed_time = 0
        for window in self.windows:
            if len(window.assigned_jobs) == 0:
                break
            if window.idle_time >= self.split_min:
                processed_time = window.pivot_time
                return processed_time
            else:
                processed_time = window.pivot_time
        return processed_time

    def reset(self):
        for window in self.windows:
            window.reset()


class SubJob(DTO):
    def __init__(self, p_time, parent_name: str = '', owner: Machine = None):
        self.p_time = p_time
        self.parent_name = parent_name
        self.owner = owner


class Job(DTO):
    def __init__(self, process_time: int, split_min: int, job_name: str = "", owner: Machine = None):
        self.process_time = process_time
        self.split_min = split_min
        self._owner = owner
        self.job_name = job_name

        # processing
        self.start_time = 0
        self.pivot_time = self.start_time
        self.end_time = self.process_time

        self.sub_jobs = []

    @property
    def remain_time(self):
        return self.end_time - self.pivot_time

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, own):
        if self._owner is not None:
            assert isinstance(own, Machine)
            assert self._owner.machine_name == own.machine_name
        else:
            self._owner = own

    @property
    def splited_job(self):
        return len(self.sub_jobs) > 1

    @property
    def completion_time(self):
        compl_time = 0
        if self.owner is None:
            return compl_time
        for window in self.owner.windows:
            exed_time = window.start_time
            for sub_job in window.assigned_jobs:
                exed_time = exed_time + sub_job.p_time
                if sub_job.parent_name == self.job_name:
                    compl_time = exed_time

        return compl_time

    def create_sub_job(self, p_time, machine):
        assert p_time <= self.remain_time
        self.owner = machine
        sub_job = SubJob(p_time=p_time, parent_name=self.job_name, owner=machine)
        self.pivot_time = self.pivot_time + p_time
        self.sub_jobs.append(sub_job)
        return sub_job

    def all_sub_jobs_generator(self):
        self._all_subjobs = []
        all_sub_jobs = get_all_sub_jobs(self.process_time, self.split_min)
        for comb_jobs in all_sub_jobs:
            sub_job_ins = []
            for sub_job_time in comb_jobs:
                sub_job_ins.append(SubJob(p_time=sub_job_time, parent_name=self.job_name))
            self._all_subjobs.append(sub_job_ins)

    def reset(self):
        self.sub_jobs.clear()
        self.pivot_time = self.start_time
        self._owner = None


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
        lst_processed_time = [machine.get_processed_time_v2() for machine in self.machines]
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

    def reset(self):
        for machine in self.machines:
            machine.reset()
        for job in self.jobs:
            job.reset()
