# class Automaton(metaclass=ABCMeta)

[Table of Contents](index.md)

The `Automaton` class is an abstract base class from which all automata
(including Turing machines) inherit. As such, it cannot be instantiated on its
own; you must use a defined subclass instead (or you may create your own
subclass if you're feeling adventurous). The `Automaton` class can be found
under `automata/base/automaton.py`.

If you wish to subclass `Automaton`, you can import it like so:

```python
from automata.base.automaton import Automaton
```

The following methods are common to all Automaton subtypes, and must be
implemented if you create your own subclass:

## Automaton.read_input(self, input_str)

Reads an input string into the automaton, returning the automaton's final
configuration (according to its subtype). If the input is rejected, the method
raises a `RejectionException`.

## Automaton.read_input_stepwise(self, input_str)

Reads an input string like `read_input()`, except instead of returning the final
configuration, the method returns a generator. The values yielded by this
generator depend on the automaton's subtype.

If the string is rejected by the automaton, the method still raises a
`RejectionException`.

## Automaton.accepts_input(self, input_str)

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

## Automaton.copy(self)

Returns a deep copy of the automaton according to its subtype.

## Disabling automatic validation

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

------

[Table of Contents](index.md)
