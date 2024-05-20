"""
Class to interact with Distiller API.
Swaggger: https://distiller-qai.abs.takeofftech.io
Confluence (documentation might be outdated or incomplete, you might need to consult relevant team):
https://takeofftech.atlassian.net/wiki/spaces/AIM/pages/1608057624/Distiller
"""

from typing import Literal, Optional, cast, Any
import requests

from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, config

from src.api.takeoff.base_api_takeoff import BaseApiTakeoff
from src.utils.http import handle_response
from src.utils.config import get_url_builder

kebabConfig = config(letter_case=LetterCase.KEBAB)


# WARNING: I have no clue why it is valuable to get a distiller PO, it should
# probably be removed from the ecosystem!
@dataclass
class DistillerPOResponse(DataClassJsonMixin):
    data: list[dict[str, Any]]


@dataclass
class RetailItemWeight(DataClassJsonMixin):
    unit_of_measure: Literal["lb", "LB", "kg", "KG"] = field(metadata=kebabConfig)
    weight: float = field(metadata=kebabConfig)


@dataclass
class RetailItemDimensions(DataClassJsonMixin):
    unit_of_measure: Literal["CM", "cm", "IN", "in"] = field(metadata=kebabConfig)
    width: float = field(metadata=kebabConfig)
    height: float = field(metadata=kebabConfig)
    length: float = field(metadata=kebabConfig)


@dataclass
class RetailItem(DataClassJsonMixin):
    weight: RetailItemWeight = field(metadata=kebabConfig)
    dimensions: RetailItemDimensions = field(metadata=kebabConfig)


@dataclass
class FeatureAttributes(DataClassJsonMixin):
    is_bulk: Optional[bool] = field(metadata=kebabConfig, default=None)
    is_crushable: Optional[bool] = field(metadata=kebabConfig, default=None)
    is_raw: Optional[bool] = field(metadata=kebabConfig, default=None)
    is_specific_chilled: Optional[bool] = field(metadata=kebabConfig, default=None)
    is_heavy: Optional[bool] = field(metadata=kebabConfig, default=None)
    is_vertical: Optional[bool] = field(metadata=kebabConfig, default=None)
    is_chemical: Optional[bool] = field(metadata=kebabConfig, default=None)
    is_requires_plastic_bag: Optional[bool] = field(metadata=kebabConfig, default=None)
    is_stackable: Optional[bool] = field(metadata=kebabConfig, default=None)
    is_egg: Optional[bool] = field(metadata=kebabConfig, default=None)
    is_case_storage: Optional[bool] = field(metadata=kebabConfig, default=None)
    is_glass_packaged: Optional[bool] = field(metadata=kebabConfig, default=None)
    food_safety: Optional[str] = field(metadata=kebabConfig, default=None)
    is_hazardous: Optional[bool] = field(metadata=kebabConfig, default=None)


# WARNING: This is likely incomplete, I just pulled in the attributes needed by
# current tests. Would be great if it verified json schema :)


@dataclass
class DistillerProductV6(DataClassJsonMixin):
    requires_expiration_date: bool = field(metadata=kebabConfig)
    ecom_ids: list[str] = field(metadata=kebabConfig)
    name: str = field(metadata=kebabConfig)
    temperature_zone: list[str] = field(metadata=kebabConfig)
    tom_id: str = field(metadata=kebabConfig)
    mfc_stop_fulfill: bool = field(metadata=kebabConfig)
    barcodes: list[str] = field(metadata=kebabConfig)
    retail_item: RetailItem = field(metadata=kebabConfig)
    is_weight_variable_on_receipt: Optional[bool] = field(
        metadata=kebabConfig, default=None
    )
    is_weight_variable_on_po: Optional[bool] = field(metadata=kebabConfig, default=None)
    feature_attributes: FeatureAttributes = field(
        metadata=kebabConfig, default_factory=FeatureAttributes()
    )
    sleeping_area: Optional[str] = field(metadata=kebabConfig, default=None)


@dataclass
class DistilerGetProductsResponse(DataClassJsonMixin):
    data: list[DistillerProductV6]


@dataclass
class DistillerGetProductIDsResponse(DataClassJsonMixin):
    data: list[str]


@dataclass
class DistillerSleepingAreaUpsertRuleResponse(DataClassJsonMixin):
    data: list[dict[str, Any]]


class Distiller(BaseApiTakeoff):
    url_builder = get_url_builder("api/", "distiller")

    get_products_sleeping_area_endpoint = (
        "v4/qa/get-products-by-location-code-tom-and-sleeping-area"
    )
    get_ecom_mapping_endpoint = "v6/mapping/get-ecom-mapping"
    get_purchase_order_by_id_endpoint = "v5/entities/get-purchase-order-by-id"
    get_purchase_orders_endpoint = "v5/entities/get-purchase-orders"
    get_products_by_tom_ids_endpoint = "v1/products/get-products-by-tom-ids"
    get_products_updates_endpoint = "v1/pickerman/get-products-updates"
    get_product_ids_endpoint = "v5/entities/get-product-ids"
    get_rules_sleeping_area_endpoint = "v1/rules/sleeping-area/get-rules"
    upsert_rule_sleeping_area_endpoint = "v1/rules/sleeping-area/upsert-rule"
    delete_rule = "v1/rules/sleeping-area/deleteRule"

    def get_products_for_sleeping_area(
        self,
        sleeping_area: tuple[str, ...],
        is_weighted: bool,
        temp_zone: Optional[list] = None,
    ) -> list[DistillerProductV6]:
        """
        QA endpoint that returns max 100 product entities for given sleeping areas and
        'is-weight-variable-on-receipt' parameter'
        Original endpoint accepts array of sleeping areas, but this function accepts a single area,
        to make you call it multiple times if you need products from multiple areas.
        Since limit is 100, and out of returned 100 there might be many autogenerated products
        with invalid data, calling endpoint each time for required area increases chances
        to find enough valid products
        """
        url = self.url_builder(rel=self.get_products_sleeping_area_endpoint)

        body = {
            "sleeping-area": sleeping_area,
            "location-code-tom": self.config.location_code_tom,
            "is-weight-variable-on-receipt": is_weighted,
            "limit": 100,
        }

        if temp_zone:
            body["temperature-zone"] = temp_zone

        response = requests.post(
            url=url,
            json=body,
            headers=self.default_headers,
        )

        return DistilerGetProductsResponse.from_json(
            cast(str, handle_response(response, 200, 201, json=False))
        ).data

    def get_ecom_id_mapping(self, ecom_ids, location_code_retailer):
        url = self.url_builder(rel=self.get_ecom_mapping_endpoint)

        body = {"ecom-ids": ecom_ids, "location-code-retailer": location_code_retailer}

        response = requests.post(
            url=url,
            json=body,
            headers=self.default_headers,
        )
        return handle_response(response, 200, 201)

    def get_products_by_tom_ids(self, products: list) -> list[DistillerProductV6]:
        url = self.url_builder(rel=self.get_products_by_tom_ids_endpoint)
        body = {
            "takeoff-item-ids": products,
            "location-code-tom": self.config.location_code_tom,
        }
        response = requests.post(url=url, json=body, headers=self.default_headers)
        return DistilerGetProductsResponse.from_json(
            cast(str, handle_response(response, 200, 201, json=False))
        ).data

    def get_purchase_order_by_id(self, purchase_order: str) -> DistillerPOResponse:
        url = self.url_builder(rel=self.get_purchase_order_by_id_endpoint)

        body = {"purchase-order-id": purchase_order}

        response = requests.post(
            url=url,
            json=body,
            headers=self.default_headers,
        )
        return DistillerPOResponse.from_json(
            cast(str, handle_response(response, 200, 201, json=False))
        )

    def get_products_updates(self, revision_from, mfc, limit) -> dict:
        url = self.url_builder(rel=self.get_products_updates_endpoint)

        body = {
            "revision-from": revision_from,
            "location-code-tom": mfc,
            "limit": limit,
        }
        response = requests.post(url=url, json=body, headers=self.default_headers)
        return handle_response(response, 200, 201)

    def get_product_ids(self, location_code_retailer: str) -> list[str]:
        """Returns ALL product ids available at the location"""
        url = self.url_builder(rel=self.get_product_ids_endpoint)

        response = requests.post(
            url=url,
            headers=self.default_headers,
            json={"store-id": location_code_retailer},
        )

        return DistillerGetProductIDsResponse.from_json(
            cast(str, handle_response(response, 200, 201, json=False))
        ).data

    def get_rules_sleeping_area(self, store_id: str) -> dict:
        url = self.url_builder(rel=self.get_rules_sleeping_area_endpoint)

        body = {"store-id": store_id}

        response = requests.post(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200, 201)

    def upsert_rule_sleeping_area(
        self,
        body: dict,
    ) -> DistillerSleepingAreaUpsertRuleResponse:
        url = self.url_builder(rel=self.upsert_rule_sleeping_area_endpoint)

        response = requests.post(url=url, headers=self.default_headers, json=body)

        return DistillerSleepingAreaUpsertRuleResponse(handle_response(response, 200))

    def delete_sleeping_area(
        self,
        body: dict,
    ):
        url = self.url_builder(rel=self.delete_rule)
        response = requests.post(url=url, headers=self.default_headers, json=body)
        return handle_response(response, 200)

    def get_purchase_orders(self) -> dict:
        url = self.url_builder(rel=self.get_purchase_orders_endpoint)

        body = {"revision-from": 54, "limit": 100}
        response = requests.post(url=url, json=body, headers=self.default_headers)
        return handle_response(response, 200, 201)


def get_revision_max(distiller: Distiller, location_code_tom: str) -> int:
    response = distiller.get_products_updates(0, location_code_tom, 10)
    return response["revision-max"]


def get_product_revision(
    distiller: Distiller, revision_max_old: int, location_code_tom: str
) -> int:
    response = distiller.get_products_updates(revision_max_old, location_code_tom, 10)
    return response["data"][0]["revision"]
