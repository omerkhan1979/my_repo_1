import os
import json
from bs4 import BeautifulSoup

input_file = os.environ.get("INPUT_HTML_FILE_PATH")

with open(input_file, "r", encoding="utf-8") as file:
    input_html = file.read()


def convert_to_json(input_html):
    soup = BeautifulSoup(input_html, "html.parser")
    release_divs = soup.find_all("div")
    release_notes = []

    for div in release_divs:
        release_note = {}
        release_note["date"] = div.h2.get_text()
        release_note["improvements"] = []

        improvements = div.find_all("h4", string="Improvement(s)")
        for improvement in improvements:
            improvement_text = improvement.find_next("span").get_text()
            release_note["improvements"].append(improvement_text)

        release_note["fixed_bugs"] = []

        fixed_bugs = div.find_all("h4", string="Fixed Bug(s)")
        for bug in fixed_bugs:
            bug_text = bug.find_next("span").get_text()
            release_note["fixed_bugs"].append(bug_text)

        release_notes.append(release_note)

    json_data = json.dumps(release_notes, ensure_ascii=False, indent=4)

    # Specify the output file path
    output_file_path = os.environ.get("OUTPUT_JSON_FILE_PATH")

    # Write the JSON data to the output file
    with open(output_file_path, "w") as output_file:
        output_file.write(json_data)


convert_to_json(input_html)
