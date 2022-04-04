from .dto import DTO
from .machine import Machine


class SubJob(DTO):
    def __init__(self, p_time, parent_name: str = '', owner_name: str = ''):
        self.p_time = p_time
        self.parent_name = parent_name
        self.owner_name = owner_name


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
        sub_job = SubJob(p_time=p_time, parent_name=self.job_name, owner_name=machine.machine_name)
        self.pivot_time = self.pivot_time + p_time
        self.sub_jobs.append(sub_job)
        return sub_job

    def reset(self):
        self.sub_jobs.clear()
        self.pivot_time = self.start_time
        self._owner = None
