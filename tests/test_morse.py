import random

from starjar.leds import FakeStrip, play
from starjar.morse import (
    CHAR_GAP,
    LEAD,
    MORSE,
    PART_PAUSE,
    WORD_GAP,
    Signal,
    encode,
    iter_signals,
    phase_one_phrase,
)
from starjar.secrets import TOKEN_ALPHABET, new_code, new_sid


def test_table_covers_the_token_alphabet():
    assert set(TOKEN_ALPHABET) <= set(MORSE)


def test_standard_timing_for_s_and_t():
    assert encode("S") == [
        Signal(True, 1),
        Signal(False, 1),
        Signal(True, 1),
        Signal(False, 1),
        Signal(True, 1),
    ]
    assert encode("T") == [Signal(True, 3)]
    sid_is = encode("SID IS")
    assert Signal(False, CHAR_GAP) in sid_is
    assert Signal(False, WORD_GAP) in sid_is


def test_phase_one_phrase_is_sid_is_then_the_token():
    token = "AB12CD34"
    phrase = phase_one_phrase(token)
    assert phrase.lead == "SID IS"
    assert phrase.lead == LEAD
    assert "SSID" not in phrase.lead
    assert phrase.parts == ("SID IS", token)
    assert phrase.parts[1] != "SID"
    assert phrase.pause_units >= WORD_GAP
    assert phrase.pause_units == PART_PAUSE
    signals = iter_signals(phrase)
    lead = encode(phrase.lead)
    assert signals[: len(lead)] == lead
    assert signals[len(lead)] == Signal(False, phrase.pause_units)
    assert signals[len(lead) + 1 :] == encode(token)


def test_generated_sid_cannot_keyerror():
    rng = random.Random(0)
    for _ in range(40):
        sid = new_sid(rng)
        code = new_code(rng, sid)
        iter_signals(phase_one_phrase(sid))
        encode(code)
        strip = FakeStrip(count=3)
        play(iter_signals(phase_one_phrase(sid)), strip, lambda _units: None)
        assert strip.frames
