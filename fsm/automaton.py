import io
from collections import defaultdict
from collections.abc import Iterable


class SpecialCharacter:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


EPSILON = SpecialCharacter("ε")


class DFA:
    def __init__(self, initial_state, final_states, rules):
        self.initial_state = initial_state
        self.final_states = frozenset(final_states)
        self.rules = rules

        self.transitions = defaultdict(dict)
        alphabet = set()
        states = set()
        for current_state, character, next_state in rules:
            self.transitions[current_state][character] = next_state
            alphabet.add(character)
            states.add(current_state)
            states.add(next_state)
        self.alphabet = frozenset(alphabet)
        self.states = frozenset(states)

    def next_state(self, state, ch):
        return self.transitions[state].get(ch)

    def accept(self, s):
        state = self.initial_state
        for c in s:
            state = self.next_state(state, c)
            if state is None:
                return False
        return state in self.final_states

    def to_dot(self, *args, **kwargs):
        return DotGenerator(*args, **kwargs).generate(self)


class NFA:
    def __init__(self, initial_state, final_states, rules):
        self.initial_state = initial_state
        self.final_states = final_states
        self.rules = rules

        self.transitions = defaultdict(lambda: defaultdict(set))
        alphabet = set()
        states = set()
        for current_state, character, next_state in rules:
            self.transitions[current_state][character].add(next_state)
            alphabet.add(character)
            states.add(current_state)
            states.add(next_state)
        self.alphabet = frozenset(alphabet)
        self.states = frozenset(states)

    def next_states(self, state, ch):
        return frozenset(self.transitions[state].get(ch, []))

    def accept(self, s):
        current_states = {self.initial_state}
        for c in s:
            next_states = set()
            for state in current_states:
                next_states |= self.next_states(state, c)
            if not next_states:
                return False
            current_states = next_states
        return len(current_states & self.final_states) > 0

    def to_DFA(self):
        transitions = defaultdict(dict)
        initial_state = frozenset({self.initial_state})
        states = {initial_state}
        queue = [initial_state]
        while queue:
            current_state = queue.pop()
            for c in self.alphabet:
                next_state = frozenset(
                    {y for x in current_state for y in self.next_states(x, c)}
                )
                if not next_state:
                    continue
                transitions[current_state][c] = next_state
                if next_state not in states:
                    states.add(next_state)
                    queue.append(next_state)
        final_states = {x for x in states if len(self.final_states.intersection(x)) > 0}
        rules = [
            (current_state, character, next_state)
            for current_state, edges in transitions.items()
            for character, next_state in edges.items()
        ]
        return DFA(initial_state, final_states, rules)

    def to_dot(self, *args, **kwargs):
        return DotGenerator(*args, **kwargs).generate(self)


class EpsillonNFA(NFA):
    def next_states_with_epsilon(self, state):
        states = set()
        queue = [state]
        while queue:
            state = queue.pop()
            next_states = self.transitions[state].get(EPSILON, set())
            states |= next_states
            queue.extend(next_states)
        return frozenset(states)

    def next_states(self, state, ch):
        states = self.transitions[state].get(ch, set())
        next_states = set(states)
        for x in states:
            next_states |= self.next_states_with_epsilon(x)
        return frozenset(next_states)

    def accept(self, s):
        current_states = {
            self.initial_state,
            *self.next_states_with_epsilon(self.initial_state),
        }
        for c in s:
            next_states = set()
            for state in current_states:
                next_states |= self.next_states(state, c)
            current_states = next_states
        return len(current_states & self.final_states) > 0

    def to_DFA(self):
        transitions = defaultdict(dict)
        initial_state = frozenset(
            {self.initial_state, *self.next_states_with_epsilon(self.initial_state)}
        )
        states = {initial_state}
        queue = [initial_state]
        while queue:
            current_state = queue.pop()
            for c in self.alphabet:
                if c == EPSILON:
                    continue
                next_state = self.next_states_with_epsilon(current_state)
                next_state |= {y for x in current_state for y in self.next_states(x, c)}
                if not next_state:
                    continue
                transitions[current_state][c] = frozenset(next_state)
                if next_state not in states:
                    states.add(next_state)
                    queue.append(next_state)
        final_states = {x for x in states if len(self.final_states.intersection(x)) > 0}
        rules = [
            (current_state, character, next_state)
            for current_state, edges in transitions.items()
            for character, next_state in edges.items()
        ]
        return DFA(initial_state, final_states, rules)


class DotGenerator:
    def __init__(self, indent=4):
        self.indent = indent

    def _format_state(self, state):
        if isinstance(state, str):
            return state
        if isinstance(state, Iterable):
            s = ",".join(self._format_state(x) for x in state)
            return "{%s}" % s
        return str(state)

    def format_state(self, state):
        s = self._format_state(state)
        return f'"{s}"'

    def generate(self, automata):
        format_state = self.format_state
        indent = " " * self.indent

        output = io.StringIO()
        output.write("digraph G {\n")
        output.write(indent + "rankdir=LR;\n")
        output.write(indent + 'empty [label = "" shape = plaintext];\n')
        output.write(indent + "node [shape = doublecircle]; ")
        output.write(" ".join([format_state(x) for x in automata.final_states]) + ";\n")
        output.write(indent + "node [shape = circle];\n")
        output.write(indent)
        output.write(
            f'empty -> {format_state(automata.initial_state)} [label = "start"];\n'
        )
        for current_state, character, next_state in automata.rules:
            output.write(indent)
            output.write(
                f'{format_state(current_state)} -> {format_state(next_state)} [label = "{character}"];\n'
            )
        output.write("}\n")
        return output.getvalue()
