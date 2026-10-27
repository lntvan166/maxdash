#!/usr/bin/env python3
"""Checks every file in vectors/ against an independent implementation of the Link A framing.

Usage: python3 tools/check_vectors.py
Prints one line per problem and exits 1 if there are any.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTORS = os.path.join(ROOT, "vectors")
OBSERVATIONS = os.path.join(ROOT, "docs", "protocol", "observations.md")

LABELS = {"observed", "documented — not yet observed", "assumed"}
MAGIC = b"nAl@"


def crc32_mpeg2(data, crc=0xFFFFFFFF):
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ 0x04C11DB7) if crc & 0x80000000 else (crc << 1)
            crc &= 0xFFFFFFFF
    return crc


def encode_frame(direction, command, flag, payload):
    head = MAGIC + bytes([0x01, direction, command]) + len(payload).to_bytes(4, "little") + bytes([flag])
    return head + crc32_mpeg2(head + payload).to_bytes(4, "little") + payload


def decode_frame(raw):
    """Returns (direction, command, flag, payload) or raises ValueError."""
    if raw[:4] != MAGIC or len(raw) < 16:
        raise ValueError("no magic / too short")
    n = int.from_bytes(raw[7:11], "little")
    if len(raw) != 16 + n:
        raise ValueError(f"length field {n} does not match {len(raw) - 16} payload bytes")
    if crc32_mpeg2(raw[:12] + raw[16:]) != int.from_bytes(raw[12:16], "little"):
        raise ValueError("crc mismatch")
    return raw[5], raw[6], raw[11], raw[16:]


def hx(s):
    return bytes.fromhex(s.replace(" ", ""))


def observation_dates(path):
    with open(path, encoding="utf-8") as fh:
        return {m.group(1) for m in re.finditer(r"^## (\d{4}-\d{2}-\d{2}) ", fh.read(), re.M)}


def check_crc(v):
    want = int(v["expect"]["crc32_mpeg2"], 16)
    got = crc32_mpeg2(hx(v["input"]["hex"]))
    return [] if got == want else [f"crc: got 0x{got:08X}, expected 0x{want:08X}"]


def check_frame(v):
    i = v["input"]
    got = encode_frame(i["direction"], i["command"], i["flag"], hx(i["payload_hex"]))
    want = hx(v["expect"]["frame_hex"])
    return [] if got == want else [f"frame: encoded {got.hex(' ').upper()}, expected {v['expect']['frame_hex']}"]


def check_command(v):
    try:
        _, cmd, flag, payload = decode_frame(hx(v["input"]["frame_hex"]))
    except ValueError as e:
        return [f"command: {e}"]
    e = v["expect"]
    got = (cmd, flag, payload)
    want = (e["command"], e["flag"], hx(e["payload_hex"]))
    return [] if got == want else [f"command: decoded {got}, expected {want}"]


RANK = {"observed": 2, "documented — not yet observed": 1, "assumed": 0}


def frame_labels(frames_file):
    """(command, flag, payload) -> label for every phone frame in frames.json."""
    try:
        with open(frames_file, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError):
        return {}
    return {(v["input"]["command"], v["input"]["flag"], hx(v["input"]["payload_hex"])): v["label"] for v in doc["vectors"]}


def check_handshake(v, frames=None):
    errs = []
    frames = frames or {}
    for n, step in enumerate(v["input"]["steps"]):
        if step["from"] == "bike":
            try:
                decode_frame(hx(step["frame_hex"]))
            except ValueError as e:
                errs.append(f"handshake step {n}: {e}")
        elif step["from"] == "phone":
            for m in step["must_send"]:
                if not {"command", "flag", "payload_hex"} <= set(m):
                    errs.append(f"handshake step {n}: must_send needs command, flag, payload_hex")
                    continue
                label = frames.get((m["command"], m["flag"], hx(m["payload_hex"])), "assumed")
                if RANK.get(label, 0) < RANK.get(v.get("label"), 0):
                    errs.append(f"handshake step {n}: cmd {m['command']} is {label!r} in frames.json; "
                                f"a composite vector carries its weakest label")
        else:
            errs.append(f"handshake step {n}: from must be bike or phone")
    return errs


def place_errors(p, what):
    if not isinstance(p, dict):
        return [f"{what}: must be an object"]
    if "lat" in p or "lng" in p:
        lat, lng = p.get("lat"), p.get("lng")
        if not (isinstance(lat, (int, float)) and isinstance(lng, (int, float)) and -90 <= lat <= 90 and -180 <= lng <= 180):
            return [f"{what}: lat/lng out of range"]
        return []
    return [] if isinstance(p.get("q"), str) and p["q"] else [f"{what}: needs lat+lng or a non-empty q"]


def check_share_link(v):
    if not isinstance(v["input"].get("text"), str):
        return ["share: input.text must be a string"]
    e = v["expect"]
    kind = e.get("kind")
    if kind == "coords":
        return place_errors(e, "share coords") if "lat" in e else ["share coords: needs lat and lng"]
    if kind == "query":
        return place_errors({"q": e.get("q")}, "share query")
    if kind == "directions":
        if "destination" not in e:
            return ["share directions: needs a destination"]
        errs = place_errors(e["destination"], "share directions destination")
        for n, stop in enumerate(e.get("stops", [])):
            errs += place_errors(stop, f"share directions stop {n}")
        return errs
    if kind == "redirect":
        return [] if e.get("then") else ["share redirect: needs then"]
    if kind == "none":
        return []
    return [f"share: unknown kind {kind!r}"]


CHECKS = {
    "share-links": check_share_link,
    "crc": check_crc,
    "frames": check_frame,
    "link-a-commands": check_command,
    "handshake": check_handshake,
}


def kind_of(path):
    name = os.path.basename(path)
    for kind in sorted(CHECKS, key=len, reverse=True):
        if name.startswith(kind):
            return kind
    return None


def check_file(path, kind, observations=OBSERVATIONS, frames_file=os.path.join(VECTORS, "frames.json")):
    name = os.path.basename(path)
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as e:
        return [f"{name}: cannot read: {e}"]
    if doc.get("schema") != 1 or not isinstance(doc.get("vectors"), list):
        return [f"{name}: needs schema 1 and a vectors list"]
    dates = observation_dates(observations)
    errs, ids = [], set()
    for v in doc["vectors"]:
        vid = v.get("id", "?")
        where = f"{name}#{vid}"
        if vid in ids:
            errs.append(f"{where}: duplicate id")
        ids.add(vid)
        if v.get("label") not in LABELS:
            errs.append(f"{where}: label {v.get('label')!r} is not one of {sorted(LABELS)}")
        if v.get("label") == "observed":
            m = re.fullmatch(r"observations\.md#(\d{4}-\d{2}-\d{2})", v.get("source", ""))
            if not m or m.group(1) not in dates:
                errs.append(f"{where}: observed vector needs a source anchor observations.md#<date> that exists")
        try:
            found = CHECKS[kind](v, frame_labels(frames_file)) if kind == "handshake" else CHECKS[kind](v)
            errs += [f"{where}: {e}" for e in found]
        except (KeyError, TypeError, ValueError) as e:
            errs.append(f"{where}: malformed: {e!r}")
    return errs


def check_all(folder=VECTORS, observations=OBSERVATIONS):
    errs = []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".json"):
            continue
        kind = kind_of(name)
        if kind is None:
            errs.append(f"{name}: unknown vector file (no checker for it)")
            continue
        errs += check_file(os.path.join(folder, name), kind, observations, os.path.join(folder, "frames.json"))
    return errs


if __name__ == "__main__":
    problems = check_all()
    for p in problems:
        print(p)
    sys.exit(1 if problems else 0)
