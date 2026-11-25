"""Play the two halves of the certified wall curve as an original piano study."""

import json
from pathlib import Path
import re
import struct
import sys

from score_spira_loops import PULSES_PER_BEAT, variable_length


SCALE = (0, 2, 4, 7, 9)
HALVES = ((0, 60, 35), (90, 48, 93))


def read_walls():
    page = Path(__file__).resolve().parents[1] / "crew_visuals" / "mirror_mix_all_angle_walls.html"
    match = re.search(r"const records = (\[.*?\]);", page.read_text(), re.S)
    if match is None:
        raise ValueError("The wall data are missing")
    return {row["angle"]: row["wall"] for row in json.loads(match[1])}


def degree_to_midi(base, degree):
    octave, index = divmod(degree, len(SCALE))
    return base + 12*octave + SCALE[index]


def score(walls):
    label = b"Two walls"
    events = [
        (0, bytes((255, 3, len(label))) + label),
        (0, b"\xff\x51\x03" + (580_000).to_bytes(3, "big")),
    ]
    for channel, (half, base, pan) in enumerate(HALVES):
        events.append((0, bytes((0xC0 | channel, 0))))  # grand piano
        events.append((0, bytes((0xB0 | channel, 10, pan))))
        for beat, angle in enumerate(range(5, 90, 5), start=1):
            sigma = walls[half + min(angle, 90-angle)]
            # Both hands use the same mapping. The flatter wall stays near
            # its starting note, and the taller wall spans several octaves.
            degree = round(13*(sigma-1))
            note = degree_to_midi(base, degree)
            velocity = 46 + min(20, degree) + (4 if beat % 4 == 1 else 0)
            tick = beat*PULSES_PER_BEAT + (20 if channel == 0 else 0)
            length = 365 if channel == 0 else 425
            events.append((tick, bytes((0x90 | channel, note, velocity))))
            events.append((tick+length, bytes((0x80 | channel, note, 0))))

    events.append((19*PULSES_PER_BEAT, b"\xff\x2f\x00"))
    events.sort(key=lambda item: item[0])
    track = bytearray()
    elapsed = 0
    for tick, message in events:
        track.extend(variable_length(tick-elapsed))
        track.extend(message)
        elapsed = tick
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, PULSES_PER_BEAT)
    return header + b"MTrk" + struct.pack(">I", len(track)) + track


if __name__ == "__main__":
    sys.stdout.buffer.write(score(read_walls()))
