import pytest

from starjar.leds import DASH_COLOR, FakeStrip, packed, play
from starjar.morse import Signal, encode


def test_play_uses_set_pixel_color():
    strip = FakeStrip(count=2)
    play(encode("T"), strip, lambda _units: None)
    assert strip.frames == [(packed(DASH_COLOR), packed(DASH_COLOR))]


def test_missing_driver_method_raises():
    with pytest.raises(AttributeError):
        play([Signal(True, 3)], object(), lambda _units: None)
