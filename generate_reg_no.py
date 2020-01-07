def last_two_dig(x):
    if x < 10: return "0" + str(x)
    return str(x)


def last_three_dig(x):
    if x < 10: return "00" + str(x)
    if x < 100: return "0" + str(x)
    return str(x)


def list_all_regs(year, cc=126, INCLUDE_LE=1,
                  branch_seats={'101': '60', '102': '60', '105': '60', '110': '60'}):
    year = str(year)
    cc = str(cc)
    #     branch_codes = list(map(str, branch_codes))

    regs = [year + bc + cc + last_three_dig(i) for bc in branch_seats
            for i in range(1, int(int(branch_seats[bc]) * 1.25))]

    if INCLUDE_LE:
        regs = regs + [str(int(year) + 1) + bc + cc + "9" + last_two_dig(i)
                       for bc in branch_seats for i in range(1, int(int(branch_seats[bc]) * .25))]
    return regs
