from datetime import datetime, timedelta
from variables import *
import re

# Utility function to convert datetime object to string (hh:mm DD/MM/YY) or vice-versa, depending on type of parameter
def toggleTimeAndString(sampleTime):
    if isinstance(sampleTime, datetime):
        convertedString = (datetime.strftime(sampleTime, defaultTimeFormat))
        return convertedString
    elif isinstance(sampleTime, str):
        convertedTime = (datetime.strptime(sampleTime, defaultTimeFormat)).replace(tzinfo=IST)
        return convertedTime

# Convert time string (hh:mm DD/MM/YY) to a better formatted string
def beautifyTimeString(timeString):
    convertedTime = (datetime.strptime(timeString, defaultTimeFormat)).replace(tzinfo=IST)
    convertedString = (datetime.strftime(convertedTime, "%B %d, %Y,\n%I:%M %p IST"))
    return convertedString

def getChannel(client, arg):                    #PASS CHANNEL MENTION STRING, GET CHANNEL OBJECT
    channel_id = re.sub("[^0-9]", "", arg)
    channel = client.get_channel(int(channel_id))
    return channel

def getRole(guild, arg):                #PASS CHANNEL MENTION STRING, GET CHANNEL OBJECT
    role_id = re.sub("[^0-9]", "", arg)
    role = guild.get_role(int(role_id))
    return role

def getServerInfo(client, guildID, myCursor):
    myCursor.execute("SELECT welcomeChannelID, announcementsID, staffRoomChannelID, studentRoleID, teacherRoleID FROM servers WHERE serverID = {0}".format(guildID))
    record = myCursor.fetchone()
    server = client.get_guild(guildID)
    welcomeChannel = getChannel(client, str(record[0]))
    announcementChannel = getChannel(client, str(record[1]))
    teachersChannel = getChannel(client, str(record[2]))
    student = getRole(server, studentID)
    students = student.members
    teacher = getRole(server, teacherID)
    teachers = teacher.members
    serverInfo = [server, welcomeChannel, announcementChannel, teachersChannel, student, teacher, students, teachers]
    return serverInfo

# Function to check if server is configured and command comes from a teacher
def isConfiguredTeacher(ctx, myCursor):
    myCursor.execute("SELECT configured, teacherRoleID FROM servers WHERE serverID = {0}".format(ctx.guild.id))
    record = myCursor.fetchone()
    if record is None:
        return False
    if record[0] != 'True':
        return False
    for i in ctx.author.roles:
        if i.id == int(record[1]):
            return True
    return False

# Function to thoroughly re-check if server is configured
async def checkIfConfigured(client, guild, myDB, myCursor):
    myCursor.execute("SELECT welcomeChannelID, announcementsID, staffRoomChannelID, studentRoleID, teacherRoleID, configured FROM servers WHERE serverID = {0}".format(guild.id))
    record = myCursor.fetchone()
    if record is None:
        return False
    if record[5] != 'True':
        return False
    try: 
        await client.fetch_channel(int(record[0]))
    except:
        sqlUpdate = "UPDATE servers SET welcomeChannelID = NULL WHERE serverID = {0}".format(guild.id)
        myCursor.execute(sqlUpdate)
        myDB.commit()
