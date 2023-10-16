# class PDA(Automaton, metaclass=ABCMeta)

[Table of Contents](../README.md)

The `PDA` class is an abstract base class from which all pushdown automata
inherit. It can be found under `automata/pda/pda.py`.

The `PDA` class has the following abstract methods:

## PDA.show_diagram(self, input_str = None, with_machine = True, with_stack = True, path = None):

Constructs and returns a pygraphviz `AGraph` corresponding to this PDA. If `input_str` is
set, then shows execution of the PDA on `input_str`. `with_machine` and `with_stack`
flags can be used to construct the state machine and transitions only or the stack and
its operations only. They are ignored if `input_str` is None. If `path` is
set, then an image of the diagram is written to the corresponding file. Other
customization options are available, see function signature for more
details.

```python
pda.show_diagram(path='./pda.png')
```

## Subclasses

### [DPDA (Deterministic Pushdown Automaton)](class-dpda.md)
### [NPDA (Non-Deterministic Pushdown Automaton)](class-npda.md)

------

[Table of Contents](../README.md)
