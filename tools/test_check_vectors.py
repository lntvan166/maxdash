import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(__file__))
import check_vectors as cv  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBS = os.path.join(ROOT, "docs", "protocol", "observations.md")


def write(doc):
    f = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump(doc, f)
    f.close()
    return f.name


def one(kind_input, expect, label="assumed", source="test", vid="v1"):
    return {"schema": 1, "vectors": [{"id": vid, "label": label, "source": source, "input": kind_input, "expect": expect}]}


class CheckVectorsTests(unittest.TestCase):
    def test_known_crc(self):
        self.assertEqual(cv.crc32_mpeg2(b""), 0xFFFFFFFF)
        self.assertEqual(cv.crc32_mpeg2(bytes.fromhex("313233343536373839")), 0x0376E6E7)

    def test_frame_roundtrip(self):
        doc = json.load(open(os.path.join(ROOT, "vectors", "frames.json")))
        v = doc["vectors"][0]
        i = v["input"]
        got = cv.encode_frame(i["direction"], i["command"], i["flag"], bytes.fromhex(i["payload_hex"]))
        self.assertEqual(got.hex(" ").upper(), v["expect"]["frame_hex"])

    def test_bad_crc_vector_rejected(self):
        p = write(one({"hex": "00"}, {"crc32_mpeg2": "0x00000000"}))
        errs = cv.check_file(p, "crc", OBS)
        self.assertTrue(any("crc" in e for e in errs), errs)

    def test_bad_label_rejected(self):
        p = write(one({"hex": ""}, {"crc32_mpeg2": "0xFFFFFFFF"}, label="from a forum"))
        errs = cv.check_file(p, "crc", OBS)
        self.assertTrue(any("label" in e for e in errs), errs)

    def test_missing_observation_anchor_rejected(self):
        p = write(one({"hex": ""}, {"crc32_mpeg2": "0xFFFFFFFF"}, label="observed", source="observations.md#1999-01-01"))
        errs = cv.check_file(p, "crc", OBS)
        self.assertTrue(any("anchor" in e for e in errs), errs)

    def test_share_link_schema(self):
        good = [
            {"kind": "coords", "lat": 10.77, "lng": 106.7},
            {"kind": "query", "q": "Ben Thanh Market"},
            {"kind": "directions", "destination": {"lat": 10.7, "lng": 106.6}, "stops": [{"q": "X"}]},
            {"kind": "redirect", "then": "follow the 302, re-parse"},
            {"kind": "none"},
        ]
        for e in good:
            p = write(one({"text": "t"}, e))
            self.assertEqual(cv.check_file(p, "share-links", OBS), [], e)
        bad = [
            {"kind": "place"},
            {"kind": "coords", "lat": 91, "lng": 106.7},
            {"kind": "query"},
            {"kind": "directions", "stops": []},
        ]
        for e in bad:
            p = write(one({"text": "t"}, e))
            self.assertNotEqual(cv.check_file(p, "share-links", OBS), [], e)

    def test_composite_vector_carries_weakest_label(self):
        frames = os.path.join(ROOT, "vectors", "frames.json")
        steps = [{"from": "phone", "must_send": [{"command": 12, "flag": 0, "payload_hex": "01 00"}]}]
        p = write(one({"steps": steps}, {}, label="observed", source="observations.md#2026-10-24"))
        errs = cv.check_file(p, "handshake", OBS, frames_file=frames)
        self.assertTrue(any("weakest" in e for e in errs), errs)

    def test_repo_vectors_pass(self):
        self.assertEqual(cv.check_all(os.path.join(ROOT, "vectors"), OBS), [])


if __name__ == "__main__":
    unittest.main()
