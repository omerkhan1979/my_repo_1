from collections import deque
import threading

from requests.models import Response, HTTPError
from pprint import pprint
from src.config.constants import VERBOSE

from src.utils.console_printing import red, cyan

_last_calls = deque[str]([], 100)


def handle_response(
    response: Response,
    *expected_statuses,
    print_details=True,
    raise_error=True,
    json=True,
):
    details = (
        f"\tSTATUS CODE RECEIVED: {response.status_code} - EXPECTED STATUSES: {expected_statuses}\n"
        f"\tREQUEST: {response.request} URL: '{response.request.path_url}'\n"
        f"\tBODY: '{response.request.body}'\n"
        f"\tRESPONSE: '{response.text[0:500]}{'...(response trimmed)...' if len(response.text) > 500 else ''}'\n"
    )
    _last_calls.append(f"{threading.get_ident()}-{response.request.path_url}")
    if VERBOSE or (
        # if we see more than 15 examples from a thread give more detail
        len(
            [
                x == f"{threading.get_ident()}-{response.request.path_url}"
                for x in _last_calls
            ]
        )
        > 15
    ):
        if VERBOSE:
            print(
                "\nVerbose request/response details (disable by unsetting RQ_VERBOSE):"
            )
        print(details)
        _last_calls.clear()
    if response.status_code not in expected_statuses:
        if print_details:
            print(
                red(
                    f"\n\nException during {response.request.method} request to {response.url}"
                )
            )
            print(cyan(f"\nStatus code: {response.status_code}"))

            body = response.request.body
            if body is not None:
                print(cyan("\nRequest body: "))
                if isinstance(body, bytes):
                    body = body.decode("utf-8")
                pprint(body)

            print(cyan("\nRequest headers: "))
            pprint(response.request.headers)

            print(cyan("\nError text:"))
            print(response.text)
            print("\n\n")

        if raise_error:
            raise HTTPError(
                f"Unexpected status code.  {details}",
                response=response,
            )
    else:
        if json:
            return response.json()
        else:
            return response.content
