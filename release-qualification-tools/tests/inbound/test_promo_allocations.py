from datetime import datetime
from pytest import mark
from src.api.third_party.sftp_interaction import (
    check_is_sftp_file,
    delete_sftp_file,
    upload_via_sftp,
)

from src.utils.console_printing import cyan
from src.utils.helpers import wait_for_pubsub_message_after_sftp_upload
from src.utils.os_helpers import get_cwd

project_root_dir = get_cwd()


@mark.rq
@mark.inbound
@mark.promo
@mark.retailers("winter")
@mark.testrail("283815")
def test_promo(cfg, switch_gcp_project, retailer, env):
    file_name = "MFC_PROMOS_WINTER_608.csv"
    file_path = f"{project_root_dir}/data/{file_name}"
    now_datetime = datetime.now()
    now_date = now_datetime.strftime("%Y%m%d")
    remote_file_name = f"MFC_PROMOS_WINTER_608_{now_date}.csv"
    now_year = now_datetime.strftime("%Y")
    remote_file_path = f"/inbound/processed/{now_year}/{now_date}"
    try:
        assert upload_via_sftp(cfg, file_name, file_path, remote_file_name)
        count = 0
        expectedList = [
            "ALMOND JOY SNACK SIZE",
            "FERR BTRFNGR FUN SIZE",
            "SWEDISH FISH MINI SHR",
        ]
        checks = 0
        while checks < 50:
            payload = wait_for_pubsub_message_after_sftp_upload(cfg)
            checks += 1
            if payload.get("DESCRIPTION") in expectedList:
                count += 1
                expectedList.remove(payload.get("DESCRIPTION"))
            if count == 3:
                break
        assert check_is_sftp_file(cfg, remote_file_name, remote_file_path)
    finally:
        # TODO: remove this if != ode stuff after fixing PROD-12391
        if cfg.env != "ode":
            assert delete_sftp_file(cfg, remote_file_name, remote_file_path)
        else:
            try:
                delete_sftp_file(cfg, remote_file_name, remote_file_path)
            except Exception as err:
                print(
                    f"Failed to check/delete sftp file {remote_file_path}/{remote_file_name}: {err}"
                )
    print(cyan("Test case promo is:"))


@mark.rq
@mark.inbound
@mark.allocations
@mark.retailers("winter")
@mark.testrail("283814")
def test_allocations(cfg, switch_gcp_project, retailer, env):
    file_name = "MFC_STATUS_AND_ALLOCATIONS.csv"
    file_path = f"{project_root_dir}/data/{file_name}"
    now_datetime = datetime.now()
    now_date = now_datetime.strftime("%Y%m%d")
    remote_file_name = f"MFC_STATUS_AND_ALLOCATIONS_{now_date}.csv"
    now_year = now_datetime.strftime("%Y")
    remote_file_path = f"/inbound/processed/{now_year}/{now_date}"
    try:
        assert upload_via_sftp(cfg, file_name, file_path, remote_file_name)
        assert check_is_sftp_file(cfg, remote_file_name, remote_file_path)
        count = 0
        expectedList = ["SRBB ENGLSH MFN LT PR", "HOST COFFEE CAKE"]
        checks = 0
        while checks < 50:
            payload = wait_for_pubsub_message_after_sftp_upload(cfg)
            checks += 1
            if payload.get("DESCRIPTION") in expectedList:
                count += 1
                expectedList.remove(payload.get("DESCRIPTION"))
            if count == 2:
                break

    finally:
        # TODO: remove this if != ode stuff after fixing PROD-12391
        if cfg.env != "ode":
            assert delete_sftp_file(cfg, remote_file_name, remote_file_path)
        else:
            try:
                delete_sftp_file(cfg, remote_file_name, remote_file_path)
            except Exception as err:
                print(
                    f"Failed to check/delete sftp file {remote_file_path}/{remote_file_name}: {err}"
                )
    print(cyan("Test case allocations is:"))
