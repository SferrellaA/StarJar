"""ITU Morse timing. The phase-one lead is the puzzle text; do not "correct" it."""

from dataclasses import dataclass

DOT = 1
DASH = 3
INTRA = 1
CHAR_GAP = 3
WORD_GAP = 7
# Longer than a word gap, so the lead and the token do not run together.
PART_PAUSE = WORD_GAP * 2
LEAD = "SID IS"

MORSE: dict[str, str] = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
}


@dataclass(frozen=True)
class Signal:
    on: bool
    units: int


@dataclass(frozen=True)
class Phrase:
    lead: str
    token: str
    pause_units: int

    @property
    def parts(self) -> tuple[str, str]:
        return (self.lead, self.token)


def phase_one_phrase(sid: str) -> Phrase:
    return Phrase(LEAD, sid, PART_PAUSE)


def encode(text: str) -> list[Signal]:
    signals: list[Signal] = []
    for word_index, word in enumerate(text.split(" ")):
        if word_index:
            signals.append(Signal(False, WORD_GAP))
        if not word:
            continue
        for char_index, char in enumerate(word):
            if char_index:
                signals.append(Signal(False, CHAR_GAP))
            pattern = MORSE[char]
            for element_index, element in enumerate(pattern):
                if element_index:
                    signals.append(Signal(False, INTRA))
                if element == ".":
                    signals.append(Signal(True, DOT))
                elif element == "-":
                    signals.append(Signal(True, DASH))
                else:
                    raise KeyError(char)
    return signals


def iter_signals(phrase: Phrase) -> list[Signal]:
    signals = encode(phrase.lead) if phrase.lead else []
    if phrase.lead and phrase.token:
        signals.append(Signal(False, phrase.pause_units))
    if phrase.token:
        signals.extend(encode(phrase.token))
    return signals
