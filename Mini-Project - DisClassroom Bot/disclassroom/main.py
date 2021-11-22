#_______________________IMPORTING DISCORD.PY LIBRARIES_____________________#
from functools import reduce
import discord
from discord.ext import commands, tasks
from discord.ext.commands import *
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

#_______________________UTILITY FUNCTIONS_______________________#
def getChannel(arg):                    #PASS CHANNEL MENTION STRING, GET CHANNEL OBJECT
    channel_id = re.sub("[^0-9]", "", arg)
    channel = client.get_channel(int(channel_id))
    return channel

def getRole(guild, arg):                #PASS CHANNEL MENTION STRING, GET CHANNEL OBJECT
    role_id = re.sub("[^0-9]", "", arg)
    role = guild.get_role(int(role_id))
    return role

#__________________________ON STARTUP__________________________#
class MyClient(commands.Bot):
    def __init__(self, command_prefix, help_command, *args, **kwargs):
        super().__init__(command_prefix, help_command, *args, **kwargs)
        # an attribute we can access from our task
        
        # start the task to run in the background
        self.loop.create_task(self.startup())
        self.reminders.start()

    async def on_ready(self):
        print(colored("{0} is now online.".format(self.user), 'green'))

    async def startup(self):
        await self.wait_until_ready()
        global server
        server = self.get_guild(903509643903512577)
        global entryChannel
        entryChannel = getChannel("910057428702339102")
        global teachersChannel
        teachersChannel = getChannel("910057586693398548")
        global announcementChannel
        announcementChannel = getChannel("910057532255514635")
        global student
        student = getRole(server, studentID)
        global students
        students = student.members
        global teacher
        teacher = getRole(server, teacherID)
        global teachers
        teachers = teacher.members
        global serverInfo
        serverInfo = [server, entryChannel, teachersChannel, announcementChannel, student, teacher, students, teachers]
        self.add_cog(events.onEvents(client, myDB, myCursor, serverInfo))
        self.add_cog(commandsTeachers.teacherCommands(client, myDB, myCursor, serverInfo))
        self.add_cog(commandsStudents.studentCommands(client, myDB, myCursor, serverInfo))
        self.add_cog(commandsAdmin.adminCommands(client, myDB, myCursor, serverInfo))

    @tasks.loop()
    async def reminders(self):
        # if you don't care about keeping records of old tasks, remove this WHERE and change the UPDATE to DELETE
        myCursor.execute("SELECT deadlineReminder, isReminder, deadline, assignmentID, subject, title, assignmentLink FROM assignments WHERE deadlineOver = '0' ORDER BY deadlineReminder")
        next_task = myCursor.fetchone()
        print(next_task)
        # if no remaining tasks, stop the loop
        if next_task is None:
            print("Task stopped")
            self.reminders.cancel()
            return
        else:
            # sleep until the task should be done
            # optionally create a new task that does the rest of this and
            # `create_task` that if it's within the next couple minutes, `await` it otherwise
            await discord.utils.sleep_until(toggleTimeAndString(next_task[0]) )

            # do your task stuff here with `next_task`
            if next_task[1] == "True":
                print("Reminder for assignment")
                myCursor.execute("UPDATE assignments SET deadlineReminder = '{0}', isReminder = 'False'".format(next_task[2]))
                myDB.commit()
                tableName = "assgn" + str(next_task[3])
                myCursor.execute("SELECT studentID FROM {0} WHERE submitted = '0'".format(tableName))
                allPendingStudents = myCursor.fetchall()
                difference = toggleTimeAndString(next_task[2]) - toggleTimeAndString(next_task[0])
                print(allPendingStudents, difference)
                for i in allPendingStudents:
                    user = client.get_user(i[0])
                    if difference.days == 1:
                        embed = discord.Embed(description = "**Due tomorrow:** [{0} - {1}]({2}).".format(next_task[4], next_task[5], next_task[6]), color = red)
                    elif difference.seconds == 3600:
                        embed = discord.Embed(description = "**Due in an hour:** [{0} - {1}]({2}).".format(next_task[4], next_task[5], next_task[6]), color = red)
                    
                    await user.send(embed = embed)
                    # except:
                    #     pass
            else:
                print("Deadline for assignment reached")
                myCursor.execute("UPDATE assignments SET deadlineOver = 'True'")
                myDB.commit()
            # await self.db_conn.execute('UPDATE tasks SET completed = true WHERE row_id = $1', next_task['row_id'])

    @reminders.before_loop
    async def before_reminders(self):
        await self.wait_until_ready() # wait until the bot logs in

    # async def on_command_error(self, context, exception):
    #     pass

client = MyClient(command_prefix = 'c!', help_command = None, intents=intents)

#_______________________RUN BOT_____________________#
TOKEN = ''                  # Add bot's token in string; omitted for security.
client.run(TOKEN)