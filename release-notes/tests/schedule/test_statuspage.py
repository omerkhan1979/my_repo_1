from datetime import datetime
import logging
import re
import os
import pytest
import requests_mock

from src.schedule.statuspage import (
    ScheduleWindow,
    StatusPage,
    URL,
    calculate_rt_str,
    create_json_file,
    read_json_file,
    send_request,
)

LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG").upper()

logging.basicConfig(level=LOGLEVEL)

json_file_data_path = "./tests/tests_data/test_windows.json"


@pytest.fixture(scope="function")
def resource_file(request):
    json_file_data_path = "./tests/tests_data/test_windows.json"

    def resource_file_teardown():
        if os.path.exists(json_file_data_path):
            os.remove(json_file_data_path)

    request.addfinalizer(resource_file_teardown)
    return json_file_data_path


def test_calculate_rt_str():
    value = calculate_rt_str()
    assert re.match("RT\\d{2}-\\d{2}", value)


def test_create_read_file(schedule_window_list: list[ScheduleWindow], resource_file):
    status_page = StatusPage(URL, schedule_window_list[0].client)
    payload = status_page.generate_request_payload(schedule_window_list[0])
    payload1 = status_page.generate_request_payload(schedule_window_list[1])
    dictList = [payload, payload1]
    create_json_file(dictList, resource_file)
    assert os.path.exists(resource_file)
    assert dictList == read_json_file(resource_file)


def test_parse_maint_file(schedule_window_list):
    assert len(schedule_window_list) == 9
    assert schedule_window_list[0].client == "test"
    assert schedule_window_list[0].week == "EVEN"
    assert schedule_window_list[0].primary == "3AM-5AM"
    assert schedule_window_list[0].day_of_week == "WED"
    assert schedule_window_list[0].time_zone == "EST"
    assert schedule_window_list[0].component == {"xgmgg4dxzl5z": "operational"}
    assert schedule_window_list[0].sub_component == ["3wjz7zbt1w11r"]
    assert schedule_window_list[1].client == "test-fake-w-ignore"
    assert schedule_window_list[1].week == "EVEN"
    assert schedule_window_list[1].primary == "4:00PM-6:00PM"
    assert schedule_window_list[1].day_of_week == "WED"
    assert schedule_window_list[1].time_zone == "Australia/Melbourne GMT+11"
    assert schedule_window_list[1].component == {"xgmgg4dxzl5z": "operational"}
    assert schedule_window_list[1].sub_component == ["ps66jfhzdl14"]
    assert schedule_window_list[2].client == "test-fake-s-ignore"
    assert schedule_window_list[2].week == "EVEN"
    assert schedule_window_list[2].primary.upper() == "4AM-6AM"
    assert schedule_window_list[2].day_of_week == "TUES"
    assert schedule_window_list[2].time_zone == "America/Santiago"
    assert schedule_window_list[2].component == {"xgmgg4dxzl5z": "operational"}
    assert schedule_window_list[2].sub_component == ["xgmgg4dxzl5z"]
    assert schedule_window_list[3].client == "test-fake-m-ignore"
    assert schedule_window_list[3].week == "EVEN"
    assert schedule_window_list[3].primary.upper() == "02:00AM-4:00AM"
    assert schedule_window_list[3].day_of_week == "TUES"
    assert schedule_window_list[3].time_zone == "GMT+4 Asia/Dubai"
    assert schedule_window_list[3].component == {"xgmgg4dxzl5z": "operational"}
    assert schedule_window_list[3].sub_component == ["3wjz7zbt1w11r"]
    assert schedule_window_list[4].client == "test-fake-a-ignore"
    assert schedule_window_list[4].week == "EVEN"
    assert schedule_window_list[4].primary.upper() == "3:00PM-6:00PM"
    assert schedule_window_list[4].day_of_week == "WED"
    assert schedule_window_list[4].time_zone == "US/Pacific"
    assert schedule_window_list[4].component == {"xgmgg4dxzl5z": "operational"}
    assert schedule_window_list[4].sub_component == ["3wjz7zbt1w11r", "xgmgg4dxzl5z"]
    assert schedule_window_list[5].client == "test-fake-p-ignore"
    assert schedule_window_list[5].week == "EVEN"
    assert schedule_window_list[5].primary.upper() == "10:00PM-12:00AM"
    assert schedule_window_list[5].day_of_week == "TUES"
    assert schedule_window_list[5].time_zone == "MST"
    assert schedule_window_list[5].component == {"mzvd0bhglzpq": "operational"}
    assert schedule_window_list[5].sub_component == ["1r8gxzqq3ljp"]
    assert schedule_window_list[6].client == "test-fake-1200AM-ignore"
    assert schedule_window_list[6].week == "EVEN"
    assert schedule_window_list[6].primary.upper() == "12:00AM-2:00AM"
    assert schedule_window_list[6].day_of_week == "WED"
    assert schedule_window_list[6].time_zone == "EST"
    assert schedule_window_list[6].component == {"mzvd0bhglzpq": "operational"}
    assert schedule_window_list[6].sub_component == ["1r8gxzqq3ljp"]
    assert schedule_window_list[7].client == "test-fake-1200PM-ignore"
    assert schedule_window_list[7].week == "EVEN"
    assert schedule_window_list[7].primary.upper() == "12PM-2PM"
    assert schedule_window_list[7].day_of_week == "WED"
    assert schedule_window_list[7].time_zone == "EST"
    assert schedule_window_list[7].component == {"mzvd0bhglzpq": "operational"}
    assert schedule_window_list[7].sub_component == ["1r8gxzqq3ljp"]
    assert schedule_window_list[8].client == "test-fake-end12PM-ignore"
    assert schedule_window_list[8].week == "EVEN"
    assert schedule_window_list[8].primary.upper() == "10:00AM-12:00PM"
    assert schedule_window_list[8].day_of_week == "THUR"
    assert schedule_window_list[8].time_zone == "Asia/Dubai"


def test_calculate_next_maint_window(schedule_window_list: list[ScheduleWindow]):
    # THESE ENTRIES HAVE WINDOWS THAT STAY IN SAME DAY
    # Adjustments must be made for time shifts that occur throught the year for the following:
    # -Woolworths time shifts 1st sunday in Oct and Apr.
    # -SMU time shifts Sept 3 and Apr 7.
    # -ABS 1st Sun in Nov and 2nd Sun in Mar.
    test_start, test_end = schedule_window_list[0].calculate_next_maint_window()
    logging.debug(f"{schedule_window_list[0].client} ----- {test_start} Test Client")
    assert "T08:00:00.000Z" in test_start
    assert "T10:00:00.000Z" in test_end
    assert test_start < test_end
    test_start, test_end = schedule_window_list[1].calculate_next_maint_window()
    logging.debug(
        f"{schedule_window_list[1].client} ----- {test_start} (Check for DST shift: Woolworths time shifts 1st sunday in Oct and Apr)"
    )
    assert "T05:00:00.000Z" in test_start
    assert "T07:00:00.000Z" in test_end
    assert test_start < test_end
    test_start, test_end = schedule_window_list[2].calculate_next_maint_window()
    logging.debug(
        f"{schedule_window_list[2].client} ----- {test_start} (Check for DST shift: SMU time shifts Sept 3 and Apr 7)"
    )
    assert "T07:00:00.000Z" in test_start
    assert "T09:00:00.000Z" in test_end
    assert test_start < test_end
    test_start, test_end = schedule_window_list[3].calculate_next_maint_window()
    logging.debug(
        f"{schedule_window_list[3].client} ----- {test_start} (MAF - does not observe dst)"
    )
    assert "T22:00:00.000Z" in test_start
    assert "T00:00:00.000Z" in test_end
    assert test_start < test_end
    test_start, test_end = schedule_window_list[4].calculate_next_maint_window()
    logging.debug(
        f"{schedule_window_list[4].client} ----- {test_start} (Check for DST shift: ABS 1st Sun in Nov and 2nd Sun in Mar)"
    )
    assert "T23:00:00.000Z" in test_start
    assert "T02:00:00.000Z" in test_end
    assert test_start < test_end
    test_start, test_end = schedule_window_list[5].calculate_next_maint_window()
    logging.debug(
        f"{schedule_window_list[5].client} ----- start: {test_start} (Pinemelon does not observe dst)"
    )
    assert "T05:00:00.000Z" in test_start
    logging.debug(
        f"{schedule_window_list[5].client} ----- end: {test_end} (Pinemelon does not observe dst)"
    )
    assert "T07:00:00.000Z" in test_end
    assert test_start < test_end
    test_start, test_end = schedule_window_list[6].calculate_next_maint_window()
    logging.debug(
        f"{schedule_window_list[6].client} ----- start: {test_start} (12:00AM test)"
    )
    assert "T05:00:00.000Z" in test_start
    logging.debug(
        f"{schedule_window_list[6].client} ----- end: {test_end} (12:00AM test)"
    )
    assert "T07:00:00.000Z" in test_end
    assert test_start < test_end
    test_start, test_end = schedule_window_list[7].calculate_next_maint_window()
    logging.debug(
        f"{schedule_window_list[7].client} ----- start: {test_start} (12:00PM test)"
    )
    assert "T17:00:00.000Z" in test_start
    logging.debug(
        f"{schedule_window_list[7].client} ----- end: {test_end} (12:00PM test)"
    )
    assert "T19:00:00.000Z" in test_end
    assert test_start < test_end
    test_start, test_end = schedule_window_list[8].calculate_next_maint_window()
    logging.debug(
        f"{schedule_window_list[8].client} ----- start: {test_start} (end at 12:00AM test)"
    )
    assert "T06:00:00.000Z" in test_start
    logging.debug(
        f"{schedule_window_list[8].client} ----- end: {test_end} (end at 12:00AM test)"
    )
    assert "T08:00:00.000Z" in test_end
    assert test_start < test_end


def test_calculate_next_maint_window_rollover(
    # THESE ENTRIES HAVE WINDOWS THAT EXPAND TO THE NEXT DAY
    schedule_window_list: list[ScheduleWindow],
):
    test_start, test_end = schedule_window_list[3].calculate_next_maint_window()
    logging.debug(
        f"{schedule_window_list[3].client} ----- Start: {test_start}  End: {test_end}"
    )
    assert "T22:00:00" in test_start
    assert "T00:00:00" in test_end
    assert test_start < test_end
    test_start, test_end = schedule_window_list[4].calculate_next_maint_window()
    logging.debug(f"{schedule_window_list[4].client} ----- {test_start}")
    assert "T23:00:00.000Z" in test_start
    assert "T02:00:00.000Z" in test_end
    assert test_start < test_end


def test_generate_payload(schedule_window_list: list[ScheduleWindow]):
    status_page = StatusPage(URL, schedule_window_list[1].client)
    payload = status_page.generate_request_payload(schedule_window_list[1])
    assert payload != None


def test_send_request(caplog, statuspage_response: dict):
    with requests_mock.Mocker() as m:
        m.post(URL, status_code=201, json=statuspage_response)
        status, client_str = send_request(URL, "HELLO")
        assert status == True
        assert client_str == "p31zjtct2jer"
        assert "BUT didn't return a UUID" not in caplog.text
        assert "incidents 201" in caplog.text


def test_send_request_negative(caplog):
    with requests_mock.Mocker() as m:
        m.post(URL, status_code=201, json={})
        status, client_str = send_request(URL, "HELLO")
        assert status == False
        assert client_str == ""
        assert "BUT didn't return a UUID" in caplog.text
        assert "incidents 201" in caplog.text


# Uncomment these when running integration locally
# def test_real_send_request(resource_file):
#    assert True in send_request(URL, read_json_file(resource_file)[1])

# This is correct - This showed the correct time in StatusPage as of 10/20/2022
# def test_send_request(schedule_window_list: list[ScheduleWindow]):
#     status_page = StatusPage(URL, schedule_window_list[3].client)
#     assert status_page.send_request(schedule_window_list[3]) == True
