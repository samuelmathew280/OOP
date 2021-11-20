from datetime import datetime, timedelta
from variables import *

# Utility function to convert datetime object to string (hh:mm DD/MM/YY) or vice-versa, depending on type of parameter
def toggleTimeAndString(sampleTime):
    if isinstance(sampleTime, datetime):
        convertedString = (datetime.strftime(sampleTime, defaultTimeFormat))
        return convertedString
    elif isinstance(sampleTime, str):
        convertedTime = (datetime.strptime(sampleTime, defaultTimeFormat)).replace(tzinfo=IST)
        return convertedTime

# Convert time string (hh:mm DD/MM/YY) to a better formatted string
def beautifyTimeString(timeString):
    convertedTime = (datetime.strptime(timeString, defaultTimeFormat)).replace(tzinfo=IST)
    convertedString = (datetime.strftime(convertedTime, "%B %d, %Y,\n%I:%M %p IST"))
    return convertedString