import pytest


class TestDFA:
    @pytest.fixture
    def target(self, *args, **kwargs):
        import fsm.automaton

        return fsm.automaton.DFA(
            1,
            {3},
            [
                (1, "a", 2),
                (1, "b", 1),
                (2, "a", 2),
                (2, "b", 3),
                (3, "a", 3),
                (3, "b", 3),
            ],
        )

    @pytest.mark.parametrize(
        "state,string,expected", [(1, "a", 2), (2, "a", 2), (2, "a", 2), (3, "a", 3)]
    )
    def test_next_state(self, target, state, string, expected):
        assert target.next_state(state, string) == expected

    @pytest.mark.parametrize(
        "string,expected", [("a", False), ("aa", False), ("baa", False), ("baba", True)]
    )
    def test_accept(self, target, string, expected):
        assert target.accept(string) == expected

    @pytest.mark.parametrize(
        "string,expected",
        [("abab", True), ("aa", False), ("baa", True), ("baba", True)],
    )
    def test_reversed(self, target, string, expected):
        nfa = target.reversed()
        assert nfa.accept(string) == expected

    @pytest.mark.parametrize(
        "string,expected", [("a", False), ("aa", False), ("baa", False), ("baba", True)]
    )
    def teset_minimized(self, target, string, expected):
        minimized_dfa = target.minimized()
        assert minimized_dfa.accept(string) == expected
        assert minimized_dfa.rules <= target.rules


class TestNFA:
    @pytest.fixture
    def target(self, *args, **kwargs):
        import fsm.automaton

        return fsm.automaton.NFA(
            1, {3}, [(1, "a", 1), (1, "b", 1), (1, "b", 2), (2, "a", 3), (2, "b", 3)]
        )

    @pytest.mark.parametrize(
        "state,string,expected",
        [(1, "a", {1}), (1, "b", {1, 2}), (2, "a", {3}), (2, "b", {3})],
    )
    def test_next_states(self, target, state, string, expected):
        assert target.next_states(state, string) == expected

    @pytest.mark.parametrize(
        "string,expected",
        [
            ("a", False),
            ("aa", False),
            ("ab", False),
            ("b", False),
            ("abba", True),
            ("aababbb", True),
        ],
    )
    def test_accept(self, target, string, expected):
        assert target.accept(string) == expected

    @pytest.mark.parametrize(
        "string,expected",
        [
            ("a", False),
            ("aa", False),
            ("ab", False),
            ("b", False),
            ("abba", True),
            ("aababbb", True),
        ],
    )
    def test_to_DFA(self, target, string, expected):
        dfa = target.to_DFA()
        assert dfa.accept(string) == expected


class TestEpsillonNFA:
    @pytest.fixture
    def target(self, *args, **kwargs):
        import fsm.automaton
        from fsm.automaton import EPSILON

        return fsm.automaton.EpsillonNFA(
            1,
            {3},
            [(1, "a", 1), (1, EPSILON, 2), (2, "b", 2), (2, EPSILON, 3), (3, "c", 3)],
        )

    @pytest.mark.parametrize(
        "state,string,expected", [(1, "a", {1, 2, 3}), (2, "b", {2, 3}), (3, "c", {3})]
    )
    def test_next_states(self, target, state, string, expected):
        assert target.next_states(state, string) == expected

    @pytest.mark.parametrize(
        "string,expected",
        [
            ("caaa", False),
            ("bba", False),
            ("ccccb", False),
            ("", True),
            ("aa", True),
            ("abb", True),
            ("aabbc", True),
            ("bbbbcccc", True),
            ("acc", True),
            ("aaaaccc", True),
        ],
    )
    def test_accept(self, target, string, expected):
        assert target.accept(string) == expected

    @pytest.mark.parametrize(
        "string,expected",
        [
            ("caaa", False),
            ("bba", False),
            ("ccccb", False),
            ("", True),
            ("aa", True),
            ("abb", True),
            ("aabbc", True),
            ("bbbbcccc", True),
            ("acc", True),
            ("aaaaccc", True),
        ],
    )
    def test_to_DFA(self, target, string, expected):
        dfa = target.to_DFA()
        assert dfa.accept(string) == expected
