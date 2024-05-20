import json


def modify_value(config_item: dict) -> dict:
    """Service catalog configuration items need a lot of parsing. This method
    takes the dict that was return from the response of the REST call and makes
    the necessary changes based on EDN in Clojure of the service catalog API.
    See service catalog for more info:
    https://github.com/takeoff-com/service-catalog
    Args:
        config_item (dict): content to parse
    Returns:
        dict: result post parse
    """
    if config_item.get("value-type") is not None:
        if config_item["value-type"] == "string":
            value = str(config_item["value"])
            if value.startswith('"[\\n'):
                value = (
                    value.replace('\\"', '"')
                    .replace("\\n", "\n")
                    .replace('"[\n', "[\n")
                )
                value = "]".join(value.rsplit(']"', 1))
            elif value.startswith('"['):
                value = (
                    value.replace('\\"', '"')
                    .replace("\\n", "\n")
                    .replace('"[', "[")
                    .replace(']"', "]")
                )
            elif value.startswith('"\\'):
                # Covers a weird entry for RINT_SINFONIETTA__INFO__OWNER
                value = value.replace('"', '"').replace("\\\\\\", "\\")
                print(value)
                value = value.replace('\\"', "")
            elif '""' in value:
                value = value.replace('""', '"')
            else:
                value = value.replace('"', "").replace("\\\\n", "\\n")
            config_item["value"] = value

        if config_item["value-type"] == "numeric":
            if "." in str(config_item["value"]):
                config_item["value"] = float(config_item["value"])
            else:
                config_item["value"] = int(config_item["value"])
        if config_item["value-type"] == "integer":
            config_item["value"] = int(config_item["value"])
        if config_item["value-type"] == "boolean":
            if str(config_item["value"]) == "false":
                config_item["value"] = False
            else:
                config_item["value"] = True
        if config_item["value-type"] == "set":
            value = (
                str(config_item["value"])
                .replace("#{", "")
                .replace("}", "")
                .replace('"', "")
            )
            if len(value) == 0:
                config_item["value"] = []
            else:
                config_item["value"] = value.split(" ")
        if config_item["value-type"] == "map":
            value = str(config_item["value"]).replace('" ', '": ')
            # value = value.replace('\\"', '"')
            # # sets can be inside maps
            # while '{"set":' in value:
            #     value = value.replace('"{', "{", 1)
            #     value = "}".join(value.rsplit('}"', 1))
            #     first_index = value.index('{"set":')
            #     temp_value = value[first_index:]
            #     temp_value = temp_value.replace('{"set":', "", 1).replace("}", "", 1)
            #     value = value[0:first_index] + temp_value
            config_item["value"] = json.loads(value)
        if config_item["value-type"] == "array":
            value = str(config_item["value"]).replace(" ", ", ")
            config_item["value"] = json.loads(value)

    return config_item
