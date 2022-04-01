import copy


def all_sum_rec(target, current_sum, start, output, result):
    if current_sum == target:
        output.append(copy.copy(result))

    for i in range(start, target):
        temp_sum = current_sum + i
        if temp_sum <= target:
            result.append(i)
            all_sum_rec(target, temp_sum, i, output, result)
            result.pop()
        else:
            return


def get_all_sub_jobs(target, split_min):
    output = []
    result = []
    all_sum_rec(target, 0, split_min, output, result)
    return output
