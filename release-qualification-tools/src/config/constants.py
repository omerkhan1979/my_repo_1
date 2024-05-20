import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# if you need more command line arguments, you can insert their indicies here,
# and increase CUSTOM_PRODUCTS_ARG_INDEX (because all that goes after it are
# user-supplied tom-ids - see scripts/orderflow.py)
# OR, if your new arguments will be used NOT IN orderflow.py or inbound_flow.py,
# you can use same index as CUSTOM_PRODUCTS_ARG_INDEX
CUSTOM_PRODUCTS_ARG_INDEX = 4

DEFAULT_USER_PASSWORD = "1234567"

RETAILERS_WITH_ISPS = ("maf", "abs", "smu")
RETAILERS_WITHOUT_MANUAL_ZONE = ("wings", "tienda")
MANUALLY_ENQUEUE_RETAILERS = "winter"
RETAILERS_WITHOUT_STAGING = "wings"
RETAILERS_WITH_NO_SPOKES_IN_SYSTEM = ("wings", "maf")
RETAILERS_WITH_PO_UPLOAD_TO_BUCKET = ("maf", "wings")
RETAILERS_WITH_TRUCK_LOAD = ("winter", "smu")
FLO_SLEEPING_AREAS = ("E", "G", "M", "N", "P", "U", "Z")
REG_SLEEPING_AREAS = ("A", "B", "C", "K")
MANUAL_SLEEPING_AREAS = ("A", "B", "C")
ALL_SLEEPING_AREAS = FLO_SLEEPING_AREAS + REG_SLEEPING_AREAS
DEFAULT_STAGING_LOCATION = "1111H010011A"
BARCODE_GENERATOR = "https://speedtesting.herokuapp.com/barcodeprint/"
DEFAULT_WEIGHT = "1.5"
INV_MOV_SUBSCRIPTION = {
    "dev": "dev-inventory-movements-subscription",
    "qai": "qai-inventory-movements-subscription",
    "uat": "uat-inventory-movements-subscription",
    "ode": "ode-inventory-movements-subscription",
}
CO_STATUS_HISTORY_SUBSCRIPTION = {
    "dev": "dev-customer-orders-status-history-subscription",
    "qai": "qai-customer-orders-status-history-subscription",
    "uat": "uat-customer-orders-status-history-subscription",
    "ode": "ode-customer-orders-status-history-subscription",
}
ETL_ENTITIES_SUBSCRIPTION = {
    "dev": "dev-etl-entities-subscription",
    "qai": "qai-etl-entities-subscription",
    "uat": "uat-etl-entities-subscription",
    "ode": "ode-etl-entities-subscription",
}

GCP_PROJECT_IDS = {
    "abs-qai": "tkf-abs-nonprod-52e1",
    "abs-uat": "tkf-abs-uat-dc19",
    "maf-uat": "tkf-maf-uat-63e9",
    "smu-uat": "tkf-smu-uat-3d04",
    "wings-uat": "tkf-wings-uat-f713",
    "winter-uat": "tkf-winter-uat-33ba",
    "abs-prod": "tkf-abs-prod-d5c0",
    "winter-prod": "takeoff-winter",
    "maf-prod": "takeoff-maf",
    "pinemelon-prod": "tkf-pinemelon-prod-b72d",
    "tienda-prod": "tkf-tienda-prod-88c8",
    "smu-prod": "tkf-smu-prod-f72b",
    "wings-prod": "tkf-wings-prod-d1e1",
}
FIREBASE_KEYS = {
    "abs-qai": "AIzaSyCF1RqZOX4aS0q6HSxq5-P0UkQ0UhtT2eM",
    "abs-uat": "AIzaSyAPX0S8Dl6mSnKPgWXve02R0aUQvjlL4Dk",
    "maf-uat": "AIzaSyAzImC1TmE2jE_dIH-hSeJVdACJcGrq-Is",
    "smu-uat": "AIzaSyBDz1e9J5013LXWefTnKvCzW6qTWggOXGc",
    "wings-uat": "AIzaSyBMPiGPXINS2tvtfPMZ76Xm_pVh1bDP030",
    "winter-uat": "AIzaSyAr4nNnYEj_HBi5wGgXg1S021ZGs9wMcuQ",
    "abs-prod": "AIzaSyAf4IcdgjR-tbp4EK6xq2aPuMq1b12UoiU",
    "winter-prod": "AIzaSyDMgTa8bH3BZiZjYHaa6n3dtcvbRacZRHg",
    "maf-prod": "AIzaSyCBOtdyWbAD5w2MWFL7QtN8IS_L4275bvU",
    "pinemelon-prod": "AIzaSyDFl3kyh2khYKXRmwkHCk77wgQ7iaDOA-U",
    "tienda-prod": "AIzaSyBsotgNPW-k_jJdXGvmh20VU3qtAfVuBiI",
    "smu-prod": "AIzaSyDf-RDxtIeAdqNGi961qenmSdlIKG3q0O4",
    "wings-prod": "AIzaSyAXqTdJcsNWO7K7AywJTm6Ra-LPAbch1dM",
}

VERBOSE = os.environ.get("RQ_VERBOSE", False)
BASE_DOMAIN = os.environ.get("BASE_DOMAIN", "tom.takeoff.com")
OUTBOUND_DOMAIN = "outbound.tom.takeoff.com"
# in on demand envs, the retailer may not align with the testing target/retailer configuration
ODE_RETAILER = os.environ.get("ODE_RETAILER")
# IAP needed for wave_plan
IAP_CLIENT_ID_MAP = {
    "default": os.environ.get("IAP_CLIENT_ID"),
    "uat": "262123068662-duae2kbmv8il625na8nkcsgqfmn3kt4b.apps.googleusercontent.com",
    "nonprod": "920437600644-a2vfogcmdfiquhn20i7stdqg1o90nlr8.apps.googleusercontent.com",
}
AUTH_SVC_USER_ID = os.environ.get("AUTH_ODE_USER_ID")
AUTH_SVC_SECRET = os.environ.get("AUTH_ODE_USER_SECRET")

WAITING_TIMEOUT = 60
ABS_ENCRYPTION_KEY = "ODdCRTk0N0RGRTNCQUEyMw=="
ABS_ENCRYPTION_VECTOR = "OTg3NjU0MzIxMDEyMzQ2NQ=="


RETAILERS_DEFAULT_LOCATION = {
    "pinemelon": "0001",
    "abs": "0068",
    "maf": "D02",
    "smu": "1917",
    "wings": "3435",
    "winter": "WF0001",
    "tienda": "414",
}

DEFAULT_USER = {"id": "IfD0lnsHXvfj2x2Jl1KjhC6jZiL2", "email": "it@takeoff.com"}
USER_ROLES = (
    "admin",
    "mfc-manager",
    "operator",
    "retailer",
    "scf-manager",
    "supervisor",
    "viewer",
)

POSSIBLE_ENVS = ("qai", "uat", "ode", "dev")

GOOGLE_IMPERSONATE_SERVICE_ACCOUNT = os.environ.get(
    "GOOGLE_IMPERSONATE_SERVICE_ACCOUNT",
    "sa-on-demand-builder@prj-on-demand-seed-5096.iam.gserviceaccount.com",
)
FIREBASE_PROJECT = os.environ.get(
    "FIREBASE_PROJECT",
    "prj-on-demand-fb-15c0",
)
DEFAULT_GCP_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
