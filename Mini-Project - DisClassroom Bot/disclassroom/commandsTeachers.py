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

class teacherCommands(commands.Cog):
    def __init__(self, client, db, cursor, serverInfo):
        self.client = client
        self.myDB = db
        self.myCursor = cursor
        # [server, entryChannel, teachersChannel, announcementChannel, student, teacher, students, teachers]
        # [0,      1,            2,               3,                   4,       5,       6,        7]
        self.serverInfo = serverInfo

    # Utility function to add assignment to database when "c!post assignment" is invoked
    async def addAssignment(self, subject, title, ctx, deadline):
        #####################################################
        ##             UPDATE ASSIGNMENTS TABLE            ##
        #####################################################
        if deadline != None:
            deadlineObj = toggleTimeAndString(deadline)
            localTime = datetime.now(IST)
            remainingTime = rdelta.relativedelta(deadlineObj, localTime)
            print(deadlineObj, localTime, remainingTime)
            if remainingTime.minutes<0 or remainingTime.seconds<0 or remainingTime.hours<0:
                embed= discord.Embed(description = 'Invalid input. Assignment deadline should not be before current time.', color = red)
                await ctx.send(embed = embed)
                return False
            if remainingTime.days>0:
                isReminder = True
                deadlineReminder = deadlineObj - timedelta(days = 1)
            elif remainingTime.hours>0:
                isReminder = True
                deadlineReminder = deadlineObj - timedelta(hours = 1)
            else:
                isReminder = False
                deadlineReminder = deadlineObj
            self.myCursor.execute("INSERT INTO assignments (serverID, subject, title, teacherID, hasDeadline, deadline, deadlineReminder, isReminder, postTime) VALUES ('{0.guild.id}', '{1}', '{2}', '{0.author.id}', 'True', '{3}', '{4}', '{5}', '{6}')".format(ctx, subject, title, toggleTimeAndString(deadlineObj), toggleTimeAndString(deadlineReminder), isReminder, toggleTimeAndString(ctx.message.created_at.astimezone(IST))))
            self.myDB.commit()
            self.myCursor.execute("SELECT assignmentID FROM assignments WHERE serverID = '{0}' AND subject = '{1}' AND postTime = '{2}'".format(ctx.guild.id, subject, toggleTimeAndString(ctx.message.created_at.astimezone(IST))))
            assignmentID = self.myCursor.fetchone()[0]
        else:
            self.myCursor.execute("INSERT INTO assignments (serverID, subject, title, teacherID, hasDeadline, postTime) VALUES ('{0.guild.id}', '{1}', '{2}', '{0.author.id}', 'False', '{3}')".format(ctx, subject, title, toggleTimeAndString(ctx.message.created_at.astimezone(IST))))
            self.myDB.commit()
            self.myCursor.execute("SELECT assignmentID FROM assignments WHERE serverID = '{0}' AND subject = '{1}' AND postTime = '{2}'".format(ctx.guild.id, subject, toggleTimeAndString(ctx.message.created_at.astimezone(IST))))
            assignmentID = self.myCursor.fetchone()[0]
        #####################################################
        ##            CREATE TABLE FOR ASSIGNMENT          ##
        #####################################################
        tableName = "assgn" + str(assignmentID)
        self.myCursor.execute("CREATE TABLE {0}(studentName VARCHAR(100), studentID BIGINT UNSIGNED PRIMARY KEY, serverID BIGINT UNSIGNED, submissions VARCHAR(1000), submissionTime VARCHAR(255), submitted VARCHAR(100) DEFAULT FALSE, submittedLate VARCHAR(100))".format(tableName))
        students = self.serverInfo[4].members
        for i in students:
            self.myCursor.execute("INSERT INTO {0} (studentName, studentID, serverID) VALUES ('{1.name}#{1.discriminator}', '{1.id}', '{2}')".format(tableName, i, ctx.guild.id))
        self.myDB.commit()
        return assignmentID

    # Command to post announcement, quiz, or assignment
    @commands.command()
    @commands.has_any_role(int(teacherID))
    async def post(self, ctx, arg1, *, arg2):
        member = ctx.guild.get_member(ctx.author.id)
        #####################################################
        ##                   ANNOUNCEMENT                  ##
        #####################################################
        if arg1.lower().strip() == 'announcement':
            # Obtaining the included parameters
            arg2 = ' ' + arg2.strip()
            if arg2.count(' -s ')<0 or arg2.count(' -d ')<0:
                embed = discord.Embed(description = 'Subject and description are required!', color = red)
                await ctx.send(embed=embed)
                return
            paramsList = re.findall(r" [-]['stdl'] ", arg2)
            params = ''
            for i in paramsList:
                params += i[2]
            print(arg2)
            # Obtaining the values for the present parameters
            myRegex = ' [-][' + params + '] '
            embedParts = re.split(myRegex, arg2)
            embedParts = embedParts[1:]
            print(embedParts)
            print(params)
            # Building embed using the parameters and their values
            embed = discord.Embed(color = member.roles[-1].color)
            k = 0
            embed.add_field(name = 'Professor', value = '{0}'.format(ctx.author.mention), inline = True)
            for i in params:
                if i == 's':
                    if params.count('t') == 0:
                        embed.title = '{0}'.format(embedParts[k])
                if i == 't':
                    subPos = params.index('s')
                    embed.title = '{0} - {1}'.format(embedParts[subPos], embedParts[k])
                if i == 'd':
                    embed.description = '{0}'.format(embedParts[k])
                if i == 'l':
                    embed.add_field(name = 'Link', value = '[Click here]({0})'.format(embedParts[k]), inline = False)
                k+=1
            if ctx.message.attachments != None and ctx.message.attachments != []:
                attach = ''
                for i in ctx.message.attachments:
                    attach+='[{0}]({1})\n'.format(i.filename, i.url)
                #attach -= '\n'
                embed.add_field(name = 'Attachments', value = attach, inline = False)
            await self.serverInfo[3].send(embed = embed)
        #####################################################
        ##                 ASSIGNMENT/QUIZ                 ##
        #####################################################
        elif arg1.lower().strip() == 'assignment' or arg1.lower().strip() == 'quiz':
            # Obtaining the included parameters
            arg2 = ' ' + arg2.strip()
            if arg2.count(' -s ')<0 or arg2.count(' -t ')<0 or arg2.count(' -d ')<0:
                embed = discord.Embed(description = 'Subject, title and description are required!', color = red)
                await ctx.send(embed=embed)
                return
            paramsList = re.findall(r" [-]['stdle'] ", arg2)
            params = ''
            for i in paramsList:
                params += i[2]
            print(arg2)
            # Obtaining the values for the present parameters
            myRegex = ' [-][' + params + '] '
            embedParts = re.split(myRegex, arg2)
            embedParts = embedParts[1:]
            print(embedParts)
            print(params)
            # Building embed using the parameters and their values
            embed = discord.Embed(color = member.roles[-1].color)
            k = 0
            embed.add_field(name = 'Professor', value = '{0}'.format(ctx.author.mention), inline = True)
            deadline = None
            for i in params:
                if i == 's':
                    subject = embedParts[k]
                    if params.count('t') == 0:
                        embed.title = '{0}'.format(embedParts[k])
                if i == 't':
                    title = embedParts[k]
                    subPos = params.index('s')
                    embed.title = '{0} - {1}'.format(embedParts[subPos], embedParts[k])
                if i == 'd':
                    embed.description = '{0}'.format(embedParts[k])
                if i == 'l':
                    embed.add_field(name = 'Link', value = '[Click here]({0})'.format(embedParts[k]), inline = False)
                if i == 'e':
                    deadlineObj = datetime.strptime(embedParts[k], "%H:%M %d/%m/%y").replace(tzinfo=IST)
                    deadline = embedParts[k] = toggleTimeAndString(deadlineObj)
                    embed.add_field(name = 'Deadline', value = '{0}'.format(beautifyTimeString(embedParts[k])), inline = False)
                k+=1
            if ctx.message.attachments != None and ctx.message.attachments != []:
                print("Attachment present", ctx.message.attachments)
                attach = ''
                for i in ctx.message.attachments:
                    attach+='[{0}]({1})\n'.format(i.filename, i.url)
                #attach -= '\n'
                embed.add_field(name = 'Attachments', value = attach, inline = False)
            assgnPosted = await self.addAssignment(subject, title, ctx, deadline)
            if assgnPosted != False:
                if arg1.lower().strip() == 'assignment':
                    message = await self.serverInfo[3].send(embed = embed)
                elif arg1.lower().strip() == 'quiz':
                    message = await self.serverInfo[3].send(content = '<@&'+studentID+'>', embed = embed)
                sqlUpdate = "UPDATE assignments SET assignmentLink = %s WHERE assignmentID = %s"
                self.myCursor.execute(sqlUpdate, (message.jump_url, assgnPosted))
                self.myDB.commit()
                # If assignment has deadline, restart reminder background task
                if self.client.reminders.is_running():
                    self.client.reminders.restart()
                else:
                    self.client.reminders.start()