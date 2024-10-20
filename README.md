# Edu-Bot

Edu-Bot is an easy-to-use Discord bot designed to help teachers manage their classes and assist students in setting and tracking their personal goals. It provides functionality to keep track of assignments, lockdown text channels, and motivate students through inspirational quotes—all within the familiar environment of Discord.

This project was created for **LyonHacks 2022**. You can find the submission for it [here](https://devpost.com/software/edu-bot-xj7ugm)

You can watch the video demonstration on YouTube:


[![Watch the video](https://img.youtube.com/vi/t_xIZprR2jY/0.jpg)](https://www.youtube.com/watch?v=t_xIZprR2jY)




## Features

- **Motivation:** Provides inspirational quotes for both students and teachers.
- **Personal Goals:** Allows students to add and track their weekly goals.
- **Assignments:** Helps teachers post assignment information and due dates that students can view.
- **Channel Lockdown:** Lock down text channels when needed.
- **Study Rooms:** Automatically creates study room sessions, which are deleted after inactivity.
- **Blacklisted Words:** Flags and deletes certain words or phrases, sending a custom DM to the teacher if any inappropriate content is detected.
- **Moderation Tools:** Provides banning and kicking commands to manage students.

## Built With

- **Discord.py:** Main framework used for building the bot.
- **Python:** Core language for the bot’s logic.
- **SQLite:** Used to store and manage goals, assignments, and blacklisted phrases.
- **ZenQuotes API:** Provides inspirational quotes for motivational purposes.

## Accomplishments

- Successfully completed the bot with most of the planned functionality.
- Implemented error handling and database interactions for adding, displaying, and deleting values.

## Lessons Learned

- Gained experience with the discord.py library.
- Learned how to effectively work with SQLite databases, especially in terms of storing and displaying data for multiple users.
- Realized the importance of databases in managing user information for bots.
