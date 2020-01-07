from multiprocessing import current_process, Process, freeze_support
import time
import math

from vars import bce_reg_list, base_link, OUT_DIR, OUT_DIR_PD
from download_results import download_and_save_results
from extract_phone_email import extract_and_save_data
from functions import _processes_stat

n_process = max(10, int(len(bce_reg_list) / 60))
processes = []
batch_size = math.ceil(len(bce_reg_list) / n_process)
t_start = time.time()


# freeze_support()

def _download_results():
    for i in range(n_process):
        REGS = bce_reg_list[i * batch_size: (i + 1) * batch_size]
        # print(f"Starting process {i}, batch_size: {len(REGS)}.")
        process = Process(target=download_and_save_results, args=(base_link, REGS, OUT_DIR),
                          kwargs=({"dump_json": True}))
        processes.append(process)
        process.start()

    _processes_stat(processes)

    t_end = time.time()
    print(f"\nTime taken: {t_end - t_start}")

    # download_and_save_results(base_link, bce_reg_list, OUT_DIR)


def _extract_phone_emails():
    for i in range(n_process):
        REGS = bce_reg_list[i * batch_size: (i + 1) * batch_size]
        process = Process(target=extract_and_save_data, args=(REGS, OUT_DIR_PD))
        processes.append(process)
        process.start()

    _processes_stat(processes)
    t_end = time.time()
    print(f"\nTime taken: {t_end - t_start}")


if __name__ == '__main__':
    _download_results()
    # _extract_phone_emails()
