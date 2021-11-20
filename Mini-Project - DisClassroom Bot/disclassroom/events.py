#_______________________IMPORTING DISCORD.PY LIBRARIES_____________________#
import discord
from discord.ext import commands, tasks
from discord.ext.commands import *
#_______________________IMPORTING PROJECT FILES_____________________#
from variables import *
#______________________________ON EVENT_____________________________#
class onEvents(commands.Cog):
    def __init__(self, client, serverInfo):
        self.client = client
        # [server, entryChannel, teachersChannel, announcementChannel, student, teacher, students, teachers]
        # [0,      1,            2,               3,                   4,       5,       6,        7]
        self.serverInfo = serverInfo

    @commands.Cog.listener()
    async def on_member_join(self, member):
        welcomeMessage = await self.serverInfo[1].send('Welcome {0}! React with :one: if you are a teacher and :two: if you are a student.'.format(member.mention))
        await welcomeMessage.add_reaction("1️⃣")
        await welcomeMessage.add_reaction("2️⃣")

        def check1(reaction, user):
            return reaction.message == welcomeMessage and user == member and (str(reaction.emoji) == '1️⃣' or str(reaction.emoji) =='2️⃣')

        reaction, user = await self.client.wait_for('reaction_add', check=check1)
        if reaction.emoji == '1️⃣':

            embed1 = discord.Embed(description = '{0} is requesting the {1} role. Kindly confirm their identity.'.format(member.mention, self.serverInfo[5].mention),
                                color = default_color)
            confirmationMessage = await self.serverInfo[2].send(embed = embed1)
            await confirmationMessage.add_reaction("✅")
            await confirmationMessage.add_reaction("❌")

            def check2(reaction, user):
                return reaction.message == confirmationMessage and user != self.client.user and (str(reaction.emoji) == '✅' or '❌')

            reaction, user = await self.client.wait_for('reaction_add', check=check2)
            if reaction.emoji == '✅':
                await member.add_roles(self.serverInfo[5])
                self.serverInfo[7].append(member)
                await confirmationMessage.delete()
                embed2 = discord.Embed(description = "Welcome to the teacher's lounge!",
                                color = default_color)
                await self.serverInfo[2].send(content = member.mention, embed=embed2)
            elif reaction.emoji == '❌':
                await member.kick()
        elif reaction.emoji == '2️⃣':
            await member.add_roles(self.serverInfo[4])
        await welcomeMessage.delete()