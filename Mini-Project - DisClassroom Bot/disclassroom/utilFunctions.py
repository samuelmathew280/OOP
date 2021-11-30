from datetime import datetime, timedelta
from variables import *
import re

# Utility function to convert datetime object to string (YY/MM/DD hh:mm:ssTZ) or vice-versa, depending on type of parameter
def toggleTimeAndString(sampleTime):
    if isinstance(sampleTime, datetime):
        convertedString = (datetime.strftime(sampleTime, defaultTimeFormat))
        return convertedString
    elif isinstance(sampleTime, str):
        convertedTime = (datetime.strptime(sampleTime, defaultTimeFormat)).replace(tzinfo=IST)
        return convertedTime

# Convert time string (YY/MM/DD hh:mm:ssTZ) to a better formatted string
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
    student = getRole(server, str(record[3]))
    students = student.members
    teacher = getRole(server, str(record[4]))
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

# Function to thoroughly re-check if server is configured. Adds the server to the database and returns False if the server does not exist in the database (table: 'servers') OR returns the updated entry of the server in the database, after checking if every ID present in valid or not.
# Do not call this function frequently, as it makes several API calls. Only use when bot joins a server/c!config is used.
async def checkIfConfigured(client, guild, myDB, myCursor):
    myCursor.execute("SELECT welcomeChannelID, announcementsID, staffRoomChannelID, studentRoleID, teacherRoleID, configured FROM servers WHERE serverID = {0}".format(guild.id))
    record = myCursor.fetchone()
    if record is None:
        myCursor.execute("INSERT INTO servers (serverID, joinTime) VALUES ({0}, '{1}')".format(guild.id, toggleTimeAndString(datetime.now(IST))))
        myDB.commit()
        return False
    if record[5] != 'True':
        return False
    # Once record has been obtained and 'configured' field is set to 'True', meaning all other fields are filled too, we check if the existing IDs in the database are still valid and if those channels/roles still exist and are accessible.
    # If not, the field is set to NULL again, server becomes un-configured and server admin will have to re-configure that field.
    try: 
        await client.fetch_channel(int(record[0]))
    except:
        sqlUpdate = "UPDATE servers SET welcomeChannelID = NULL, configured = '0' WHERE serverID = {0}".format(guild.id)
        myCursor.execute(sqlUpdate)
        myDB.commit()
    try: 
        await client.fetch_channel(int(record[1]))
    except:
        sqlUpdate = "UPDATE servers SET announcementsID = NULL, configured = '0' WHERE serverID = {0}".format(guild.id)
        myCursor.execute(sqlUpdate)
        myDB.commit()
    try: 
        await client.fetch_channel(int(record[2]))
    except:
        sqlUpdate = "UPDATE servers SET staffRoomChannelID = NULL, configured = '0' WHERE serverID = {0}".format(guild.id)
        myCursor.execute(sqlUpdate)
        myDB.commit()
    try: 
        guild.get_role(int(record[3]))
    except:
        sqlUpdate = "UPDATE servers SET studentRoleID = NULL, configured = '0' WHERE serverID = {0}".format(guild.id)
        myCursor.execute(sqlUpdate)
        myDB.commit()
    try: 
        guild.get_role(int(record[4]))
    except:
        sqlUpdate = "UPDATE servers SET teacherRoleID = NULL, configured = '0' WHERE serverID = {0}".format(guild.id)
        myCursor.execute(sqlUpdate)
        myDB.commit()
    myCursor.execute("SELECT welcomeChannelID, announcementsID, staffRoomChannelID, studentRoleID, teacherRoleID, configured FROM servers WHERE serverID = {0}".format(guild.id))
    record = myCursor.fetchone()
    return record