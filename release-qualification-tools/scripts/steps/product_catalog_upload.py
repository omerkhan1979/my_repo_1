from time import sleep
from src.api.takeoff.distiller import Distiller, get_revision_max

from src.utils.console_printing import done, red, waiting


def input_path_to_im_file():
    path_to_im = input(
        "Please, enter absolute path to the product_catalog file. "
        "Product_Catalog should be in the format:"
        "MFC_product_catalog_YYYYMMDDHHMMSS.json\n"
        "Press ENTER when you are done\n"
    )
    return path_to_im, path_to_im.split("/")[-1]


def check_revision_max_updated(
    distiller: Distiller, revision_max_old, location_code_tom
) -> bool:
    print(waiting("Waiting when the file will be processed"))
    num_of_retries = 0
    revision_max_new = get_revision_max(distiller, location_code_tom)
    while revision_max_old == revision_max_new and num_of_retries < 10:
        resp = distiller.get_products_updates(1, location_code_tom, 10)
        revision_max_new = resp["revision-max"]
        num_of_retries += 1
        retry_after = 6 * num_of_retries
        print(
            f"The info in database still not updated. Retrying in {retry_after} seconds..."
        )
        sleep(retry_after)
    if revision_max_old != revision_max_new:
        print(done("Product_catalog successfully uploaded and processed"))
        return True
    else:
        print(
            red(
                "You'd probably uploaded the same file. "
                "Please make some changes in product_catalog, and try again. \n"
                "Ensure at least one product exists in the source Product Catalog file (RQT's data "
                "directory) where 'storeNumber' matches your ENV's 'location'.\n"
                "If the error appears again, "
                "contact the team who is in charge of the product_catalog upload and processing"
            )
        )
    return False


def check_revision_product_updated(revision_max_old, product_revision):
    if revision_max_old < product_revision:
        return True
    else:
        print(
            red(
                "You'd probably uploaded the same file. "
                "Please make some changes in product_catalog, and try again. \n"
                "Or check logs in DB "
            )
        )
