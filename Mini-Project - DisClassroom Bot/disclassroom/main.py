#_______________________IMPORTING DISCORD.PY LIBRARIES_____________________#
from functools import reduce
import discord
from discord.ext import commands, tasks
from discord.ext.commands import *
#___________________IMPORTING GOOGLE API WRAPPER LIBRARIES______ __________#
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#_______________________IMPORTING OTHER LIBRARIES_____________________#
from collections import*
from datetime import datetime, timedelta
from datetime import date
from dateutil import relativedelta as rdelta
import pytz
import pprint
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

#____________________GOOGLE DRIVE AND SHEETS AUTHENTICATION____________________#
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
json_keyfile_path = "beaming-caster-333210-e65124f45536.json"
#Read the service account key
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    json_keyfile_path, scope)
#Authenticate for gspread
gc = gspread.authorize(credentials)

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
from mysql.connector.errors import *

myDB = mysql.connector.connect(
    host = 'localhost',               # Locally hosted database, not on a web server
    user = 'sam',
    password = 'password',            # Password for locally hosted database
    database = 'disclassroom'         # Select pre-existing database
)

# Create cursor instance
myCursor = myDB.cursor(buffered=True)   # The buffered = True is required because when you use "fetchone", the cursor actually fetches all the results and only shows you the 1st one.
                                        # Meaning the results are "lazily" loaded. If you try using fetchall right after that, it will complain or show an error saying "Unread result found".
                                        # Meaning, that there are still (n-1) results that were loading which weren't read
                                        # This problem is solved with a buffered cursor that loads ALL the rows behind the scenes, but only takes one from the connector, so MySQL won't show an error
myCursor.execute('SET GLOBAL wait_timeout = 31535999')

#________________________CREATE CLIENT_________________________#
class MyClient(commands.Bot):
    def __init__(self, command_prefix, help_command, *args, **kwargs):
        super().__init__(command_prefix, help_command, *args, **kwargs)
        # start the task to run in the background
        self.loop.create_task(self.startup())
        self.keepDBAlive.start()

    async def on_ready(self):
        print(colored("{0} is now online.".format(self.user), 'green'))

    # Function is invoked when the bot starts up
    async def startup(self):
        await self.wait_until_ready()
        self.add_cog(backgroundTasks.Tasks(self, myDB, myCursor))
        self.add_cog(events.onEvents(self, myDB, myCursor, gc))
        self.add_cog(commandsTeachers.teacherCommands(self, myDB, myCursor, drive, gc))
        self.add_cog(commandsStudents.studentCommands(self, myDB, myCursor, drive))
        self.add_cog(commandsAdmin.adminCommands(self, myDB, myCursor))

    # Function to unload and then re-load cogs, to instance variables for cog objects
    def refreshCogs(self, myDB, myCursor):
        self.remove_cog('Tasks')
        self.remove_cog('Events')
        self.remove_cog('teacherCommands')
        self.remove_cog('studentCommands')
        self.remove_cog('adminCommands')
        self.add_cog(backgroundTasks.Tasks(self, myDB, myCursor))
        self.add_cog(events.onEvents(self, myDB, myCursor, gc))
        self.add_cog(commandsTeachers.teacherCommands(self, myDB, myCursor, drive, gc))
        self.add_cog(commandsStudents.studentCommands(self, myDB, myCursor, drive))
        self.add_cog(commandsAdmin.adminCommands(self, myDB, myCursor))

    # Loop to ensure that connection with database isn't lost
    @tasks.loop(seconds = 28700.0)
    async def keepDBAlive(self):
        try:
            global myCursor
            myCursor.execute('SELECT assignmentID FROM assignments')
            results = myCursor.fetchall()
        except:
            myDB = mysql.connector.connect(
                host = 'localhost',
                user = 'sam',
                password = 'password',
                database = 'disclassroom'
            )
            # Create cursor instance
            newCursor = myDB.cursor(buffered=True)
            self.refreshCogs(myDB, newCursor)

    @keepDBAlive.before_loop
    async def before_keepDBAlive(self):
        await self.wait_until_ready() # wait until the bot logs in

    # Handling exceptions when an error while invoking a command or in the process of using a command occurs
    async def on_command_error(self, context, exception):
        if hasattr(exception, 'original'):
            if isinstance(exception.original, DatabaseError):
                print("MySQL database error detected")
                # DatabaseError (4031) : The client was disconnected by the server because of inactivity. See wait_timeout and interactive_timeout for configuring this behavior.
                if exception.original.errno == 4031:
                    myDB = mysql.connector.connect(
                        host = 'localhost',
                        user = 'sam',
                        password = 'password',
                        database = 'disclassroom'
                    )
                    # Create cursor instance
                    myCursor = myDB.cursor(buffered=True)
                    self.refreshCogs(myDB, myCursor)
                    embed = discord.Embed(description = "Internal database error occured. Kindly retry the command.", color = red)
                    await context.send(embed = embed)
        elif isinstance(exception, CommandNotFound):
            if context.message.content.strip() == 'c!confirm':
                pass
            else:
                print(context)
                print(type(exception), exception)   
        else:
            print(context)
            print(type(exception), exception)

client = MyClient(command_prefix = 'c!', help_command = None, intents=intents)

#_______________________RUN BOT_____________________#
TOKEN = ''                  # Add bot's token in string; omitted for security.
client.run(TOKEN)