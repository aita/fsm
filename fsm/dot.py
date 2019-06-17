import io
from collections.abc import Iterable


def _format_state(state):
    if isinstance(state, str):
        return state
    if isinstance(state, Iterable):
        states = sorted(_format_state(x) for x in state)
        if len(states) == 1:
            return states[0]
        s = ",".join(states)
        return "{%s}" % s
    return str(state)


def format_state(state):
    s = _format_state(state)
    return f'"{s}"'


def generate(automaton, indent=4):
    indent = " " * indent

    output = io.StringIO()
    output.write("digraph {\n")
    output.write(indent + "rankdir=LR;\n")
    output.write(indent + 'empty [label = "" shape = plaintext];\n')
    output.write(indent + "node [shape = doublecircle]; ")
    output.write(" ".join([format_state(x) for x in automaton.final_states]) + ";\n")
    output.write(indent + "node [shape = circle];\n")
    output.write(indent)
    output.write(
        f'empty -> {format_state(automaton.initial_state)} [label = "start"];\n'
    )
    for current_state, character, next_state in automaton.rules:
        output.write(indent)
        output.write(
            f'{format_state(current_state)} -> {format_state(next_state)} [label = "{character}"];\n'
        )
    output.write("}\n")
    return output.getvalue()
