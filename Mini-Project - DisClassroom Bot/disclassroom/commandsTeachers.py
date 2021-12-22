#_______________________IMPORTING DISCORD.PY LIBRARIES_____________________#
import discord
from discord.ext import commands
#_______________________IMPORTING OTHER LIBRARIES_____________________#
import asyncio
from datetime import datetime, timedelta
from datetime import date
from dateutil import relativedelta as rdelta
import re
#_______________________IMPORTING PROJECT FILES_____________________#
from variables import *
from utilFunctions import *
#__________________________COMMANDS___________________________#

class teacherCommands(commands.Cog):
    def __init__(self, client, db, cursor, drive, gc):
        self.client = client
        self.myDB = db
        self.myCursor = cursor
        self.drive = drive
        self.gc = gc
        # serverInfo:
        # [server, entryChannel, announcementsChannel, teacherChannel, studentRole, teacherRole, students, teachers]
        # [0,      1,            2,                    3,              4,           5,           6,        7]

    # Command is used to retrieve information about a Student in the server
    @commands.command(name='info', aliases = ['i'])
    async def info(self, ctx, arg):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif check[0] == True or check[1] == False or check[3] == False:
            return
        serverInfo = getServerInfo(self.client, ctx.guild.id, self.myCursor)
        ID = re.sub("[^0-9]", "", arg)
        try:
            member = await ctx.guild.fetch_member(int(ID))
        except:
            embed = discord.Embed(description="Student not found.",
                          color=red)
            await ctx.send(embed=embed)
            return
        if serverInfo[4] not in member.roles:
            embed = discord.Embed(description="User is not a student.",
                          color=red)
            await ctx.send(embed=embed)
            return
        self.myCursor.execute("SELECT * FROM students WHERE studentID = '{0}' AND serverID = {1}".format(ID, ctx.guild.id))
        record = self.myCursor.fetchone()
        embed = discord.Embed(title =  ":man_in_tuxedo: Student information", color = default_color)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="Name", value=record[0], inline=True)
        embed.add_field(name="Username", value="{0} | `".format(member.mention) + record[1] + '`', inline=True)
        embed.add_field(name="ID", value=str(record[2]), inline=True)
        embed.add_field(name="Roll number", value=record[4], inline=True)
        embed.add_field(name="Email", value=record[5], inline=True)
        embed.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    # Utility function to add assignment to database when "c!post assignment" is invoked
    async def addAssignment(self, subject, title, marks, ctx, deadline, serverInfo):
        #####################################################
        ##             UPDATE ASSIGNMENTS TABLE            ##
        #####################################################
        if deadline != None:
            deadlineObj = toggleTimeAndString(deadline)
            localTime = datetime.now(IST)
            remainingTime = rdelta.relativedelta(deadlineObj, localTime)
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
            if marks is not None:
                self.myCursor.execute("INSERT INTO assignments (serverID, subject, title, teacherID, hasDeadline, deadline, deadlineReminder, isReminder, postTime, totalMarks) VALUES ('{0.guild.id}', '{1}', '{2}', '{0.author.id}', 'True', '{3}', '{4}', '{5}', '{6}', {7})".format(ctx, subject, title, toggleTimeAndString(deadlineObj), toggleTimeAndString(deadlineReminder), isReminder, toggleTimeAndString(ctx.message.created_at.astimezone(IST)), marks))
            else:
                self.myCursor.execute("INSERT INTO assignments (serverID, subject, title, teacherID, hasDeadline, deadline, deadlineReminder, isReminder, postTime) VALUES ('{0.guild.id}', '{1}', '{2}', '{0.author.id}', 'True', '{3}', '{4}', '{5}', '{6}')".format(ctx, subject, title, toggleTimeAndString(deadlineObj), toggleTimeAndString(deadlineReminder), isReminder, toggleTimeAndString(ctx.message.created_at.astimezone(IST))))
            self.myDB.commit()
            self.myCursor.execute("SELECT assignmentID FROM assignments WHERE serverID = '{0}' AND subject = '{1}' AND postTime = '{2}'".format(ctx.guild.id, subject, toggleTimeAndString(ctx.message.created_at.astimezone(IST))))
            assignmentID = self.myCursor.fetchone()[0]
        else:
            if marks is not None:
                self.myCursor.execute("INSERT INTO assignments (serverID, subject, title, teacherID, hasDeadline, postTime, totalMarks) VALUES ('{0.guild.id}', '{1}', '{2}', '{0.author.id}', 'False', '{3}', {4})".format(ctx, subject, title, toggleTimeAndString(ctx.message.created_at.astimezone(IST)), marks))
            else:
                self.myCursor.execute("INSERT INTO assignments (serverID, subject, title, teacherID, hasDeadline, postTime) VALUES ('{0.guild.id}', '{1}', '{2}', '{0.author.id}', 'False', '{3}')".format(ctx, subject, title, toggleTimeAndString(ctx.message.created_at.astimezone(IST))))
            self.myDB.commit()
            self.myCursor.execute("SELECT assignmentID FROM assignments WHERE serverID = '{0}' AND subject = '{1}' AND postTime = '{2}'".format(ctx.guild.id, subject, toggleTimeAndString(ctx.message.created_at.astimezone(IST))))
            assignmentID = self.myCursor.fetchone()[0]
        #####################################################
        ##            CREATE TABLE FOR ASSIGNMENT          ##
        #####################################################
        f = self.drive.CreateFile({
            'title': '{0} {1} - {2}'.format(assignmentID, subject, title),
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            "parents": [{"id": folder_id}]})
        f.Upload()
        f.InsertPermission({"role" : "writer", 
                        "type" : "anyone",
                        "additionalRoles" : ['commenter']})
        workbook = self.gc.open_by_key(f['id'])
        worksheet = workbook.sheet1
        if marks is not None:
            worksheetTable = [['Sr. no.', 'Tag | Name', 'Roll no.', 'Marks']]
        else:
            worksheetTable = [['Sr. no.', 'Tag | Name', 'Roll no.', 'Marks ({0})'.format(marks)]]
        tableName = "assgn" + str(assignmentID)
        self.myCursor.execute("CREATE TABLE {0}(ID INT AUTO_INCREMENT PRIMARY KEY, studentName VARCHAR(100), studentID BIGINT UNSIGNED, serverID BIGINT UNSIGNED, submissions VARCHAR(1000), submissionTime VARCHAR(255), submitted VARCHAR(100) DEFAULT FALSE, submittedLate VARCHAR(100), marks INT)".format(tableName))
        k = 1
        for i in serverInfo[6]:
            self.myCursor.execute("SELECT studentTag, studentName, rollNo FROM students WHERE studentID = {0} AND serverID = {1}".format(i.id, ctx.guild.id))
            record = self.myCursor.fetchone()
            worksheetTable.append([k, record[0] + ' | ' + record[1], record[2]])
            self.myCursor.execute("INSERT INTO {0} (studentName, studentID, serverID) VALUES ('{1.name}#{1.discriminator}', '{1.id}', '{2}')".format(tableName, i, ctx.guild.id))
            k+=1
        worksheet.update('A1:D{0}'.format(len(worksheetTable)), worksheetTable)
        worksheet.columns_auto_resize(0, 4)
        sqlUpdate = "UPDATE assignments SET marksheet = '{0}' WHERE assignmentID = {1}".format(f['id'], assignmentID)
        self.myCursor.execute(sqlUpdate)
        self.myDB.commit()
        return assignmentID

    # Command to post announcement, quiz, or assignment
    @commands.command()
    async def post(self, ctx, arg1 = '', *, arg2 = ''):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif check[0] == True or check[1] == False or check[3] == False:
            return
        serverInfo = getServerInfo(self.client, ctx.guild.id, self.myCursor)
        member = ctx.guild.get_member(ctx.author.id)
        #####################################################
        ##                   ANNOUNCEMENT                  ##
        #####################################################
        if arg1.lower().strip() == 'announcement' or arg1.lower().strip() == 'announce':
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
            # Obtaining the values for the present parameters
            myRegex = ' [-][' + params + '] '
            embedParts = re.split(myRegex, arg2)
            embedParts = embedParts[1:]
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
                    embedParts[k] = embedParts[k].lower()
                    if embedParts[k].startswith('https://') == False and embedParts[k].startswith('http://') == False:
                        embedParts[k] = "https://" + embedParts[k]
                    embed.add_field(name = 'Link', value = '[Click here]({0})'.format(embedParts[k]), inline = False)
                k+=1
            if ctx.message.attachments != None and ctx.message.attachments != []:
                attach = ''
                imageSelected = False
                for i in ctx.message.attachments:
                    if imageSelected == False and i.content_type.startswith('image') == True:
                        embed.set_image(url = i.url)
                        imageSelected = True
                    else:
                        attach+='[{0}]({1})\n'.format(i.filename, i.url)
                if attach != '':
                    embed.add_field(name = 'Attachments', value = attach, inline = False)
            announcement = await serverInfo[2].send(embed = embed)
            embed = discord.Embed(description = '[Announcement posted!]({0})'.format(announcement.jump_url), color = default_color)
            await serverInfo[3].send(embed = embed)
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
            paramsList = re.findall(r" [-]['stdlme'] ", arg2)
            params = ''
            for i in paramsList:
                params += i[2]
            # Obtaining the values for the present parameters
            myRegex = ' [-][' + params + '] '
            embedParts = re.split(myRegex, arg2)
            embedParts = embedParts[1:]
            # Building embed using the parameters and their values
            embed = discord.Embed(color = member.roles[-1].color)
            k = 0
            embed.add_field(name = 'Professor', value = '{0}'.format(ctx.author.mention), inline = True)
            deadline = None
            marks = None
            for i in params:
                if i == 's':
                    subject = embedParts[k]
                    if params.count('t') == 0:
                        embed.title = embedParts[k]
                if i == 't':
                    title = embedParts[k]
                    subPos = params.index('s')
                    embed.title = embedParts[subPos] + ' - ' + embedParts[k]
                if i == 'd':
                    embed.description = '{0}'.format(embedParts[k])
                if i == 'l':
                    embedParts[k] = embedParts[k].lower()
                    if embedParts[k].startswith('https://') == False and embedParts[k].startswith('http://') == False:
                        embedParts[k] = "https://" + embedParts[k]
                    embed.add_field(name = 'Link', value = '[Click here]({0})'.format(embedParts[k]), inline = False)
                if i == 'm':
                    try:
                        marks = int(embedParts[k])
                    except:
                        invalidMarks = discord.Embed(description = 'Marks entered are invalid. Ensure the marks are an integer.', color = red)
                        await ctx.send(embed = invalidMarks)
                        return
                    embed.add_field(name = 'Marks', value = embedParts[k], inline = False)
                if i == 'e':
                    deadlineObj = datetime.strptime(embedParts[k], "%H:%M %d/%m/%y").replace(tzinfo=IST)
                    deadline = embedParts[k] = toggleTimeAndString(deadlineObj)
                    embed.add_field(name = 'Deadline', value = '{0}'.format(beautifyTimeString(embedParts[k])), inline = False)
                k+=1
            if ctx.message.attachments != None and ctx.message.attachments != []:
                attach = ''
                imageSelected = False
                for i in ctx.message.attachments:
                    if imageSelected == False and i.content_type.startswith('image') == True:
                        embed.set_image(url = i.url)
                        imageSelected = True
                    else:
                        attach+='[{0}]({1})\n'.format(i.filename, i.url)
                if attach != '':
                    embed.add_field(name = 'Attachments', value = attach, inline = False)
            assgnPosted = await self.addAssignment(subject, title, marks, ctx, deadline, serverInfo)
            if assgnPosted != False:
                if arg1.lower().strip() == 'assignment':
                    message = await serverInfo[2].send(embed = embed)
                elif arg1.lower().strip() == 'quiz':
                    message = await serverInfo[2].send(content = '<@&'+serverInfo[4]+'>', embed = embed)
                sqlUpdate = "UPDATE assignments SET assignmentLink = %s WHERE assignmentID = %s"
                self.myCursor.execute(sqlUpdate, (message.jump_url, assgnPosted))
                self.myDB.commit()
                embed = discord.Embed(description = '[Assignment posted!]({0})'.format(message.jump_url), color = default_color)
                await serverInfo[3].send(embed = embed)
                # If assignment has deadline, restart reminder background task
                if self.client.cogs['Tasks'].reminders.is_running():
                    self.client.cogs['Tasks'].reminders.restart()
                else:
                    self.client.cogs['Tasks'].reminders.start()
        else:
            embed = discord.Embed(description = 'Type `c!help post` for help with this command.', 
                                        color = default_color)
            await ctx.send(embed = embed)

    # Function that takes a list of assignments as input, asks the user to select one based on the number, and returns the selected assignment out of the list
    # Other arguments like bottomText and option are just to modify the text appearing in the embed as per our needs
    async def getAssignment(self, ctx, assignmentList, bottomText, option):
        embed = discord.Embed(description = '**#  |  Subject  |      Title      |  Teacher  |  Marks  |  Deadline**\n', 
                                color = default_color)
        if option == 1:
            embed.title = "All assignments"
        elif option == 2:
            embed.title = "Your assignments"

        k = 0
        for i in assignmentList:
            if i[6] is not None:
                convertedTime = (datetime.strptime(i[6], defaultTimeFormat)).replace(tzinfo=IST)
                convertedString = (datetime.strftime(convertedTime, "%I:%M %p IST, %b %d, %Y"))
            else:
                convertedString = "`None`"
            if i[9] is not None:
                marks = i[9]
            else:
                marks = '`None`'
            embed.description += "`{0}`  | {1} | [{2}]({3}) | <@{4}> | `{5}`\n".format(str(k+1).zfill(len(str(len(assignmentList)))), i[2], i[3], i[5], i[4], marks)+"​ "*(len(str(len(assignmentList)))*2+3)+"`{0}`\n".format(convertedString)
            k+=1
        embed.description += "\n"+ bottomText
        await ctx.send(embed=embed)
        def check(m):
            try:
                return int(m.content) in range(1, len(assignmentList)+1) and m.channel == ctx.channel
            except:
                return
        try:
            msg = await self.client.wait_for('message', check=check, timeout = 300.0)     # Accept input to select which assignment to view
        except asyncio.TimeoutError:
            return
        choice = int(msg.content)
        selectedAssignment = assignmentList[choice-1]
        return selectedAssignment

    # Utility function to post all the details of an assignment. This includes an overview of the assignment, its marksheet and list of students along with their submissions
    async def postAssignmentDetails(self, ctx, assignment):      # assignment = [assignmentID, serverID, subject, title, teacherID, assignmentLink, deadline, deadlineOver, postTime, totalMarks, marksheet, marksReleased]
        tableName = "assgn" + str(assignment[0])
        embed1 = discord.Embed(title = ':pencil: Assignment details',
                                description = '**[{0}]({1})**'.format(assignment[3], assignment[5]),
                                color = default_color)
        embed1.add_field(name = "Subject", value = assignment[2])
        embed1.add_field(name = "Professor", value = "<@"+str(assignment[4])+">")
        if assignment[9] is not None:
            embed1.add_field(name = "Total marks", value = str(assignment[9]))
        else:
            embed1.add_field(name = "Total marks", value = '`None`')
        if assignment[6] is not None:
            embed1.add_field(name = "Deadline", value = beautifyTimeString(assignment[6]))
        else:
            embed1.add_field(name = "Deadline", value = '`None`')
        embed1.add_field(name = "Posted time", value = beautifyTimeString(assignment[8]))
        if assignment[7] == '0':
            embed1.add_field(name = "Deadline over", value = "No")
        else:
            embed1.add_field(name = "Deadline over", value = "Yes")
        self.myCursor.execute("SELECT studentName, studentID, serverID, submissions, submissionTime, submitted, submittedLate, marks FROM {0} ORDER BY ID".format(tableName))
        allStudents = self.myCursor.fetchall()
        sum = 0
        count = 0
        for i in allStudents:
            if i[7] is not None:
                sum += int(i[7])
                count += 1
        self.myCursor.execute("SELECT studentName, studentID, serverID, submissions, submissionTime, submitted, submittedLate, marks FROM {0} WHERE submitted != '0' ORDER BY ID".format(tableName))
        submittedStudents = self.myCursor.fetchall()
        embed1.add_field(name = "Submitted by", value = "{0}/{1}".format(len(submittedStudents), len(allStudents)))
        lateSubmissions = 0
        for i in submittedStudents:
            if i[6] == '1':
                lateSubmissions +=1
        embed1.add_field(name = "Late submissions", value = "{0}/{1}".format(lateSubmissions, len(submittedStudents)))
        if count != 0:
            embed1.add_field(name = "Average marks", value = "{0}".format(sum/count))
        else:
            embed1.add_field(name = "Average marks", value = "`N/A`")
        if assignment[11] != '0':
            embed1.add_field(name = "Marks released", value = ":white_check_mark:")
        else:
            embed1.add_field(name = "Marks released", value = ":x:")
        embed1.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed = embed1)
        embed2 = discord.Embed(title = ":bar_chart: Marksheet", description = "[__Click here__]({0})".format("https://docs.google.com/spreadsheets/d/"+assignment[10]+"/edit#gid=0"), color = default_color)
        await ctx.send(embed = embed2)
        embed3 = discord.Embed(title = ':student: List of students', description = '**#  |   Mention   |    User    |  ID  |  Submitted  |  Submissions**\n', color = default_color)
        k = 1
        for i in allStudents:
            if i[5] != '0':
                if i[6] == '0':
                    embed3.description += "`{0}`  | <@{1}> | {2} | `{1}` | :white_check_mark:\n".format(str(k).zfill(len(str(len(allStudents)))), i[1], i[0])
                else:
                    embed3.description += "`{0}`  | <@{1}> | {2} | `{1}` | :white_check_mark: *(late)*\n".format(str(k).zfill(len(str(len(allStudents)))), i[1], i[0])
                if i[3] is not None:
                    submissionIDs = i[3].split(', ')
                    submissions = []
                    l = 1
                    for j in submissionIDs:
                        submissions.append("[Submission {0}]({1})".format(l, "https://drive.google.com/file/d/" + j + "/view?usp=sharing"))
                        l+=1
                    submissionString = ', '.join(submissions)
                    embed3.description += '​ ​ ​ ​ ​ ​ ​ ' + submissionString + '\n'
            else:
                embed3.description += "`{0}`  | <@{1}> | {2} | `{1}` | :x:\n".format(str(k).zfill(len(str(len(allStudents)))), i[1], i[0])
            k+=1
        embed3.description += "\nType the corresponding number to get more details on a student."
        await ctx.send(embed = embed3)
        def check(m):
            try:
                return int(m.content) in range(1, len(allStudents)+1) and m.channel == ctx.channel
            except:
                return
        try:
            msg = await self.client.wait_for('message', check=check, timeout = 300.0)     # Accept input to select which assignment to view
        except asyncio.TimeoutError:
            return
        choice = int(msg.content)
        studentRecord = allStudents[choice-1]
        embed3 = discord.Embed(title = "Student assignment details", description = '**[{0} - {1}]({2})**'.format(assignment[2], assignment[3], assignment[5]), color = default_color)
        self.myCursor.execute("SELECT * FROM students WHERE studentID = '{0}' AND serverID = {1}".format(studentRecord[1], ctx.guild.id))
        studentDetails = self.myCursor.fetchone()
        embed3.add_field(name="Name [Roll no.]", value=studentDetails[0] + '\n['+studentDetails[4]+']', inline=True)
        embed3.add_field(name="Username", value="<@{0}> | `{1}`".format(studentDetails[2], studentDetails[1]), inline=True)
        embed3.add_field(name="ID", value=str(studentDetails[2]), inline=True)
        if studentRecord[4] is not None:
            embed3.add_field(name = "Submission time", value = beautifyTimeString(studentRecord[4]))
        else:
            embed3.add_field(name = "Submission time", value = "`None`")
        if assignment[6] is not None:
            embed3.add_field(name = "Deadline", value = beautifyTimeString(assignment[6]))
        else:
            embed3.add_field(name = "Deadline", value = '`None`')
        timeChecks = ''
        if studentRecord[5] == '0':
            timeChecks += ":x: Submitted"
        else:
            timeChecks += ":white_check_mark: Submitted\n"
            if studentRecord[6] != '0':
                timeChecks += ":x: Submitted on time"
            else:
                timeChecks += ":white_check_mark: Submitted on time"
        embed3.add_field(name = "Checks", value = timeChecks)
        if studentRecord[3] is not None:
            submissionIDs = studentRecord[3].split(', ')
            submissionString = ''
            for i in submissionIDs:
                file = self.drive.CreateFile({"id": i})
                file.FetchMetadata(fields='id,title')
                submissionString += ":small_orange_diamond: [{0}]({1})\n".format(file['title'], "https://drive.google.com/file/d/" + i + "/view?usp=sharing")
            embed3.add_field(name = "Submissions", value = submissionString, inline = False)
        await ctx.send(embed = embed3)

    # Command for teachers to select an assignment and review its details.
    # This provides an overview of the assignment, the submissions, and the marksheet.
    @commands.command()
    async def review(self, ctx, arg = 'me'):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif check[0] == True or check[1] == False or check[3] == False:
            return
        serverInfo = getServerInfo(self.client, ctx.guild.id, self.myCursor)
        bottomText = "Select the assignment you want to view in detail, by typing the corresponding number."
        #          = [server, entryChannel, announcementsChannel, teacherChannel, studentRole, teacherRole, students, teachers]
        if arg.strip().lower() == 'all':
            self.myCursor.execute("SELECT assignmentID, serverID, subject, title, teacherID, assignmentLink, deadline, deadlineOver, postTime, totalMarks, marksheet, marksReleased FROM assignments WHERE serverID = {0}".format(ctx.guild.id))
            allAssignments = self.myCursor.fetchall()                    # Get all assignments from the server
            selectedAssignment = await self.getAssignment(ctx, allAssignments, bottomText, 1)
            if selectedAssignment is not None:
                await self.postAssignmentDetails(ctx, selectedAssignment)
        elif arg.strip().lower() == 'me' or arg.strip().lower() == 'mine':
            self.myCursor.execute("SELECT assignmentID, serverID, subject, title, teacherID, assignmentLink, deadline, deadlineOver, postTime, totalMarks, marksheet, marksReleased FROM assignments WHERE serverID = {0.guild.id} AND teacherID = {0.author.id}".format(ctx))
            myAssignments = self.myCursor.fetchall()                    # Get techer's assignments from the server
            selectedAssignment = await self.getAssignment(ctx, myAssignments, bottomText, 2)
            if selectedAssignment is not None:
                await self.postAssignmentDetails(ctx, selectedAssignment)
        else:
            embed = discord.Embed(description = 'Type `c!help review` for help with this command.', 
                                        color = default_color)
            await ctx.send(embed = embed)

    # Utility function to release the scores for a selected assignment. Marks are read from the Google Sheet attached to the assignment and updates them in the database and sends them out to all students, whose scores had a change.
    # The first time, all students receive their scores. The second time, only if there was a change in marks from the previous time, the scores are updated.
    async def releaseScores(self, ctx, selectedAssignment):
        tableName = "assgn" + str(selectedAssignment[0])
        workbook = self.gc.open_by_key(selectedAssignment[10])
        worksheet = workbook.sheet1
        markList = worksheet.get('D2:D', major_dimension = 'COLUMNS')
        if len(markList) == 0 or markList is None:
            embed = discord.Embed(description = 'Marks column in worksheet is empty. Make sure you have saved any changes to it.\nType `c!review` to retrieve the worksheet and grade the students.', 
                                  color = red)
            await ctx.send(embed = embed)
            return
        markList = markList[0]
        self.myCursor.execute("SELECT studentID, marks FROM {0} ORDER BY ID".format(tableName))
        allStudentRecords = self.myCursor.fetchall()
        k = 0
        for i in markList[:len(allStudentRecords)]:
            if i == '':
                sqlUpdate = "UPDATE {0} SET marks = NULL WHERE studentID = {1}".format(tableName, allStudentRecords[k][0])
                self.myCursor.execute(sqlUpdate)
                k += 1
                continue
            try:
                test = int(i)
            except:
                embed = discord.Embed(description = 'Marks column in worksheet contains non-integer value(s). Type `c!review` to retrieve it.', 
                                        color = red)
                await ctx.send(embed = embed)
                return
            if int(i) != allStudentRecords[k][1]:
                sqlUpdate = "UPDATE {0} SET marks = {1} WHERE studentID = {2}".format(tableName, i, allStudentRecords[k][0])
                self.myCursor.execute(sqlUpdate)
                user = self.client.get_user(allStudentRecords[k][0])
                embed = discord.Embed()
                if allStudentRecords[k][1] is None:
                    embed.title = "Score released"
                    embed.color = default_color
                else:
                    embed.title = "Score updated"
                    embed.color = green
                if selectedAssignment[9] is None:
                    embed.description = "**[{0} - {1}]({2}) : {3}**".format(selectedAssignment[2], selectedAssignment[3], selectedAssignment[5], i)
                else:
                    embed.description = "**[{0} - {1}]({2}) : {3}/{4}**".format(selectedAssignment[2], selectedAssignment[3], selectedAssignment[5], i, selectedAssignment[9])
                try:
                    await user.send(embed = embed)
                except:
                    pass
            k += 1 
        sqlUpdate = "UPDATE assignments SET marksReleased = 'True' WHERE assignmentID = {0}".format(selectedAssignment[0])
        self.myCursor.execute(sqlUpdate)
        self.myDB.commit()
        embed = discord.Embed(description = 'Marks have been successfully released!', 
                                        color = default_color)
        await ctx.send(embed = embed)

    # Function to release scores to all students for an assignment.
    @commands.command()
    async def release(self, ctx, arg = 'me'):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif check[0] == True or check[1] == False or check[3] == False:
            return
        bottomText = "Select the assignment you want to release the marks for, by typing the corresponding number."
        def check(m):
            return (m.content.lower() == 'yes' or m.content.lower() == 'no') and m.channel == ctx.channel and m.author == ctx.author
        if arg.strip().lower() == 'all':
            self.myCursor.execute("SELECT assignmentID, serverID, subject, title, teacherID, assignmentLink, deadline, deadlineOver, postTime, totalMarks, marksheet, marksReleased FROM assignments WHERE serverID = {0}".format(ctx.guild.id))
            allAssignments = self.myCursor.fetchall()                    # Get all assignments from the server
            selectedAssignment = await self.getAssignment(ctx, allAssignments, bottomText, 1)
            if selectedAssignment is not None:
                embed = discord.Embed(description = "Ensure you have saved all changes to the marksheet of selected assignment before proceeding.\n\nType **Yes** to proceed or **No** to abort.", color = default_color)
                await ctx.send(embed = embed)
                try:
                    msg = await self.client.wait_for('message', check=check, timeout = 120.0)
                except asyncio.TimeoutError:
                    return
                if msg.content.lower() == 'no':
                    embed = discord.Embed(description = 'Process aborted.', 
                                        color = red)
                    await ctx.send(embed = embed)
                    return
                await self.releaseScores(ctx, selectedAssignment)
        elif arg.strip().lower() == 'me' or arg.strip().lower() == 'mine':
            self.myCursor.execute("SELECT assignmentID, serverID, subject, title, teacherID, assignmentLink, deadline, deadlineOver, postTime, totalMarks, marksheet, marksReleased FROM assignments WHERE serverID = {0.guild.id} AND teacherID = {0.author.id}".format(ctx))
            myAssignments = self.myCursor.fetchall()                    # Get teacher's assignments from the server
            selectedAssignment = await self.getAssignment(ctx, myAssignments, bottomText, 2)
            if selectedAssignment is not None:
                embed = discord.Embed(description = "Ensure you have saved all changes to the marksheet of selected assignment before proceeding.\n\nType **Yes** to proceed or **No** to abort.", color = default_color)
                await ctx.send(embed = embed)
                try:
                    msg = await self.client.wait_for('message', check=check, timeout = 120.0)
                except asyncio.TimeoutError:
                    return
                if msg.content.lower() == 'no':
                    embed = discord.Embed(description = 'Process aborted.', 
                                        color = red)
                    await ctx.send(embed = embed)
                    return
                await self.releaseScores(ctx, selectedAssignment)
        else:
            embed = discord.Embed(description = 'Type `c!help release` for help with this command.', 
                                        color = default_color)
            await ctx.send(embed = embed)