import json
import os

devices_file = open("balena-devices.json", "r")
devices = json.load(devices_file)
devices_file.close()

for device in devices:
    print(f"Rebooting device {device['uuid']}")
    output = os.system(f"balena device reboot {device['uuid']}")
