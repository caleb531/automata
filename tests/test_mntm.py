#!/usr/bin/env python3
"""Classes and functions for testing the behavior of MNTMs."""
from automata.tm.mntm import MNTM
import random
import matplotlib.pyplot as plt

tm = MNTM(
    states={"q0", "q1"},
    input_symbols={"0", "1"},
    tape_symbols={"0", "1", "#"},
    n_tapes=3,
    transitions={
        "q0": {
            ("1", "#"): [("q0", (("1", "R"), ("1", "R")))],
            ("0", "#"): [("q0", (("0", "R"), ("#", "N")))],
            ("#", "#"): [("q1", (("#", "N"), ("#", "N")))],
        }
    },
    initial_state="q0",
    blank_symbol="#",
    final_states={"q1"},
)

lengths = [i for i in range(10)]
accepted_ntm = []
rejected_ntm = []
accepted_mntm = []
rejected_mntm = []
x_accepted = []
x_rejected = []
for length in lengths:
    input_str = ""
    for _ in range(length):
        k = random.randint(0, 1)  # decide on a k each time the loop runs
        input_str += str(int(k))

    print(input_str)
    accepts = tm.accepts(input_str)
    steps_as_ntm = tm.steps_as_ntm
    tm.simulate_as_ntm(input_str)
    steps_as_mntm = tm.steps_as_mntm
    print(steps_as_ntm)
    print(steps_as_mntm)

    if accepts:
        x_accepted.append(length)
        accepted_ntm.append(steps_as_ntm)
        accepted_mntm.append(steps_as_mntm)
    else:
        x_rejected.append(length)
        rejected_ntm.append(steps_as_ntm)
        rejected_mntm.append(steps_as_mntm)

plt.figure()
plt.scatter(x_accepted, accepted_ntm, color="b", label="Single-tape")
plt.scatter(x_accepted, accepted_mntm, color="b", label="Multi-tape")
plt.scatter(x_rejected, rejected_ntm, color="r", label=None)
plt.scatter(x_rejected, rejected_mntm, color="r", label=None)
plt.show()
plt.close()

tm = MNTM(
    states=set(["q" + str(i) for i in range(-1, 27)] + ["qc", "qf", "qr"]),
    input_symbols={"0"},
    tape_symbols={"0", "X", "Y", "S", "#"},
    n_tapes=3,
    transitions={
        "q-1": {("#", "#", "#"): [("q0", (("#", "R"), ("#", "N"), ("#", "N")))],},
        "q0": {("0", "#", "#"): [("q1", (("0", "N"), ("#", "R"), ("#", "R")))]},
        "q1": {("0", "#", "#"): [("q2", (("0", "N"), ("0", "R"), ("#", "N")))]},
        "q2": {("0", "#", "#"): [("qc", (("0", "N"), ("#", "L"), ("X", "R")))],},
        "qc": {
            ("0", "0", "#"): [
                ("qc", (("0", "R"), ("0", "R"), ("#", "N")))
            ],  # Testing whether tape 1 and 2 have the same length
            ("0", "#", "#"): [
                ("q3", (("0", "N"), ("#", "N"), ("#", "N")))
            ],  # length of tape 1 is greater than the length of tape 2 (continues)
            ("#", "#", "#"): [
                ("qf", (("#", "N"), ("#", "N"), ("#", "N")))
            ],  # tape 1 and 2 were found to be of equal length (accepts)
            ("#", "0", "#"): [
                ("qr", (("#", "N"), ("0", "N"), ("#", "N")))
            ],  # length of tape 2 is greater than the length of tape 1 (rejects)
        },
        "q3": {("0", "#", "#"): [("q4", (("0", "N"), ("#", "N"), ("#", "L")))],},
        "q4": {
            ("0", "#", "X"): [("q5", (("0", "N"), ("#", "N"), ("X", "R")))],
            ("0", "#", "Y"): [("q13", (("0", "N"), ("#", "N"), ("Y", "R")))],
        },
        "q5": {
            ("0", "#", "Y"): [("q5", (("0", "N"), ("#", "N"), ("Y", "L")))],
            ("0", "#", "#"): [("q6", (("0", "N"), ("#", "N"), ("Y", "L")))],
        },
        "q6": {
            ("0", "#", "X"): [("q6", (("0", "N"), ("#", "N"), ("X", "L")))],
            ("0", "#", "Y"): [("q7", (("0", "N"), ("#", "N"), ("Y", "R")))],
            ("0", "#", "S"): [("q7", (("0", "N"), ("#", "N"), ("S", "R")))],
            ("0", "#", "#"): [
                ("q24", (("0", "N"), ("#", "N"), ("#", "R")))
            ],  # Caso especial cuando cinta 3 = #X
        },
        "q7": {("0", "#", "X"): [("q9", (("0", "N"), ("#", "N"), ("S", "R")))]},
        "q9": {
            ("0", "#", "X"): [("q9", (("0", "N"), ("#", "N"), ("X", "R")))],
            ("0", "#", "Y"): [("q9", (("0", "N"), ("#", "N"), ("Y", "R")))],
            ("0", "#", "#"): [("q10", (("0", "N"), ("#", "N"), ("Y", "L")))],
        },
        "q10": {
            ("0", "#", "Y"): [("q10", (("0", "N"), ("#", "N"), ("Y", "L")))],
            ("0", "#", "X"): [("q6", (("0", "N"), ("#", "N"), ("X", "L")))],
            ("0", "#", "S"): [("q11", (("0", "N"), ("#", "N"), ("X", "L")))],
        },
        "q11": {
            ("0", "#", "S"): [("q11", (("0", "N"), ("#", "N"), ("X", "L")))],
            ("0", "#", "Y"): [("q11", (("0", "N"), ("#", "N"), ("Y", "R")))],
            ("0", "#", "X"): [("q11", (("0", "N"), ("#", "N"), ("X", "R")))],
            ("0", "#", "#"): [("q12", (("0", "N"), ("#", "N"), ("Y", "L")))],
        },
        "q12": {
            ("0", "#", "X"): [("q20", (("0", "N"), ("#", "N"), ("X", "L")))],
            ("0", "#", "Y"): [("q21", (("0", "N"), ("#", "N"), ("Y", "L")))],
        },
        "q13": {
            ("0", "#", "X"): [("q13", (("0", "N"), ("#", "N"), ("X", "L")))],
            ("0", "#", "#"): [("q14", (("0", "N"), ("#", "N"), ("X", "L")))],
        },
        "q14": {
            ("0", "#", "Y"): [("q14", (("0", "N"), ("#", "N"), ("Y", "L")))],
            ("0", "#", "X"): [("q15", (("0", "N"), ("#", "N"), ("X", "R")))],
            ("0", "#", "S"): [("q15", (("0", "N"), ("#", "N"), ("S", "R")))],
        },
        "q15": {("0", "#", "Y"): [("q17", (("0", "N"), ("#", "N"), ("S", "R")))]},
        "q17": {
            ("0", "#", "Y"): [("q17", (("0", "N"), ("#", "N"), ("Y", "R")))],
            ("0", "#", "X"): [("q17", (("0", "N"), ("#", "N"), ("X", "R")))],
            ("0", "#", "#"): [("q18", (("0", "N"), ("#", "N"), ("X", "L")))],
        },
        "q18": {
            ("0", "#", "X"): [("q18", (("0", "N"), ("#", "N"), ("X", "L")))],
            ("0", "#", "Y"): [("q14", (("0", "N"), ("#", "N"), ("Y", "L")))],
            ("0", "#", "S"): [("q19", (("0", "N"), ("#", "N"), ("Y", "L")))],
        },
        "q19": {
            ("0", "#", "S"): [("q19", (("0", "N"), ("#", "N"), ("Y", "L")))],
            ("0", "#", "X"): [("q19", (("0", "N"), ("#", "N"), ("X", "R")))],
            ("0", "#", "Y"): [("q19", (("0", "N"), ("#", "N"), ("Y", "R")))],
            ("0", "#", "#"): [("q12", (("0", "N"), ("#", "N"), ("X", "L")))],
        },
        "q20": {
            ("0", "#", "X"): [("q20", (("0", "N"), ("#", "N"), ("X", "L")))],
            ("0", "#", "Y"): [("q22", (("0", "N"), ("#", "N"), ("Y", "R")))],
        },
        "q21": {
            ("0", "#", "Y"): [("q21", (("0", "N"), ("#", "N"), ("Y", "L")))],
            ("0", "#", "X"): [("q22", (("0", "N"), ("#", "N"), ("X", "R")))],
        },
        "q22": {
            ("0", "#", "X"): [("q22", (("0", "N"), ("0", "R"), ("X", "R")))],
            ("0", "#", "Y"): [("q22", (("0", "N"), ("0", "R"), ("Y", "R")))],
            ("0", "#", "#"): [("q23", (("0", "N"), ("#", "N"), ("#", "N")))],
        },
        "q23": {
            ("0", "#", "#"): [("q23", (("0", "L"), ("#", "N"), ("#", "N")))],
            ("#", "#", "#"): [("q26", (("#", "R"), ("#", "L"), ("#", "N")))],
        },
        "q26": {
            ("0", "0", "#"): [("q26", (("0", "N"), ("0", "L"), ("#", "N")))],
            ("0", "#", "#"): [("qc", (("0", "N"), ("#", "R"), ("#", "N")))],
        },
        # Caso especial cuando cinta 3 = #X
        "q24": {
            ("0", "#", "Y"): [("q24", (("0", "N"), ("#", "N"), ("Y", "R")))],
            ("0", "#", "X"): [("q24", (("0", "N"), ("#", "N"), ("X", "R")))],
            ("0", "#", "#"): [("q25", (("0", "N"), ("#", "N"), ("Y", "R")))],
        },
        "q25": {("0", "#", "#"): [("q12", (("0", "N"), ("#", "N"), ("Y", "L")))]},
    },
    initial_state="q-1",
    blank_symbol="#",
    final_states={"qf"},
)

# for conf in tm.read_input_stepwise("#0"):
#     print(conf)

# for conf in tm.simulate_as_ntm("#0"):
#     print(conf)
