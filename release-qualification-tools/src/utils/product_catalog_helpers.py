import json
import random

from src.utils.os_helpers import give_file_body


def give_modified_product_catalog_from_template(retailer, project_root_dir):
    if retailer == "winter":
        template_path = f"{project_root_dir}/data/Takeoff_product_catalog_{retailer}"
    if retailer == "abs":
        template_path = f"{project_root_dir}/data/MFC_product_catalog_{retailer}"
    else:
        template_path = f"{project_root_dir}/data/takeoff_product_catalog_{retailer}"

    body = give_file_body(f"{template_path}.json")
    product_catalog_body = json.loads(body)[0]
    product_catalog_body = [
        customize_json_product_catalog_dimensions(product_catalog_body, retailer)
    ]
    product_catalog = json.dumps(product_catalog_body, indent="")

    return product_catalog


def customize_json_product_catalog_dimensions(body, retailer):
    if retailer == "abs":
        body["itemDimensions"]["itemWeight"] = gen_random_dimension(10.0, 30.0)
        body["itemDimensions"]["averageWeight"] = gen_random_dimension(10.0, 30.0)
        return body
    body["retail-item"]["dimensions"]["height"] = gen_random_dimension(10.0, 30.0)
    body["retail-item"]["dimensions"]["width"] = gen_random_dimension(10.0, 30.0)
    return body


def gen_random_dimension(lower, upper):
    number = round(random.uniform(lower, upper), 2)
    return str(number)


def give_modified_product_catalog_from_pc_version(
    pc_version, location_code_tom, pc_version_json_path, temp_zone="ambient"
):
    body = give_file_body(f"{pc_version_json_path}")
    product_catalog_body = json.loads(body)[0]
    product_catalog_body["tom-id"] = random.randint(2000, 8000)
    product_catalog_body["ecom-ids"][0] = str(random.randint(2000, 8000))
    product_catalog_body["barcodes"][0] = str(random.randint(2000, 8000))
    product_catalog_body["temperature-zone"][0] = temp_zone
    product_catalog_body["retail-item"]["dimensions"]["height"] = gen_random_dimension(
        10.0, 30.0
    )
    product_catalog_body["retail-item"]["dimensions"]["width"] = gen_random_dimension(
        10.0, 30.0
    )
    if pc_version == "v5custom":
        product_catalog_body["location-info"][0] = str(
            product_catalog_body["location-info"][0]
        ).replace("9999", location_code_tom)
    else:
        product_catalog_body["mfc-id"] = product_catalog_body["mfc-id"].replace(
            "9999", location_code_tom
        )

    return product_catalog_body
