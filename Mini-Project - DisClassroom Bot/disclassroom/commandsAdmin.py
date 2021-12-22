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

class adminCommands(commands.Cog):
    def __init__(self, client, db, cursor):
        self.client = client
        self.myDB = db
        self.myCursor = cursor

    # Function to check the bot's response time and to test if it's online.
    @commands.command()
    async def ping(self, ctx):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif check[0] == True or check[1] == False or check[3] == False:
            return
        start_time = datetime.utcnow()
        message = await ctx.send(":ping_pong:")
        end_time = datetime.utcnow()
        ping = rdelta.relativedelta(end_time, start_time)
        embed = discord.Embed(description=':ping_pong: Pong! {0}ms'.format(round(ping.microseconds/1000)),
                            color=default_color)
        await message.edit(content = '', embed = embed)

    # Command to configure the bot for a server
    @commands.command(name='config', aliases = ['configure'])
    async def config(self, ctx):
        await checkIfConfigured(self.client, ctx.guild, self.myDB, self.myCursor)
        # record = [welcomeChannelID, announcementsID, staffRoomChannelID, studentRoleID, teacherRoleID, configured]
        # ID for channel is None if not configured.
        self.myCursor.execute("SELECT welcomeChannelID, announcementsID, staffRoomChannelID, studentRoleID, teacherRoleID, configured FROM servers WHERE serverID = {0}".format(ctx.guild.id))
        record = self.myCursor.fetchone()
        embed = discord.Embed(description = "Select which channel you want to configure, by typing the corresponding number below:\n", color = default_color)
        embed.description += "**1. Entry channel** "
        if record[0] == None:
            embed.description += ":x:"
        else:
            embed.description += ":white_check_mark: - <#"+str(record[0])+">"
        embed.description += "\n\tThis channel should be visible to any user entering the server.\n"
        embed.description += "**2. Announcement channel** "
        if record[1] == None:
            embed.description += ":x:"
        else:
            embed.description += ":white_check_mark: - <#"+str(record[1])+">"
        embed.description += "\n\tThis channel is for posting announcements or assignments. It should be visible to all and read-only for students.\n"
        embed.description += "**3. Teacher's channel** "
        if record[2] == None:
            embed.description += ":x:"
        else:
            embed.description += ":white_check_mark: - <#"+str(record[2])+">"
        embed.description += "\n\tPrivate channel for teachers to use the bot and its commands.\n"
        embed.description += "**4. Student's role** "
        if record[3] == None:
            embed.description += ":x:"
        else:
            embed.description += ":white_check_mark: - <@&"+str(record[3])+">"
        embed.description += "\n\tThis role will be given to all students joining the server.\n"
        embed.description += "**5. Teacher's role** "
        if record[4] == None:
            embed.description += ":x:"
        else:
            embed.description += ":white_check_mark: - <@&"+str(record[4])+">"
        embed.description += "\n\tThis role will be given to all approved teachers joining the server.\n\nType 0, if you're done configuring the bot."
        await ctx.send(embed = embed)
        def check(m):
            try:
                return int(m.content) in range(0, 6) and m.channel == ctx.channel
            except:
                return
        try:
            msg = await self.client.wait_for('message', check=check, timeout = 300.0)     # Accept input to select which assignment to view
        except asyncio.TimeoutError:
            return
        option = int(msg.content)
        if option == 0:
            embed = discord.Embed(description = "Configuration commenced.", color = default_color)
            await ctx.send(embed = embed)
            return
        elif option == 1:
            embed = discord.Embed(description = "Ping the channel you want to set as entry channel below: (eg. #channel-name)", color = default_color)
            await ctx.send(embed = embed)
            def check(m):
                try:
                    channel = getChannel(self.client, m.content)
                    return channel.guild == ctx.guild and m.channel == ctx.channel
                except:
                    return False
            msg = await self.client.wait_for('message', check=check)
            sqlUpdate = "UPDATE servers SET welcomeChannelID = {0} WHERE serverID = {1}".format(re.sub("[^0-9]", "", msg.content), ctx.guild.id)
            self.myCursor.execute(sqlUpdate)
            self.myDB.commit()
            embed = discord.Embed(description = "{0} has been configured as the entry channel!".format(msg.content), color = default_color)
            await ctx.send(embed = embed)
        elif option == 2:
            embed = discord.Embed(description = "Ping the channel you want to set as announcements channel below: (eg. #channel-name)", color = default_color)
            await ctx.send(embed = embed)
            def check(m):
                try:
                    channel = getChannel(self.client, m.content)
                    return channel.guild == ctx.guild and m.channel == ctx.channel
                except:
                    return False
            msg = await self.client.wait_for('message', check=check)
            sqlUpdate = "UPDATE servers SET announcementsID = {0} WHERE serverID = {1}".format(re.sub("[^0-9]", "", msg.content), ctx.guild.id)
            self.myCursor.execute(sqlUpdate)
            self.myDB.commit()
            embed = discord.Embed(description = "{0} has been configured as the announcements channel!".format(msg.content), color = default_color)
            await ctx.send(embed = embed)
        elif option == 3:
            embed = discord.Embed(description = "Ping the channel you want to set as the teacher's channel below: (eg. #channel-name)", color = default_color)
            await ctx.send(embed = embed)
            def check(m):
                try:
                    channel = getChannel(self.client, m.content)
                    return channel.guild == ctx.guild and m.channel == ctx.channel
                except:
                    return False
            msg = await self.client.wait_for('message', check=check)
            sqlUpdate = "UPDATE servers SET staffRoomChannelID = {0} WHERE serverID = {1}".format(re.sub("[^0-9]", "", msg.content), ctx.guild.id)
            self.myCursor.execute(sqlUpdate)
            self.myDB.commit()
            embed = discord.Embed(description = "{0} has been configured as the teacher's channel!".format(msg.content), color = default_color)
            await ctx.send(embed = embed)       
        elif option == 4:
            embed = discord.Embed(description = "Ping the role you want to set as the student's role below: (eg. @roleName)", color = default_color)
            await ctx.send(embed = embed)
            def check(m):
                try:
                    role = getRole(ctx.guild, m.content)
                    return role.guild == ctx.guild and m.channel == ctx.channel
                except:
                    return False
            msg = await self.client.wait_for('message', check=check)
            sqlUpdate = "UPDATE servers SET studentRoleID = {0} WHERE serverID = {1}".format(re.sub("[^0-9]", "", msg.content), ctx.guild.id)
            self.myCursor.execute(sqlUpdate)
            self.myDB.commit()
            embed = discord.Embed(description = "{0} has been configured as the student's role!".format(msg.content), color = default_color)
            await ctx.send(embed = embed)
        elif option == 5:
            embed = discord.Embed(description = "Ping the role you want to set as the teacher's role below: (eg. @roleName)", color = default_color)
            await ctx.send(embed = embed)
            def check(m):
                try:
                    role = getRole(ctx.guild, m.content)
                    return role.guild == ctx.guild and m.channel == ctx.channel
                except:
                    return False
            msg = await self.client.wait_for('message', check=check)
            sqlUpdate = "UPDATE servers SET teacherRoleID = {0} WHERE serverID = {1}".format(re.sub("[^0-9]", "", msg.content), ctx.guild.id)
            self.myCursor.execute(sqlUpdate)
            self.myDB.commit()
            embed = discord.Embed(description = "{0} has been configured as the teacher's role!".format(msg.content), color = default_color)
            await ctx.send(embed = embed)
        self.myCursor.execute("SELECT welcomeChannelID, announcementsID, staffRoomChannelID, studentRoleID, teacherRoleID FROM servers WHERE serverID = {0}".format(ctx.guild.id))
        record = self.myCursor.fetchone()
        if None not in record:
            sqlUpdate = "UPDATE servers SET configured = 'True' WHERE serverID = {0}".format(ctx.guild.id)
            self.myCursor.execute(sqlUpdate)
            self.myDB.commit()

    @commands.group(name='help', aliases = ['h'], invoke_without_command = True)          #invoke_without_command = True doesn't invoke this base help command when you type "c!help view", else you get 2 messages
    async def help(self, ctx):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif check[0] == False and check[1] == True:
            embed = discord.Embed(title = ":information_source: All Available Commands",
                            description = "Bot prefix: `c!`. Type `c!help <command>` to get additional help with a command.",
                            color = default_color)
            embed.add_field(name = "info", value = "Get a student's information.", inline=True)
            embed.add_field(name = "configure", value = "Configure bot for the server.", inline=True)
            embed.add_field(name = "ping", value = "Checks the bot's response time.", inline=True)
            embed.add_field(name = "post", value = "Post an announcement or assignment.", inline=True)
            embed.add_field(name = "review", value = "Review details of an assignment, submissions and assign marks.", inline=True)
            embed.add_field(name = "release", value = "Release marks for an assignment.", inline=True)
            embed.add_field(name = "submit", value = "Submit an assignment.", inline=True)
            embed.add_field(name = "resubmit", value = "Resubmit a previously submitted assignment.", inline=True)
            embed.add_field(name = "view", value = "For a student to view all/pending assignments.", inline=True)
            embed.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        elif check[0] == True and check[2] == True:
            embed = discord.Embed(title = ":information_source: Available Commands",
                            description = "Bot prefix: `c!`. Type `c!help <command>` to get additional help with a command.",
                            color = default_color)
            embed.add_field(name = "submit", value = "Submit an assignment.", inline=True)
            embed.add_field(name = "resubmit", value = "Resubmit a previously submitted assignment.", inline=True)
            embed.add_field(name = "view", value = "View all/pending assignments.", inline=True)
            embed.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @help.command(name = 'info', aliases = ['i'])
    async def infoHelp(self, ctx):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif check[0] == False and check[1] == True:
            embed = discord.Embed(title = ":information_source: Additional Command Help",
                                  color = default_color)
            embed.add_field(name = "Command", value = "c!info", inline=True)
            embed.add_field(name = "Aliases", value = "c!i", inline=True)
            embed.add_field(name = "Description", value = "Get personal details of a student in the server.", inline=False)
            embed.add_field(name = "Syntax", value = "```c!info <user mention>``` or ```c!info <user ID>```", inline=False)
            embed.add_field(name = "Examples", value = "```c!info <@760901597470392401>``````c!info 760901597470392401```", inline=False)
            embed.add_field(name = "Group", value = "Teachers", inline=False)
            embed.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @help.command(name = 'configure', aliases = ['config'])
    async def configHelp(self, ctx):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif check[0] == False and check[1] == True:
            embed = discord.Embed(title = ":information_source: Additional Command Help",
                                  color = default_color)
            embed.add_field(name = "Command", value = "c!configure", inline=True)
            embed.add_field(name = "Aliases", value = "c!config", inline=True)
            embed.add_field(name = "Description", value = "Configure the bot for the server. Needs to be done before using any other command.", inline=False)
            embed.add_field(name = "Syntax", value = "```c!configure``` or ```c!config```", inline=False)
            embed.add_field(name = "Group", value = "Admin", inline=False)
            embed.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @help.command(name = 'ping')
    async def pingHelp(self, ctx):
        embed = discord.Embed(title = ":information_source: Additional Command Help",
                        color = default_color)
        embed.add_field(name = "Command", value = "c!ping", inline=True)
        embed.add_field(name = "Aliases", value = "`<None>`", inline=True)
        embed.add_field(name = "Description", value = "Checks the bot's response time.", inline=False)
        embed.add_field(name = "Syntax", value = "```c!ping```", inline=False)
        embed.add_field(name = "Parameters or Arguments", value = "`<None>`", inline=False)
        embed.add_field(name = "Group", value = "Admin", inline=False)
        embed.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @help.command(name = 'post')
    async def postHelp(self, ctx):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif check[0] == False and check[1] == True:
            embed = discord.Embed(title = ":information_source: Additional Command Help",
                                  color = default_color)
            embed.add_field(name = "Command", value = "c!post", inline=True)
            embed.add_field(name = "Aliases", value = "`<None>`", inline=True)
            embed.add_field(name = "Description", value = "Post an announcement, assignment or quiz in the announcement channel.", inline=False)
            embed.add_field(name = "Syntax", value = "```c!post <argument> <-s> <-t> <-d> <-l> <-m> <-e>```", inline=False)
            embed.add_field(name = "Arguments", value = "`announcement`/`announce` - Make an announcement. Subject and description are compuslory.\n`assignment` - Post an assignment. Subject, title and description are compulsory.\n`quiz` - Same as an assignment, except it pings all the Students.", inline=False)
            embed.add_field(name = "Parameters", value = "`-s` - Subject name/code.\n`-t` - Title of the post.\n`-d` - Description of the post.\n`-l` - External link related to the post.\n`-m` - Only for assignments, maximum marks. Should be an integer.\n`-e` - Only for assignments, the deadline. Format to be used is hh:mm DD/MM/YY (24-hour).", inline=False)
            embed.add_field(name = "Other information", value = "This command also supports attachments, so you can even attach files to your `post` command.\nThe description can be multi-line.", inline=False)
            embed.add_field(name = "Examples", value = "```c!post announcement -s Probability -d There will be no lecture today. Use the time to complete your assignments. ``````c!post assignment -s OOP -t Mid-sem Exam -d Time: 2 hours -l https://docs.google.com/forms/d/1coClkeI1wYTu -m 30 -e 17:00 21/12/21```", inline=False)
            embed.add_field(name = "Group", value = "Teachers", inline=False)
            embed.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @help.command(name = 'review')
    async def reviewHelp(self, ctx):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif check[0] == False and check[1] == True:
            embed = discord.Embed(title = ":information_source: Additional Command Help",
                                  color = default_color)
            embed.add_field(name = "Command", value = "c!review", inline=True)
            embed.add_field(name = "Aliases", value = "`<None>`", inline=True)
            embed.add_field(name = "Description", value = "Review details of an assignment, submissions by students and assign marks through attached Google Sheet.", inline=False)
            embed.add_field(name = "Syntax", value = "```c!review <optional argument>```", inline=False)
            embed.add_field(name = "Arguments", value = "`all` - Review all assignments.\n`me`/`mine` - Review your assignments. (default)", inline=False)
            embed.add_field(name = "Examples", value = "```c!review all```", inline=False)
            embed.add_field(name = "Group", value = "Teachers", inline=False)
            embed.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @help.command(name = 'release')
    async def releaseHelp(self, ctx):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif check[0] == False and check[1] == True:
            embed = discord.Embed(title = ":information_source: Additional Command Help",
                                  color = default_color)
            embed.add_field(name = "Command", value = "c!release", inline=True)
            embed.add_field(name = "Aliases", value = "`<None>`", inline=True)
            embed.add_field(name = "Description", value = "Release the marks of an assignment, which are retrieved from the Google Sheet linked to the assignment. The Google Sheet can be found by using `c!review` and selecting the assignment you want to release the marks for.", inline=False)
            embed.add_field(name = "Syntax", value = "```c!release```", inline=False)
            embed.add_field(name = "Group", value = "Teachers", inline=False)
            embed.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @help.command(name = 'submit')
    async def submitHelp(self, ctx):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif (check[0] == False and check[1] == True) or (check[0] == True and check[2] == True):
            embed = discord.Embed(title = ":information_source: Additional Command Help",
                                  color = default_color)
            embed.add_field(name = "Command", value = "c!submit", inline=True)
            embed.add_field(name = "Aliases", value = "`<None>`", inline=True)
            embed.add_field(name = "Description", value = "Submit an assignment, by invoking the command in DMs and uploading all attachments. Type `c!confirm` once done uploading to submit them.", inline=False)
            embed.add_field(name = "Syntax", value = "```c!submit```", inline=False)
            embed.add_field(name = "Group", value = "Students", inline=False)
            embed.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @help.command(name = 'resubmit')
    async def resubmitHelp(self, ctx):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif (check[0] == False and check[1] == True) or (check[0] == True and check[2] == True):
            embed = discord.Embed(title = ":information_source: Additional Command Help",
                                  color = default_color)
            embed.add_field(name = "Command", value = "c!resubmit", inline=True)
            embed.add_field(name = "Aliases", value = "`<None>`", inline=True)
            embed.add_field(name = "Description", value = "Resubmit a previously submitted assignment.", inline=False)
            embed.add_field(name = "Syntax", value = "```c!resubmit```", inline=False)
            embed.add_field(name = "Group", value = "Students", inline=False)
            embed.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @help.command(name = 'view')
    async def viewHelp(self, ctx):
        check = await isConfiguredStudentOrTeacher(ctx, self.myCursor)
        # check = [DM, Teacher, Student, TeachersChannel] or False, if not configured
        if check == False:
            return
        elif (check[0] == False and check[1] == True) or (check[0] == True and check[2] == True):
            embed = discord.Embed(title = ":information_source: Additional Command Help",
                                  color = default_color)
            embed.add_field(name = "Command", value = "c!view", inline=True)
            embed.add_field(name = "Aliases", value = "`<None>`", inline=True)
            embed.add_field(name = "Description", value = "View all/pending assignments, from every mutual server with the bot. Select an assignment to view details about it and your submissions.", inline=False)
            embed.add_field(name = "Syntax", value = "```c!view <optional argument>```", inline=False)
            embed.add_field(name = "Arguments", value = "`all` - View all assignments from mutual servers. (default)\n`pending` - View pending assignments.", inline=False)
            embed.add_field(name = "Examples", value = "```c!view pending```", inline=False)
            embed.add_field(name = "Group", value = "Students", inline=False)
            embed.set_footer(text="Requested by {0.name}#{0.discriminator} | {0.id}".format(ctx.author), icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)