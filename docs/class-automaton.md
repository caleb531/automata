# class Automaton(metaclass=ABCMeta)

[Table of Contents](README.md)

The `Automaton` class is an abstract base class from which all automata
(including Turing machines) inherit. As such, it cannot be instantiated on its
own; you must use a defined subclass instead (or you may create your own
subclass if you're feeling adventurous). The `Automaton` class can be found
under `automata/base/automaton.py`.

If you wish to subclass `Automaton`, you can import it like so:

```python
from automata.base.automaton import Automaton
```

## Automaton Characteristics

### Automaton instances are immutable

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

### Automaton instances are validated by default

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

## Automaton Methods

The following methods are common to all Automaton subtypes, and must be
implemented if you create your own subclass:

### Automaton.read_input(self, input_str)

Reads an input string into the automaton, returning the automaton's final
configuration (according to its subtype). If the input is rejected, the method
raises a `RejectionException`.

### Automaton.read_input_stepwise(self, input_str)

Reads an input string like `read_input()`, except instead of returning the final
configuration, the method returns a generator. The values yielded by this
generator depend on the automaton's subtype.

If the string is rejected by the automaton, the method still raises a
`RejectionException`.

### Automaton.accepts_input(self, input_str)

Reads an input string like `read_input()`, except it returns a boolean instead
of returning the automaton's final configuration (or raising an exception).
That is, the method always returns `True` if the input is accepted, and it
always returns `False` if the input is rejected. Alternatively, you can use the
`in` keyword such as `word in automaton` to check whether the input is
acccepted.

```python
word in automaton
automaton.accepts_input(word)
```

### Automaton.copy(self)

Returns a deep copy of the automaton according to its subtype.

------

[Table of Contents](README.md)
