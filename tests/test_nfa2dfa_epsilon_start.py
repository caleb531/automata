from automata.fa.nfa import NFA
from automata.fa.dfa import DFA

""" Test NFA->DFA when initial state has epsilon transitions """

# NFA which matches strings beginning with 'a', ending with 'a', and containing
# no consecutive 'b's
nfa = NFA(
    states={'q0', 'q1', 'q2'},
    input_symbols={'a', 'b'},
    transitions={
        'q0': {'': {'q2'}},
        'q1': {'a': {'q1'}},
        'q2': {'a': {'q1'}}
    },
    initial_state='q0',
    final_states={'q1'}
)

print("NFA: {}".format(nfa.read_input('a')))

dfa = DFA.from_nfa(nfa)  # returns an equivalent DFA
print("DFA: ")
print("Initial State: {}".format(dfa.initial_state))
print(dfa.read_input('a') )
