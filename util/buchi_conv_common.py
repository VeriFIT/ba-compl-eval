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
def parseHOA(fd):
    """parseHOA(fd) -> dict()

Parses Hanoi Omega Automata format into a simple dictionary.
(Supports only a subset focused on state-based acceptance Buchi automata.)
"""
    aut = dict()
    aut["initial"] = []
    aut["transitions"] = []
    aut["final"] = []

    aps = dict()   # atomic propositions

    # reading header
    while True:
        line = fd.readline()
        if not line: # no body
            raise Exception("Missing body!")
        line = line.strip()
        if line == "":
            continue
        if line == "--BODY--":
            break
        match = re.match(r'^(?P<key>[^:]+):\s*(?P<value>.*)$', line)
        if not match:
            raise Exception("Invalid header format: {}".format(line))

        # input sanity checks
        if match['key'] == "acc-name":
            if (match['value'] != "Buchi"):
                raise Exception("Not Buchi acceptance: {}".format(match['value']))
        if match['key'] == "Acceptance":
            if (match['value'] != "1 Inf(0)"):
                raise Exception("Expected acceptance: \"1 Inf(0)\" Received: \"{}\"".format(match['value']))

        # start state
        if match['key'] == "Start":
            aut["initial"] = [match['value']]

        # atomic propositions
        if match['key'] == "AP":
            ap_ls = match['value'].split()
            aps_num = int(ap_ls[0])
            ap_ls = ap_ls[1:]
            cnt = 0
            for ap in ap_ls:   # mam APs to numbers
                aps[cnt] = ap.strip("\"")
                cnt += 1
            if cnt != aps_num:
                raise Exception("Invalid number of atomic propositions (does not match the declared number: {}".format(line))

    # reading body
    state = None
    while True:
        line = fd.readline()
        if not line: # end of input
            raise Exception("Unexpected end of file")
        line = line.strip()
        if line == "":
            continue
        if line == "--END--":
            break

        match = re.match(r'^State:\s*(?P<state>\d+)\s*(?P<final>.+)?$', line)
        if not match:
            if state is None:   # first state not declared
                raise Exception("Invalid beginning of the body: {}".format(line))

            trans_match = re.match(r'\[(?P<aps>[^\]].*)\]\s*(?P<dst>\d+)$', line)
            if not trans_match:
                raise Exception("Invalid transition: {}".format(line))

            dst = trans_match['dst']

            str_aps = trans_match['aps']
            ls_str_aps = str_aps.split("&")
            symb = None
            for one_ap in ls_str_aps:
                one_ap = one_ap.strip()
                ap_match = re.match(r'^(?P<neg>!)?\s*(?P<ap>\d+)$', one_ap)
                if not ap_match:
                    raise Exception("Invalid AP: {}".format(line))
                if not ap_match['neg']: # positive AP
                    if symb is not None:   # if other AP was positive
                        raise Exception("More than one positive AP: {}".format(line))

                    symb_num = int(ap_match['ap'])
                    symb = aps[symb_num]

            aut['transitions'].append((state, symb, dst))

        # continue in the transition of the current state
        else:    # if new state declared
            state = int(match['state'])
            if match['final']:
                aut['final'].append(str(state))

    return aut


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
def get_ap_alphabet_one_hot(symbols):
    """get_ap_alphabet_one_hot(symbols) -> (list(), dict())

Creates an AP alphabet (for HOA automata) in the one-hot encoding.

Returns a pair (list of APs, dict of input symbol -> output symbol)
"""
    res_dict = dict()
    res_list = list(set(symbols))

    for i in range(len(res_list)):
        symb = res_list[i]
        new_symb = "["
        for j in range(len(res_list)):
            if j != 0:
                new_symb += " & "

            if i != j:
                new_symb += "!"

            new_symb += str(j)

        new_symb += "]"
        res_dict[symb] = new_symb

    return (res_list, res_dict)


###########################################
def int_to_binary_str(num, bits):
    """int_to_binary_str(num, bits) -> string

Converts an integer into a Boolean combination of 'bits'-many atomic
propositions represented with a string.
"""
    symb_bin = [num >> i & 1 for i in range(bits-1,-1,-1)]
    res = ""
    for i in range(len(symb_bin)):
        if i != 0:
            res += " & "
        if symb_bin[i] == 0:
            res += "!"
        res += str(i)

    return res


###########################################
def get_ap_alphabet_binary_nonexhaust(symbols):
    """get_ap_alphabet_binary_nonexhaust(symbols) -> (list(), dict())

Creates an AP alphabet (for HOA automata) in the binary non-exhaustive encoding.

Returns a pair (list of APs, dict of input symbol -> output symbol)
"""
    res_dict = dict()
    symbols = list(set(symbols))

    aps = max(int.bit_length(len(symbols)-1), 1)
    for cnt in range(len(symbols)):
        symb_bin = [cnt >> i & 1 for i in range(aps-1,-1,-1)]
        new_symb = "[" + int_to_binary_str(cnt, aps) + "]"
        res_dict[symbols[cnt]] = new_symb

    res_list = ["a" + str(i) for i in range(aps)]
    return (res_list, res_dict)


###########################################
def get_ap_alphabet_binary_exhaust(symbols):
    """get_ap_alphabet_binary_exhaust(symbols) -> (list(), dict())

Creates an AP alphabet (for HOA automata) in the binary exhaustive encoding.

Returns a pair (list of APs, dict of input symbol -> output symbol)
"""
    res_dict = dict()
    symbols = list(set(symbols))

    aps = max(int.bit_length(len(symbols)-1), 1)
    for cnt in range(len(symbols)):
        symb_bin = [cnt >> i & 1 for i in range(aps-1,-1,-1)]
        new_symb = "[" + int_to_binary_str(cnt, aps) + "]"
        res_dict[symbols[cnt]] = new_symb

        # making the encoding exhaustive
        if cnt == len(symbols)-1:
            # recompute new_symb:
            tmp = int_to_binary_str(cnt, aps)
            for j in range(cnt+1,2**aps):
                tmp += " | " + int_to_binary_str(j, aps)
            new_symb = f"[{tmp}]"
            res_dict[symbols[cnt]] = new_symb

    res_list = ["a" + str(i) for i in range(aps)]
    return (res_list, res_dict)


###########################################
def aut2HOA(aut, encoding="BINARY_NONEXHAUSTIVE"):
    """aut2HOA(aut, encoding) -> string

Serializes an automaton as the Hanoi Omega Automata file format using the
selected encoding of explicit alphabet into combinations of atomic propositions.

Possible values of encoding:
    * "ONE_HOT": every symbol is an atomic proposition
    * "BINARY_NONEXHAUSTIVE": binary encoding into log2(number_of_symbols)
        atomic propositions (there might still be some unused Boolean
        combination of atomic propositions if number_of_symbols is not a power
        of 2
    * "BINARY_EXHAUSTIVE": similar to "BINARY_NONEXHAUSTIVE" but all Boolean
        combinations of atomic propositions are used (by mapping one symbol of
        the input alphabet to several combinations)
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

    symb_set = set()

    # count states and transitions
    for st in aut["initial"]:
        state_transl(st)
    for trans in aut["transitions"]:
        src, symb, tgt = trans
        state_transl(src)
        symb_set.add(symb)
        state_transl(tgt)
    for st in aut["final"]:
        state_transl(st)

    if encoding == "ONE_HOT":
        ap_list, symb_transl_dict = get_ap_alphabet_one_hot(symb_set)
    elif encoding == "BINARY_NONEXHAUSTIVE":
        ap_list, symb_transl_dict = get_ap_alphabet_binary_nonexhaust(symb_set)
    elif encoding == "BINARY_EXHAUSTIVE":
        ap_list, symb_transl_dict = get_ap_alphabet_binary_exhaust(symb_set)
    else:
        raise Exception("Invalid value of 'encoding'")

    ###########################################
    def symb_transl(symb):
        """symb_transl(symb) -> int

    Translates symbol names into numbers.
    """
        nonlocal symb_transl_dict

        if symb not in symb_transl_dict.keys():
            assert False

        return str(symb_transl_dict[symb])
    ###########################################

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
    res += "properties: explicit-labels state-acc trans-labels\n"

    # atomic propositions
    # res += "AP: {}".format(symb_cnt)
    res += "AP: {}".format(len(ap_list))
    for ap in ap_list:
        res += f" \"{ap}\""
    res += "\n"

    res += "--BODY--\n"
    for (name, num) in state_transl_dict.items():
        res += f"State: {num} \"{name}\""
        if name in aut["final"]:
            res += " { 0 }"
        res += "\n"

        for trans in aut["transitions"]:
            src, symb, tgt = trans
            if src == name:
                # res += "  ["
                # for i in range(symb_cnt):
                #     if i != 0:
                #         res += " & "
                #     if symb_transl_dict[symb] != i:
                #         res += "!"
                #     res += str(i)
                res += f"  {symb_transl_dict[symb]} {state_transl(tgt)}\n"
    res += "--END--\n"

    return res


###########################################
def aut2GFF(aut):
    """aut2GFF(aut) -> string

Serializes an automaton as the GOAL file format.
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

    res = ""
    res += "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n"
    res += "<structure label-on=\"transition\" type=\"fa\">\n"

    # get the alphabet
    alphabet = set()
    states = set()
    for trans in aut["transitions"]:
        src, symb, tgt = trans
        alphabet.add(symb)
        states.add(src)
        states.add(tgt)
    for st in aut["initial"]:
        states.add(st)
    for st in aut["final"]:
        states.add(st)

    res += "<alphabet type=\"classical\">\n"
    for symb in alphabet:
        res += "<symbol>" + symb + "</symbol>\n"
    res += "</alphabet>\n"

    res += "<stateset>\n"
    for st in states:
        res += "<state sid=\"" + state_transl(st) +  "\"></state>\n";
    res += "</stateset>\n"

    res += "<acc type=\"buchi\">\n"
    for st in aut["final"]:
        res += "<stateID>" + state_transl(st) +  "</stateID>\n"
    res += "</acc>\n"

    res += "<initialStateSet>\n"
    for st in aut["initial"]:
        res += "<stateID>" + state_transl(st) + "</stateID>\n"
    res += "</initialStateSet>\n";

    res += "<transitionset>\n"
    tid = 0
    for trans in aut["transitions"]:
        src, symb, tgt = trans
        res += "<transition tid=\"" + str(tid) + "\">\n"
        tid += 1
        res += "<from>" + state_transl(src) + "</from>\n" +\
               "<to>" + state_transl(tgt) + "</to>\n" + \
               "<read>" + symb + "</read>\n"
        res += "</transition>\n"
    res += "</transitionset>\n"

    res += "</structure>\n"

    return res
