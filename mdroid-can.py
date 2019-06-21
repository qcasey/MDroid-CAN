from canard import can
from canard.hw import cantact
import handlers
import requests
import logging
import argparse
import os
import json

# BE SURE TO CHANGE THESE
# Logging address more than likely should be commented out
LOGGING_ADDRESS = "http://localhost:5353/session/" # This is where we'll log the data with a RESTful post
DEVICE = "/dev/ttyACM0"

# Start logging
logging.basicConfig(level=logging.DEBUG)
# Make requests a little quieter
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# Reference the handlers in handlers.py, 
# mapping Frame IDs to a function that can decode them
handlers = {
	339: handlers.parseASC1,
	790: handlers.parseDME1,
	809: handlers.parseDME2,
	824: handlers.parseDME3,
	1349: handlers.parseDME4,
	1555: handlers.parseIC,
	1557: handlers.parseAC,
	504: handlers.parseBrakePressure
}

def parseConfig():
	global LOGGING_ADDRESS, DEVICE

	# parse program arguments
	parser = argparse.ArgumentParser(description='Read from BMW E46 CAN Bus, forward to REST API.')
	parser.add_argument('--settings', action='store', required=True, help='Config file to load Device and API settings.')
	args  = parser.parse_args()

	# Overwrite defaults if settings file is provided
	if args.settings:
		if os.path.isfile(args.settings): 
			try:
				with open(args.settings) as json_file:
					data = json.load(json_file)
					if "CONFIG" in data:
						# Setup MDroid API
						if "MDROID_HOST" in data["CONFIG"]:
							LOGGING_ADDRESS = data["CONFIG"]["MDROID_HOST"]
						else:
							logging.debug("MDROID_HOST not found in config file, not using MDroid API.")

					# Setup device
					if "CAN_DEVICE" in data["CONFIG"]:
						DEVICE = data["CONFIG"]["CAN_DEVICE"]
					else: 
						logging.debug("CAN_DEVICE not found in config file, using defaults.")

			except IOError as e:
				logging.error("Failed to open settings file:"+args.settings)
				logging.error(e)
		else:
			logging.error("Could not load settings from file"+str(args.settings))

# Log the decoded values to MDroid Core
def logFrame(decodedValues):
	for key,value in decodedValues.iteritems():
		try: 
			postingKey = key.upper().replace(" ", "_") # Format this to look consistent in Session db
			r = requests.post(LOGGING_ADDRESS+postingKey, json={"value": str(value)}, headers={'Content-type': 'application/json', 'Accept': 'text/plain'})
			if r.status_code != 200:
				logging.debug("Failed to POST data to API: "+r.reason)
		except Exception as e:
			logging.debug("Error when posting frame to MDroid Core: ")
			logging.debug(e)

# Decode frame
def getFrame():
	frame = dev.recv() # Receive a CAN frame
	#dev.send(frame) # Echo the CAN frame back out on the bus
	return [frame.id, frame.data]

if __name__ == "__main__":
	parseConfig() # overwrite defaults if necessary
	dev = cantact.CantactDev(DEVICE) # Connect to CANable that enumerated as ttyACM0
	dev.set_bitrate(500000) # Set the bitrate to a 500kbps
	dev.start() # Go on the bus

	while True:
		id, data = getFrame()
		logging.info(str(id)+" ("+str(hex(id))+"): "+str(data))

		if id in handlers:
			decodedValues = handlers[id](data)
			logging.info(decodedValues)
			if LOGGING_ADDRESS and decodedValues: 
				logFrame(decodedValues)
		else:
			logging.debug("Unknown ID "+str(id)+" ("+str(hex(id))+")")

		print('\n')