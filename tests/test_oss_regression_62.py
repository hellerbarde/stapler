"""Regression coverage for prefix-only PDF page labels (issue #62)."""

import pytest
from PyPDF2 import PdfFileWriter
from PyPDF2.generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    NumberObject,
    createStringObject,
)

from staplelib import main


@pytest.mark.parametrize(
    "ranges, expected",
    [
        (
            [(0, {"/P": "1"}), (1, {"/P": "2"}), (2, {"/P": "3"})],
            ["1", "2", "3"],
        ),
        (
            [(0, {"/P": "i"}), (1, {"/P": "ii"}),
             (2, {"/P": "1"}), (3, {"/P": "2"})],
            ["i", "ii", "1", "2"],
        ),
        ([(0, {"/P": "Cover", "/St": 12})], ["Cover", "Cover", "Cover"]),
        ([(0, {})], ["", ""]),
        ([(0, {"/S": "/D", "/P": "A-", "/St": 9})], ["A-9", "A-10"]),
        (
            [(0, {"/S": "/D", "/St": 7}),
             (1, {"/S": "/A", "/St": 27}),
             (2, {"/S": "/a", "/St": 2}),
             (3, {"/S": "/R", "/St": 4}),
             (4, {"/S": "/r", "/St": 6})],
            ["7", "AA", "b", "IV", "vi"],
        ),
        (None, ["1", "2", "3"]),
    ],
    ids=[
        "numeric-prefixes",
        "roman-and-numeric-prefixes",
        "prefix-only-range",
        "empty-prefix",
        "decimal-prefix-and-start",
        "explicit-numbering-styles",
        "no-page-labels",
    ],
)
def test_list_logical_page_labels(tmp_path, capsys, ranges, expected):
    writer = PdfFileWriter()
    for _ in expected:
        writer.addBlankPage(72, 72)

    if ranges is not None:
        nums = ArrayObject()
        for index, values in ranges:
            label = DictionaryObject()
            for key, value in values.items():
                if key == "/S":
                    label[NameObject(key)] = NameObject(value)
                elif key == "/St":
                    label[NameObject(key)] = NumberObject(value)
                else:
                    label[NameObject(key)] = createStringObject(value)
            nums.extend([NumberObject(index), label])
        writer._root_object[NameObject("/PageLabels")] = DictionaryObject(
            {NameObject("/Nums"): nums}
        )

    path = tmp_path / "labels.pdf"
    with path.open("wb") as stream:
        writer.write(stream)

    main(["list-logical", str(path)])

    assert capsys.readouterr().out == "".join(
        "{}\t{}\n".format(label, index)
        for index, label in enumerate(expected, 1)
    )
