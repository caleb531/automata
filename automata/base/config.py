"""Global configuration for the library and its primitives"""


should_validate_automata: bool = True
# When set to True, it disables the freeze_value step
#   -> You must guarantee that your code does not modify the automata
allow_mutable_automata: bool = False
