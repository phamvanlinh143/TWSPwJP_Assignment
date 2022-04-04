import math
import time
import random
from typing import List
from operator import itemgetter
from .machine import Machine
from .job import Job
from .dto import DTO
from utils import get_neighbor_index


class TWSPwJP(DTO):

    NEG_INF_CMAX = -1

    def __init__(self, jobs: List[Job], machines: List[Machine], split_min: int):
        self.jobs = jobs
        self.machines = machines
        self.split_min = split_min

        self.job_order = list(range(len(self.jobs)))
        self.cmax_memory = dict()

    def reset_job_order(self):
        self.job_order = list(range(len(self.jobs)))

    @property
    def num_jobs(self):
        return len(self.jobs)

    @property
    def cmax(self):
        return max(job.completion_time for job in self.jobs)

    @property
    def num_machines(self):
        return len(self.machines)

    @property
    def LB(self):
        total_ptime = sum(job.process_time for job in self.jobs)
        return math.ceil(total_ptime / self.num_machines)

    def reset(self):
        for machine in self.machines:
            machine.reset()
        for job in self.jobs:
            job.reset()

    def get_machine_has_ready(self, job: Job):
        lst_processed_time = [machine.get_processed_time() for machine in self.machines]
        # min_idx = np.argmin(np.array(lst_processed_time)).item()
        min_idx, _ = min(enumerate(lst_processed_time), key=itemgetter(1))
        return self.machines[min_idx]

    # Assignment Algorithm
    def solve(self):
        self.reset()
        exe_order_jobs = [self.jobs[idx] for idx in self.job_order]
        for job in exe_order_jobs:
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

    def update_cmax_mem(self, info):
        self.cmax_memory.update(info)

    def get_cmax_from_memory(self, info):
        order_ptime = info.get('order_ptime', ())
        return self.cmax_memory.get(order_ptime, self.NEG_INF_CMAX)

    def solution_info(self):
        order_ptime = tuple(self.jobs[idx].process_time for idx in self.job_order)
        cmax = self.cmax
        self.update_cmax_mem({order_ptime: cmax})
        return {'order_ptime': order_ptime, 'cmax': cmax, 'index': tuple(self.job_order)}

    def tabu_search(self, limit_time: float = 270.0, tabu_size: int = 4096):
        self.reset_job_order()
        tabu_list = []
        start_time = time.time()

        neighbor_index_cache = get_neighbor_index(self.num_jobs)
        self.solve()
        sol_info = self.solution_info()
        self.reset()

        best_solution = sol_info
        tabu_list.append(sol_info['order_ptime'])

        best_job_order = self.job_order
        candidate_job_order = self.job_order

        lower_bound = self.LB
        exec_flag = True
        elapsed_time = time.time() - start_time

        while best_solution.get('cmax', lower_bound + 1) > lower_bound and elapsed_time < limit_time and exec_flag:
            neighbor_infos = []
            for neighbor_index in neighbor_index_cache:
                neighbor_info = dict()
                neighbor_info['index'] = tuple(candidate_job_order[idx] for idx in neighbor_index)
                neighbor_info['order_ptime'] = tuple(self.jobs[idx].process_time for idx in neighbor_info['index'])
                neighbor_info['cmax'] = self.get_cmax_from_memory(neighbor_info)
                if neighbor_info['order_ptime'] not in tabu_list:
                    neighbor_infos.append(neighbor_info)

            if len(neighbor_infos) == 0:
                exec_flag = False
                continue

            for neighbor_info in neighbor_infos:
                if neighbor_info['cmax'] > self.NEG_INF_CMAX:
                    continue
                self.job_order = neighbor_info['index']
                self.solve()
                cur_sol_info = self.solution_info()
                neighbor_info['cmax'] = cur_sol_info['cmax']

            lst_cmax = [neighbor_info['cmax'] for neighbor_info in neighbor_infos]
            best_cand_idx = lst_cmax.index(min(lst_cmax))
            best_candidate = neighbor_infos[best_cand_idx]
            candidate_job_order = best_candidate['index']

            if best_solution['cmax'] > best_candidate['cmax']:
                best_solution = best_candidate
                best_job_order = best_solution['index']

            tabu_list.append(best_candidate['order_ptime'])
            if len(tabu_list) > tabu_size:
                tabu_list.pop(0)
            elapsed_time = time.time() - start_time

        print(f"elapsed time = {elapsed_time}")
        self.job_order = best_job_order
        self.solve()
        print(best_solution)

    def hill_climbing(self, limit_time: float = 270.0):
        self.reset_job_order()
        start_time = time.time()

        neighbor_index_cache = get_neighbor_index(self.num_jobs)
        self.solve()
        sol_info = self.solution_info()
        self.reset()

        best_solution = sol_info
        best_job_order = self.job_order
        candidate_job_order = self.job_order

        lower_bound = self.LB
        stop_flag = False
        elapsed_time = time.time() - start_time

        while best_solution.get('cmax', lower_bound + 1) > lower_bound and elapsed_time < limit_time and not stop_flag:
            neighbor_infos = []
            for neighbor_index in neighbor_index_cache:
                neighbor_info = dict()
                neighbor_info['index'] = tuple(candidate_job_order[idx] for idx in neighbor_index)
                neighbor_info['order_ptime'] = tuple(self.jobs[idx].process_time for idx in neighbor_info['index'])
                neighbor_info['cmax'] = self.get_cmax_from_memory(neighbor_info)
                neighbor_infos.append(neighbor_info)

            for neighbor_info in neighbor_infos:
                if neighbor_info['cmax'] > self.NEG_INF_CMAX:
                    continue
                self.job_order = neighbor_info['index']
                self.solve()
                cur_sol_info = self.solution_info()
                neighbor_info['cmax'] = cur_sol_info['cmax']

            lst_cmax = [neighbor_info['cmax'] for neighbor_info in neighbor_infos]
            best_cand_idx = lst_cmax.index(min(lst_cmax))
            best_candidate = neighbor_infos[best_cand_idx]
            candidate_job_order = best_candidate['index']

            if best_solution['cmax'] > best_candidate['cmax']:
                best_solution = best_candidate
                best_job_order = best_solution['index']
            else:
                stop_flag = True

            elapsed_time = time.time() - start_time
        print(f"elapsed time = {elapsed_time}")
        self.job_order = best_job_order
        self.solve()
        print(best_solution)

    def local_beam_search(self, limit_time: float = 270.0, beam_width=5):
        self.reset_job_order()
        start_time = time.time()
        neighbor_index_cache = get_neighbor_index(self.num_jobs)
        beam_sols = []
        org_order = self.job_order
        for _ in range(beam_width):
            job_order = [index for index in org_order]
            random.shuffle(job_order)
            self.job_order = job_order
            self.solve()
            cur_sol_info = self.solution_info()
            beam_sols.append(cur_sol_info)
            self.job_order = org_order
            self.reset()

        lst_beam_cmax = [neighbor_info['cmax'] for neighbor_info in beam_sols]
        best_cand_idx = lst_beam_cmax.index(min(lst_beam_cmax))
        best_solution = beam_sols[best_cand_idx]

        best_job_order = best_solution['index']

        lower_bound = self.LB
        stop_flag = False
        elapsed_time = time.time() - start_time

        while best_solution.get('cmax', lower_bound + 1) > lower_bound and elapsed_time < limit_time and not stop_flag:
            neighbor_infos = []
            for beam_sol in beam_sols:
                selected_neighbors = random.sample(neighbor_index_cache, k=beam_width)
                for neighbor_index in selected_neighbors:
                    neighbor_info = dict()
                    neighbor_info['index'] = tuple(beam_sol['index'][idx] for idx in neighbor_index)
                    neighbor_info['order_ptime'] = tuple(self.jobs[idx].process_time for idx in neighbor_info['index'])
                    neighbor_info['cmax'] = self.get_cmax_from_memory(neighbor_info)
                    neighbor_infos.append(neighbor_info)

            for neighbor_info in neighbor_infos:
                if neighbor_info['cmax'] > self.NEG_INF_CMAX:
                    continue
                self.job_order = neighbor_info['index']
                self.solve()
                cur_sol_info = self.solution_info()
                neighbor_info['cmax'] = cur_sol_info['cmax']

            lst_cmax = [neighbor_info['cmax'] for neighbor_info in neighbor_infos]
            index_with_res = list(sorted(enumerate(lst_cmax), key=itemgetter(1)))[:beam_width]
            beam_sols = [neighbor_infos[x[0]] for x in index_with_res]
            best_candidate = beam_sols[0]

            if best_solution['cmax'] >= best_candidate['cmax']:
                best_solution = best_candidate
                best_job_order = best_solution['index']
            else:
                stop_flag = True

            elapsed_time = time.time() - start_time

        print(f"elapsed time = {elapsed_time}")
        self.job_order = best_job_order
        self.solve()
        print(best_solution)
