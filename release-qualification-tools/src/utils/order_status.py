from src.api.takeoff.oms import OMS

from src.utils.console_printing import blue, done, red, waiting, yellow


def check_status_change_interactively(oms: OMS, order_id: str, target_status: str):
    """Used in orderflow scripts, requires user interaction"""
    print(waiting(f"Checking if status has changed to {blue(target_status)}..."))
    status_change = oms.check_status_change(order_id, target_status)
    _continue = "no"
    while not status_change and _continue != "yes":
        print(red(f"Status change to {target_status} not detected."))
        print(
            red(
                "Press Enter to try check again or type 'yes' if you want to proceed anyway"
            )
        )
        print(red("(test might fail on next step): "))
        _continue = input()
        status_change = oms.check_status_change(order_id, target_status)
    if status_change:
        print(done(f"Status {target_status} arrived!"))
        return True
    else:
        print(
            yellow(
                f"Status change to {target_status} not detected, proceeding regardless"
            )
        )
        return False
