#_______________________IMPORTING DISCORD.PY LIBRARIES_____________________#
from typing_extensions import _AnnotatedAlias
import discord
from discord.ext import commands
#_______________________IMPORTING OTHER LIBRARIES_____________________#
import asyncio
from datetime import datetime, timedelta
from datetime import date
from dateutil import relativedelta as rdelta
import re
import os
import time
#_______________________IMPORTING PROJECT FILES_____________________#
from variables import *
from utilFunctions import *
#__________________________COMMANDS___________________________#

class studentCommands(commands.Cog):
    def __init__(self, client, db, cursor, drive):
        self.client = client
        self.myDB = db
        self.myCursor = cursor
        self.drive = drive

    # Returns a list with all mutual servers' IDs only if the user is a Student in one of them and the bot is fully configured for that server. Otherwise, returns False.
    async def getAllMutualServerIDs(self, ctx):
        mutual_servers = ctx.author.mutual_guilds
        k = 0
        student = False
        for i in mutual_servers:
            self.myCursor.execute("SELECT configured, studentRoleID FROM servers WHERE serverID = {0}".format(i.id))
            record = self.myCursor.fetchone()
            if record is None:
                continue
            if record[0] != 'True':
                continue
            member = await i.fetch_member(ctx.author.id)
            for j in member.roles:
                if j.id == int(record[1]):
                    student = True
            mutual_servers[k] = i.id
            k+=1
        if student == True:
            mutual_servers = tuple(mutual_servers)
            return mutual_servers
        else:
            return False

    # Function to pull pending assignments or already submitted assignments, from all mutual servers, select one, and to submit/resubmit it.
    async def submitAssignment(self, ctx, mutual_servers, option):                  # Option 1 = Submit, Option 2 = Resubmit
        format_strings = ','.join(['%s'] * len(mutual_servers))                 # To create a string "%s, %s, %s ...." for the number of mutual servers
        self.myCursor.execute("SELECT assignmentID, serverID, subject, title, teacherID, assignmentLink, deadline FROM assignments WHERE serverID IN ({0}) ORDER BY deadline".format(format_strings), mutual_servers)
        allAssignments = self.myCursor.fetchall()                    # Get all assignments to the student from all mutual servers with the bot             
        assignmentOptions = []
        submissions = []
        for i in allAssignments:
            tableName = "assgn" + str(i[0])
            self.myCursor.execute("SELECT submitted, submissions FROM {0} WHERE studentID = {1}".format(tableName, ctx.author.id))
            entry = self.myCursor.fetchone()
            if entry == None:
                continue
            if option == 1:
                if entry[0] == '0':                   # If assignment hasn't been submitted by user yet, it is added to the pending assignments
                    assignmentOptions.append(i)
            elif option == 2:
                if entry[0] != '0':                   # If assignment has been submitted by user, it is added to the submitted assignments
                    assignmentOptions.append(i)
                    submissions.append(entry[1])
        if len(assignmentOptions) == 0:
            if option == 1:
                embed = discord.Embed(description = 'Hurray! No pending classwork.', 
                                    color = default_color)
            elif option == 2:
                embed = discord.Embed(description = 'No submitted assignment yet.', 
                                    color = default_color)
            await ctx.send(embed = embed)
            return
        embed = discord.Embed(title = "Pick one of the assignments, by typing the corresponding number.",
                            description = '**#  |  Subject  |      Title      |  Teacher  |  Deadline**\n', 
                            color = default_color)
        k = 0
        for i in assignmentOptions:
            if i[6] is not None:
                deadlineObj = toggleTimeAndString(i[6])
                deadlineDisplay = datetime.strftime(deadlineObj, "%I:%M %p %d/%m/%y")
            else:
                deadlineDisplay = "`None`"
            embed.description += "`{0}`  | {1} | [{2}]({3}) | <@{4}> | {5}\n".format(str(k+1).zfill(len(str(len(assignmentOptions)))), i[2], i[3], i[5], i[4], deadlineDisplay)
            k+=1 
        await ctx.send(embed=embed)                             # Display all pending/submitted assignments
        def check(m):
            try:
                return int(m.content) in range(1, len(assignmentOptions)+1) and m.channel == ctx.channel
            except:
                return
        try:
            msg = await self.client.wait_for('message', check=check, timeout = 300.0)     # Accept input to select which assignment to submit
        except asyncio.TimeoutError:
            return
        choice = int(msg.content)
        assgnToSubmit = assignmentOptions[choice-1]
        if option == 2:
            embed = discord.Embed(title = "Previously submitted work", description = '', color = default_color)
            submissionIDs = submissions[choice-1].split(', ')
            for j in submissionIDs:
                file = self.drive.CreateFile({"id": j})
                file.FetchMetadata(fields='id,title')
                embed.description += ":small_orange_diamond: [{0}]({1})\n".format(file['title'], "https://drive.google.com/file/d/" + j + "/view?usp=sharing")
            embed.description += "\nType **Yes** to unsubmit the previous work and re-submit or\nType **No** to cancel."
            await ctx.send(embed = embed)
            def check(m):
                return (m.content.lower() == 'yes' or m.content.lower() == 'no') and m.channel == ctx.channel and m.author == ctx.author
            msg = await self.client.wait_for('message', check=check)
            if msg.content.lower() == 'no':
                embed = discord.Embed(description = 'Submission cancelled.', 
                                    color = red)
                await ctx.send(embed = embed)
                return
        embed = discord.Embed(description = "Upload all your submissions as attachments below. Type `c!confirm` once you've done so.", color = default_color)
        await ctx.send(embed = embed)
        submissionIDs = []
        filenames = []
        while 1:                                                # Keeps reading messages for attachments until c!confirm is typed
            def check(m):
                return m.channel == ctx.channel and m.author == ctx.author
            msg = await self.client.wait_for('message', check=check)
            if msg.content == 'c!confirm':
                break
            if msg.attachments != None and msg.attachments != []:
                for i in msg.attachments:
                    fileName = re.sub('_', ' ', i.filename)
                    filenames.append(fileName)
                    # Uploading to Google Drive and obtaining ID
                    path = "/home/sam/OOP/Mini-Project - DisClassroom Bot"
                    await i.save(path + '\\' + i.filename)
                    file = self.drive.CreateFile({"title" : fileName,
                                                  "parents": [{"id": folder_id}]})
                    file.SetContentFile(path + '\\' + i.filename)
                    file.Upload()
                    file.InsertPermission({"role" : "reader", 
                                            "type" : "anyone",
                                            "additionalRoles" : ['commenter']})
                    submissionIDs.append(file.metadata['id'])
                    file.content.close()
                    try:
                        os.remove(path + '\\' + i.filename)
                    except:
                        pass
        if submissionIDs != []:
            embed = discord.Embed(description = "Are you sure you want to submit?\nYour attachments:\n", color = default_color)
            k = 0
            for i in submissionIDs:                               # Print all the attachments to submit, for the user to confirm
                embed.description += "[{0}]({1})\n".format(filenames[k], "https://drive.google.com/file/d/" + i + "/view?usp=sharing")
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
        if submissionIDs != []:
            submissions_string = ', '.join(submissionIDs)
            sqlUpdate = "UPDATE {0} SET submissions = '{1}', submissionTime = '{2}', submitted = '1', submittedLate = '{3}' WHERE studentID = {4}".format(tableName, submissions_string, toggleTimeAndString(localTime), submittedLate, ctx.author.id)
        else:
            sqlUpdate = "UPDATE {0} SET submissionTime = '{1}', submitted = '1', submittedLate = '{2}' WHERE studentID = {3}".format(tableName, toggleTimeAndString(localTime), submittedLate, ctx.author.id)
        self.myCursor.execute(sqlUpdate)
        self.myDB.commit()
        embed = discord.Embed(description = "Submission successful and assignment marked as done!", color = default_color)
        await ctx.send(embed = embed)

    @commands.command()
    async def submit(self, ctx):
        if ctx.guild != None:                                   # Command should only work in DMs
            return
        mutual_servers = await self.getAllMutualServerIDs(ctx)
        if mutual_servers == False:                             # Meaning either the bot is not configured for the server(s) the user is in or the user is not a Student in the server(s) where the bot is present
            return
        await self.submitAssignment(ctx, mutual_servers, 1)

    @commands.command()
    async def resubmit(self, ctx):
        if ctx.guild != None:                                   # Command should only work in DMs
            return
        mutual_servers = await self.getAllMutualServerIDs(ctx)
        if mutual_servers == False:                             # Meaning either the bot is not configured for the server(s) the user is in or the user is not a Student in the server(s) where the bot is present
            return
        await self.submitAssignment(ctx, mutual_servers, 2)

    # Command to view all/pending assignments
    @commands.command()
    async def view(self, ctx, arg2 = 'all'):
        if arg2.strip().lower() == 'all' or arg2.strip().lower() == 'pending':
            if ctx.guild != None:                                   # Command should only work in DMs
                return
            mutual_servers = await self.getAllMutualServerIDs(ctx)
            if mutual_servers == False:                             # Meaning either the bot is not configured for the server(s) the user is in or the user is not a Student in the server(s) where the bot is present
                return
            format_strings = ','.join(['%s'] * len(mutual_servers))                 # To create a string "%s, %s, %s ...." for the number of mutual servers
            self.myCursor.execute("SELECT assignmentID, serverID, subject, title, teacherID, assignmentLink, deadline, deadlineOver FROM assignments WHERE serverID IN ({0}) ORDER BY deadline".format(format_strings), mutual_servers)
            allAssignments = self.myCursor.fetchall()                    # Get all assignments to the student from all mutual servers with the bot             
            pendingAssignments = []
            for i in allAssignments:
                tableName = "assgn" + str(i[0])
                self.myCursor.execute("SELECT submitted, submissions FROM {0} WHERE studentID = {1}".format(tableName, ctx.author.id))
                record = self.myCursor.fetchone()
                if record[0] == '0':                   # If assignment hasn't been submitted by user yet, it is added to the pending assignments
                    pendingAssignments.append(i)
            k = 0
            if arg2.strip().lower() == 'all':
                embed = discord.Embed(title = "All assignments.",
                                description = '**#  |  Subject  |      Title      |  Teacher  |  Deadline  |  Submitted**\n', 
                                color = default_color)
                for i in allAssignments:
                    if i[6] is not None:
                        convertedTime = (datetime.strptime(i[6], defaultTimeFormat)).replace(tzinfo=IST)
                        convertedString = (datetime.strftime(convertedTime, "%I:%M %p IST, %B %d, %Y"))
                    else:
                        convertedString = "`None`"
                    if i in pendingAssignments:
                        embed.description += "`{0}`  | {1} | [{2}]({3}) | <@{4}> | {5} | :x:".format(str(k+1).zfill(len(str(len(allAssignments)))), i[2], i[3], i[5], i[4], convertedString)
                    else:
                        embed.description += "`{0}`  | {1} | [{2}]({3}) | <@{4}> | {5} | :white_check_mark:".format(str(k+1).zfill(len(str(len(allAssignments)))), i[2], i[3], i[5], i[4], convertedString)
                    k+=1
                    embed.description += "\n"
                embed.description += "\nType the corresponding number to get more details about the assignment."
                await ctx.send(embed = embed)
                def check(m):
                    try:
                        return int(m.content) in range(1, len(allAssignments)+1) and m.channel == ctx.channel
                    except:
                        return
                try:
                    msg = await self.client.wait_for('message', check=check, timeout = 100.0)     # Accept input to select which assignment to view
                except asyncio.TimeoutError:
                    return
                choice = int(msg.content)
                selectedAssignment = allAssignments[choice-1]
                                #  = [assignmentID, serverID, subject, title, teacherID, assignmentLink, deadline, deadlineOver]
                assignmentID = selectedAssignment[0]
                tableName = "assgn" + str(assignmentID)
                self.myCursor.execute("SELECT submissions, submissionTime, submitted, submittedLate, marks FROM {0} WHERE studentID = {1}".format(tableName, ctx.author.id))
                record = self.myCursor.fetchone()
                embed = discord.Embed(title = ':pencil: Assignment details',
                                      description = '**[{0}]({1})**'.format(selectedAssignment[3], selectedAssignment[5]))
                # Assigning the embed color
                if record[2] != '0' and record[3] == '0':       # If assignment submitted AND done on time
                    embed.color = green
                    submitted = True
                elif record[2] != '0' and record[3] != '0':     # If assignment submitted AND done late
                    embed.color = lightRed
                    submitted = True
                elif record[2] == '0' and selectedAssignment[7] == '0':     # If assignment not submitted AND deadline is over aka "Missing"
                    embed.color = red
                    submitted = False
                else:
                    embed.color = default_color
                    submitted = False
                # Creating embed fields
                embed.add_field(name = "Subject", value = selectedAssignment[2])
                embed.add_field(name = "Professor", value = "<@"+str(selectedAssignment[4])+">")
                server = self.client.get_guild(int(selectedAssignment[1]))
                embed.add_field(name = "Server", value = server.name)
                if record[1] is not None:
                    embed.add_field(name = "Submission time", value = beautifyTimeString(record[1]))
                else:
                    embed.add_field(name = "Submission time", value = "`None`")
                if selectedAssignment[6] is not None:
                    embed.add_field(name = "Deadline", value = beautifyTimeString(selectedAssignment[6]))
                else:
                    embed.add_field(name = "Deadline", value = '`None`')
                if selectedAssignment[7] == '0':
                    embed.add_field(name = "Deadline over", value = "No")
                else:
                    embed.add_field(name = "Deadline over", value = "Yes")
                if record[0] is not None:
                    submissionIDs = record[0].split(', ')
                    submissionString = ''
                    for i in submissionIDs:
                        file = self.drive.CreateFile({"id": i})
                        file.FetchMetadata(fields='id,title')
                        submissionString += ":small_orange_diamond: [{0}]({1})\n".format(file['title'], "https://drive.google.com/file/d/" + i + "/view?usp=sharing")
                    embed.add_field(name = "Submissions", value = submissionString, inline = False)
                else:
                    embed.add_field(name = "Submissions", value = '`<None>`', inline = True)
                if record[4] is not None:
                    embed.add_field(name = "Marks", value = str(record[4]))
                timeChecks = ''
                if submitted == False:
                    timeChecks += ":x: Submitted"
                else:
                    timeChecks += ":white_check_mark: Submitted\n"
                    if record[3] != '0':
                        timeChecks += ":x: Submitted on time"
                    else:
                        timeChecks += ":white_check_mark: Submitted on time"
                embed.add_field(name = "Checks", value = timeChecks)
                await ctx.send(embed = embed)

            elif arg2.strip().lower() == 'pending':
                if len(pendingAssignments) == 0:
                    embed = discord.Embed(description = 'Hurray! No pending classwork.', 
                                        color = default_color)
                    await ctx.send(embed = embed)
                    return
                embed = discord.Embed(title = "Pending assignments.",
                                description = '**#  |  Subject  |      Title      |  Teacher  |  Deadline**\n', 
                                color = default_color)
                for i in pendingAssignments:
                    if i[6] is not None:
                        convertedTime = (datetime.strptime(i[6], defaultTimeFormat)).replace(tzinfo=IST)
                        convertedString = (datetime.strftime(convertedTime, "%I:%M %p IST, %B %d, %Y"))
                    else:
                        convertedString = "`None`"
                    embed.description += "`{0}`  | {1} | [{2}]({3}) | <@{4}> | {5}\n".format(str(k+1).zfill(len(str(len(pendingAssignments)))), i[2], i[3], i[5], i[4], convertedString)
                    k+=1 
                await ctx.send(embed=embed)                             # Display all pending assignments
        else:
            embed = discord.Embed(description = 'Type `c!help view` for help with this command.', 
                                        color = default_color)
            await ctx.send(embed = embed)