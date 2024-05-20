import json
import sys
import warnings
import subprocess

from firebase_admin import firestore
from google.cloud import pubsub_v1
from google.api_core import retry
from google.cloud import storage
from google.auth import exceptions, default, impersonated_credentials
from google.auth.credentials import Credentials
from google.cloud.exceptions import NotFound
from google.auth.transport import requests
from google.cloud import secretmanager

import firebase_admin

from src.config.constants import (
    GOOGLE_IMPERSONATE_SERVICE_ACCOUNT,
    DEFAULT_GCP_SCOPES,
    IAP_CLIENT_ID_MAP,
    FIREBASE_PROJECT,
)
from src.utils.console_printing import blue, green, red


def create_firebase_document(collection: str, doc_id: str, body: dict) -> bool:
    """
    Create/replace a document in the specified Firestore database
     Args:
         collection: str - reference to a collection
         doc_id: str - document identifier
         body: dict - document body
     Return:
           bool - result of the operation
    """
    firebase_admin.initialize_app(get_firebase_creds())
    db = firestore.client()
    ref_doc = db.collection(collection).document(doc_id).set(body)
    return True if ref_doc else False


def get_firebase_creds() -> firebase_admin.credentials.Certificate:
    """
    Retrieve the Firebase Admin Certificate from Google Secret, then
    use it to create a Firebase Admin Credential and return it.

    Assumes a secret named firebase_adminsdk_on-demand_shared is stored
    in the project identified in ENV VAR FIREBASE_PROJECT or default.

    Assumes secret can be accessed by GOOGLE_IMPERSONATE_SERVICE_ACCOUNT
    and that we can impersonate from default GCP creds.
    """
    creds, _ = default(scopes=DEFAULT_GCP_SCOPES)
    icreds = impersonated_credentials.Credentials(
        source_credentials=creds,
        target_principal=GOOGLE_IMPERSONATE_SERVICE_ACCOUNT,
        target_scopes=DEFAULT_GCP_SCOPES,
        lifetime=500,
    )
    client = secretmanager.SecretManagerServiceClient(credentials=icreds)

    secret_uri = (
        f"projects/{FIREBASE_PROJECT}/secrets/"
        "firebase_adminsdk_on-demand_shared/versions/latest"
    )
    response = client.access_secret_version(name=secret_uri)
    sa_info = json.loads(response.payload.data.decode("UTF-8"))
    sa_cert = json.loads(sa_info["firebase_adminsdk_service_account_key"])

    return firebase_admin.credentials.Certificate(sa_cert)


def get_bearer(env: str) -> str:
    request = requests.Request()
    SCOPES = DEFAULT_GCP_SCOPES
    # try for "default" but if it wasn't passed in otherwise try the one for a given
    # environment type "nonprod" or "uat"

    audience = IAP_CLIENT_ID_MAP["default"]
    if not audience:
        audience = (
            IAP_CLIENT_ID_MAP["uat"] if env == "uat" else IAP_CLIENT_ID_MAP["nonprod"]
        )
    creds, _ = default(scopes=SCOPES, request=request)

    icreds = impersonated_credentials.Credentials(
        source_credentials=creds,
        target_principal=GOOGLE_IMPERSONATE_SERVICE_ACCOUNT,
        target_scopes=SCOPES,
    )

    id = impersonated_credentials.IDTokenCredentials(
        icreds, target_audience=audience, include_email=True
    )

    id.refresh(request)
    return "Bearer " + str(id.token)


def login_to_gcp(interactive: bool = True) -> Credentials:
    warnings.simplefilter("ignore")
    if interactive:
        input(
            blue(
                "Make sure you are set your cloud project-id.\n "
                "To check which project is selected, run command:\n"
                "<gcloud config get-value project>"
                "If you are not connected, please run another command:\n"
                "<gcloud config set project myProject-id> "
                "Press ENTER when done\n"
            )
        )

        try:
            credentials, project_id = default()
            print(
                blue(
                    "!!!!Make sure you are set your cloud project-id. "
                    "To check which project is selected, run command:\n"
                    "<gcloud config get-value project>\n"
                    "If project is not set, please run command in a format:\n "
                    "<gcloud config set project myProject-id\n\n "
                    "Your current project-id is:"
                )
            )
            print(f"{green(project_id)}")
            input(blue("Press ENTER to confirm:"))
            return credentials

        except exceptions.DefaultCredentialsError:
            print(
                red(
                    "Your default credentials are not set. "
                    "To set them, please execute command: \n"
                    "<gcloud auth application-default login> \n"
                    "Then please rerun the script."
                )
            )
            sys.exit(1)
    else:
        credentials, _ = default()
        return credentials


def change_gcp_project(project_id: str) -> subprocess.CompletedProcess:
    subprocess.run(["gcloud", "config", "set", "disable_prompts", "true"], stdout=True)
    result = subprocess.run(
        ["gcloud", "config", "set", "project", project_id], stdout=True
    )
    return result


def upload_file_to_google_bucket(
    project_id: str,
    credentials: Credentials,
    integration_etl_bucket_name: str,
    source_filename: str,
    source_filepath: str,
) -> None:  # Requires local google cloud credentials
    try:
        client = storage.Client(credentials=credentials, project=project_id)
        bucket = client.get_bucket(integration_etl_bucket_name)

        blob = bucket.blob(f"inbound/data/{source_filename}")
        try:
            blob.upload_from_filename(source_filepath)
            print(
                blue(
                    f"File {source_filename} uploaded to {integration_etl_bucket_name} in project: {project_id}"
                )
            )
        except:
            print(red(f"Error uploading {source_filename} to google bucket!"))
            return
    except NotFound:
        print(
            red(
                f"Bucket {integration_etl_bucket_name} doesn't exist in {project_id} GCP project."
            )
        )
    except:
        print(
            red(
                f"Local GCP project {project_id} doesn't exist! Please set project locally:"
                "gcloud config set project myproject"
            )
        )
        sys.exit(1)


def pubsub_puller(
    project_id: str, subscription_name: str, num_messages: int = 1
) -> dict | None:
    subscription = subscription_name
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, subscription)

    try:
        response = subscriber.pull(
            request={"subscription": subscription_path, "max_messages": num_messages},
            retry=retry.Retry(deadline=300),
        )
        if len(response.received_messages) > 0:
            msg = response.received_messages[-1]
            payload = json.loads(msg.message.data.decode("utf-8"))

            subscriber.acknowledge(
                request={"subscription": subscription_path, "ack_ids": [msg.ack_id]}
            )

            return payload
        else:
            return None
    except Exception as e:
        return {"message": f"{e}"}
