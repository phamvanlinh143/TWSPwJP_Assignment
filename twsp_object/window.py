from .dto import DTO


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
