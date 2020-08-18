import re


###########################################
def parseBA(fd):
    """parseBA(fd) -> dict()

Parses Rabit's BA format into a simple dictionary.
"""
    aut = dict()
    first_line = fd.readline().strip()
    aut["initial"] = [first_line]
    aut["transitions"] = []
    aut["final"] = []

    while True:
        line = fd.readline()
        if not line:
            return aut

        line = line.strip()
        if line == "":
            continue

        match = re.match(r'^(?P<state>[^-,>]+)$', line)
        if match:
            aut["final"].append(match.group("state"))
            continue

        match = re.match(r'^(?P<symb>[^-,>]+),(?P<src>[^-,>]+)->(?P<tgt>[^-,>]+)$',
                         line)
        if match:
            symb = match.group("symb")
            src = match.group("src")
            tgt = match.group("tgt")
            aut["transitions"].append((src, symb, tgt))
            continue

        raise Exception("Invalid format: " + line)


###########################################
def aut2BA(aut):
    """aut2BA(aut) -> string

Serializes an automaton as Rabit's BA file.
"""
    res = ""
    for st in aut["initial"]:
        res += st + "\n"
    for trans in aut["transitions"]:
        src, symb, tgt = trans
        res += "{},{}->{}".format(symb, src, tgt) + "\n"
    for st in aut["final"]:
        res += st + "\n"

    return res


###########################################
def aut2HOA(aut):
    """aut2HOA(aut) -> string

Serializes an automaton as the Hanoi Omega Automata file.
"""
    state_cnt = 0
    state_transl_dict = dict()

    ###########################################
    def state_transl(state):
        """state_transl(state) -> int

    Translates state names into numbers.
    """
        nonlocal state_cnt
        nonlocal state_transl_dict

        if state not in state_transl_dict.keys():
            state_transl_dict[state] = state_cnt
            state_cnt += 1

        return str(state_transl_dict[state])
    ###########################################

    # count states
    for st in aut["initial"]:
        state_transl(st)
    for trans in aut["transitions"]:
        src, _, tgt = trans
        state_transl(src)
        state_transl(tgt)
    for st in aut["final"]:
        state_transl(st)

    res = ""
    res += "HOA: v1\n"
    res += "States: {}\n".format(state_cnt)

    res += "Start: "
    for state in aut["initial"]:
        res += state_transl(state) + " "
    res += "\n"

    # magic setting for Buchi condition
    res += "acc-name: Buchi\n"
    res += "Acceptance: 1 Inf(0)\n"

    res += "--BODY--\n"
    for (name, num) in state_transl_dict.items():
        res += "State {}:".format(num)
        if name in aut["final"]:
            res += " { 0 }"
        res += "\n"

        for trans in aut["transitions"]:
            src, symb, tgt = trans
            if src == name:
                res += "[{}] {}\n".format(symb, state_transl(tgt))
    res += "--END--\n"

    return res
