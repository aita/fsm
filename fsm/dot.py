import io
from collections.abc import Iterable

from graphviz import Digraph


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
    return f"{s}"


def generate(automaton):
    dot = Digraph()
    dot.attr(rankdir="LR")
    empty_node = "empty"
    while empty_node in automaton.states:
        empty_node = "_" + empty_node
    dot.node(empty_node, label="", shape="plaintext")
    dot.attr("node", shape="doublecircle")
    for x in automaton.final_states:
        dot.node(format_state(x))
    dot.attr("node", shape="circle")
    dot.edge("empty", format_state(automaton.initial_state), label="start")
    for current_state, character, next_state in automaton.rules:
        dot.edge(
            format_state(current_state), format_state(next_state), label=str(character)
        )
    return dot
