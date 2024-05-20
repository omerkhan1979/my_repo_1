import copy
from datetime import date, datetime, timedelta
import json
import logging
import os
import pandas as pd
import pytz
from requests import post, Response
import sys

LOGLEVEL = os.environ.get("LOGLEVEL", "DEBUG").upper()

RT_DAY = os.environ.get("RT_DAY", "WED").upper()
RT_WEEK = os.environ.get("RT_WEEK", "EVEN").upper()
RT_TIME_UTC = os.environ.get("RT_TIME_UTC", "17:00").upper()

FOLDER = "INCIDENTS"

URL = os.environ.get(
    "STATUSPAGE_URL", "https://api.statuspage.io/v1/pages/qth8l8vxd7y4/incidents"
)

logging.basicConfig(level=LOGLEVEL)


# Get the value of 'TOKEN'
# environment variable
key = "TOKEN"
TOKEN_VALUE = os.getenv(key, "fae623a8-da96-4cd5-8c9c-7430d03349c4")


def calculate_rt_str(currentTime=date.today()) -> str:
    week_number = int(currentTime.strftime("%U"))
    year = currentTime.strftime("%y")
    adjusted_week_number = week_number + 1
    adjusted_week_str = f"{adjusted_week_number:02d}"
    return "RT" + adjusted_week_str + "-" + year


def calculate_week_num(currentTime=date.today()) -> int:
    return currentTime.isocalendar()[1]


def convert_day_of_week_numeric(day_of_week: str) -> int:
    if "SUN" in day_of_week.upper():
        return 0
    elif "MON" in day_of_week.upper():
        return 1
    elif "TUE" in day_of_week.upper():
        return 2
    elif "WED" in day_of_week.upper():
        return 3
    elif "THU" in day_of_week.upper():
        return 4
    elif "FRI" in day_of_week.upper():
        return 5
    elif "SAT" in day_of_week.upper():
        return 6
    raise ValueError(f"Day of the week passed in is invalid: {day_of_week}")


def check_if_day_of_week_is_after_RT(day_of_week: str, rt_day="WED") -> bool:
    """Return True if day is after or on the same day

    Args:
        day_of_week (str): str representation of the day of the week
        rt_day (str, optional): _description_. Defaults to "WED".

    Returns:
        bool: True if day is after or on the same day otherwise False
    """
    return convert_day_of_week_numeric(day_of_week) >= convert_day_of_week_numeric(
        rt_day
    )


def get_time_in_timezone(time: datetime, timezone: str) -> datetime:
    """Takes the given datetime object and converts it to a datetime of the
    specified timezone provided
     Args:
         time (datetime): datetime object to convert
         timezone (str): TimeZone string representation

     Returns:
         (datetime): datetime object to convert
    """
    for tz in timezone.split(" "):
        try:
            return time.astimezone(pytz.timezone(tz))
        except pytz.exceptions.UnknownTimeZoneError as invalid_tz:
            # possible that two timezone where provided so try the next one
            logging.debug(f"DID NOT USE TIME ZONE:{invalid_tz}")
            continue


def convert_time_24_hours(time_to_convert: str, start_time=False):
    """Takes in the time portion of a datetime object in str format and returns
    a tuple of the hour and minutes in 24 hours
      specified timezone provided
       Args:
           time_to_convert (str): time portion string representation

       Returns:
           tuple(int, int): hour and min
    """
    mins = 00
    hour = 00

    if time_to_convert.endswith("PM"):
        # Check PM
        if ":" in time_to_convert:
            mins = int(
                time_to_convert[
                    time_to_convert.index(":") + 1 : time_to_convert.index("PM")
                ]
            )
            hour = int(time_to_convert[: time_to_convert.index(":")])
        else:
            hour = int(time_to_convert[: time_to_convert.index("PM")])

        # add 12 for 24 hours time
        if hour != 12:
            hour += 12
    elif time_to_convert.endswith("AM"):
        # case for AM
        if ":" in time_to_convert:
            mins = int(
                time_to_convert[
                    time_to_convert.index(":") + 1 : time_to_convert.index("AM")
                ]
            )
            hour = int(time_to_convert[: time_to_convert.index(":")])
        else:
            hour = int(time_to_convert[: time_to_convert.index("AM")])

        # if it was 12 AM set it to 24 so it can go to the next day
        if start_time and hour == 24:
            hour = 0
        else:
            hour = hour if hour != 12 else 24
    return hour, mins


class ScheduleWindow:
    """Internal representation of 'ScheduleWindow' entity, with only essential
    data necessary to provide to the statuspage.io API"""

    def __init__(self, info):
        # Client, Takeoff_Weeks,Primary_Window,DAY_OF_WEEK,Time_Zone,
        # Component ID,Sub-component ID

        self.client = info["Client"]
        self.week = info["Takeoff_Weeks"].upper()
        self.primary = info["Primary_Window"]
        self.day_of_week = info["DAY_OF_WEEK"].upper()
        self.time_zone = info["Time_Zone"]
        self.component = {info["Component ID"]: "operational"}
        self.sub_component = info["Sub-component ID"].replace('"', "").split(" ")
        # Ignoring the last columne for now - Secondary Window - possible to use later

    def __repr__(self):
        """Format to be used to print out or logging information of the class"""
        return (
            f"ScheduleWindow {{client: {self.client}, week: {self.week}, primary: {self.primary}, "
            f"day_of_week: {self.day_of_week}, time_zone: {self.time_zone}, "
            f"component: {self.component}, sub_component: {self.sub_component} }}"
        )

    def _scrub_iso_date_str(self, d_tz: datetime) -> str:
        """Modifies the timedate string that StatusPage wants using strftime
        Args:
            d_tz (datetime): datetime of client time

        Returns:
            str: modified datetime
        """
        utc_dt = d_tz.astimezone(pytz.utc)
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-4] + "Z"

    def _calculate_time(self, d_tz: datetime) -> tuple[str, str]:
        """_calculate_time
           RT is cut in EST time
           convert that time to client time zone
           convert the next deployment date in client time zone
           send tuple in UTC time

        Args:
            d_tz (datetime): the current time in the clients time zone

        Raises:
            ValueError: Error caused when trying to determine the start and end times

        Returns:
            tuple[str, str]: start time in str format and end time in str format for the window
        """

        start_date_tz: datetime = copy.deepcopy(d_tz).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end_date_tz: datetime = copy.deepcopy(d_tz).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        split_primary_time_window = self.primary.split("-", 1)
        starttime = split_primary_time_window[0].strip().upper()
        end_time = split_primary_time_window[1].strip().upper()
        # set the local hours correct
        start_hour, start_mins = convert_time_24_hours(starttime, True)
        logging.debug(f"Start Hour: {start_hour}")
        # all to rotate to the next day for end
        endtime_hour, endtime_mins = convert_time_24_hours(end_time, False)
        logging.debug(f"End Hour: {endtime_hour}")
        if endtime_hour < start_hour:
            endtime_hour += start_hour

        try:
            # use timedelta instead of replace since timedelta will take care
            # of the rollover conditions as of the next day, month, year, etc
            start_date_tz += timedelta(hours=start_hour, minutes=start_mins)
            end_date_tz += timedelta(hours=endtime_hour, minutes=endtime_mins)
        except ValueError:
            raise ValueError(
                f'Expecting Primary window: "{split_primary_time_window}" to include AM and/or PM'
            )

        return (
            self._scrub_iso_date_str(start_date_tz),
            self._scrub_iso_date_str(end_date_tz),
        )

    def calculate_next_maint_window(self) -> tuple[str, str]:
        """calculate_next_maint_window
           RT is cut in EST time
           convert that time to client time zone
           convert the next deployment date in client time zone
           send tuple in UTC time

        Returns:
            tuple[str, str]: start time and end time for the window
        """
        week_type = "ODD"
        if calculate_week_num() % 2 == 0:
            week_type = "EVEN"

        # set d_tz to the proper week
        d_tz = get_time_in_timezone(datetime.now(), self.time_zone)

        # make sure the week we are running this corresponds to a RT_WEEK
        while RT_WEEK != week_type:
            d_tz = d_tz + timedelta(days=1)
            if calculate_week_num(d_tz) % 2 == 0:
                week_type = "EVEN"
            else:
                week_type = "ODD"

        logging.debug(f"RT WEEK {d_tz}")
        if self.week == week_type:
            # check if the current day of the week is after RT_DAY
            if (
                check_if_day_of_week_is_after_RT(
                    d_tz.strftime("%A").upper()[0:3], RT_DAY
                )
                != False
            ):
                d_tz = d_tz + timedelta(days=8)
                logging.debug(f"{self.client} ----- {d_tz}")
                week_type = "ODD"
                if calculate_week_num() % 2 == 0:
                    week_type = "EVEN"

        while self.week != week_type:
            d_tz = d_tz + timedelta(days=1)
            if calculate_week_num(d_tz) % 2 == 0:
                week_type = "EVEN"
            else:
                week_type = "ODD"

        # move d_utc to the proper day of the week
        while d_tz.strftime("%A").upper()[0:3] != self.day_of_week[0:3]:
            logging.debug(d_tz)
            d_tz = d_tz + timedelta(days=1)

        return self._calculate_time(d_tz)


class StatusPage:
    url: str
    client: str
    status = "scheduled"
    impact_override: str = "none"
    scheduled_remind_prior = True
    scheduled_auto_in_progress = True
    scheduled_auto_completed = True
    metadata = {}
    deliver_notifications = True
    auto_transition_deliver_notifications_at_end = True
    auto_transition_deliver_notifications_at_start = True
    auto_transition_to_maintenance_state = True
    auto_transition_to_operational_state = True
    body = (
        "A Takeoff maintenance window is being planned for your organization. During this time, Takeoff services will be briefly offline. "
        "<h3>Release Notes</h3>"
        "Release notes and other documentation is available at the following location: https://takeoffhelp.zendesk.com/hc/en-us/categories/360003572857\n"
        "If you have any questions, please reach out to your Technical Account Manager."
    )
    scheduled_auto_transition = True

    def __init__(self, url: str, client: str):
        self.url = url
        self.client = client
        self.incident_name = f"Maintenance Window - {self.client}"

    def generate_request_payload(self, window: ScheduleWindow) -> dict:
        """Generate the scheduled maintenance window request data

        Args:
            window (ScheduleWindow): contains the need data for the calculation

        Returns:
            dict: results to be sent as payload
        """

        scheduled_for, scheduled_until = window.calculate_next_maint_window()
        logging.info(f"Start time of window: {scheduled_for}")
        logging.info(f"End time of window: {scheduled_until}")

        return {
            "incident": {
                "name": self.incident_name,
                "status": self.status,
                "impact_override": self.impact_override,
                "scheduled_for": scheduled_for,
                "scheduled_until": scheduled_until,
                "scheduled_remind_prior": self.scheduled_remind_prior,
                "scheduled_auto_in_progress": self.scheduled_auto_in_progress,
                "scheduled_auto_completed": self.scheduled_auto_completed,
                "metadata": self.metadata,
                "deliver_notifications": self.deliver_notifications,
                "auto_transition_deliver_notifications_at_end": self.auto_transition_deliver_notifications_at_end,
                "auto_transition_deliver_notifications_at_start": self.auto_transition_deliver_notifications_at_start,
                "auto_transition_to_maintenance_state": self.auto_transition_to_maintenance_state,
                "auto_transition_to_operational_state": self.auto_transition_to_operational_state,
                "body": "A Takeoff maintenance window is being planned for your organization. During this time, Takeoff services will be briefly offline. <br><h3>Release Notes</h3><br>Release notes and other documentation is available at the following location: https://takeoffhelp.zendesk.com/hc/en-us/categories/360003572857<br>If you have any questions, please reach out to your Technical Account Manager.",
                "components": window.component,
                "component_ids": window.sub_component,
                "scheduled_auto_transition": self.scheduled_auto_transition,
            }
        }


def send_request(url, window_payload: str) -> tuple[bool, str]:
    """Sends the scheduled maintenance window

    Args:
        window (ScheduleWindow): contains the need data for the calculation

    Returns:
        bool: True if successful, false otherwise
    """

    success = False
    client_uuid: str = ""
    x: Response = post(
        url,
        json=window_payload,
        headers={"Authorization": TOKEN_VALUE},
    )

    if x.status_code != 201 and x.reason != None:
        # log errors
        logging.error("There was an issue with the request")
        logging.error(x.reason)
        logging.error(x.text)

    if x.status_code > 400:
        # exit right away if its a 401 or higher issue. Previous conditional will print out more details
        logging.error("StatusPage TOKEN provided is either invalid or expired.")

    if x.status_code == 201:
        if x.json() and x.json()["id"]:
            client_uuid = x.json()["id"]
            success = True
        else:
            logging.error(
                "Maintenance Window was created BUT didn't return a "
                f"UUID. Here was the response body: {x.json}"
            )
    return success, client_uuid


def parse_maint_file(file_name) -> list[ScheduleWindow]:
    """Goes through a maintenance file and parses for the representation of ScheduleWindow data
    Args:
        file_name (str): Name of the file to read

    Returns:
        list: ScheduleWindow objects
    """
    df = pd.read_csv(file_name, dtype=str)
    # go there each row and add the Schedule
    logging.debug(df)
    map_client_schedule_window = []
    for index, row in df.iterrows():
        # Columns
        # Client,Takeoff_Weeks,Primary_Window,DAY_OF_WEEK,Time_Zone,Component ID,Sub-component ID,Secondary Window
        temp_data = ScheduleWindow(row)
        # creates a map of client to
        map_client_schedule_window.append(temp_data)

    logging.debug("The following data was read in:\n")
    logging.debug(map_client_schedule_window)
    return map_client_schedule_window


def create_json_file(dictList, file_name="./data/Window_Times.json"):
    """Takes the list of ScheduleWindow and updates a file with the information
    Args:
        dictList (dict[]): list of ScheduleWindow
        file_name (str): Name of the file to read
    """
    # convert into json
    json_string = json.dumps(dictList, indent=2)

    # Using a JSON string
    with open(file_name, "w") as outfile:
        outfile.write(json_string)

    logging.debug(f"The following is the content of the json file:\n {json_string}")


def read_json_file(file_name="./data/Window_Times.json"):
    """Takes a json file with the information of Scheduled Windows
    Args:
        file_name (str): Name of the file to read
    Returns:
        json_string: list of ScheduleWindow
    """
    with open(file_name, "r") as infile:
        json_string = json.load(infile)

    logging.debug(f"The following is the content of the json file:\n {json_string}")
    return json_string


if __name__ == "__main__":
    """Exit Codes:
    0 - Success
    1 - No token was made available
    2 - Arguments provided are invalid
    3 - At least one of the send window requests failed.
    """

    args = sys.argv
    sendWindows = False
    failure = False

    if args != None and len(args) >= 2:
        # only need args for send and token for send
        if TOKEN_VALUE == None or len(TOKEN_VALUE.strip()) == 0:
            # check for token and exit if one doesn't exist
            logging.error(
                "environment variable StatusPage TOKEN didn't exist. StatusPage token is needed to send requests"
            )
            exit(1)
        elif "send" in args[1].lower():
            # 'send' is the only argument acceptable
            sendWindows = True
            logging.info("Proceeding since environment variable TOKEN exists")
            pass
        else:
            # exit if an argument other than 'send' was provided
            logging.error(f"Invalid request as {args[1]} is not valid")
            logging.error(
                "Providing no arguments generation the schedule window json file."
            )
            logging.error("Providing the argument 'send' will send the requests")
            exit(2)

    if sendWindows:
        # only send request on send
        schedule_windows = read_json_file()
        if not os.path.exists(FOLDER):
            os.makedirs(FOLDER)

        with open(
            os.path.join(FOLDER, calculate_rt_str() + "_incidents.yaml"), "a"
        ) as file:
            for window in schedule_windows:
                window_name: str = window["incident"]["name"]
                client = window_name[window_name.index("-") + 1 :]
                client = client.strip().lower()
                msg = f"{window_name} was: "

                # Sends request print successful or failed depending on result
                success, client_uuid = send_request(URL, window)
                logging.info({True: msg + "Successful", False: msg + "Failed"}[success])
                if success:
                    file.write(client + ": " + client_uuid + "\n")
                else:
                    failure = True
        if failure:
            logging.error("At least one sene request window failed review logs.")
            exit(3)

    else:
        # other create json file

        # assumption that this is executed at route level or repo
        schedule_windows: list[ScheduleWindow] = parse_maint_file(
            "./data/Statuspage_Client_Times.csv"
        )
        logging.debug(
            f"The following was the output from reading in the client scheduled information:\n {schedule_windows}"
        )

        dictList = []
        # go through each window and send request
        for window in schedule_windows:
            status_page = StatusPage(URL, window.client)
            dictList.append(status_page.generate_request_payload(window))

        create_json_file(dictList)
