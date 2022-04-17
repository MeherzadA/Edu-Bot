import discord

import sqlite3

from inspire import get_inspire
from validDate import checkDate
from discord.ext import commands
# from nextcord.ext import commands

import os
import asyncio

censorCon = sqlite3.connect('censor.db')
censorCur = censorCon.cursor()
censorCur.execute('''CREATE TABLE IF NOT EXISTS censor
                  (phrase text)''')

assignmentCon = sqlite3.connect('assignments.db')
assignmentCur = assignmentCon.cursor()
assignmentCur.execute('''CREATE TABLE IF NOT EXISTS assignments
            (assignment_name text, description text, duedate text)''')

goalCon = sqlite3.connect('goals.db')
goalCur = goalCon.cursor()
goalCur.execute('''CREATE TABLE IF NOT EXISTS goalsPerUser
            (username text, goal text PRIMARY KEY)''')

client = commands.Bot(command_prefix="e!")


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.command()
async def testPing(ctx):
    await ctx.send(f"Hi this command works, {ctx.author.mention}")


@client.group(invoke_without_command=True)
async def goal(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f'{ctx.author.mention} Goal commands: `add`, `delete`, `current`')


@goal.command(name='add')
async def goalAdd(ctx):
    await ctx.send(f"{ctx.author.mention}, Please enter the name of the goal to be created:")

    try:
        msg = await client.wait_for('message', check=lambda message: message.author.id == ctx.author.id, timeout=25.0)
        if len(msg.content) <= 1024:
            goalCur.execute('insert or ignore into goalsPerUser (username, goal) values (?, ?)',
                            (str(ctx.author), str(msg.content)))
            goalCon.commit()
            await ctx.send(f'{ctx.author.mention} the goal ``{msg.content}`` was sucessfully added!')
            print()
            for row in goalCur.execute('''SELECT * FROM goalsPerUser'''):
                print(row)
        else:
            await ctx.send(f'{ctx.author.mention}, the goal created is too long! Retry with a goal less than or equal to 1024 characters!\n(Current length is ``{len(msg.content)}`` characters)')

        # await ctx.send(f"{ctx.author.mention}, Please enter the goal to be created:")


    except asyncio.TimeoutError:
        await ctx.send(f'{ctx.author.mention}, you timed out!')


@goal.command(name='current', aliases=['cur'])
async def goalCurrent(ctx):
    count = 0
    embed = discord.Embed(title=f"{ctx.author}'s Goals", color=0x00f00)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    for row in goalCur.execute('''SELECT * FROM goalsPerUser'''):
        if str(ctx.author) in row:
            count += 1
            goal = ":regional_indicator_g::regional_indicator_o::regional_indicator_a::regional_indicator_l:"
            embed.add_field(name=f"{goal}   {count}", value=row[1], inline=False)
    await ctx.send(embed=embed)


@goal.command(name='delete', aliases=['del'])
async def goalDelete(ctx, *, nameOfGoal):
    for row in goalCur.execute('''SELECT * FROM goalsPerUser'''):
        if str(ctx.author) in row:
            print()
            print(row)
            goalCur.execute("SELECT * FROM goalsPerUser WHERE goal = ?", (nameOfGoal,))
            data = goalCur.fetchall()
            print(len(data))
            if len(data) == 0:
                await ctx.send(f'{ctx.author.mention} There is no goal named that!')
            else:
                goalCur.execute("DELETE FROM goalsPerUser WHERE username = ? and goal = ?",
                                (str(ctx.author), str(nameOfGoal)))
                goalCon.commit()
                await ctx.send(
                    f"{ctx.author.mention}, Goal ``{nameOfGoal}`` succesfully deleted! Congrats on completing it! (I hope)")


@client.command()
async def inspire(ctx):
    quote, author = get_inspire()
    embed = discord.Embed(title=author, description=f'"{quote}"', color=0x00f00)
    await ctx.send(embed=embed)


@client.group(invoke_without_command=True)
async def studyvc(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f'{ctx.author.mention} VC commands: `open`, `close`')


@studyvc.command(name='open')
async def openVC(ctx, subject):
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name='Study Channels')
    if not category:
        category = await guild.create_category('Study Channels')
    vc = await guild.create_voice_channel(f"{ctx.author}'s {subject} Study Room", category=category)
    await ctx.send(f'{ctx.author.mention} Your study VC has been opened.')
    await asyncio.sleep(30)
    while len(vc.members) > 0:
        await asyncio.sleep(30)
    await vc.delete()
    await ctx.send(f'{ctx.author.mention} Your study VC has closed due to inactivity.')


@studyvc.command(name='close')
@commands.has_permissions(administrator=True)
async def closeVC(ctx, channel_id: int):
    channel = client.get_channel(channel_id)
    await channel.delete()
    await ctx.send(f'{ctx.author.mention}, VC ``{channel}`` has been deleted!')


@client.group(invoke_without_command=True, description='A command for teachers to create and delete assignments, as well as their due date! Students can also view the asssignments posted!')
async def assignment(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f'{ctx.author.mention} Assignment commands: `new`, `delete`, `current`')


@assignment.command(name='new')
@commands.has_permissions(administrator=True)
async def assignmentNew(ctx):
    await ctx.send(
        f"{ctx.author.mention}, Please enter the name of the assignment to be created (Enter .exit at any point during the next few steps to exit this procedure):")
    try:
        assignmentName = await client.wait_for('message', check=lambda message: message.author.id == ctx.author.id,
                                               timeout=25.0)
        if assignmentName.content == '.exit':
            await ctx.send(f"Exiting assignment creation...")
            pass
        else:
            await ctx.send(
                f"{ctx.author.mention}, Please provide a brief description of assignment or external link to assignment page:")
            try:
                assignmentDesc = await client.wait_for('message',
                                                       check=lambda message: message.author.id == ctx.author.id,
                                                       timeout=120.0)
                if assignmentDesc.content == '.exit':
                    await ctx.send(f"Exiting assignment creation...")
                    pass
                else:
                    await ctx.send(
                        f"{ctx.author.mention}, Please enter due date of assignment! (YYYY-MM-DD H:M PM/AM Example: ``2022-07-09 5:45 PM``)")
                    try:
                        submission = await client.wait_for('message',
                                                           check=lambda message: message.author.id == ctx.author.id,
                                                           timeout=25.0)
                        if submission.content == '.exit':
                            await ctx.send(f"Exiting assignment creation...")
                            pass
                        else:
                            date_check_message = checkDate(str(submission.content))
                            print(submission.content)
                            if date_check_message == 'Success!':
                                assignmentCur.execute(
                                    'insert or ignore into assignments (assignment_name, description, duedate) values (?, ?, ?)',
                                    (str(assignmentName.content), str(assignmentDesc.content), str(submission.content)))
                                assignmentCon.commit()
                                print()
                                for row in assignmentCur.execute('''SELECT * FROM assignments'''):
                                    print(row)

                                await ctx.send(f"Sucessfully created assignment ``{assignmentName.content}``!")

                            else:
                                await ctx.send(f"{ctx.author.mention}, {date_check_message}")

                    except asyncio.TimeoutError:
                        await ctx.send(f"{ctx.author.mention}, You timed out!")
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention}, You timed out!")
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, You timed out!")


@assignment.command(name='current', aliases=['cur'])
async def assignmentCurrent(ctx):
    serverName = ctx.guild
    embed = discord.Embed(title=f"{serverName} Assignments", color=0x00f00)
    for row in assignmentCur.execute('''SELECT * FROM assignments '''):
        message = checkDate(row[2])
        if message == 'Date not valid! Enter a date that is not in the past!':
            embed.add_field(name=f"{row[0]} - WAS DUE:  {row[2]}   :x:", value=row[1], inline=False)
        elif message == 'Success!':
            embed.add_field(name=f"{row[0]} - DUE:  {row[2]}   :white_check_mark:", value=row[1], inline=False)
    await ctx.send(embed=embed)


@assignment.command(name='delete', aliases=['del'])
@commands.has_permissions(administrator=True)
async def assignmentDel(ctx, *, nameOfAssignment):
    for row in assignmentCur.execute('''SELECT * FROM assignments'''):
        print(row)
        assignmentCur.execute("SELECT * FROM assignments WHERE assignment_name = ?", (nameOfAssignment,))
        data = assignmentCur.fetchall()
        print("length:")
        print(len(data))
        if len(data) == 0:
            await ctx.send(f'{ctx.author.mention} There is no assignment named that!')
        else:
            assignmentCur.execute("DELETE FROM assignments WHERE assignment_name = ?", ((nameOfAssignment,)))
            assignmentCon.commit()
            await ctx.send(f"{ctx.author.mention}, Assignment ``{nameOfAssignment}`` succesfully removed!")

@client.group(invoke_without_command=True, description = 'Blacklist words and you will become notified when a user says any of them! (They will also be auto-deleted)')
async def censor(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send(f'{ctx.author.mention} Censor commands: `censorAdd`, `censorDel`, `censorCurrent`')




@client.command()
@commands.has_permissions(administrator=True)
async def censorAdd(ctx, *, phrase):
    censorCur.execute('insert or ignore into censor (phrase) values (?)', (phrase,))
    censorCon.commit()
    await ctx.send("Phrase blacklisted!")
    await ctx.message.delete()


@client.command()
@commands.has_permissions(administrator=True)
async def censorCurrent(ctx):
    embed = discord.Embed(title=f"__**BLACKLISTED PHRASES**__", color=0x00f00)
    for row in censorCur.execute('''SELECT * FROM censor '''):
        embed.add_field(name=f"•{row[0]}", value=":x:", inline=False)
    await ctx.send(embed=embed)


@client.command()
@commands.has_permissions(administrator=True)
async def censorDel(ctx, *, phrase):
    for row in censorCur.execute('''SELECT * FROM censor'''):
        censorCur.execute("SELECT * FROM censor WHERE phrase = ?", (phrase,))
        data = censorCur.fetchall()
        # print("length:")
        # print(len(data))
        if len(data) == 0:
            await ctx.send(f'{ctx.author.mention} There is no phrase named that!')
        else:
            censorCur.execute("DELETE FROM censor WHERE phrase = ?", ((phrase,)))
            censorCon.commit()
            await ctx.send(f"{ctx.author.mention}, Phrase succesfully whitelisted!")


# @client.command()
# @commands.has_permissions(manage_messages=True)
# async def mute(ctx, member: discord.Member, *, reason=None):
    # guild = ctx.guild
    # muted_role = discord.utils.get(guild.roles, name='Bad Student')

    # Creating bad student role if it doesnt already exist
    # if not muted_role:
    #     await guild.create_role(name='Bad Student')

        # Going through each channel and changing the permissions of it
    #     for channel in guild.text_channels:
    #         await channel.set_permissions(muted_role, speak=False, send_messages=False, read_messages=False)
    # await member.add_roles(muted_role)
    # await ctx.send(f"{member.mention} has been muted!")
    # await member.send(f"You have been muted in the **{guild}** server for ``{reason}!``")


# @client.command()
# @commands.has_permissions(manage_messages=True)
# async def unmute(ctx, member: discord.Member):
#     muted_role = discord.utils.get(ctx.guild.roles, name='Bad Student')
#     await member.remove_roles(muted_role)
#     await ctx.send(f"Unmuted {member.mention}!")


@client.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    await member.send(f"You have been kicked from the **{guild}** server for ``{reason}``")
    await member.kick()
    await ctx.send(f"{member.mention} has been kicked from the server!")


@client.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    guild = ctx.guild
    await member.send(f"You have been banned from the **{guild}** server for ``{reason}``")
    await member.ban()
    await ctx.send(f"{member.mention} has been banned from the server! ")


# @client.command()
# @commands.has_permissions(administrator=True)
# async def attendance(ctx, code):
#   guild = ctx.guild
#   await ctx.send(f"{ctx.message.guild.default_role} attendance is starting! Verify your presence by responding with code ``{code}`` in the next 2 minutes or you will be marked absent!")

# await member.send(f"You have been banned from the **{guild}** server for ``{reason}``")
# await member.ban()
# await ctx.send(f"{member.mention} has been banned from the server! ")


@client.command()
@commands.has_permissions(administrator=True)
async def lockdown(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages = False)
    await ctx.send(f"{ctx.channel.mention} ***is now in lockdown.***")


@client.command()
@commands.has_permissions(administrator=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(ctx.channel.mention + " ***has been unlocked.***")


@client.event
async def on_message(message):
    owner_id = message.guild.owner_id
    owner = await client.fetch_user(owner_id)
    # Only gets id of server owner, not the acc discord tag and stuff
    print(owner)
    serverName = message.guild
    if any(phrase[0] in message.content.lower() for phrase in censorCur.execute('''SELECT * FROM censor''')):
        await message.delete()
        await owner.send(
            f"User @{message.author} has just said *blacklisted word* ||{message.content}|| in **{serverName}** in channel ``{message.channel}``")
        await message.channel.send(f"{message.author.mention}, DM sent to teacher regarding usage of blacklisted word!")
    await client.process_commands(message)
# @unmute.error
# @mute.error
@closeVC.error
@unlock.error
@lockdown.error
@ban.error
@kick.error
@assignmentNew.error
@assignmentDel.error
@censorDel.error
@censorAdd.error
@censorCurrent.error
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{ctx.author.mention}, You do not have permission to use this command!")


@goalDelete.error
@openVC.error
@closeVC.error
@assignmentDel.error
@censorAdd.error
@censorDel.error
@ban.error
@kick.error
async def on_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "**Please input some more arguments!**\ngoal delete ``<name of goal>``\nstudyvc open ``<subject>`` \nstudyvc close ``<vc id>``\nassignment delete ``<name of assignment>``\ncensorAdd ``<phrase to blacklist>``\ncensorDel ``<phrase to whitelist>``\nban ``<user>``\nkick ``<user>``")

        # try:
    #   msg = await client.wait_for('message', check = lambda message: message.author.id == ctx.author.id, timeout = 25.0)
    #   goalCur.execute('insert or ignore into goalsPerUser (username, goal) values (?, ?)', (str(ctx.author), str(msg.content)))
    #   goalCon.commit()
    #   await ctx.send(f'{ctx.author.mention} the goal ``{msg.content}`` was sucessfully added!')

    #   for row in goalCur.execute('''SELECT * FROM goalsPerUser'''):
    #     print(row)

    # except:
    #   quote, author = get_inspire()
    #   embed = discord.Embed(title= author, description = f'"{quote}"', color = 0x00f00)
    #   await ctx.send(embed = embed)
    # embed.add_field(name=f"{goal}   {count}", value=row[1], inline=False)

    # if str(nameOfGoal) in row:
    #   goalCur.execute("DELETE FROM goalsPerUser WHERE username = ? and goal = ?", (str(ctx.author), str(nameOfGoal)))
    #   goalCon.commit()
    #   await ctx.send("Goal succesfully deleted! Congrats on completing them! (I hope) also also")
    #   await ctx.send(nameOfGoal)
    # else:
    #   await ctx.send(nameOfGoal)

    # for row in goalCur.execute('''SELECT * FROM goalsPerUser'''):
    #   print(row)

    # except:
    #   await ctx.send("nah")


client.run(os.environ['TOKEN'])