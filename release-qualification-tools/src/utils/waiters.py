import time
from pprint import pprint
from time import sleep

from src.config.constants import VERBOSE
from src.utils.console_printing import bold, red, cyan


def waiter_factory(timeout=240, fail_on_timeout=True):
    def get_data_with_retries(func):
        def wrapper(*args, **kwargs):
            started = time.time()
            data = None
            last_except = ""
            if VERBOSE:
                import traceback

                print("\n\tIn a waiter, showing traceback:\n\t", end="")
                traceback.print_stack(limit=5)
            print(f"Trying to get some data from {func.__name__} in {timeout} seconds.")
            while not data and time.time() < started + timeout:
                try:
                    data = func(*args, **kwargs)
                    sleep(1)
                except Exception as err:
                    last_except = f"! Last exception was {err}"
                    pass
            if not data:
                print(
                    red(
                        f"\nNo data returned by {func.__name__} in {timeout} seconds{last_except}!\n{'-'*10}\nargs={args}\nkwargs={kwargs}\n{'-'*10}\n)"
                    )
                )
                if fail_on_timeout:
                    raise TimeoutError(
                        f"{func.__name__} failed after a timeout of {timeout} seconds"
                    )
            else:
                print(
                    cyan(
                        f"\nData returned by {func.__name__} in {time.time() - started} seconds!\ndata={data}\n"
                    )
                )
                return data

        return wrapper

    return get_data_with_retries


def wait_for_data_interactively(func):
    """Decorator - makes function waits for data (non-empty variable) and retry for provided time:"""

    def get_data(*args, **kwargs):
        try:
            time_to_wait = int(
                input(
                    "Please type for how long we will be retrying to get data - enter number of seconds: "
                )
            )
        except ValueError:
            print(bold("No time provided, will be retrying for 15 seconds..."))
            time_to_wait = 15
        attempts = 0
        waited = 0
        data = func(*args, **kwargs)
        while not data and waited < time_to_wait:
            wait_for = attempts * 3
            attempts += 1
            waited += wait_for
            print(f"Retrying in {wait_for}...")
            sleep(wait_for)
            data = func(*args, **kwargs)
        if data:
            print(bold("Data found: "))
            pprint(data)
            return data
        else:
            print(red(f"No data found in {waited}"))
            return None

    return get_data


wait = waiter_factory()
optional_wait = waiter_factory(fail_on_timeout=False)
