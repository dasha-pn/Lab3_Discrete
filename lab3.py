"""Lab3"""

from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):
    """
    Abstract base class for a finite state in the regex FSM.

    next_states : list[State]
    A list of possible next states from the current state.
    """

    def __init__(self) -> None:
        self.next_states: list[State] = []

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        Abstract method to determine whether the current character
        satisfies the transition condition for this state.
        """

        pass


class StartState(State):
    """
    Start state of the FSM.
    Always accepts any character (acts as an epsilon start).

    >>> StartState().check_self("a")
    True
    """

    def check_self(self, char: str) -> bool:
        return True


class TerminationState(State):
    """
    Termination (accepting) state of the FSM.
    Never accepts any characters; used to signal end of input.

    >>> TerminationState().check_self("a")
    False
    """

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """
    State that accepts any single character ('.').

    >>> DotState().check_self("x")
    True
    >>> DotState().check_self("7")
    True
    """

    def check_self(self, char: str) -> bool:
        return True


class AsciiState(State):
    """
    State that accepts a specific ASCII character.

    >>> a = AsciiState("a")
    >>> a.check_self("a")
    True
    >>> a.check_self("b")
    False
    """

    def __init__(self, symbol: str) -> None:
        super().__init__()
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        return curr_char == self.curr_sym


class StarState(State):
    """
    State that implements the Kleene star ('*') — zero or more repetitions.

    >>> a = AsciiState("a")
    >>> s = StarState(a)
    >>> s.check_self("a")
    True
    >>> s.check_self("b")
    False
    """

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state
        self.next_states.append(self)

    def check_self(self, char: str) -> bool:
        return self.checking_state.check_self(char)


class PlusState(State):
    """
    State that implements the plus ('+') — one or more repetitions.

    >>> a = AsciiState("a")
    >>> p = PlusState(a)
    >>> p.check_self("a")
    True
    >>> p.check_self("b")
    False
    """

    def __init__(self, checking_state: State):
        super().__init__()
        self.checking_state = checking_state
        self.next_states.append(self)

    def check_self(self, char: str) -> bool:
        return self.checking_state.check_self(char)


class RegexFSM:
    """
    Finite State Machine to evaluate simplified regular expressions.

    Supported features:
    - ASCII characters (letters, digits, symbols)
    - '.' (matches any character)
    - '*' (Kleene star: zero or more repetitions)
    - '+' (one or more repetitions)

    >>> regex = RegexFSM("a*4.+hi")
    >>> regex.check_string("aaaaa4uhi")
    True
    >>> regex.check_string("4uhi")
    True
    >>> regex.check_string("meow")
    False
    """

    def __init__(self, regex_expr: str) -> None:
        self.start_state = StartState()
        self.states: list[State] = [self.start_state]

        i = 0
        while i < len(regex_expr):
            char = regex_expr[i]

            if char.isascii() and char not in "*+.":
                new_state = AsciiState(char)
                self.states[-1].next_states.append(new_state)
                self.states.append(new_state)
                i += 1

            elif char == ".":
                new_state = DotState()
                self.states[-1].next_states.append(new_state)
                self.states.append(new_state)
                i += 1

            elif char == "*":
                base_state = self.states[-1]
                star_state = StarState(base_state)
                star_state.next_states.extend(base_state.next_states)
                base_state.next_states.extend(star_state.next_states)
                self.states[-2].next_states.append(star_state)
                self.states.append(star_state)
                i += 1

            elif char == "+":
                base_state = self.states[-1]
                plus_state = PlusState(base_state)
                plus_state.next_states.extend(base_state.next_states)
                self.states[-2].next_states.append(plus_state)
                self.states.append(plus_state)
                i += 1

            else:
                raise ValueError("Invalid character")

        termination = TerminationState()
        self.states[-1].next_states.append(termination)

    def check_string(self, input_string: str) -> bool:
        """
        Test if the given string matches the compiled regex.

        input_string : str
            The string to validate.

        Returns:
        bool
            True if the string is accepted by the FSM, False otherwise.
        """

        visited = set()

        def dfs(state: State, idx: int) -> bool:
            if (id(state), idx) in visited:
                return False
            visited.add((id(state), idx))

            if idx == len(input_string):
                return any(isinstance(s, TerminationState) for s in state.next_states)

            for next_state in state.next_states:
                if next_state.check_self(input_string[idx]):
                    if dfs(next_state, idx + 1):
                        return True
                elif dfs(next_state, idx):
                    return True
            return False

        return dfs(self.start_state, 0)

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)

    regex_pattern = "a*4.+hi"
    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  #True
    print(regex_compiled.check_string("4uhi"))        #True
    print(regex_compiled.check_string("meow"))        #False
