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
    def __init__(self, client, db, cursor, serverInfo):
        self.client = client
        self.myDB = db
        self.myCursor = cursor
        # [server, entryChannel, teachersChannel, announcementChannel, student, teacher, students, teachers]
        # [0,      1,            2,               3,                   4,       5,       6,        7]
        self.serverInfo = serverInfo

    @commands.command()
    @commands.has_any_role(int(teacherID))
    async def ping(self, ctx):
        start_time = datetime.utcnow()
        message = await ctx.send(":ping_pong:")
        end_time = datetime.utcnow()
        ping = rdelta.relativedelta(end_time, start_time)
        embed = discord.Embed(description=':ping_pong: Pong! {0}ms'.format(round(ping.microseconds/1000)),
                            color=default_color)
        await message.edit(content = '', embed = embed)