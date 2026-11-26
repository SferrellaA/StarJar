"""PWM on GPIO 18. Fake strip for tests. The real driver is imported only when opened."""

from dataclasses import dataclass, field

DOT_COLOR = (246, 209, 6)
DASH_COLOR = (1, 22, 137)
OFF = (0, 0, 0)


@dataclass
class FakeStrip:
    """Records setPixelColor/show. Same methods as PixelStrip, no GPIO."""

    count: int
    frames: list[tuple[int, ...]] = field(default_factory=list)
    _current: list[int] = field(init=False)

    def __post_init__(self) -> None:
        self._current = [0] * self.count

    def numPixels(self) -> int:
        return self.count

    def setPixelColor(self, index: int, packed: int) -> None:
        self._current[index] = packed

    def show(self) -> None:
        self.frames.append(tuple(self._current))


def pwm_kwargs(count: int, pin: int, order: str) -> dict[str, object]:
    # Channel 0 is the PWM channel on GPIO 18. Not SPI, not GPIO 10.
    strip_type = {"RGB": "WS2811_STRIP_RGB", "GRB": "WS2811_STRIP_GRB"}[order]
    return {
        "num": count,
        "pin": pin,
        "freq_hz": 800_000,
        "dma": 10,
        "invert": False,
        "brightness": 255,
        "channel": 0,
        "strip_type_name": strip_type,
    }


def open_strip(count: int, pin: int = 18, order: str = "RGB"):
    from rpi_ws281x import PixelStrip, ws

    kwargs = pwm_kwargs(count, pin, order)
    strip_type = getattr(ws, str(kwargs.pop("strip_type_name")))
    strip = PixelStrip(strip_type=strip_type, **kwargs)
    strip.begin()
    return strip


def packed(rgb: tuple[int, int, int]) -> int:
    red, green, blue = rgb
    return (red << 16) | (green << 8) | blue


def paint(strip, rgb: tuple[int, int, int]) -> None:
    color = packed(rgb)
    for index in range(strip.numPixels()):
        strip.setPixelColor(index, color)


def play(signals, strip, sleep_units) -> None:
    from starjar.morse import DOT

    for signal in signals:
        if not signal.on:
            color = OFF
        elif signal.units == DOT:
            color = DOT_COLOR
        else:
            color = DASH_COLOR
        paint(strip, color)
        strip.show()
        sleep_units(signal.units)
