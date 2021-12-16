#_______________________IMPORTING DISCORD.PY LIBRARIES_____________________#
import discord
from discord.ext import commands, tasks
from discord.ext.commands import *
#_______________________IMPORTING PROJECT FILES_____________________#
import asyncio
from variables import *
from utilFunctions import *
#______________________________ON EVENT_____________________________#
class onEvents(commands.Cog):
    def __init__(self, client, myDB, myCursor, gc):
        self.client = client
        self.myDB = myDB
        self.myCursor = myCursor
        self.gc = gc
        # serverInfo
        # [server, entryChannel, announcementsChannel, teacherChannel, student, teacher, students, teachers]
        # [0,      1,            2,                    3,              4,       5,       6,        7]

    @commands.Cog.listener()
    async def on_member_join(self, member):
        user = await self.client.fetch_user(member.id)
        dmChannel = user.dm_channel
        if dmChannel == None:
            dmChannel = await user.create_dm()
        self.myCursor.execute("SELECT configured FROM servers WHERE serverID = {0}".format(member.guild.id))
        record = self.myCursor.fetchone()
        if record[0] == '0':
            embed = discord.Embed(description = "Kindly contact a server admin to configure the bot and request them for the Teacher/Student role.\n\nIf you're a student, type **Yes** below.", color = default_color)
            try:
                await user.send(embed = embed)
            except:
                return
            def check(m):
                return m.content.lower() == 'yes' and m.channel == dmChannel and m.author == user
            try:
                msg = await self.client.wait_for('message', check=check, timeout = 600.0)
            except asyncio.TimeoutError:
                return
            if msg.content.lower() == 'yes':
                await self.getPersonalDetails(member, user, dmChannel)
                self.addToExistingTables(member)
            return
            
        serverInfo = getServerInfo(self.client, member.guild.id, self.myCursor)
        welcomeMessage = await serverInfo[1].send('Welcome {0}! React with :one: if you are a teacher and :two: if you are a student.'.format(member.mention))
        await welcomeMessage.add_reaction("1️⃣")
        await welcomeMessage.add_reaction("2️⃣")
        def check1(reaction, user):
            return reaction.message == welcomeMessage and user == member and (str(reaction.emoji) == '1️⃣' or str(reaction.emoji) =='2️⃣')
        reaction, user = await self.client.wait_for('reaction_add', check=check1)
        if reaction.emoji == '1️⃣':
            embed1 = discord.Embed(description = '{0} is requesting the {1} role. Kindly confirm their identity.'.format(member.mention, serverInfo[5].mention),
                                color = default_color)
            confirmationMessage = await serverInfo[3].send(embed = embed1)
            await confirmationMessage.add_reaction("✅")
            await confirmationMessage.add_reaction("❌")

            def check2(reaction, user):
                return reaction.message == confirmationMessage and user != self.client.user and (str(reaction.emoji) == '✅' or '❌')

            reaction, user = await self.client.wait_for('reaction_add', check=check2)
            if reaction.emoji == '✅':
                await member.add_roles(serverInfo[5])
                serverInfo[7].append(member)
                await confirmationMessage.delete()
                embed2 = discord.Embed(description = "Welcome to the teacher's lounge!",
                                color = default_color)
                await serverInfo[3].send(content = member.mention, embed=embed2)
            elif reaction.emoji == '❌':
                await member.kick()
        elif reaction.emoji == '2️⃣':
            await self.getPersonalDetails(member, user, dmChannel)
            await member.add_roles(serverInfo[4])
            self.addToExistingTables(member)
        await welcomeMessage.delete()

    # Add new students joining the server to all assignments that are still due
    def addToExistingTables(self, member):
        self.myCursor.execute("SELECT assignmentID, marksheet FROM assignments WHERE deadlineOver = '0' AND serverID = {0}".format(member.guild.id))
        dueAssignments = self.myCursor.fetchall()
        for i in dueAssignments:
            tableName = "assgn" + str(i[0])
            self.myCursor.execute("SELECT studentID FROM {0} WHERE studentID = {1}".format(tableName, member.id))
            record = self.myCursor.fetchone()
            if record is None:
                self.myCursor.execute("SELECT studentID FROM {0}".format(tableName, member.id))
                allStudents = self.myCursor.fetchall()
                self.myCursor.execute("SELECT studentTag, studentName, rollNo FROM students WHERE studentID = {0.id} AND serverID = {0.guild.id}".format(member))
                studentRecord = self.myCursor.fetchone()
                workbook = self.gc.open_by_key(i[1])
                worksheet = workbook.sheet1
                worksheet.update('A{0}'.format(len(allStudents)+2), [[len(allStudents)+1, studentRecord[0] + ' | ' + studentRecord[1], studentRecord[2]]])
                worksheet.columns_auto_resize(0, 4)
                self.myCursor.execute("INSERT INTO {0} (studentName, studentID, serverID) VALUES ('{1.name}#{1.discriminator}', '{1.id}', '{2}')".format(tableName, member, member.guild.id))
        self.myDB.commit()


    async def getPersonalDetails(self, member, user, dmChannel):
        # Check if student's record in same server already exists or not
        self.myCursor.execute("SELECT studentName, rollNo, email FROM students WHERE studentID = {0} AND serverID = {1}".format(member.id, member.guild.id))
        record = self.myCursor.fetchone()
        updation = False
        if record is not None:
            embed = discord.Embed(description = 'Your personal details are already present in the database.\n**Name:** {0}\n**Roll no.:** {1}\n**Email:** {2}\n\nDo you want to update them?\n**Enter Yes/No to confirm.**'.format(record[0], record[1], record[2]),
                                color = default_color)
            await member.send(embed = embed)
            def check(m):
                return (m.content.lower() == 'yes' or m.content.lower() == 'no') and m.channel == dmChannel and m.author == user
            msg = await self.client.wait_for('message', check=check)
            if msg.content.lower() == 'no':
                return
            updation = True
        # Get all the details
        embed = discord.Embed(description = 'Enter your full name below:',
                                color = default_color)
        await member.send(embed = embed)
        def check(m):
            return m.author == user and m.channel == dmChannel
        studentName = await self.client.wait_for('message', check=check)
        embed = discord.Embed(description = 'Enter your roll number:',
                            color = default_color)
        await member.send(embed = embed)
        def check(m):
            return m.author == user and m.channel == dmChannel
        studentRollNo = await self.client.wait_for('message', check=check)
        embed = discord.Embed(description = 'Enter your email address (school/institute email, if you have one):',
                            color = default_color)
        await member.send(embed = embed)
        def check(m):
            return m.author == user and m.channel == dmChannel
        email = await self.client.wait_for('message', check=check)
        embed = discord.Embed(description = "Here are your personal details which will be available to the teachers:\n**Name:** {0}\n**Roll no.:** {1}\n**Email:** {2}\n\n**Enter Yes/No to confirm these details.**".format(studentName.content, studentRollNo.content, email.content),
                            color = default_color)
        await member.send(embed = embed)
        def check(m):
            return (m.content.lower() == 'yes' or m.content.lower() == 'no') and m.channel == dmChannel and m.author == user
        msg = await self.client.wait_for('message', check=check)
        if msg.content.lower() == 'no':                         # User inputted "No", hence cancelling the submission
            embed = discord.Embed(description = "Re-enter the details.", color = red)
            await member.send(embed = embed)
            await self.getPersonalDetails(member, user, dmChannel)
            return
        # Decide whether to update existing record or add new record for student joining a server for the first time
        if updation == False:
            sqlInsert = "INSERT INTO students (studentName, studentTag, studentID, serverID, rollNo, email) VALUES('{0}', '{1.name}#{1.discriminator}', {1.id}, {2}, '{3}', '{4}')".format(studentName.content, user, member.guild.id, studentRollNo.content, email.content)
            self.myCursor.execute(sqlInsert)
        else:
            sqlUpdate = "UPDATE students SET studentName = '{0}', rollNo = '{1}', email = '{2}' WHERE studentID = '{3}' AND serverID = '{4}'".format(studentName.content, studentRollNo.content, email.content, user.id, member.guild.id)
            self.myCursor.execute(sqlUpdate)
        self.myDB.commit()
        embed = discord.Embed(description = "Details submitted. Welcome to the server!",
                            color = default_color)
        await member.send(embed = embed)

    # When a bot joins the server, it has to find a channel where it can send the message. If it can't write in any of the channels, it will DM the server owner.
    # embed1 is for the message in the server, embed2 is for the message to the owner.
    # Returns the channel to which the message was sent
    async def sendMessageToNewGuild(self, guild, embed1, embed2):
        posted = False
        for i in guild.channels:
            try:
                await i.send(embed = embed1)
                posted = True
                return i
            except:
                continue
        if posted == False:
            try:
                await guild.owner.send(embed = embed2)
                return guild.owner
            except:
                pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.myCursor.execute("SELECT welcomeChannelID, announcementsID, staffRoomChannelID, studentRoleID, teacherRoleID, configured FROM servers WHERE serverID = {0}".format(guild.id))
        record = self.myCursor.fetchone()
        print(record)
        if record is not None:
            channels = []
            for i in record[:3]:
                if i is not None:
                    channels.append("<#"+str(i)+">")
            roles = []
            for i in record[3:5]:
                if i is not None:
                    roles.append("<@&"+str(i)+">")
            embed = discord.Embed(title = "Currently configured channel(s) and role(s)",
                                  description = "Channels: {0}\nRoles: {1}\nKindly make sure the bot has `View Channel` and `Send Messages` permission for the above listed channels.\n\n**Type \"Done\" once you've done so.**".format(", ".join(channels), ", ".join(roles)),
                                  color = default_color)
            channel = await self.sendMessageToNewGuild(guild, embed, embed)
            def check(m):
                return (m.content.lower() == 'done') and m.channel == channel
            await self.client.wait_for('message', check=check)

        record = await checkIfConfigured(self.client, guild, self.myDB, self.myCursor)
        print(record)
        if record == False:
            # New server, no existing record, hence all channels/roles need to be configured
            embed1 = discord.Embed(description = "Kindly configure the bot for your server using the `c!config` command, before you can use all other commands.", color = default_color)
            embed2 = discord.Embed(description = "Kindly configure the bot for your server using the `c!config` command in the server, before you can use all other commands.\n\nMake sure the bot has access to the channel(s) and can write in it.", color = default_color)
            await self.sendMessageToNewGuild(guild, embed1, embed2)
        else:
            # record = [welcomeChannelID, announcementsID, staffRoomChannelID, studentRoleID, teacherRoleID, configured]
            if record[5] != 'True':
                # record exists, but server isn't fully configured or some channel is missing
                embed1 = discord.Embed(description = "Kindly re-configure the bot for your server using the `c!config` command, before you can use all other commands.", color = default_color)
                embed2 = discord.Embed(description = "Kindly re-configure the bot for your server using the `c!config` command in the server, before you can use all other commands.\n\nMake sure the bot has access to the channel(s) and can write in it.", color = default_color)
                await self.sendMessageToNewGuild(guild, embed1, embed2)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        self.myCursor.execute("SELECT welcomeChannelID, announcementsID, staffRoomChannelID FROM servers WHERE serverID = {0}".format(channel.guild.id))
        record = self.myCursor.fetchone()
        channels = ['welcomeChannelID', 'announcementsID', 'staffRoomChannelID']
        k = 0
        for i in record:
            if channel.id == i:
                sqlUpdate = "UPDATE servers SET {0} = NULL, configured = '0' WHERE serverID = {1}".format(channels[k], channel.guild.id)
                self.myCursor.execute(sqlUpdate)
                self.myDB.commit()
            k+=1

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        self.myCursor.execute("SELECT studentRoleID, teacherRoleID FROM servers WHERE serverID = {0}".format(role.guild.id))
        record = self.myCursor.fetchone()
        roles = ['studentRoleID', 'teacherRoleID']
        k = 0
        for i in record:
            if role.id == i:
                sqlUpdate = "UPDATE servers SET {0} = NULL, configured = '0' WHERE serverID = {1}".format(roles[k], role.guild.id)
                self.myCursor.execute(sqlUpdate)
                self.myDB.commit()
            k+=1