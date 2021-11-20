from datetime import datetime
import pytz
#_______________________PRE-DEFINED VARIABLES_______________________#
IST = pytz.timezone("Asia/Kolkata")
IST = IST.localize(datetime(2012, 7, 10, 12, 0))    # To get IST
IST = IST.tzinfo                            # Indian Standard Time (+5:30 GMT)
default_color = 0xe6ddc4
blue = 0x1da1f2
red = 0xd10000
studentID = "903552048811888650"
teacherID = "903551848378683403"
defaultTimeFormat = "%Y-%m-%d %H:%M:%S.%f%z"