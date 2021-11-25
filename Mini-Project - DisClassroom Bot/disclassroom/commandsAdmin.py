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

class adminCommands(commands.Cog):
    def __init__(self, client, db, cursor):
        self.client = client
        self.myDB = db
        self.myCursor = cursor

    @commands.command()
    async def ping(self, ctx):
        if isConfiguredTeacher(ctx, self.myCursor) == False:
            return
        start_time = datetime.utcnow()
        message = await ctx.send(":ping_pong:")
        end_time = datetime.utcnow()
        ping = rdelta.relativedelta(end_time, start_time)
        embed = discord.Embed(description=':ping_pong: Pong! {0}ms'.format(round(ping.microseconds/1000)),
                            color=default_color)
        await message.edit(content = '', embed = embed)

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
        msg = await self.client.wait_for('message', check=check)
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