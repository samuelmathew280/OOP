#_______________________IMPORTING DISCORD.PY LIBRARIES_____________________#
import discord
from discord.ext import commands, tasks
from discord.ext.commands import *
#_______________________IMPORTING PROJECT FILES_____________________#
from variables import *
from utilFunctions import *
#______________________________ON EVENT_____________________________#
class Tasks(commands.Cog):
    def __init__(self, client, myDB, myCursor):
        self.client = client
        self.myDB = myDB
        self.myCursor = myCursor
        self.reminders.start()
        # serverInfo
        # [server, entryChannel, announcementsChannel, teacherChannel, student, teacher, students, teachers]
        # [0,      1,            2,                    3,              4,       5,       6,        7]

    @tasks.loop()
    async def reminders(self):
        self.myCursor.execute("SELECT deadlineReminder, isReminder, deadline, assignmentID, subject, title, assignmentLink FROM assignments WHERE deadlineOver = '0' AND deadline != 'NULL' ORDER BY deadlineReminder")
        next_task = self.myCursor.fetchone()
        print(next_task)
        # if no remaining tasks, stop the loop
        if next_task is None:
            print("Task stopped")
            self.reminders.cancel()
            return
        else:
            # sleep until the task should be done
            await discord.utils.sleep_until(toggleTimeAndString(next_task[0]))

            # once next_task's end time has been reached
            if next_task[1] == "True":
                print("Reminder for assignment")
                self.myCursor.execute("UPDATE assignments SET deadlineReminder = '{0}', isReminder = 'False' WHERE assignmentID = {1}".format(next_task[2], next_task[3]))
                self.myDB.commit()
                tableName = "assgn" + str(next_task[3])
                self.myCursor.execute("SELECT studentID FROM {0} WHERE submitted = '0'".format(tableName))
                allPendingStudents = self.myCursor.fetchall()
                difference = toggleTimeAndString(next_task[2]) - toggleTimeAndString(next_task[0])
                print(allPendingStudents, difference)
                for i in allPendingStudents:
                    user = self.client.get_user(i[0])
                    if difference.days == 1:
                        embed = discord.Embed(description = "**Due tomorrow:** [{0} - {1}]({2}).".format(next_task[4], next_task[5], next_task[6]), color = red)
                    elif difference.seconds == 3600:
                        embed = discord.Embed(description = "**Due in an hour:** [{0} - {1}]({2}).".format(next_task[4], next_task[5], next_task[6]), color = red)
                    try:
                        await user.send(embed = embed)
                    except:
                        pass
            else:
                print("Deadline for assignment reached")
                self.myCursor.execute("UPDATE assignments SET deadlineOver = 'True' WHERE assignmentID = {0}".format(next_task[3]))
                self.myDB.commit()

    @reminders.before_loop
    async def before_reminders(self):
        await self.client.wait_until_ready() # wait until the bot logs in