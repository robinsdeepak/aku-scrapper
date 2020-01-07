from multiprocessing import Process
import json, time, math, os, atexit

from functions import start_chrome, mailjet_mail, mailjet_sms, _processes_stat
from hparams import Params
from download_results import download_and_save_results
from result_tracker import find_sem, find_new_elements, get_result_links, \
    _updated, update_link_json, get_initial_state

# parsing arguments

params = Params().parser.parse_args()
DEBUG = params.debug


# atexit.register(lambda chrome: chrome.quit())

def _download_results(n_process, batch_size, reg_list, base_link, OUT_DIR, **kwargs):
    """
    :param n_process: number of processes for multiprocessing, default = 5
    :param batch_size: size of batch, automatically calculated.
    :param reg_list: list of regs, for results to be downloaded.
    :param kwargs: keywords arguments to be passed to Process
    :return: None
    """

    print("Download starting ...")
    processes = []
    t_start = time.time()

    for i in range(n_process):
        REGS = reg_list[i * batch_size: (i + 1) * batch_size]
        # print(f"Starting process {i}, batch_size: {len(REGS)}.")
        process = Process(target=download_and_save_results, args=(base_link, REGS, OUT_DIR),
                          kwargs=kwargs)
        processes.append(process)
        process.start()
    _processes_stat(processes)

    t_end = time.time()
    print(f"\nTime taken: {t_end - t_start}")


def download_with_multiprocessing(link_data):
    """
    :param link_data:
    :return:
    """
    print("downloading results with multiprocessing...")
    SEM = link_data['sem']
    # sem_year_map = {'sem1': '19', 'sem': '19', '3rd': '18', '4th': '18', '5th': '17', '7th': '16'}

    # need to be updated time to time, can't be generalized
    YEAR = str(19 - (int(SEM.lstrip('sem')) - 1) // 2)

    base_link = link_data['base_res_link']
    OUT_DIR = os.path.join('data', 'output', 'results', YEAR, SEM)

    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    with open('data/inputs/reg_list.json') as f:
        reg_list = json.load(f)
        bce_reg_list = [reg for reg in reg_list[YEAR] if reg[5:8] == '126']

    n_process = params.n_process
    batch_size = math.ceil(len(bce_reg_list) / n_process)
    _download_results(n_process, batch_size, bce_reg_list, base_link, OUT_DIR, dump_json=False)


if __name__ == '__main__':

    print("Starting Script...")
    result_link = "http://akuexam.net/Results/"
    init_state = get_initial_state(result_link)
    updated = False
    t_last_err_sms = time.time()

    while True:
        try:
            chrome = start_chrome()
            if DEBUG: print(time.ctime(), "----    Checking Update.")

            updated = _updated(chrome, init_state['_html'], result_link)
            if updated:
                if DEBUG: print(time.ctime(), "----    Update found.")

                # List of indexes for new elements
                new_elements_id = find_new_elements(chrome, init_state['_tr_texts'])

                link_data = get_result_links(chrome, result_link, new_elements_id)

                if link_data:
                    if DEBUG: print(time.ctime(), "----    link_data is being mailed")
                    mailjet_sms(link_data['base_res_link'])
                    mail_data = "<br>\n".join(map(lambda x: f"<strong>{x[0]}</strong>: {x[1]}",
                                                  link_data.items()))
                    mailjet_mail('Link Data', mail_data)
                    update_link_json(link_data)

                    if link_data['is_btech_result']:
                        if DEBUG: print(time.ctime(), "----    It's a B.Tech Result, Starting Download...")
                        download_with_multiprocessing(link_data)
                    else:
                        if DEBUG: print(time.ctime(), "----    Not a B.Tech result.")
                else:
                    if DEBUG: print(time.ctime(), "----    Could not extract link_data")

                # update initial states
                init_state = get_initial_state(result_link)
                if DEBUG: print(time.ctime(), "----    Initial state updated...")

            else:
                if DEBUG: print(time.ctime(), "----    Not updated.")

        except Exception as e:
            print(f"{'=' * 50}\n{time.ctime()}")
            print(e)
            print(f"{'=' * 50}\n")
            if t_last_err_sms < time.time() - 3600:
                mailjet_sms("Error occurred while running bot. Check email or console for error detail.")
            mailjet_mail('Error', time.ctime() + "\n\n" + str(e))
            t_last_err_sms = time.time()

        chrome.quit()
        time.sleep(params.delay)
