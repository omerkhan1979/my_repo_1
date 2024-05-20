import os

from gtin import append_check_digit
import webbrowser


def create_barcode_page(codes):
    div_head = '<div><img src="http://bwipjs-api.metafloor.com/?bcid=code128&text='
    div_tail = '">'
    barcode_block = ""
    for code in codes:
        barcode_block += div_head + str(code) + div_tail + f"<h3>{code}</h3>"

    html_file = "<!DOCTYPE html><html><body></body></html>"
    html_file = html_file[:27] + barcode_block + html_file[27:]

    path = os.path.dirname(os.path.dirname(__file__)) + "/data/barcodes.html"

    with open(path, "w") as fp:
        fp.write(html_file)
        webbrowser.get(using=None).open_new("file:" + path)


def weighted_barcode(barcode, weight):
    # in theory, should not occur in flow scripts: weighted products with no
    # weighted barcodes are excluded, see utils/assortment.py.check_if_product_data_is_valid
    if barcode[-6:-1] != "00000":
        return barcode
    trimmed_barcode = barcode[:-6]
    weight_int = int(float(weight) * 1000)

    # if weight of the product equals less than 1, we need to add 00 as a prefix
    if len(str(weight_int)) <= 3:
        weight_in_grams = "00" + str(weight_int)
    # if weight of the product equals less than 10 we need to add 0 as a prefix
    elif len(str(weight_int)) < 5:
        weight_in_grams = "0" + str(weight_int)
    # if the weight of the product equals more than 10 we leave as it is
    else:
        weight_in_grams = str(weight_int)
    # saving final barcode with weight but without check digit
    barcode_with_weight = str(trimmed_barcode + weight_in_grams)
    # calculating and appending check digit
    final_barcode = append_check_digit(barcode_with_weight)
    return final_barcode
