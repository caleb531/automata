# Automaton Characteristics

## Automaton instances are immutable

All Automaton instances are fully immutable to protect against common pitfalls,
such as mutating an automaton to an invalid state after it's already been
validated.

This means that if you wish to make a change to an automaton instance, you must
retrieve its attributes as a dictionary (using the `input_parameters` property),
make your desired change, then pass those parameters to the relevant
constructor. For example:

```python
from automata.fa.dfa import DFA

dfa1 = DFA(
    states={'q0', 'q1', 'q2'},
    input_symbols={'0', '1'},
    transitions={
        'q0': {'0': 'q0', '1': 'q1'},
        'q1': {'0': 'q0', '1': 'q2'},
        'q2': {'0': 'q2', '1': 'q1'}
    },
    initial_state='q0',
    final_states={'q1'}
)
# If you want to make a change, you must create a new instance; please note
# that dfa1.input_parameters is always a deep copy of the input parameters for
# dfa1 (in other words, mutating dfa1.input_parameters will not actually mutate
# dfa1)
params = dfa1.input_parameters
params['final_states'] = {'q2'}
dfa2 = DFA(**params)
```

### Enabling mutable automata

Automaton immutability is enforced via a "freeze" step during object
initialization that turns mutable parameters (such as sets or dicts) into their
immutable counterparts (frozensets/frozendicts).

If your application requires maximum performance, you can disable this
conversion via the `allow_mutable_automata` global configuration option. If
enabled, the user must ensure that their automaton instances are never modified,
otherwise correct behavior cannot be guaranteed.

```python
import automata.base.config as global_config

global_config.allow_mutable_automata = True
# The rest of your code...
```

## Automaton instances are validated by default

By default, all Automaton instances are checked for common inconsistencies when
they are instantiated. If inconsistencies are found, the appropriate exception
from `automata.base.exceptions` is raised.

Because this validation can be performance-intensive for large automaton
instances with many states/transitions, you can disable the automatic validation
using the global configuration feature (introduced in v7):

```python
import automata.base.config as global_config

global_config.should_validate_automata = False

# The rest of your code...
```

If, at any point, you wish to opt into validation for a specific Automaton instance, you can call the `validate` method:

```python
my_automaton.validate()
```
