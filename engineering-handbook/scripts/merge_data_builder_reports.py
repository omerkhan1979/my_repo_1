import json
import re
import sys

TMP_COMPLEXITY_REPORT_PATH = "./tmp/reports/complexity.json"
TMP_STORAGES_REPORT_PATH = "./tmp/reports/storages.json"
DATA_COMPLEXITY_REPORT_PATH = "./data/data-model/complexity.json"
DATA_STORAGES_REPORT_PATH = "./data/data-model/storages.json"


def read_json(filepath):
    f = open(filepath)
    data = json.load(f)
    f.close()

    return data


def write_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, sort_keys=True, indent="  ")


def write_storages_report(data):
    for storage_type, storages in data.items():
        storages.sort(key=lambda s: s["storage"])

    write_json(DATA_STORAGES_REPORT_PATH, data)


def write_complexity_report(data):
    data.sort(key=lambda s: s["name"])
    for storage in data:
        if storage["entities"]:
            storage["entities"].sort(key=lambda s: s["name"])

    write_json(DATA_COMPLEXITY_REPORT_PATH, data)


def copy_storages_report():
    data = read_json(TMP_STORAGES_REPORT_PATH)
    write_storages_report(data)


def copy_complexity_report():
    data = read_json(TMP_COMPLEXITY_REPORT_PATH)
    write_complexity_report(data)


def match_any(matchers, value):
    return any(re.match(m, value) for m in matchers)


def merge_storages_report(storages_filters):
    existing_report = read_json(DATA_STORAGES_REPORT_PATH)
    updated_report = read_json(TMP_STORAGES_REPORT_PATH)

    merged_report = {}
    for storage_type in set().union(existing_report, updated_report):
        existing_storages = existing_report.get(storage_type, [])
        filtered_storages = [s for s in existing_storages if not match_any(storages_filters, s["storage"])]

        merged_storages = filtered_storages + updated_report.get(storage_type, [])
        merged_report[storage_type] = merged_storages

    write_storages_report(merged_report)


def merge_complexity_report(storages_filters):
    existing_report = read_json(DATA_COMPLEXITY_REPORT_PATH)
    updated_report = read_json(TMP_COMPLEXITY_REPORT_PATH)

    filtered_storages = [s for s in existing_report if not match_any(storages_filters, s["name"])]
    merged_storages = filtered_storages + updated_report

    write_complexity_report(merged_storages)


def parse_filters(filters_expr):
    return [expr.split(":")[0] for expr in filters_expr.split(",")]


if __name__ == "__main__":
    storages_filter = sys.argv[1]

    if storages_filter == "*":
        print(f"Copying reports")
        copy_storages_report()
        copy_complexity_report()
    else:
        print(f"Merging '{storages_filter}' reports")

        parsed = parse_filters(sys.argv[1])
        merge_storages_report(parsed)
        merge_complexity_report(parsed)
