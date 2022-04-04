import json
from itertools import combinations


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

