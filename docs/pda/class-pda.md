# class PDA(Automaton, metaclass=ABCMeta)

[Table of Contents](../README.md)

The `PDA` class is an abstract base class from which all pushdown automata
inherit. It can be found under `automata/pda/pda.py`.

The `PDA` class has the following abstract methods:

## PDA.show_diagram(self, input_str = None, path = None):

Constructs and returns a pygraphviz `AGraph` corresponding to this PAD. If `input_str` is
set, then shows execution of the PDA on `input_str`. If `path` is
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
