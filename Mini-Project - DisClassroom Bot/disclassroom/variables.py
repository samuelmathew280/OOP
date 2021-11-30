from datetime import datetime
import pytz
#_______________________PRE-DEFINED VARIABLES_______________________#
IST = pytz.timezone("Asia/Kolkata")
IST = IST.localize(datetime(2012, 7, 10, 12, 0))    # To get IST
IST = IST.tzinfo                            # Indian Standard Time (+5:30 GMT)
default_color = 0xe6ddc4
blue = 0x1da1f2
red = 0xd10000
lightRed = 0xFD4D4D
green = 0x2bcf6d
defaultTimeFormat = "%Y-%m-%d %H:%M:%S.%f%z"
folder_id = '1EtAcUxgBJwB1dZZ7w-A2M2JS0cSOH_Zd'     # Google Drive folder