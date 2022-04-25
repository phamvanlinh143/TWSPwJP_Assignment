import json
from itertools import combinations
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from mycolorpy import colorlist as mcp
from pathlib import Path


def load_json_data(json_path):
    with open(json_path, mode='r', encoding='utf-8') as f:
        data = json.load(f)
        f.close()
    return data


def swap_func(lst_size, pos_1, pos_2):
    res_lst = list(range(lst_size))
    res_lst[pos_1], res_lst[pos_2] = res_lst[pos_2], res_lst[pos_1]
    return tuple(res_lst)


def insert_backward_func(lst_size, pos_1, pos_2):
    res_lst = list(range(lst_size))
    pop_value = res_lst.pop(pos_2)
    res_lst.insert(pos_1, pop_value)
    return tuple(res_lst)


def insert_forward_func(lst_size, pos_1, pos_2):
    res_lst = list(range(lst_size))
    pop_value = res_lst.pop(pos_1)
    res_lst.insert(pos_2, pop_value)
    return tuple(res_lst)


def get_neighbor_index(lst_job_size):
    swap = list(combinations(range(lst_job_size), 2))
    insert = list(filter(lambda x: abs(x[0] - x[1]) > 1, swap))

    swap_list = list(map(lambda x: swap_func(lst_job_size, x[0], x[1]), swap))
    backward_list = list(map(lambda x: insert_backward_func(lst_job_size, x[0], x[1]), insert))
    forward_list = list(map(lambda x: insert_forward_func(lst_job_size, x[0], x[1]), insert))

    neighbor_index = {*swap_list, *backward_list, *forward_list}

    return list(neighbor_index)


def visualize(machines, lst_jobs, image_name='image', prefix="fcfs"):
    color1 = mcp.gen_color(cmap="tab20", n=len(lst_jobs))
    job_color_dict = {}
    for idx, job in enumerate(lst_jobs):
        job_color_dict[job.job_name] = color1[idx]

    machine_idx_map = {}
    for idx, machine in enumerate(machines):
        machine_idx_map[machine.machine_name] = idx

    plot_arr = []
    for machine in machines:
        for window in machine.windows:
            start_time = window.start_time
            for sub_job in window.assigned_jobs:
                res = {}
                res['Machine'] = machine.machine_name
                res['Duration'] = sub_job.p_time
                res['Job'] = sub_job.parent_name
                res['Start'] = start_time
                res['Finish'] = start_time + sub_job.p_time
                res['Color'] = job_color_dict[sub_job.parent_name]
                start_time = res['Finish']
                plot_arr.append(res)

    df = pd.DataFrame(plot_arr)
    max_finish = max(df['Finish'])
    fig, ax = plt.subplots(len(machines), 1, figsize=(12, 5 + (len(lst_jobs) + len(machines)) / 4))
    for idx, machine in enumerate(machines):
        ax[idx].set_ylim([0, 0.5])
        ax[idx].set_xlim([0, max_finish + 2])
        ax[idx].xaxis.set_ticks(np.arange(0, max_finish + 2, 2))
        ax[idx].set_yticklabels([])
        ax[idx].set_ylabel(machine.machine_name, rotation=0)
        ax[idx].set_xlabel('Time', rotation=0)
        ax[idx].spines['top'].set_visible(False)
        ax[idx].spines['right'].set_visible(False)
        ax[idx].plot(1, 0, ">k", transform=ax[idx].get_yaxis_transform(), clip_on=False)
        #     ax[idx].plot(0, 1, "^k", transform=ax[idx].get_xaxis_transform(), clip_on=False)
        for window in machine.windows:
            ax[idx].axvline(window.end_time, ymax=0.7, color='red', linewidth=3.2)

    for item in plot_arr:
        rectangle = Rectangle((item['Start'], 0), item['Finish'] - item['Start'], 0.25, color=item['Color'], alpha=0.25,
                              linewidth=2.5)
        ax[machine_idx_map[item['Machine']]].add_patch(rectangle)
        rx, ry = rectangle.get_xy()
        #     cx = rx + rectangle.get_width()/2.0
        #     cy = ry + rectangle.get_height()/2.0
        cx = rx + rectangle.get_width() / 2.0 + 0.24
        cy = ry + rectangle.get_height() + 0.03
        ax[machine_idx_map[item['Machine']]].annotate(item['Job'] + ' = ' + str(item['Duration']), (cx, cy),
                                                      color='black', weight='bold', fontsize=9, ha='center',
                                                      va='center')
    fig.set_facecolor('white')
    output_dir = Path(f'outputs/{image_name}')
    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)
    output_name = output_dir.joinpath(f"{prefix}.png")
    plt.savefig(str(output_name))

