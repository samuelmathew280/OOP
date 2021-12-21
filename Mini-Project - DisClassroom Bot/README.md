# DisClassroom Bot
DisClassroom is a Discord bot written in Python, created to help educational institutions with setting up their online learning platform on Discord.

It uses the following softwares/interfaces:
1. **Discord API** via discord.py
2. **Google Drive API** via pydrive
3. **Google Sheets API** via gspread
4. **MySQL** for DBMS
5. **Google Cloud** for its Virtual Private Server


Once the bot is configured for the server, students will be able to
<br />👁️ View their pending/all assignments
<br />📤 Submit an assignment, by uploading attachments
<br />♻️ Re-submit a previously submitted assignment

Teachers will be able to
<br />:student: View a student's personal information
<br />📝 Post an announcement/assignment
<br />📚 Review an assignment and check all submissions by students
<br />📋 Grade and release all marks, that will be privately sent to the students


Other key features:
1. Students will also receive reminders for assignments that have deadlines, in their DMs.
2. Role assignment when a new user joins the server is also handled by the bot. 
    <br />For the teacher's role, the bot will request confirmation from an admin/teacher already present in the server.
    <br />For the student's role, the bot will ask for details like name, roll number and email from the user, in DMs.
3. Announcements and assignments also accept attachments. This will allow teachers to share study material with students.


**Project developed by: Samuel Mathew (20BCS116).**
