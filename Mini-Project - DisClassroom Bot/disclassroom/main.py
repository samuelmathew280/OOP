#_______________________IMPORTING DISCORD.PY LIBRARIES_____________________#
from functools import reduce
import discord
from discord.ext import commands, tasks
from discord.ext.commands import *
#_______________________IMPORTING PYRDRIVE LIBRARIES_____________________#
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
#_______________________IMPORTING OTHER LIBRARIES_____________________#
from collections import*
from datetime import datetime, timedelta
from datetime import date
from dateutil import relativedelta as rdelta
import pytz
import time
import re
from colorama import init
from termcolor import colored
#_______________________IMPORTING PROJECT FILES_____________________#
from variables import *
import backgroundTasks
import events
import commandsTeachers
import commandsStudents
import commandsAdmin  
from utilFunctions import *

#__________________________INTENTS ENABLED__________________________#
intents = discord.Intents.default()
intents.members = True
intents.bans = True
#client = commands.Bot(command_prefix='c!', help_command=None, intents=intents)
init() #colorama

#____________________GOOGLE DRIVE AUTHENTICATION____________________#
gauth = GoogleAuth()
# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.CommandLineAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")
drive = GoogleDrive(gauth)

#_______________________MYSQL_____________________#
import mysql.connector

myDB = mysql.connector.connect(
    host = 'localhost',               # Locally hosted database, not on a web server
    user = 'root',
    password = 'password',                    # Password for locally hosted database
    database = 'disclassroom'         # Select pre-existing database
)
# Create cursor instance
myCursor = myDB.cursor(buffered=True)   # The buffered = True is required because when you use "fetchone", the cursor actually fetches all the results and only shows you the 1st one.
                                        # Meaning the results are "lazily" loaded. If you try using fetchall right after that, it will complain or show an error saying "Unread result found".
                                        # Meaning, that there are still (n-1) results that were loading which weren't read
                                        # This problem is solved with a buffered cursor that loads ALL the rows behind the scenes, but only takes one from the connector, so MySQL won't show an error

#__________________________ON STARTUP__________________________#
class MyClient(commands.Bot):
    def __init__(self, command_prefix, help_command, *args, **kwargs):
        super().__init__(command_prefix, help_command, *args, **kwargs)
        # start the task to run in the background
        self.loop.create_task(self.startup())

    async def on_ready(self):
        print(colored("{0} is now online.".format(self.user), 'green'))

    async def startup(self):
        await self.wait_until_ready()
        self.add_cog(backgroundTasks.Tasks(client, myDB, myCursor))
        self.add_cog(events.onEvents(client, myDB, myCursor))
        self.add_cog(commandsTeachers.teacherCommands(client, myDB, myCursor, drive))
        self.add_cog(commandsStudents.studentCommands(client, myDB, myCursor, drive))
        self.add_cog(commandsAdmin.adminCommands(client, myDB, myCursor))

    # async def on_command_error(self, context, exception):
    #     pass

client = MyClient(command_prefix = 'c!', help_command = None, intents=intents)

#_______________________RUN BOT_____________________#
TOKEN = ''                  # Add bot's token in string; omitted for security.
client.run(TOKEN)