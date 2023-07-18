# class FA(Automaton, metaclass=ABCMeta)

[Table of Contents](../README.md)

The `FA` class is an abstract base class from which all finite automata inherit.
The `FA` class can be found under `automata/fa/fa.py`. Every subclass of FA
can be rendered natively inside of a Jupyter notebook (automatically calling
`show_diagram` without any arguments) if installed with the `visual` optional
dependency.

If you wish to subclass `FA`, you can import it like so:

```python
from automata.fa.fa import FA
```

The `FA` class has the following abstract methods:

## FA.iter_transitions(self):

Returns a generator of all of the transitions in the FA, where each
transition is specified by a tuple of the form `(from_state, to_state, symbol)`.

The `FA` class has the following method:

## FA.show_diagram(self, input_str = None, path = None):

Constructs and returns a pygraphviz `AGraph` corresponding to this FA. If `input_str` is
set, then shows execution of the FA on `input_str`. If `path` is
set, then an image of the diagram is written to the corresponding file. Other
customization options are available, see function signature for more
details.

```python
fa.show_diagram(path='./fa1.png')
```

## Subclasses

### [DFA (Deterministic Finite Automaton)](class-dfa.md)
### [NFA (Non-Deterministic Finite Automaton)](class-nfa.md)
### [GNFA (Generalized Non-Deterministic Finite Automaton)](class-gnfa.md)

------

[Table of Contents](../README.md)
