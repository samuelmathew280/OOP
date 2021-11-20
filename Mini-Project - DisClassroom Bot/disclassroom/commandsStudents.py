#_______________________IMPORTING DISCORD.PY LIBRARIES_____________________#
import discord
from discord.ext import commands
#_______________________IMPORTING OTHER LIBRARIES_____________________#
from datetime import datetime, timedelta
from datetime import date
from dateutil import relativedelta as rdelta
import re
#_______________________IMPORTING PROJECT FILES_____________________#
from variables import *
from utilFunctions import *
#__________________________COMMANDS___________________________#

class studentCommands(commands.Cog):
    def __init__(self, client, db, cursor, serverInfo):
        self.client = client
        self.myDB = db
        self.myCursor = cursor
        # [server, entryChannel, teachersChannel, announcementChannel, student, teacher, students, teachers]
        # [0,      1,            2,               3,                   4,       5,       6,        7]
        self.serverInfo = serverInfo

    @commands.command()
    async def submit(self, ctx):
        if ctx.guild != None:                                   # Command should only work in DMs
            return
        mutual_servers = ctx.author.mutual_guilds
        k = 0
        for i in mutual_servers:                                # Create a list with mutual servers' IDs
            mutual_servers[k] = i.id
            k+=1
        mutual_servers = tuple(mutual_servers)
        format_strings = ','.join(['%s'] * len(mutual_servers))                 # To create a string "%s, %s, %s ...." for the number of mutual servers
        self.myCursor.execute("SELECT assignmentID, serverID, subject, title, teacherID, assignmentLink, deadline FROM assignments WHERE serverID IN ({0}) ORDER BY deadline".format(format_strings), mutual_servers)
        allAssignments = self.myCursor.fetchall()                    # Get all assignments to the student from all mutual servers with the bot             
        pendingAssignments = []
        for i in allAssignments:
            tableName = "assgn" + str(i[0])
            self.myCursor.execute("SELECT submitted FROM {0} WHERE studentID = {1}".format(tableName, ctx.author.id))
            entry = self.myCursor.fetchone()
            if entry == None:
                continue
            if entry[0] == '0':                   # If assignment hasn't been submitted by user yet, it is added to the pending assignments
                pendingAssignments.append(i)
        if len(pendingAssignments) == 0:
            embed = discord.Embed(description = 'Hurray! No pending classwork.', 
                                  color = default_color)
            await ctx.send(embed = embed)
            return
        embed = discord.Embed(title = "Pick one of the assignments, by typing the corresponding number.",
                            description = '**#  |  Subject  |      Title      |  Teacher  |  Deadline**\n', 
                            color = default_color)
        k = 0
        for i in pendingAssignments:
            deadlineObj = toggleTimeAndString(i[6])
            deadlineDisplay = datetime.strftime(deadlineObj, "%I:%M %p %d/%m/%y")
            embed.description += "{0}  | {1} | [{2}]({3}) | <@{4}> | {5}\n".format(str(k+1).zfill(len(pendingAssignments)), i[2], i[3], i[5], i[4], deadlineDisplay)
            k+=1 
        await ctx.send(embed=embed)                             # Display all pending assignments
        def check(m):
            try:
                return int(m.content) in range(1, len(pendingAssignments)+1) and m.channel == ctx.channel
            except:
                return

        msg = await self.client.wait_for('message', check=check)     # Accept input to select which pending assignment to submit
        choice = int(msg.content)
        assgnToSubmit = pendingAssignments[choice-1]
        embed = discord.Embed(description = "Upload all your submissions as attachments below. Type `c!confirm` once you've done so.", color = default_color)
        await ctx.send(embed = embed)
        submissions = []
        filenames = []
        while 1:                                                # Keeps reading messages for attachments until c!confirm is typed
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author
            msg = await self.client.wait_for('message', check=check)
            if msg.content == 'c!confirm':
                break
            if msg.attachments != None and msg.attachments != []:
                for i in msg.attachments:
                    submissions.append(i.url)
                    filenames.append(i.filename)
        if submissions != []:
            embed = discord.Embed(description = "Are you sure you want to submit?\nYour attachments:\n", color = default_color)
            k = 0
            for i in submissions:                               # Print all the attachments to submit, for the user to confirm
                embed.description += "[{0}]({1})\n".format(filenames[k], i)
                k+=1
            embed.description += "\n**Type Yes/No to confirm.**"
        else:                                                   # If submissions is empty, it means user didn't provide any attachments and typed "c!confirm"
            embed = discord.Embed(description = "Are you sure you want to submit? You have added no attachments, so the assignment will be simply marked as done.\n**Type Yes/No to confirm.**", color = default_color)
        await ctx.send(embed = embed)
        def check(m):
            return (m.content.lower() == 'yes' or m.content.lower() == 'no') and m.channel == ctx.channel and m.author == ctx.author
        msg = await self.client.wait_for('message', check=check)
        if msg.content.lower() == 'no':                         # User inputted "No", hence cancelling the submission
            embed = discord.Embed(description = "Submission aborted. Try re-submitting.", color = red)
            await ctx.send(embed = embed)
            return
        tableName = "assgn" + str(assgnToSubmit[0])
        localTime = datetime.now(IST)
        deadline = toggleTimeAndString(assgnToSubmit[6])
        remainingTime = rdelta.relativedelta(deadline, localTime)
        if remainingTime.minutes < 0:
            submittedLate = '1'
        else:
            submittedLate = '0'
        submissions_string = ', '.join(submissions)
        sqlUpdate = "UPDATE {0} SET submissions = '{1}', submissionTime = '{2}', submitted = '1', submittedLate = '{3}' WHERE studentID = {4}".format(tableName, submissions_string, toggleTimeAndString(localTime), submittedLate, ctx.author.id)
        self.myCursor.execute(sqlUpdate)
        self.myDB.commit()
        embed = discord.Embed(description = "Submission successful and assignment marked as done!", color = default_color)
        await ctx.send(embed = embed)

    @commands.command()
    async def view(self, ctx, arg2):
        if arg2.strip().lower() == 'all' or arg2.strip().lower() == 'pending':
            if ctx.guild != None:                                   # Command should only work in DMs
                return
            mutual_servers = ctx.author.mutual_guilds
            k = 0
            for i in mutual_servers:                                # Create a list with mutual servers' IDs
                mutual_servers[k] = i.id
                k+=1
            mutual_servers = tuple(mutual_servers)
            format_strings = ','.join(['%s'] * len(mutual_servers))                 # To create a string "%s, %s, %s ...." for the number of mutual servers
            self.myCursor.execute("SELECT assignmentID, serverID, subject, title, teacherID, assignmentLink, deadline FROM assignments WHERE serverID IN ({0}) ORDER BY deadline".format(format_strings), mutual_servers)
            allAssignments = self.myCursor.fetchall()                    # Get all assignments to the student from all mutual servers with the bot             
            pendingAssignments = []
            for i in allAssignments:
                tableName = "assgn" + str(i[0])
                self.myCursor.execute("SELECT submitted FROM {0} WHERE studentID = {1}".format(tableName, ctx.author.id))
                if self.myCursor.fetchone()[0] == '0':                   # If assignment hasn't been submitted by user yet, it is added to the pending assignments
                    pendingAssignments.append(i)
            k = 0
            if arg2.strip().lower() == 'all':
                for i in allAssignments:
                    embed = discord.Embed(title = "All assignments.",
                                description = '**#  |  Subject  |      Title      |  Teacher  |  Deadline**\n', 
                                color = default_color)
                    embed.description += "{0}  | {1} | [{2}]({3}) | <@{4}> | {5}\n".format(str(k+1).zfill(len(pendingAssignments)), i[2], i[3], i[5], i[4], i[6])
                    k+=1
            elif arg2.strip().lower() == 'pending':
                if len(pendingAssignments) == 0:
                    embed = discord.Embed(description = 'Hurray! No pending classwork.', 
                                        color = default_color)
                    await ctx.send(embed = embed)
                    return
                for i in pendingAssignments:
                    embed = discord.Embed(title = "Pending assignments.",
                                description = '**#  |  Subject  |      Title      |  Teacher  |  Deadline**\n', 
                                color = default_color)
                    embed.description += "{0}  | {1} | [{2}]({3}) | <@{4}> | {5}\n".format(str(k+1).zfill(len(pendingAssignments)), i[2], i[3], i[5], i[4], i[6])
                    k+=1 
            await ctx.send(embed=embed)                             # Display all pending assignments
        else:
            embed = discord.Embed(description = 'Type `c!help view` for help with this command.', 
                                        color = default_color)
            await ctx.send(embed = embed)