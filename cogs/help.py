import discord
from discord.ext import commands
import random
import os
import asyncio
import discord.ext.commands
import time
import datetime

intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix='.', case_insensitive=True, help_command=None, intents=intents)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def help(self, ctx):
        embed = discord.Embed(title="Commands", description="To view a category, use <prefix>help <category>",
                              color=discord.Color.orange())
        embed.add_field(name="Categories", value="<a:pikachu:864000092231041024> Pokemon\n"
                                                 " <a:charmander:863996919873142794> Pokemon TCG (tcg) \n"
                                                 ":musical_note: Music\n"
                                                 ":8ball: Games\n"
                                                 ":mag: Search\n"
                                                 "<:kanna:868719469088874496> Anime\n"
                                                 ":mailbox: Message (msg)\n"
                                                 ":newspaper: Information (info)\n"
                                                 ":newspaper2: Miscellaneous (misc) \n"
                                                 ":tickets: Admin")
        embed.add_field(name="** Command Information**",
                        value="To view a category, use <prefix>help <category> to see a full list of commands from "
                              "that category.\n "
                              "**Example:** <prefix>help games")
        embed.add_field(name="Support Dragonite", value="Currently, to support me, you can use the <prefix>invite "
                                                        "command to invite me to your server. More ways to support "
                                                        "me coming soon :smile: ")
        await ctx.send(embed=embed)
        return


    @help.command()
    async def tcg(self, ctx):
        embed = discord.Embed(
            title="** <a:charmander:863996919873142794> Trading Card Game <a:charmander:863996919873142794> **",
            description="Try to collect all the cards! (List of commands)",
            color=discord.Color.orange())
        embed.add_field(name="**<prefix>tcg**",
                        value="Add yourself to the TCG database. Shows this help command once added to the TCG.")
        embed.add_field(name="**<prefix>gald**", value="Check the completion of your TCG journey.")
        embed.add_field(name="**<prefix>unpack**", value="Unpack a random card from the TCG for 10 gald.")
        embed.add_field(name="**<prefix>cards**", value="Check the cards that a player in the TCG owns.")
        embed.add_field(name="**<prefix>dex**", value="Shows pokedex information on a Pokemon.")
        embed.add_field(name="**<prefix>trade**", value="Give a Pokemon card to another user in the TCG database.")
        embed.add_field(name="**<prefix>amount**",
                        value="Shows how many Pokemon cards a user owns of a specific Pokemon.")
        await ctx.send(embed=embed)

    @help.command()
    async def admin(self, ctx):
        embed = discord.Embed(title="**:ticket: Admin Commands :ticket:**",
                              description="blacklist, prefix, whitelist",
                              color=discord.Color.orange())
        embed.add_field(name='** **',
                        value='Use <prefix>help <command name> for more info on a specific command :smile: ',
                        inline=False)
        await ctx.send(embed=embed)

    @help.command(aliases=['msg'])
    async def message(self, ctx):
        embed = discord.Embed(title="**:newspaper: Message Commands :newspaper:**",
                              description="afk, block, blocks, dm, read, remind, reminder, nrm",
                              color=discord.Color.orange())
        embed.add_field(name='** **',
                        value='Use <prefix>help <command name> for more info on a specific command :smile: ',
                        inline=False)

        await ctx.send(embed=embed)

    @help.command()
    async def music(self, ctx):
        embed = discord.Embed(title="**:musical_note: Music Commands :musical_note:**",
                              description="join, leave, pause, play, queue, resume, skip",
                              color=discord.Color.orange())
        embed.add_field(name='** **',
                        value='Use <prefix>help <command name> for more info on a specific command :smile: ',
                        inline=False)
        await ctx.send(embed=embed)

    @help.command()
    async def games(self, ctx):
        embed = discord.Embed(title="** :8ball: Games Commands :8ball: **",
                              description="8ball, bj, choice, flip, guess, hangman, lottery, pguess, place, rps, rr, "
                                          "scramble, tictactoe, who",
                              color=discord.Color.orange())
        embed.add_field(name='** **',
                        value='Use <prefix>help <command name> for more info on a specific command :smile: ',
                        inline=False)
        await ctx.send(embed=embed)

    @help.command(aliases=['misc'])
    async def miscellaneous(self, ctx):
        embed = discord.Embed(title="** :newspaper2: Miscellaneous Commands :newspaper2: **",
                              description="factorial, help, id_to_name, invite, math, math_functions, rsay, say, "
                                          "serverinvite, spin",
                              color=discord.Color.orange())
        embed.add_field(name='** **',
                        value='Use <prefix>help <command name> for more info on a specific command :smile: ',
                        inline=False)
        await ctx.send(embed=embed)

    @help.command()
    async def search(self, ctx):
        embed = discord.Embed(title="** :mag: Search Commands :mag: **",
                              description="antonym, define, defs, ddef, gis, synonym, urban, word, youtube",
                              color=discord.Color.orange())
        embed.add_field(name='** **',
                        value='Use <prefix>help <command name> for more info on a specific command :smile: ',
                        inline=False)
        await ctx.send(embed=embed)

    @help.command()
    async def invite(self, ctx):
        embed = discord.Embed(title="**Invite Dragonite to your server**", color=discord.Color.orange())
        embed.add_field(name="**Info**",
                        value="You must have administrator permissions in the server you invite Dragonite to.")
        embed.add_field(name="**Syntax**", value="<prefix>invite ")
        await ctx.send(embed=embed)

    @help.command()
    async def serverinvite(self, ctx):
        embed = discord.Embed(title="**Generate a Server Invite Link**", color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>serverinvite ")
        embed.add_field(name="**Info**", value="Dragonite must have permissions to create a server invite link.")
        await ctx.send(embed=embed)

    @help.command()
    async def hangman(self, ctx):
        embed = discord.Embed(title="**Hangman**",
                              description="Play a pokemon-themed hangman game. Start a game with .hang and guess a letter with .hang <letter>",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>hang <letter to guess>")
        embed.add_field(name="**Give up**",
                        value="say 'i quit' to quit the current hangman game. Only the player that started the game can do this.")
        embed.add_field(name="**Timeout**", value="120 seconds")
        await ctx.send(embed=embed)

    @help.command()
    async def lovecalc(self, ctx):
        embed = discord.Embed(title="**Lovecalc**",
                              description="Calculates the love percentage between two members.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>lovecalc <member1> <member2>")
        await ctx.send(embed=embed)

    @help.command()
    async def cuddle(self, ctx):
        embed = discord.Embed(title="**Cuddle a Person**",
                              description="Cuddle a person and make them feel better :smile: ",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>cuddle <member> ")
        await ctx.send(embed=embed)

    async def slap(self, ctx):
        embed = discord.Embed(title="**Slap a Person**",
                              description="Slap a person and make them feel better :smile: ",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>slap <member> ")
        await ctx.send(embed=embed)

    @help.command()
    async def prefix(self, ctx):
        embed = discord.Embed(title="**Server Prefix**",
                              description="Change the server prefix.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>prefix <prefix>")
        await ctx.send(embed=embed)

    @help.command()
    async def blacklist(self, ctx):
        embed = discord.Embed(title="**Blacklist**",
                              description="Blacklist a user from using the bot on the server.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>blacklist <member>")
        await ctx.send(embed=embed)

    @help.command()
    async def whitelist(self, ctx):
        embed = discord.Embed(title="**Whitelist**",
                              description="Remove a user on the blacklist so that they can use the bot on the server.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>whitelist <member>")
        await ctx.send(embed=embed)

    @help.command()
    async def lottery(self, ctx):
        embed = discord.Embed(title="**Lottery**",
                              description="Enter a lottery for a chance to win 90 times the amount betted.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>lottery <gald to bet>")
        await ctx.send(embed=embed)

    @help.command()
    async def channelinfo(self, ctx):
        embed = discord.Embed(title="**Channel Info**", description="Returns information about a discord channel.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>channel <id of channel>")
        await ctx.send(embed=embed)

    @help.command()
    async def avi(self, ctx):
        embed = discord.Embed(title="**Server Avatar**", description="Returns server avatar picture.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>avi <server = optional>")
        await ctx.send(embed=embed)

    # MESSAGE MODULE
    @help.command()
    async def block(self, ctx):
        embed = discord.Embed(title="**Block**",
                              description="Block a user of your choice. The user will be unable to send you remind "
                                          "messages.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>block <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def blocks(self, ctx):
        embed = discord.Embed(title="**Block List**",
                              description="Returns the author's blocklist. Member cannot check other members' "
                                          "blocklists.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>blocks")
        await ctx.send(embed=embed)

    @help.command()
    async def dm(self, ctx):
        embed = discord.Embed(title="**Private Message**",
                              description="Private message a user through the bot. The user must be in the server the "
                                          "bot is in.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>dm <user> <message>")
        await ctx.send(embed=embed)

    @help.command()
    async def read(self, ctx):
        embed = discord.Embed(title="**Read Message**",
                              description="Read a message from your inbox. This can only be used if the user sets "
                                          "automatic reminds to be off.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>read")
        await ctx.send(embed=embed)

    @help.command()
    async def remind(self, ctx):
        embed = discord.Embed(title="**Remind**", description="Sends a message to a user of your choice.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>remind <user> <message>")
        await ctx.send(embed=embed)

    @help.command()
    async def nrm(self, ctx):
        embed = discord.Embed(title="**Automatic Reminds Off/On**",
                              description="Turns automatic reminds off or on. If automatic reminds are off, the user "
                                          "must use .read to read new messages sent.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>nrm")
        await ctx.send(embed=embed)

    @help.command()
    async def reminder(self, ctx):
        embed = discord.Embed(title="**Reminder**",
                              description="Set a reminder message on the bot. The bot will ping you after the "
                                          "selected number of minutes the message.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>reminder <minutes> <message>")
        await ctx.send(embed=embed)

    # END OF MESSAGE MODULE
    @help.command()
    async def about(self, ctx):
        embed = discord.Embed(title="**About**", description="Displays information about the bot.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>about")
        await ctx.send(embed=embed)

    @help.command()
    async def anime(self, ctx):

        embed = discord.Embed(title="** <:kanna:868719469088874496> Anime Commands <:kanna:868719469088874496> **",
                              description=" anime, baka, cuddle, eat, hug, kiss, pat, punch, slap",
                              color=discord.Color.orange())
        embed.add_field(name='** **',
                        value='Use <prefix>help <command name> for more info on a specific command :smile: ',
                        inline=False)
        embed.add_field(name="Anime Search", value=" Searches up information  about an anime from MAL")
        embed.add_field(name="**Syntax**", value="<prefix>anime <name of anime>")
        await ctx.send(embed=embed)

    @help.command()
    async def eat(self, ctx):
        embed = discord.Embed(title="**Anime Eat**",
                              description="Returns a random anime eating or food gif or picture.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>eat")
        await ctx.send(embed=embed)

    @help.command()
    async def baka(self, ctx):
        embed = discord.Embed(title="**Baka**", description="Call a user a baka. Displays a random baka picture.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>baka <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def bag(self, ctx):
        embed = discord.Embed(title="**Bag**", description="Displays how many items a user has in their bag.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>bag <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def hug(self, ctx):
        embed = discord.Embed(title="**Hug**", description="Hug a specified user. Returns a random hug picture.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>hug <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def bj(self, ctx):
        embed = discord.Embed(title="**Blackjack**",
                              description="Bet 20 gald with the dealer through a game of blackjack. Type .hit for a "
                                          "hit and .stay to stay.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>bj")
        await ctx.send(embed=embed)

    @help.command()
    async def bomb(self, ctx):
        embed = discord.Embed(title="**Bomb**",
                              description="Bomb a user. They lose a random amount of gald and you gain that gald.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>bomb <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def join(self, ctx):
        embed = discord.Embed(title="**Join**", description="The bot joins the voice channel.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>join")
        await ctx.send(embed=embed)

    @help.command()
    async def leave(self, ctx):
        embed = discord.Embed(title="**Leave**", description="The bot leaves the voice channel.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>leave")
        await ctx.send(embed=embed)

    @help.command()
    async def pause(self, ctx):
        embed = discord.Embed(title="**Pause**", description="Pauses the music currently being played.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>pause")
        await ctx.send(embed=embed)

    @help.command()
    async def play(self, ctx):
        embed = discord.Embed(title="**Play**",
                              description="The bot joins the voice channel and plays the desired music.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>play <music name>")
        await ctx.send(embed=embed)

    @help.command()
    async def queue(self, ctx):
        embed = discord.Embed(title="**Queue**", description="The bot displays the queue.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>queue")
        await ctx.send(embed=embed)

    @help.command()
    async def resume(self, ctx):
        embed = discord.Embed(title="**Resume**", description="The bot resumes playing music.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>resume")
        await ctx.send(embed=embed)

    @help.command()
    async def skip(self, ctx):
        embed = discord.Embed(title="**Skip**", description="The bot skips the current track being played.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>skip")
        await ctx.send(embed=embed)

    @help.command()
    async def afk(self, ctx):
        embed = discord.Embed(title="**AFK**", description="Leave an AFK notice.", color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>afk <reason for AFK>")
        await ctx.send(embed=embed)

    @help.command()
    async def _8ball(self, ctx):
        embed = discord.Embed(title="**8ball**", description="Ask the 8ball your question.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>8ball <question>")
        await ctx.send(embed=embed)

    @help.command()
    async def antonym(self, ctx):
        embed = discord.Embed(title="**Antonym**", description="Gives antonyms of a word.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>ant <word>")
        await ctx.send(embed=embed)

    @help.command()
    async def arrow(self, ctx):
        embed = discord.Embed(title="**Arrow**",
                              description="Randomly shoots a person with an arrow from your bag. The person shot "
                                          "loses some gald.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>arrow")
        await ctx.send(embed=embed)

    @help.command()
    async def avatar(self, ctx):
        embed = discord.Embed(title="**Avatar**", description="Displays the avatar of a user.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>avatar <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def award(self, ctx):
        embed = discord.Embed(title="**Award**", description="Awards gald to a user. Owner only command.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>award <user> <gald>")
        await ctx.send(embed=embed)

    @help.command()
    async def buy(self, ctx):
        embed = discord.Embed(title="**Buy**", description="Purchase an item from AntLionMan's shop.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>buy <item> <amount>")
        await ctx.send(embed=embed)

    @help.command()
    async def catch(self, ctx):
        embed = discord.Embed(title="**Catch**",
                              description="Capture someone in the server and adds them to your party.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>catch <pokeball> <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def choice(self, ctx):
        embed = discord.Embed(title="**Choice**", description="Selects a random choice from a list of choices",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>choice <choice1> or <choice2> or <choice3> [...]")
        await ctx.send(embed=embed)

    @help.command()
    async def define(self, ctx):
        embed = discord.Embed(title="**Define**",
                              description="Define a word to add to the user-defined dictionary or look up an already "
                                          "defined word.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**",
                        value="To define: .define <word> as <meaning> ||| To lookup: .define <word> ||| To redefine: .def <word> as <meaning>")
        await ctx.send(embed=embed)

    @help.command()
    async def defs(self, ctx):
        embed = discord.Embed(title="**Definitions**",
                              description="Returns a list of the definitions owned by the specified user.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>defs <user1>")
        await ctx.send(embed=embed)

    @help.command()
    async def ddef(self, ctx):
        embed = discord.Embed(title="**Delete Definition**",
                              description="Deletes a definition from the user-defined dictionary.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>ddef <word>")
        await ctx.send(embed=embed)

    @help.command()
    async def dict(self, ctx):
        embed = discord.Embed(title="**Definitions**",
                              description="Displays the meaning of a word from the user-defined dictionary.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>dict <word>")
        await ctx.send(embed=embed)

    @help.command()
    async def e(self, ctx):
        embed = discord.Embed(title="**Eval**", description="No idea what this does.", color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>e <code>")
        await ctx.send(embed=embed)

    @help.command()
    async def factorial(self, ctx):
        embed = discord.Embed(title="**Factorial**", description="Returns a factorial of the inputted number.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>fact <number>")
        await ctx.send(embed=embed)

    @help.command()
    async def flip(self, ctx):
        embed = discord.Embed(title="**Flip**",
                              description="Bet gald. If heads, you win double the amount. If tails, you lose the "
                                          "amount betted.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>flip <number of gald to bet>")
        await ctx.send(embed=embed)

    @help.command()
    async def gis(self, ctx):
        embed = discord.Embed(title="**Google Image Search**", description="Search Google for Images.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>gis <image to search>")
        await ctx.send(embed=embed)

    @help.command()
    async def give(self, ctx):
        embed = discord.Embed(title="**Give Gald**", description="Transfer gald you own to another user.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>give <number of gald to transfer> <username>")
        await ctx.send(embed=embed)

    '''@help.command()
    async def help(ctx):
        embed = discord.Embed(title = "**Help**", description = "Shows a list of commands in the bot.", color=discord.Color.orange())
        embed.add_field(name = "**Syntax**", value = "<prefix>help")
        await ctx.send(embed = embed)'''

    @help.command()
    async def id_to_name(self, ctx):
        embed = discord.Embed(title="**ID To Name**",
                              description="Input a Discord UserID and returns the display name of the user.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>id_to_name <User#6969>")
        await ctx.send(embed=embed)

    @help.command()
    async def serverinfo(self, ctx):
        embed = discord.Embed(title="**Information**", description="Returns information about the server.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>serverinfo")
        await ctx.send(embed=embed)

    @help.command(aliases=['information'])
    async def info(self, ctx):
        embed = discord.Embed(title="** :newspaper2: Information Commands :newspaper2: **",
                              description="about, avi, afk, avatar, channelinfo, info, lovecalc, ping, serverinfo",
                              color=discord.Color.orange())
        embed.add_field(name='** **',
                        value='Use <prefix>help <command name> for more info on a specific command :smile: ',
                        inline=False)

        embed.add_field(name="info",
                        value="Returns information about a user.")
        embed.add_field(name="**Syntax**", value="<prefix>info <username>")
        await ctx.send(embed=embed)

    @help.command()
    async def kiss(self, ctx):
        embed = discord.Embed(title="**Kiss**", description="Kiss a specified user. Returns a kiss picture.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>kiss <User>")
        await ctx.send(embed=embed)

    @help.command()
    async def punch(self, ctx):
        embed = discord.Embed(title="**Punch**", description="Punch a specified user. Returns a punch picture.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>punch <User>")
        await ctx.send(embed=embed)

    @help.command()
    async def owner(self, ctx):
        embed = discord.Embed(title="**Owner of Pokemon**",
                              description="Enter a user and returns the name of the user who currently has that user "
                                          "in their Pokemon party.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>owner <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def party(self, ctx):
        embed = discord.Embed(title="**Party**",
                              description="Displays the Pokemon that the specified user has in their party.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>party <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def pat(self, ctx):
        embed = discord.Embed(title="**Pat**",
                              description="Pat a specified user of your choice. Returns a random patting picture.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>pat <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def guess(self, ctx):
        embed = discord.Embed(title="**Guess the Number**",
                              description="The bot selects a random number between 0 and n. 10 tries. If a parameter "
                                          "is not selected, n defaults to 100. Gald is rewarded for playing.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>guess <n>")
        await ctx.send(embed=embed)

    @help.command()
    async def ping(self, ctx):
        embed = discord.Embed(title="**Ping**", description="Returns the client latency.", color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>ping")
        await ctx.send(embed=embed)

    @help.command()
    async def place(self, ctx):
        embed = discord.Embed(title="**Place**",
                              description="Used for tictactoe. Use numbers 1-9. Each number corresponds to a grid "
                                          "location on the tictactoe board. Example: !place 1 would add an X or O to "
                                          "the top left of the board.",
                              color=discord.Color.orange())
        embed.add_field(name="**Place**", value="!place <grid location>")
        await ctx.send(embed=embed)

    @help.command()
    async def pokemon(self, ctx):

        embed = discord.Embed(
            title="** <a:pikachu:864000092231041024> Pokemon Commands <a:pikachu:864000092231041024> **",
            description="arrow, amount, bag, bomb, buy, cards, catch, dex, gald, give, hangman, owner, party, pguess, "
                        "pokemon, release, roll, rps, scramble, shop, trade, tcg, unpack, who, xp",
            color=discord.Color.orange())

        embed.add_field(name='** **',
                        value='Use <prefix>help <command name> for more info on a specific command :smile: ',
                        inline=False)
        await ctx.send(embed=embed)

    @help.command()
    async def roll(self, ctx):
        embed = discord.Embed(title="**Pokemon Slot Machine**",
                              description="Roll a slot machine and win gald! Each roll costs 5 gald!",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="Example: <prefix>roll")
        await ctx.send(embed=embed)

    @help.command()
    async def pguess(self, ctx):
        embed = discord.Embed(title="**Pokemon Guess**",
                              description="Guess the name of a Pokemon based on a picture or gif within 15 seconds.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="Example: <prefix>pguess")
        await ctx.send(embed=embed)

    @help.command()
    async def dex(self, ctx):
        embed = discord.Embed(title="**Pokedex**",
                              description="A brief pokedex command. Enter either the pokedex number or pokemon number "
                                          "to get facts of the Pokemon.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="Example: <prefix>dex <151> OR .dex <mew>")
        await ctx.send(embed=embed)

    @help.command()
    async def release(self, ctx):
        embed = discord.Embed(title="**Pokemon Release**",
                              description="Release a Pokemon in your party back into the wild.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>release <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def rps(self, ctx):
        embed = discord.Embed(title="**Rock, Paper, Scissors Pokemon Edition**",
                              description="Play rock, paper, scissors with Dragonite. You will either win or lose gald.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**",
                        value="First: .rps Then: Wait for Dragonite's Message. Finally: choose either fire, water, "
                              "or grass.")
        await ctx.send(embed=embed)

    @help.command()
    async def rsay(self, ctx):
        embed = discord.Embed(title="**Reverse Say**", description="Returns the message entered in reverse.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>rsay <message>")
        await ctx.send(embed=embed)

    @help.command()
    async def rr(self, ctx):
        embed = discord.Embed(title="**Russian Roulette**",
                              description="Play Russian Roulette. You will either win or lose gald.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>rr")
        await ctx.send(embed=embed)

    @help.command()
    async def say(self, ctx):
        embed = discord.Embed(title="**Say**", description="Returns the exact message entered back.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>say <message>")
        await ctx.send(embed=embed)

    @help.command()
    async def scramble(self, ctx):
        embed = discord.Embed(title="**Pokemon Scramble Game**",
                              description="A pokemon scramble game. Randomly scrambles a pokemon and the player must "
                                          "guess what the scrambled pokemon is. Player wins gald for a correct guess. "
                                          "An optional argument n sets how many Pokemon to guess in the game.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>w <number of pokemon to guess>")
        embed.add_field(name="**Give up**", value="Say 'i give up' to quit the current game")
        embed.add_field(name="**Timeout**", value="240 seconds")
        await ctx.send(embed=embed)

    @help.command()
    async def w(self, ctx):
        embed = discord.Embed(title="**Pokemon Scramble Game**",
                              description="A pokemon scramble game. Randomly scrambles a pokemon and the player must "
                                          "guess what the scrambled pokemon is. Player wins gald for a correct guess. "
                                          "An optional argument n sets how many Pokemon to guess in the game.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>w <number of pokemon to guess>")
        embed.add_field(name="**Give up**", value="Say 'i give up' to quit the current game")
        embed.add_field(name="**Timeout**", value="240 seconds")
        await ctx.send(embed=embed)

    @help.command()
    async def shop(self, ctx):
        embed = discord.Embed(title="**Shop**",
                              description="Displays AntLionMan's shop. YOU GIVE GALD TO ANTLIONMAN THEN ANTLIONMAN "
                                          "HAPPY",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>shop")
        await ctx.send(embed=embed)

    @help.command()
    async def shutdown(self, ctx):
        embed = discord.Embed(title="**Eternal Slumber**", description="Puts the bot to eternal slumber. Owner only.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>shutdown")
        await ctx.send(embed=embed)

    @help.command()
    async def math(self, ctx):
        embed = discord.Embed(title="**Math**",
                              description="Will perform the given operation. Do .math_functions to see a list of "
                                          "possible functions to use.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>math <operation>")
        await ctx.send(embed=embed)

    @help.command()
    async def math_functions(self, ctx):
        embed = discord.Embed(title="**Math Functions**",
                              description="Gives a list of math functions to use for the math command.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>math_functions")
        await ctx.send(embed=embed)

    @help.command()
    async def synonym(self, ctx):
        embed = discord.Embed(title="**Synonym**", description="Returns synonyms of a word.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>synonym <word>")
        await ctx.send(embed=embed)

    @help.command()
    async def tictactoe(self, ctx):
        embed = discord.Embed(title="**Tic-Tac-Toe**",
                              description="Play Tic-Tac-Toe with another user. Ping yourself and another user to play "
                                          "with. See <prefix>help place for more on how to play.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>tictactoe <user1> <user2>")
        await ctx.send(embed=embed)

    @help.command()
    async def urban(self, ctx):
        embed = discord.Embed(title="**Urban Dictionary**",
                              description="Searches the urban dictionary for a word. Easter egg: .urban random will "
                                          "randomly return a random word from the urban dictionary.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>urban <word>")
        await ctx.send(embed=embed)

    @help.command()
    async def word(self, ctx):
        embed = discord.Embed(title="**Official Dictionary**",
                              description="Searches the actual meaning of a word from an official dictionary.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>word <word>")
        await ctx.send(embed=embed)

    @help.command()
    async def xp(self, ctx):
        embed = discord.Embed(title="**Gald**", description="Displays the total gald a user owns.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>gald <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def gald(self, ctx):
        embed = discord.Embed(title="**Gald**", description="Displays the total gald a user owns.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>gald <user>")
        await ctx.send(embed=embed)

    @help.command()
    async def youtube(self, ctx):
        embed = discord.Embed(title="**YouTube**",
                              description="Searches YouTube for a video. There are three possible videos that could "
                                          "be returned. Thus, if you do the same command twice, a different video can "
                                          "be returned.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>yt <video to search up>")
        await ctx.send(embed=embed)

    @help.command()
    async def yt(self, ctx):
        embed = discord.Embed(title="**YouTube**",
                              description="Searches YouTube for a video. "
                                          + "There are three possible videos that could be returned. "
                                          + "Thus, if you do the same command twice, "
                                          + "a different video can be returned.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>yt <video to search up>")
        await ctx.send(embed=embed)


    @help.command()
    async def trade(self, ctx):
        embed = discord.Embed(title="**Trade a Pokemon Card**",
                              description="Give a Pokemon card to another user in the TCG database.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>trade <amount> <pokemon> <user> ", inline=False)
        await ctx.send(embed=embed)

    @help.command()
    async def amount(self, ctx):
        embed = discord.Embed(title="**Show Pokemon Cards**",
                              description="Shows how many Pokemon cards a user owns of a specific Pokemon.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>amount <pokemon> <user> ", inline=False)
        await ctx.send(embed=embed)

    @help.command()
    async def cards(self, ctx):
        embed = discord.Embed(title="**Trading Card Game**", description="Check the cards a Discord member owns.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>cards <member> <page>", inline=False)
        await ctx.send(embed=embed)

    @help.command()
    async def unpack(self, ctx):
        embed = discord.Embed(title="**Trading Card Game**", description="Unpack a card for 10 gald.",
                              color=discord.Color.orange())
        embed.add_field(name="**Syntax**", value="<prefix>unpack", inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
