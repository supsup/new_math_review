"""Write the portrait's four reflected zero paths as a Standard MIDI File."""

import json
import re
import struct
import sys
from pathlib import Path


PULSES_PER_BEAT = 480
FRAMES = 48
FRAME_PULSES = PULSES_PER_BEAT // 2
BASE_NOTES = (48, 55, 62, 69)


def read_loops():
    page = Path(__file__).resolve().parents[1] / "crew_visuals" / "spira_four_pairs.html"
    match = re.search(r'<script id="samples" type="application/json">(.*?)</script>', page.read_text(), re.S)
    return json.loads(match[1])


def separation(points, angle):
    if not points[0][0] < angle < points[-1][0]:
        return None
    index = next(i for i, point in enumerate(points) if point[0] >= angle)
    (a, xa, _), (b, xb, _) = points[index - 1:index + 1]
    right = xa + (xb - xa) * (angle - a) / (b - a)
    return round(22 * (right - 0.5))


def variable_length(value):
    groups = [value & 127]
    value >>= 7
    while value:
        groups.append(128 | (value & 127))
        value >>= 7
    return bytes(reversed(groups))


def midi_score(loops):
    name = b"Spira mirror quartet"
    events = [(0, bytes((255, 3, len(name))) + name),
              (0, b"\xff\x51\x03" + (625000).to_bytes(3, "big"))]
    for voice, (base, loop) in enumerate(zip(BASE_NOTES, loops)):
        intervals = [separation(loop, 90 * j / FRAMES) for j in range(FRAMES + 1)]
        for side, pan in ((-1, 35), (1, 93)):
            channel = 2 * voice + int(side == 1)
            events.append((0, bytes((0xC0 | channel, 0))))  # grand piano
            events.append((0, bytes((0xB0 | channel, 10, pan))))
            held = None
            for frame, distance in enumerate(intervals):
                note = None if distance is None else base + side*distance
                if held == note:
                    continue
                time = frame * FRAME_PULSES
                if held is not None:
                    events.append((time, bytes((0x80 | channel, held, 0))))
                if note is not None:
                    velocity = min(67, 45 + 2*distance)
                    events.append((time, bytes((0x90 | channel, note, velocity))))
                held = note
            assert held is None
    events.append(((FRAMES + 2) * FRAME_PULSES, b"\xff\x2f\x00"))
    events.sort(key=lambda event: event[0])

    prior = 0
    track = bytearray()
    for ticks, message in events:
        track.extend(variable_length(ticks - prior))
        track.extend(message)
        prior = ticks
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, PULSES_PER_BEAT)
    return header + b"MTrk" + struct.pack(">I", len(track)) + track


if __name__ == "__main__":
    loops = read_loops()
    assert len(loops) == len(BASE_NOTES)
    sys.stdout.buffer.write(midi_score(loops))
