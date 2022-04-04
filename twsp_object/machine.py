from typing import List
from .dto import DTO
from .window import Window


class Machine(DTO):
    def __init__(self, num_wins: int, windows: List[Window], split_min: int, machine_name: str):
        self.num_wins = num_wins
        self.windows = windows
        self.split_min = split_min
        self.machine_name = machine_name

    @property
    def total_idle_time(self):
        assert len(self.windows) > 1
        return sum([window.idle_time for window in self.windows[:-1]])

    def get_processed_time(self):
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
