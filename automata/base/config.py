"""Global configuration for the library and its primitives"""


should_validate_automata = True
# When set to False, it disables the freezeValue step to speed up the automata creation
#   -> You must guarantee that your code does not modify the automata
ensure_frozen_values = True
