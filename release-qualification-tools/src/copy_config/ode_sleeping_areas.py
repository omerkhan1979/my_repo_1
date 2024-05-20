import os
import sys
import typer


project_root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(project_root_dir)


from src.api.takeoff.distiller import Distiller
from src.api.takeoff.tsc import TSC
from src.config.config import Config
from src.config.constants import ODE_RETAILER

app = typer.Typer()


@app.command()
def apply_default_rules(location_code_tom: str):
    """Apply default sleeping area rules to an ODE"""
    token = os.environ.get("SERVICE_WORKER_TOKEN")
    if not token:
        raise RuntimeError(
            "This is only valid for running with rq-tools container in ODE context"
        )
    cfg = Config(ODE_RETAILER, "ode", location_code_tom, token)

    distiller = Distiller(cfg)
    tsc = TSC(cfg)
    location_code = tsc.get_location_code("location-code-retailer")

    rules = [
        {
            "store-id": location_code,
            "sleeping-area": "B",
            "priority": 10,
            "rule": '#and [#eq[#arg[:temperature-zone],["frozen"]], #or [#eq [#arg [:location-info :item-type], "REG"],'
            '#eq[#arg[:storage-zone], "manual"]]]',
            "update-note": "B for frozen REG or manual zone products",
        },
        {
            "store-id": location_code,
            "sleeping-area": "C",
            "priority": 20,
            "rule": '#and[#insec[#arg[:temperature-zone] ["chilled"]] #or[ #and[ #eq[#arg[:location-info :item-type] '
            '"REG"] #eq[#arg[:feature-attributes :is-hazardous], true]] #eq[#arg[:storage-zone] "manual"] '
            '#and[ #eq[#arg[:storage-zone] "osr"] #eq[#arg[:feature-attributes :is-hazardous], true ]]]]',
            "update-note": "C for chilled hazardous products or manual zone products",
        },
        {
            "store-id": location_code,
            "sleeping-area": "A",
            "priority": 30,
            "rule": '#and[ #eq [#arg[:temperature-zone] ["ambient"]] #or[ #and[#eq[#arg[:location-info :item-type] '
            '"REG"]'
            ' #eq[#arg[:feature-attributes :is-hazardous], true]]#eq[#arg[:storage-zone] "manual"] '
            '#and[ #eq[#arg[:storage-zone] "osr"] #eq[#arg[:feature-attributes :is-hazardous], true]]]]',
            "update-note": "A for ambient hazardous products",
        },
        {
            "store-id": location_code,
            "sleeping-area": "N",
            "priority": 40,
            "rule": '#or [#eq [#arg [:location-info :item-type], "FLO"], #eq[#arg[:storage-zone], "in-store"]]',
            "update-note": "N for other FLO items",
        },
        {
            "store-id": location_code,
            "sleeping-area": "E",
            "priority": 50,
            "rule": '#and[ #and[ #in[#arg [:categories-hierarchy 1 :id], ["88"]], #in[#arg [:categories-hierarchy 2 :id], '
            '["1","2","4","5","8","9","10","15","20","25","29","30","33","40","41","46","50","55","59","63","65",'
            '"66","89","90"]]], #or [#eq [#arg [:location-info :item-type], "FLO"], #eq[#arg[:storage-zone], "in-store"]]]',
            "update-note": "E for meat",
        },
        {
            "store-id": location_code,
            "sleeping-area": "Z",
            "priority": 60,
            "rule": '#and[ #and[ #in[#arg [:categories-hierarchy 1 :id], ["86"]], #in[#arg [:categories-hierarchy 2 :id],'
            ' ["1","5","8","10","15","25","30","40","45","50","55","85","90","93","96"]]], #or [#eq [#arg '
            '[:location-info :item-type], "FLO"], #eq[#arg[:storage-zone], "in-store"]]]',
            "update-note": "Z for seafood",
        },
        {
            "store-id": location_code,
            "sleeping-area": "N",
            "priority": 70,
            "rule": "#or[#eq[#arg[:location-info :mfc-stop-buy], true], #eq[#arg[:mfc-stop-buy], true]]",
            "update-note": "Added new path for mfc-stop-buy",
        },
        {
            "store-id": location_code,
            "sleeping-area": "M",
            "priority": 80,
            "rule": '#and[  #eq[#arg[:storage-zone], "in-store"], #in[#arg [:categories-hierarchy 2 :id], ["161", "162",'
            '"163", "164", "165", "166", "167", "168", "169", "170"]]]',
            "update-note": "M for bakery",
        },
        {
            "store-id": location_code,
            "sleeping-area": "P",
            "priority": 90,
            "rule": '#and[  #eq[#arg[:storage-zone], "in-store"], #in[#arg [:categories-hierarchy 2 :id], ["100", "101",'
            ' "102", "103", "104", "105", "106", "107","108", "109", "110", "111", "112", "113", "114", "115","116"]]]',
            "update-note": "P for deli",
        },
        {
            "store-id": location_code,
            "sleeping-area": "G",
            "priority": 100,
            "rule": '#and [#in[#arg [:categories-hierarchy 1 :id], ["89"]], #or [#eq [#arg [:location-info :item-type]'
            ', "FLO"], #eq[#arg[:storage-zone], "in-store"]]]',
            "update-note": "G for alcohol",
        },
        {
            "store-id": location_code,
            "sleeping-area": "Z",
            "priority": 110,
            "rule": '#and[  #eq[#arg[:storage-zone], "in-store"], #in[#arg [:categories-hierarchy 2 :id], ["151", "152"'
            ',"153", "154", "155", "156", "157", "158", "159", "160"]]]',
            "update-note": "Added new path for mfc-stop-buy",
        },
        {
            "store-id": location_code,
            "sleeping-area": "M",
            "priority": 120,
            "rule": '#and [#in[#arg [:categories-hierarchy 1 :id], ["94","95","96","97"]], #or [#eq [#arg '
            '[:location-info :item-type], "FLO"], #eq[#arg[:storage-zone], "in-store"]]]',
            "update-note": "M for bakery",
        },
        {
            "store-id": location_code,
            "sleeping-area": "P",
            "priority": 130,
            "rule": '#and[ #or [ #in[#arg [:categories-hierarchy 1 :id], ["81"]], #and[ #in[#arg '
            '[:categories-hierarchy 1 :id], ["82"]], #in[#arg [:categories-hierarchy 2 :id], '
            '["1","2","3","4","5","6","11","15","20","25","31","70","85"]]], '
            '#and[ #in[#arg [:categories-hierarchy 1 :id], ["37"]], #in[#arg [:categories-hierarchy 2 :id],'
            ' ["15"]]]], #or [#eq [#arg [:location-info :item-type], "FLO"], #eq[#arg[:storage-zone], '
            '"in-store"]]]',
            "update-note": "Added new path for mfc-stop-buy",
        },
        {
            "store-id": location_code,
            "sleeping-area": "K",
            "priority": 140,
            "rule": '#and[ #or[#insec[#arg[:temperature-zone],["chilled"]] #insec[#arg[:temperature-zone],'
            '["ambient"]]] #or[#eq[#arg[:location-info :item-type], "REG"] #eq[#arg[:storage-zone], "osr"]]'
            " #or[#eq[#arg[:feature-attributes :is-hazardous], false], #eq[#arg[:feature-attributes :is-hazardous],"
            " nil]]]",
            "update-note": "K for non-hazardous products",
        },
        {
            "store-id": location_code,
            "sleeping-area": "K",
            "priority": 150,
            "rule": "#default[true]",
            "update-note": "Default to K",
        },
    ]

    for rule in rules:
        print(distiller.upsert_rule_sleeping_area({"rule": rule}))


if __name__ == "__main__":
    app()
