import requests
import json
import pprint
import time

from gpiozero import LED

_red_led = LED(18)
_green_led = LED(23)

class Status(object):
    def __init__(self, errorLevel):
        self.errorLevel = errorLevel

def call_Uptrends_Api(method_url):

    # Fill in your Uptrends credentials here
    username = "my-email@my-domain.com"
    password = "XXXXXXXX"

    # Prepare data for the request
    baseUrl = "https://api.uptrends.com/v3/"
    authentication = (username, password)
    headers = { "Accept": "application/json" }

    # Execute the request
    response = requests.get(baseUrl + method_url, auth=authentication, headers = headers)

    # Convert the response into string data, which will contain JSON content
    byteData = response.content
    stringData = byteData.decode("utf-8")
    return stringData

def statusInitializer(statusItem):
    return Status(statusItem["ErrorLevel"])

def update_error_LED(error_count):

    if error_count > 0:
        _red_led.on()
        _green_led.off()
    else:
        _green_led.on()
        _red_led.off()

    print("Monitors with errors: {:d}".format(error_count))

def get_monitor_groups():
    group_info = call_Uptrends_Api("probegroups")
    print("groups:")
    print(group_info)

def get_status_update():
    try:
        # Call the API to retrieve status data for every monitor in the All Monitors group
        monitor_group_id = "656c1ffaebf04f389782128461ceabc7"
        api_status_data = call_Uptrends_Api("probegroups/" + monitor_group_id + "/status")

        # Use the json.loads function to convert each object in the JSON array into a Status object
        statusList = json.loads(api_status_data, object_hook = statusInitializer)

        # Count the number of objects in the array of Status objects that have an error level of Confirmed Error
        errorCount = sum(1 for status in statusList if status.errorLevel == "Confirmed")

        update_error_LED(errorCount)

    except requests.exceptions.ConnectionError:
        print("Connection failed.")

# Main loop
while True:
    get_status_update()
    time.sleep(60)
