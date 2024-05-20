"""This file is for processing raw xunit.xml output produced by testing tools
1. For a given xml file it sorts test case failures for accurate reporting status
2. Removes invalid characters
3. By default (but optionally) drops results that were "skips"
"""

from pathlib import Path
import re
from typing import Optional
import xml.etree.ElementTree as ET

import typer
from typing_extensions import Annotated


REMOVE_COLOR_RE = re.compile(r"\x1B\[\d+(;\d+){0,2}m")


def main(
    result_xml: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=True,
            readable=True,
            resolve_path=True,
        ),
    ],
    drop_skips: Optional[bool] = True,
):
    result_text = result_xml.read_text()

    # clean out any oddities
    result_text = REMOVE_COLOR_RE.sub("", result_text)
    result_text = sorted_with_failures_last(result_text)
    if not drop_skips:
        result_xml.write_text(result_text)
    else:
        parsed_xml = ET.fromstring(result_text)
        parent_map = {c: p for p in parsed_xml.iter() for c in p}
        for element in list(parsed_xml.iter()):
            if element.tag == "skipped":
                case = parent_map[element]
                print(f"Removing: {case.attrib.items()}: {element.text}")
                suite = parent_map[case]
                suite.remove(case)  # drop it like it's hot
            result_xml.write_text(ET.tostring(parsed_xml).decode("utf-8"))


def custom_comparator(element) -> int:
    if element.findall(".//failure"):
        return 0
    else:
        return -1


def sorted_with_failures_last(xml):
    root = ET.fromstring(xml)

    for testsuite in root:
        # Sort the testcase elements
        testsuite[:] = sorted(testsuite.findall("testcase"), key=custom_comparator)

    return ET.tostring(root, encoding="unicode")


if __name__ == "__main__":
    typer.run(main)
