import discord
from discord.ext import commands
import random
import os
import asyncio
import discord.ext.commands
import time
import asyncpg
from cogs.pokemon import pokemon
from main import client
import datetime
from PyDictionary import PyDictionary
import ast
import functools
import operator
from udpy import UrbanClient
from googleapiclient.discovery import build
from youtubesearchpython import VideosSearch
from datetime import date, datetime

dictionary = PyDictionary()

urban_d = UrbanClient()
api_key = "AIzaSyAJGcK_fHGyf2--HCA42rrXpjQUyMYMmWI"  # used for google image search
intents = discord.Intents.default()
intents.members = True
intents.presences = True
p = pokemon(client)


class search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['dictionary'], description="Searches the dictionary for a word's meaning.")
    async def word(self, ctx, word):
        """Searches the official meaning of a word from a dictionary. This is not the user-defined dictionary."""
        await ctx.send(dictionary.meaning(str(word)))
        await p.reward(ctx.author.id, 1)

    @commands.command(aliases=['ant', 'antonyms'])
    async def antonym(self, ctx, word):
        """Gives an antonym of a word."""
        x = dictionary.antonym(str(word))
        await ctx.send(", ".join(x))
        await p.reward(ctx.author.id, 1)

    @antonym.error
    async def antonym_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the word to look up.")
            await p.reward(ctx.author.id, 1)
        else:
            raise error

    @commands.command(aliases=['syn', 'synonyms'])
    async def synonym(self, ctx, word):
        """Gives a synonym of a word. """
        x = dictionary.synonym(str(word))
        await ctx.send(", ".join(x))
        await p.reward(ctx.author.id, 1)

    @synonym.error
    async def synonym_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the word to lookup.")
            await p.reward(ctx.author.id, 1)
        else:
            raise error

    def convertTuple(self, tup):
        str = functools.reduce(operator.add, (tup))
        return str

    @commands.command()
    async def urban(self, ctx, *, message):
        """Search the urban dictionary for the slang meaning of a word."""
        await p.reward(ctx.author.id, 1)
        string = self.convertTuple(message)
        if string != 'random':
            word = string
        else:  # if the inputted word = random, then a random word is chosen to be looked up.
            message = urban_d.get_random_definition()[0].word
            word = message
        defs = urban_d.get_definition(message)[0].definition
        print(defs)
        example = urban_d.get_definition(message)[0].example
        upvotes = urban_d.get_definition(message)[0].upvotes
        downvotes = urban_d.get_definition(message)[0].downvotes
        embedVar = discord.Embed(title="Urban Dictionary", color=0xe67e22)
        embedVar.add_field(name="Word", value=str(word), inline=False)
        embedVar.add_field(name="Definition", value=str(defs), inline=False)
        embedVar.add_field(name="Example", value=str(example), inline=False)
        embedVar.add_field(name=":thumbsup:", value=str(upvotes), inline=True)
        embedVar.add_field(name=":thumbsdown:", value=str(downvotes), inline=True)
        await ctx.send(embed=embedVar)

    @urban.error
    async def urban_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the word to lookup.")
            await p.reward(ctx.author.id, 1)
        else:
            raise error

    @commands.command(aliases=['yt'])
    async def youtube(self, ctx, *, message):
        """Search youtube for videos. """
        await p.reward(ctx.author.id, 1)
        videosSearch = VideosSearch(str(message), limit=3)
        answers = [0, 1]  # put only zero for most relevant searches
        id = videosSearch.result()['result'][random.choice(answers)]['id']
        await ctx.send("https://www.youtube.com/watch?v=" + str(id))

    @commands.command(aliases=['image'])
    async def gis(self, ctx, *, image):
        """Displays a google image of the searched result."""
        await p.reward(ctx.author.id, 1)
        ran = random.randint(0,
                             2)  # will select a random image. I chose to do (0,3) so that the most relevant pictures can be shown.
        resource = build("customsearch", "v1", developerKey=api_key).cse()
        result = resource.list(q=f"{image}", cx="1a74c162666ca212f", searchType="image").execute()
        url = result["items"][ran]["link"]
        embed1 = discord.Embed(title=f"Here's the image! ({image.title()}) ")
        embed1.set_image(url=url)
        await ctx.send(embed=embed1)

    @commands.command(aliases=['def'])
    async def define(self, ctx, *, message):
        """A user-defined dictionary. Each word can have a unique definition for each guild.
        In other words, every guild has a unique dictionary. Only the owner of the word
        can redefine a word. Owners and administrators can delete a definition of a word."""
        await p.reward(ctx.author.id, 1)
        today = date.today()
        now = datetime.now()
        x = message.split()
        if len(x) == 1:
            word = x[0]
        elif len(x) != 1 and 'as' not in message:
            word = message
        else:
            word = message.split(" as", 1)[0]
            if len(word) > 90:
                await ctx.send("The given word is too long to define.")
                return
            definition = message.split(" as", 1)[1]
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
        if not in_dict and 'as' in message:
            await client.pg_con.execute("INSERT INTO dict (word, def, date, id, guildid) VALUES ($1, $2, $3, $4, $5) ",
                                        word.lower(), definition,
                                        today.strftime("%B %d, %Y ") + now.strftime("%H:%M:%S"),
                                        ctx.author.id, ctx.guild.id)
            await ctx.send("I have now defined **" + str(word) + " **")
            return
        elif not in_dict and 'as' not in message:
            await ctx.send("**" + str(
                word) + "** is not defined. You can define it using <prefix>def <word or phrase> as <word or phrase>")
            return
        dict = await client.pg_con.fetch("SELECT * FROM dict WHERE word = $1 and guildid = $2", word.lower(),
                                         ctx.guild.id)
        if dict[0]['id'] == ctx.author.id and 'as' in message:
            await client.pg_con.execute(
                "UPDATE dict SET def = $2, date = $3, id = $4  WHERE word = $1 and guildid = $5 ", word.lower(),
                definition,
                today.strftime("%B %d, %Y ") + now.strftime("%H:%M:%S"), ctx.author.id,
                ctx.guild.id)  # updates gald by one
            await ctx.send("I have now redefined " + str(word))
        elif 'as' not in message:
            await ctx.send("** " + dict[0]['word'] + " ** means " + dict[0]['def'])
            embed = discord.Embed(color=discord.Color.orange(), timestamp=ctx.message.created_at)
            embed.add_field(name="Defined by", value=ctx.guild.get_member(dict[0]['id']).display_name)
            embed.add_field(name='Date defined', value=dict[0]['date'])
            await ctx.send(embed=embed)

    @define.error
    async def define_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("I need a word to recall...")
            await p.reward(ctx.author.id, 1)
        else:
            raise error

    @commands.command()
    async def ddef(self, ctx, *, word):
        """Delete a word from the user-defined dictionary."""
        word = word.lower()
        await p.reward(ctx.author.id, 1)
        in_dict = await client.pg_con.fetch("SELECT * FROM dict WHERE word = $1 and guildid = $2", word, ctx.guild.id)
        print(in_dict)
        if not in_dict:
            await ctx.send("**" + str(
                word) + "** is not defined. You can define it using <prefix>def <word or phrase> as <word or phrase>")
            return
        dict = in_dict
        if dict[0]['id'] == ctx.author.id:
            await client.pg_con.execute("DELETE FROM dict WHERE word = $1 and guildid = $2", word, ctx.guild.id)
            await ctx.send(str(word) + " has been deleted successfully from the dictionary.")
        elif ctx.author.id == 203020214332424192 or ctx.author.guild_permissions.administrator == True:
            await client.pg_con.execute("DELETE FROM dict WHERE word = $1 and guildid = $2", word, ctx.guild.id)
            await ctx.send(str(word) + " has been deleted successfully from the dictionary through brute force.")
        else:
            await ctx.send("You do not own this word.")

    @commands.command()
    async def defs(self, ctx, *, member: discord.Member = None):
        """Returns a list of words that the member has defined on the guild.
        There are 25 words per page and emojis are used to turn the page. """
        await p.reward(ctx.author.id, 1)
        member = ctx.author if member is None else member
        in_dict = await client.pg_con.fetch("SELECT * FROM dict WHERE id = $1 and guildid = $2", member.id,
                                            ctx.guild.id)
        dict = in_dict
        if not in_dict:
            await ctx.send(str(ctx.author.display_name) + " has no defined words.")
        else:
            definitions = sorted([dict[x]['word'] for x in range(len(dict))])
            key_list = []
            for j in range(0, int(len(definitions) / 25 + 1)):
                key_list.append([])

            j = -1
            for i in range(0, len(definitions)):
                if i % 25 == 0:
                    j += 1
                try:
                    key_list[j].append(definitions[i])
                except:
                    print(key_list)
            # print(key_list)
            contents = key_list
            # print(contents)
            pages = len(key_list)
            cur_page = 1
            i = 0
            embedVar = discord.Embed(title=str(member) + "'s " + "Defined Words", color=0xe67e22)
            embedVar.add_field(name="List of Words", value=f"Page {cur_page}/{pages}:\n{contents[cur_page - 1]}",
                               inline=False)  # value = str(sorted(keys))
            embedVar.add_field(name="Total Defined Words", value=str(len(sorted(definitions))), inline=False)

            message = await ctx.send(embed=embedVar)
            # getting the message object for editing and reacting

            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
                # This makes sure nobody except the command sender can interact with the "menu"

            while True:  # and i < 50:
                try:
                    reaction, user = await client.wait_for("reaction_add", timeout=60, check=check)
                    # waiting for a reaction to be added - times out after x seconds, 60 in this
                    # example

                    if str(reaction.emoji) == "▶️" and cur_page != pages:
                        cur_page += 1
                        embedVar = discord.Embed(title=str(member) + "'s " + "Defined Words", color=0xe67e22)
                        embedVar.add_field(name="List of Words",
                                           value=f"Page {cur_page}/{pages}:\n{contents[cur_page - 1]}",
                                           inline=False)  # value = str(sorted(keys))
                        embedVar.add_field(name="Total Defined Words", value=str(len(sorted(definitions))),
                                           inline=False)
                        await message.edit(embed=embedVar)
                        # await message.remove_reaction(reaction, user)
                    elif str(reaction.emoji) == "◀️" and cur_page > 1:
                        cur_page -= 1
                        embedVar = discord.Embed(title=str(member) + "'s " + "Defined Words", color=0xe67e22)
                        embedVar.add_field(name="List of Words",
                                           value=f"Page {cur_page}/{pages}:\n{contents[cur_page - 1]}",
                                           inline=False)  # value = str(sorted(keys))
                        embedVar.add_field(name="Total Defined Words", value=str(len(sorted(definitions))),
                                           inline=False)
                        await message.edit(
                            embed=embedVar)  # (content=f"Page {cur_page}/{pages}:\n{contents[cur_page - 1]}")
                        # await message.remove_reaction(reaction, user)

                    else:
                        await message.remove_reaction(reaction, user)
                        # removes reactions if the user tries to go forward on the last page or
                        # backwards on the first page
                except asyncio.TimeoutError:
                    break


def setup(bot):
    bot.add_cog(search(bot))
