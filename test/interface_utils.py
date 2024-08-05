import logging

from consult_viewer.consult_interface import Definition
from consult_viewer.consult_interface.utils import scan_match


def test_scan_match():
    inputs = [
        (b'\xFF\xFF\xFF\xEF\x5A', Definition.init),
        (b'\xFF\xFF\xFF\xEF', Definition.init),
        (b'\xFF\xFF\xEF', Definition.init),
        (b'\xFF\xEF', Definition.init),
        (b'\xFF\x5A\x03\x5A', Definition.register_param)
    ]
    results = [
        (True, b'\x5A'),
        (False, b''),
        (True, b''),
        (True, b''),
        (True, b'\x03\x5A')
    ]

    assert (len(inputs) == len(results))
    for i in range(len(inputs)):
        print(f"PTesting scan_match with input: {inputs[i]}")
        logging.warning(f"WTesting scan_match with input: {inputs[i]}")
        assert (scan_match(inputs[i][0], inputs[i][1]) == results[i])
