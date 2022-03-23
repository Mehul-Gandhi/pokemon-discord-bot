import os
import json
import io
from datetime import date, datetime
import contextlib
import random
import asyncio
import math
import discord
from discord.ext import commands
from discord.ext.commands import ConversionError
import textwrap
import time
from random import choice
from discord_slash import SlashCommand  # Importing the newly installed library.
from discord_slash import cog_ext, SlashContext
from pathlib import Path
from util import clean_code, Pag
from traceback import format_exception
from async_timeout import timeout
import sys
from udpy import UrbanClient
import datetime
import ast
from discord_slash.utils.manage_commands import create_option
import functools
import operator
from pathlib import Path
from random import sample
from asyncio import sleep
from pathlib import Path
from private.config import token  # secret bot token in the private folder

import asyncpg

from datetime import date, datetime
from ratelimiter import RateLimiter
from youtubesearchpython import VideosSearch

intents = discord.Intents.default()
intents.members = True
intents.presences = True
pingas = UrbanClient()

DEFAULT_PREFIX = ","


async def get_prefix(bot, message):
    """Uses PostgreSQL to retrieve the prefix used in a guild. The default prefix is ',' which can be changed
    by an administrator of the guild or the bot owner. """
    if not message.guild:
        return commands.when_mentioned_or(DEFAULT_PREFIX)(bot, message)
    prefix = await client.pg_con.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", message.guild.id)
    if len(prefix) == 0:
        await client.pg_con.fetch("INSERT INTO guilds (guild_id, prefix) VALUES ($1, $2)", message.guild.id,
                                  DEFAULT_PREFIX)
        prefix = DEFAULT_PREFIX
    else:
        prefix = prefix[0].get("prefix")
    return commands.when_mentioned_or(prefix)(bot, message)


client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, help_command=None, intents=intents)

# client.add_cog(music(client))
slash = SlashCommand(client, sync_commands=True)
Bot = client
client.load_extension("cogs.pokemon")
client.load_extension("cogs.blackjack")
client.load_extension("cogs.information")  # in poke.py
client.load_extension("cogs.anime")  # in poke.py
client.load_extension("cogs.math")
client.load_extension("cogs.music_cog")
client.load_extension("cogs.search")  # in poke.py
client.load_extension("cogs.help")
client.load_extension("cogs.poll")
client.load_extension("cogs.misc")
client.load_extension("cogs.message")
client.load_extension("cogs.games")
client.load_extension("cogs.tcg")
client.load_extension("cogs.trainer")
client.load_extension("cogs.tictactoe")


async def create_db_pool():
    """Connects to the local PostgreSQL server."""
    client.pg_con = await asyncpg.create_pool(database='postgres', user='postgres', password='Mehul09!')


@client.event
async def on_ready():
    activity = discord.Game(name=".help")
    await client.change_presence(status=discord.Status.online, activity=activity)
    await create_db_pool()
    print("We have logged in as Dragonite.")


@client.command()
async def ping(ctx):
    """Returns the client latency."""
    await ctx.send(f"Pong! {round(client.latency * 1000)} ms")


@client.listen()
async def on_message(message):
    """Used for level and total number of posts for the
    command xp (gald) in poke file. Stores the total number of posts a user has posted."""

    try:
        user = await client.pg_con.fetchrow("SELECT * FROM users WHERE id = $1", message.author.id)
        await client.pg_con.execute("UPDATE users SET total = $1 WHERE id = $2 ", user['total'] + 1,
                                    message.author.id)  # updates gald by one
        growth = lambda n: ((n ** 3 * (100 - n)) / 50) / 3 if n < 100 else float('inf')  # 200K exp needed for level 100
        if user['total'] > growth(user['level']):  # if the user can level up based on the formula for growth.
            await client.pg_con.execute("UPDATE users SET level = $1 WHERE id = $2 ", user['level'] + 1,
                                        message.author.id)  # updates gald by one
    except:
        pass


""""A dictionary that stores the users who are currently away from keyboard."""
afkdict = {}


@client.listen()
async def on_message(message):
    """If a discord member says 'brb', the discord member is added to the afkdict."""
    if message.author == client.user:
        return
    if "brb" == message.content.lower():
        afkdict[message.author] = "brb'd"


@client.listen()
async def on_message(message):
    """If a member in the afkdict sends a message, they are removed from the
    afkdict and are no longer afk. If a member is mentioned and that member is
    afk, the pinger is notified."""
    global afkdict
    if message.author in afkdict:
        afkdict.pop(message.author)

    for member in message.mentions:
        if member != message.author:
            if member in afkdict:
                afkmsg = afkdict[member]
                await message.channel.send(f"Oh noes! {member} is afk. afk message: {afkmsg}")
    await client.process_commands(message)


@client.command()
async def afk(ctx, *, reason=None):
    """A command that allows users to set their afk status. If the user is pinged while
    they are afk, the pinger is notified that the user is afk."""
    afkdict[ctx.author] = reason
    await ctx.send("You are now afk.")


####PREFIXES#####

@client.listen()
async def on_message(message):
    print(message.author.name + ": " + message.content)


@client.command()
async def prefix(ctx, new_prefix):
    if ctx.author.guild_permissions.administrator == True or ctx.author.id == 203020214332424192 or ctx.author.id == 254833853112254464:
        await client.pg_con.execute("UPDATE guilds SET prefix = $1 WHERE guild_id = $2", new_prefix, ctx.guild.id)
        await ctx.send("The server prefix is now " + str(new_prefix))


# client.loop.run_until_complete(create_db_pool())

###############
##REMINDERS####
###############
@client.event
async def on_message(message):
    """Sends a message to a user if they have a message in their inbox and nrm is not toggled.
    More details in cogs.message"""
    user = await client.pg_con.fetch("SELECT * FROM message WHERE id = $1", message.author.id)  # member.id)
    if user and len(user[0]['msg']) > 0 and user[0]['nrm'] == False:
        msg = user[0]['msg']
        length = len(msg)
        await client.pg_con.execute("UPDATE message SET msg = array_remove (msg, $1) where id = $2", msg[0],
                                    message.author.id)
        await client.pg_con.execute("UPDATE message SET archive = array_append (archive, $1) where id = $2",
                                    msg[0], message.author.id)  # stores all messages in the archive
        await message.channel.send(
            f" {message.author.mention}, {msg[0]}. You have {length - 1} messages remaining in your inbox.")
    else:
        pass


#################
# EVAL FUNCTION###
#################
def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


@client.command(aliases=['eval'])
@commands.is_owner()
async def eval_fn(ctx, *, cmd):
    """Evaluates input.
    Input is interpreted as newline seperated statements.
    If the last statement is an expression, that is the return value.
    Usable globals:
      - `bot`: the bot instance
      - `discord`: the discord module
      - `commands`: the discord.ext.commands module
      - `ctx`: the invokation context
      - `__import__`: the builtin `__import__` function
    Such that `>eval 1 + 1` gives `2` as the result.
    The following invokation will cause the bot to send the text '9'
    to the channel of invokation and return '3' as the result of evaluating
    >eval ```
    a = 1 + 2
    b = a * 2
    await ctx.send(a + b)
    a
    ```
    """
    fn_name = "_eval_expr"

    cmd = cmd.strip("` ")

    # add a layer of indentation
    cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

    # wrap in async def body
    body = f"async def {fn_name}():\n{cmd}"

    parsed = ast.parse(body)
    body = parsed.body[0].body

    insert_returns(body)

    env = {
        'bot': ctx.bot,
        'discord': discord,
        'commands': commands,
        'ctx': ctx,
        '__import__': __import__
    }
    exec(compile(parsed, filename="<ast>", mode="exec"), env)
    await ctx.send("```input: \n"
                   "" + str(cmd) + "```")
    result = (await eval(f"{fn_name}()", env))


@client.command(name="evaluate", aliases=["e"])
@commands.is_owner()
async def _eval(ctx, *, code):
    code = clean_code(code)

    local_variables = {
        "discord": discord,
        "commands": commands,
        "bot": client,
        "ctx": ctx,
        "channel": ctx.channel,
        "author": ctx.author,
        "guild": ctx.guild,
        "message": ctx.message,
        "client": client
    }

    stdout = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout):
            exec(
                f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
            )

            obj = await local_variables["func"]()
            result = f"{stdout.getvalue()}\n-- {obj}\n"
    except Exception as e:
        result = "".join(format_exception(e, e, e.__traceback__))

    pager = Pag(
        timeout=100,
        entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
        length=1,
        prefix="```py\n",
        suffix="```"
    )
    await ctx.send(f"```py\n"
                   f"#input:\n"
                   f"{code}```")
    await pager.start(ctx)


@slash.slash(name='remind', description='Remind someone a message through the bot ', options=[create_option(
    name="member",
    description="This is the first option we have.",
    option_type=6,
    required=True),
    create_option(name='message', description='message to send to user.', option_type=3, required=True)])
async def _rm(ctx: SlashContext, member: discord.Member, message: str):
    """A slash command for reminding another user a message. The prefix command version is in
     cogs.message """
    assert len(message) < 300, await ctx.send("The given message is too long to send :frowning: ")
    assert len(message) > 0, await ctx.send("The given message is too short to send :frowning:")
    member = ctx.author if member is None else member
    user = await client.pg_con.fetch("SELECT * FROM message WHERE id = $1", member.id)
    usage = await client.pg_con.fetch("SELECT * from tusage where cmd = $1", 'rm')
    if not user:
        await client.pg_con.execute("INSERT INTO message (id) VALUES ($1) ", member.id)
        user = await client.pg_con.fetch("SELECT * FROM message WHERE id = $1", member.id)
    if len(user[0]['msg']) > 9:
        await ctx.send("The user's inbox is full :frowning: ")
        return
    if ctx.author.id in user[0]['blocks']:
        await ctx.send(f"{member.display_name} has you blocked :frowning: ")
        return
    rm_number = usage[0]['usage'] + 1
    message_to_send = f"{ctx.author}  sent you a message saying: ** {message}  **  (reminder #{rm_number}) [change this alert with the nrm command]"
    await client.pg_con.execute("UPDATE message SET msg = array_append (msg, $1) where id = $2", message_to_send,
                                member.id)
    await client.pg_con.execute("UPDATE tusage SET usage = $1 where cmd = $2", rm_number,
                                'rm')  # reminder message number
    await ctx.send(f"I will remind {member.display_name} the message :smile: ")


def convertTuple(tup):
    str = functools.reduce(operator.add, (tup))
    return str


@slash.slash(name='urban', description='Search a word on urban dictionary. ', options=[create_option(
    name="word",
    description="Word to lookup",
    option_type=3,
    required=True)])
async def _urban(ctx: SlashContext, *, word: str):
    message = word
    "Search the urban dictionary for the slang meaning of a word."
    string = convertTuple(word)

    # print(string)
    if string != 'random':
        word = string
    else:  # if the inputted word = random, then a random word is chosen to be looked up.
        message = pingas.get_random_definition()[0].word
        word = message
    # print("word: " + word)
    defs = pingas.get_definition(message)[0].definition
    print(defs)
    example = pingas.get_definition(message)[0].example
    # print("example: " + example)
    upvotes = pingas.get_definition(message)[0].upvotes
    downvotes = pingas.get_definition(message)[0].downvotes
    # print(upvotes)
    # print(downvotes)
    embedVar = discord.Embed(title="Urban Dictionary", color=0xe67e22)
    embedVar.add_field(name="Word", value=str(word), inline=False)
    embedVar.add_field(name="Definition", value=str(defs), inline=False)
    embedVar.add_field(name="Example", value=str(example), inline=False)
    embedVar.add_field(name=":thumbsup:", value=str(upvotes), inline=True)
    embedVar.add_field(name=":thumbsdown:", value=str(downvotes), inline=True)
    await ctx.send(embed=embedVar)


@slash.slash(name='youtube', description='Search up a youtube video ', options=[create_option(
    name="search",
    description="Search term.",
    option_type=3,
    required=True)])
async def youtube(ctx: SlashContext, search: str):
    "Search youtube for videos."
    message = search
    videosSearch = VideosSearch(str(message), limit=3)
    answers = [0, 1]  # put only zero for most relevant searches
    id = videosSearch.result()['result'][random.choice(answers)]['id']
    await ctx.send("https://www.youtube.com/watch?v=" + str(id))


@slash.slash(name='define', description='Search up a word in the user defined dictionary ', options=[create_option(
    name="word",
    description="Word.",
    option_type=3,
    required=True), create_option(name='definition', description='Set definition.', option_type=3, required=False)])
async def define(ctx, word: str, definition: str = None):
    """A user-defined dictionary. Each word can have a unique definition for each guild."""
    assert '<@!' not in word, await ctx.send("Don't be annoying :frowning: ")  # cannot ping people in definitions
    today = date.today()
    now = datetime.now()
    if definition == None:
        lookup = True
    elif definition != None:
        lookup = False
    else:
        if len(word) > 90:
            await ctx.send("The given word is too long to define.")
            return
        if len(definition) > 500:  # avoid spamming
            await ctx.send("The given definition is too long.")
            return
        # words of length less than 3 cannot be defined.
        if len(definition) < 4:
            await ctx.send("The given definition is too short.")
            return
        if len(definition) == 0:
            await ctx.send("You must define the word.")
            return
    in_dict = await client.pg_con.fetch("SELECT * FROM dict WHERE word = $1 and guildid = $2", word.lower(),
                                        ctx.guild.id)
    try:
        owner = ctx.guild.get_member(in_dict[0]['id'])
    except:
        owner = ctx.author
    try:
        owner.id
        left_server = False
    except:
        left_server = True
    if not in_dict and lookup == False and left_server == False:
        await client.pg_con.execute("INSERT INTO dict (word, def, date, id, guildid) VALUES ($1, $2, $3, $4, $5) ",
                                    word.lower(), definition, today.strftime("%B %d, %Y ") + now.strftime("%H:%M:%S"),
                                    ctx.author.id, ctx.guild.id)
        await ctx.send("I have now defined **" + str(word) + " **")
        return
    elif in_dict and lookup == False and left_server == True:  # when owner of word left the server and another person redefines the word
        # await ctx.send('test')
        await client.pg_con.execute("DELETE FROM dict WHERE word = $1 and guildid = $2", word, ctx.guild.id)
        await client.pg_con.execute("INSERT INTO dict (word, def, date, id, guildid) VALUES ($1, $2, $3, $4, $5) ",
                                    word.lower(), definition,
                                    today.strftime("%B %d, %Y ") + now.strftime("%H:%M:%S"),
                                    ctx.author.id, ctx.guild.id)
        await ctx.send("I have now updated the word (previous owner of word left the server) **" + str(word) + " **")
        return
    elif not in_dict and lookup == True:
        await ctx.send("**" + str(
            word) + "** is not defined. You can define it using <prefix>def <word or phrase> as <word or phrase>")
        return
    dict = await client.pg_con.fetch("SELECT * FROM dict WHERE word = $1 and guildid = $2", word.lower(), ctx.guild.id)
    if dict[0]['id'] == ctx.author.id and lookup == False:  # when owner of word redefines their own word
        await client.pg_con.execute(
            "UPDATE dict SET def = $2, date = $3, id = $4  WHERE word = $1 and guildid = $5 ", word.lower(), definition,
            today.strftime("%B %d, %Y ") + now.strftime("%H:%M:%S"), ctx.author.id,
            ctx.guild.id)  # updates gald by one
        # await client.pg_con.execute("INSERT INTO dict (word, def, date, id) VALUES ($1, $2, $3, $4) ", word, definition, today.strftime("%B %d, %Y ") + now.strftime("%H:%M:%S"), ctx.author.id)
        await ctx.send("I have now redefined " + str(word))
    # elif 'as' not in message:
    else:
        embed = discord.Embed(color=discord.Color.orange())
        try:
            embed.add_field(name="Defined by", value=ctx.guild.get_member(dict[0]['id']).display_name)
            await ctx.send("** " + dict[0]['word'] + " ** means " + dict[0]['def'])
            embed.add_field(name='Date defined', value=dict[0]['date'])
            await ctx.send(embed=embed)
        except:
            embed.add_field(name="Defined by",
                            value=in_dict[0]['id'])  # person that defined the word has left the server
            await ctx.send("** " + dict[0]['word'] + " ** means " + dict[0]['def'])
            embed.add_field(name='Date defined', value=dict[0]['date'])
            embed.add_field(name="Information",
                            value="Since the word's owner has left the server, this word can be redefined using <prefix>define <word or phrase> as <word or phrase>")

            await ctx.send(embed=embed)


@client.command()
async def invite(ctx):
    embed = discord.Embed(title="Here's the link to invite me to your server :smile:", color=discord.Color.orange())
    embed.add_field(name='Server Invite Link',
                    value='  https://discord.com/api/oauth2/authorize?client_id=779219727582756874&permissions=0&scope=bot%20applications.commands')
    await ctx.send(embed=embed)


@client.listen()
async def on_message(message):
    """Responds with a friendly greeting if any user says 'hey drago'. """
    greetings = ['hey dragonite', 'hey drago', 'hello dragonite', 'dragonite', 'drago', 'hi dragonite', 'hi drago',
                 'howdy drago'
        , 'hello drago', 'hewwo drago']
    responses = ['Hey', 'Hello', 'Konichiwa', 'Sup', 'Howdy', 'Yo', 'Bonjour', 'Hola', 'Heya', 'hewwo', 'hai',
                 '-nuzzles- hewwo', 'Hai']
    emojis = [':smiley:', ":smile:", ":laughing:", ":upside_down:", ":blush:", ":slight_smile:"
        , ":wink:", ":heart:"]
    if message.content == 'hey drago' or message.content == 'hey dragonite' \
            or message.content == 'hello dragonite' or message.content == 'drago' \
            or message.content == 'hi dragonite' or message.content == 'hi drago' \
            or message.content == 'hello drago' or message.content == 'dragonite':
        await message.channel.send(str(random.choice(responses)) + " " + format(message.author.mention) + " " + str(
            random.choice(emojis)) + ' !')
    elif client.user.mentioned_in(message) and message.author.id != 779219727582756874:
        prefix = await client.pg_con.fetch("SELECT prefix FROM guilds WHERE guild_id = $1", message.guild.id)
        prefix = prefix[0].get("prefix")
        await message.channel.send(
            f"{random.choice(responses)} {format(message.author.mention)} {random.choice(emojis)}. The current server prefix is {prefix}")


@client.command()
@commands.is_owner()
async def a(ctx, channel: int, *, message):
    bot = client
    channel = bot.get_channel(channel)
    if channel:
        await channel.send(message)
    else:
        await ctx.send('Could not find that channel')





#
# @client.command()
# async def guessC(ctx):
#     """Guess a random number selected between 1 and 100."""
#     global game
#     if ctx.channel.id in game:
#         return
#     else:
#         await ctx.send(f"Hello {ctx.guild.name}! I'm thinking of a number between 1 and 100." +
#                        f" You are given 10 tries to find the number. Good luck!")
#         game[ctx.channel.id] = ctx.author.id
#         number = random.randint(1, 100)
#         tries = 0
#
#         async def win(guess: int):
#             nonlocal tries
#             if guess == number:
#                 await ctx.send(f"Congrats, you guessed the number {number} in {tries} tries!")
#                 del game[ctx.channel.id]
#                 return
#             elif tries == 10:
#                 await ctx.send(f"Sorry, you took too many tries! The number was {number}")
#                 del game[ctx.channel.id]
#                 return
#             elif guess < number:
#                 await ctx.send(f"Higher! {abs(10 - tries)}  tries remaining!")
#             else:
#                 await ctx.send(f"Lower! {abs(10 - tries)} tries remaining!")
#
#         def check(message):
#             return message.author == ctx.author and message.channel == ctx.channel \
#                    and ctx.channel.id in game and message.content.isdigit()
#
#         while ctx.channel.id in game and tries != 10:
#             try:
#                 msg = await client.wait_for('message', check=check, timeout=120)
#             except asyncio.TimeoutError:
#                 del game[ctx.channel.id]
#                 return
#             tries += 1
#             await win(int(msg.content))
# @client.event
# async def on_message(message):
#     if not message.author.bot:
#         with open('level.json', 'r') as f:
#             users = json.load(f)
#         await update_data(users, message.author, message.guild)
#         await add_experience(users, message.author, 4)
#         await level_up(users, message.author, message.channel)
#
#         with open('level.json', 'w') as f:
#             json.dump(users, f)
#     await client.process_commands(message)
#
#
# async def update_data(users, user, server):
#     if not str(server.id) in users:
#         users[str(server.id)] = {}
#         if not str(user.id) in users[str(server.id)]:
#             users[str(server.id)][str(user.id)] = {}
#             users[str(server.id)][str(user.id)]['experience'] = 0
#             users[str(server.id)][str(user.id)]['level'] = 1
#     elif not str(user.id) in users[str(server.id)]:
#         users[str(server.id)][str(user.id)] = {}
#         users[str(server.id)][str(user.id)]['experience'] = 0
#         users[str(server.id)][str(user.id)]['level'] = 1
#
#
# async def add_experience(users, user, exp):
#     users[str(user.guild.id)][str(user.id)]['experience'] += exp
#
#
# async def level_up(users, user, channel):
#     experience = users[str(user.guild.id)][str(user.id)]['experience']
#     lvl_start = users[str(user.guild.id)][str(user.id)]['level']
#     lvl_end = int(experience ** (1 / 4))
#
#     if lvl_start < lvl_end:
#         await channel.send('{} has leveled up to Level {}'.format(user.mention, lvl_end))
#         users[str(user.guild.id)][str(user.id)]['level'] = lvl_end
#
#
# @client.command()
# async def level(ctx, member: discord.Member = None):
#     if not member:
#         user = ctx.message.author
#         with open('level.json', 'r') as f:
#             users = json.load(f)
#         lvl = users[str(ctx.guild.id)][str(user.id)]['level']
#         exp = users[str(ctx.guild.id)][str(user.id)]['experience']
#
#         embed = discord.Embed(title='Level {}'.format(lvl), description=f"{exp} XP ", color=discord.Color.green())
#         embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
#         await ctx.send(embed=embed)
#     else:
#         with open('level.json', 'r') as f:
#             users = json.load(f)
#         lvl = users[str(ctx.guild.id)][str(member.id)]['level']
#         exp = users[str(ctx.guild.id)][str(member.id)]['experience']
#         embed = discord.Embed(title='Level {}'.format(lvl), description=f"{exp} XP", color=discord.Color.green())
#         embed.set_author(name=member, icon_url=member.avatar_url)
#
#         await ctx.send(embed=embed)

@client.command()
async def talk(ctx, *, message):
    """Talk with cleverbot! """
    if ctx.author.bot:
        return
    response = await rs.get_ai_response(message)
    response = response[0]['message']
    async with ctx.typing():
        await asyncio.sleep(random.randint(1, 5))
    await ctx.reply(response)
    rs.close()



client.run(token)
