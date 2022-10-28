
#import automata.regex.regex as re
import random
from time import perf_counter
from itertools import product

from automata.fa.dfa import DFA
from automata.fa.nfa import NFA


def get_random_string(n):
    return f"({''.join(random.choices('01', k=n))})*"

def reference_NFA():

    return NFA(
        states=set(product(range(5), range(4))),
        input_symbols={'f', 'o', 'd', 'a'},
        transitions={
            (0, 0): {'f': {(1, 0), (1, 1), (0, 1)}, 'a': {(0, 1), (1, 1)}, 'o': {(0, 1), (1, 1)}, 'd': {(0, 1), (1, 1)}, '': {(1, 1)}},
            (0, 1): {'f': {(1, 1), (1, 2), (0, 2)}, 'a': {(0, 2), (1, 2)}, 'o': {(0, 2), (1, 2)}, 'd': {(0, 2), (1, 2)}, '': {(1, 2)}},
            (0, 2): {'f': {(1, 2)}},
            (1, 0): {'o': {(1, 1), (2, 0), (2, 1)}, 'a': {(1, 1), (2, 1)}, 'f': {(1, 1), (2, 1)}, 'd': {(1, 1), (2, 1)}, '': {(2, 1)}},
            (1, 1): {'o': {(1, 2), (2, 1), (2, 2)}, 'a': {(1, 2), (2, 2)}, 'f': {(1, 2), (2, 2)}, 'd': {(1, 2), (2, 2)}, '': {(2, 2)}},
            (1, 2): {'o': {(2, 2)}},
            (2, 0): {'o': {(3, 1), (2, 1), (3, 0)}, 'a': {(3, 1), (2, 1)}, 'f': {(3, 1), (2, 1)}, 'd': {(3, 1), (2, 1)}, '': {(3, 1)}},
            (2, 1): {'o': {(3, 1), (3, 2), (2, 2)}, 'a': {(3, 2), (2, 2)}, 'f': {(3, 2), (2, 2)}, 'd': {(3, 2), (2, 2)}, '': {(3, 2)}},
            (2, 2): {'o': {(3, 2)}},
            (3, 0): {'d': {(3, 1), (4, 0), (4, 1)}, 'a': {(3, 1), (4, 1)}, 'f': {(3, 1), (4, 1)}, 'o': {(3, 1), (4, 1)}, '': {(4, 1)}},
            (3, 1): {'d': {(3, 2), (4, 1), (4, 2)}, 'a': {(3, 2), (4, 2)}, 'f': {(3, 2), (4, 2)}, 'o': {(3, 2), (4, 2)}, '': {(4, 2)}},
            (3, 2): {'d': {(4, 2)}},
            (4, 0): {'a': {(4, 1)}, 'f': {(4, 1)}, 'o': {(4, 1)}, 'd': {(4, 1)}},
            (4, 1): {'a': {(4, 2)}, 'f': {(4, 2)}, 'o': {(4, 2)}, 'd': {(4, 2)}},
        },
        initial_state=(0,0),
        final_states=set(product([4], range(3)))
    )


def speed_test():
    '''
    k = 200
    n = 100
    random_regex = '|'.join(get_random_string(n) for _ in range(k))

    equiv_dfa = DFA.from_nfa(regex_2_nfa())
    '''
    alphabet = {'f', 'o', 'd', 'a'}
    temp_dfa = DFA.levenshtein(alphabet, 'food', 2)
    temp_nfa = NFA.levenshtein(alphabet, 'food', 2)

    assert reference_NFA() == temp_nfa
    assert DFA.from_nfa(reference_NFA()) == temp_dfa


def main():
    speed_test()


if __name__ == "__main__":
    main()
