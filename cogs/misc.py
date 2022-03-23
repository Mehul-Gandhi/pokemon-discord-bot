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

p = pokemon(client)


class misc(commands.Cog):
    """A class containing miscellaneous commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def say(self, ctx, *, message):
        await p.reward(ctx.author.id, 1)
        await ctx.send(message)

    @commands.command()
    async def rsay(self, ctx, *, message):
        await p.reward(ctx.author.id, 1)
        await ctx.send(message[::-1])

    @commands.command()
    async def factorial(self, ctx, number: int):
        assert number < 501, await ctx.send("The number must be less than or equal to 500.")
        total, i = 1, 1
        while i <= number:
            total = total * i
            i += 1
        await ctx.send(total)

    @commands.command()
    async def id_to_name(self, ctx, *, member: discord.Member = None):
        member = ctx.author if member is None else member
        embed = discord.Embed(color=discord.Color.orange(), timestamp=ctx.message.created_at)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name=member, value=str(member.display_name) + " = " + str(member.id))
        await ctx.send(embed=embed)

    @commands.command()
    async def seen(self, ctx, user: discord.Member, channel: discord.TextChannel = None):
        channel = ctx.channel if channel is None else channel
        oldestMessage = None  # ctx.guild.text_channels
        fetchMessage = await channel.history(limit=None).find(lambda m: m.author.id == user.id)

        if oldestMessage is None:
            oldestMessage = fetchMessage
        else:
            if fetchMessage.created_at > oldestMessage.created_at:
                oldestMessage = fetchMessage

        if oldestMessage is not None:
            await ctx.send(str(user.display_name) + "'s " f"last message in #{channel.name} : {oldestMessage.content}")
        else:
            await ctx.send("No message found.")

    @commands.command(aliases=['option'])
    async def choice(self, ctx, *, message):
        "Returns a random word from the message sent. Split the choice based off of the 'or' keyword."
        await self.reward(ctx.author.id, 1)
        lst = message.split('or')
        await ctx.send(random.choice(lst))

    @choice.error
    async def choice_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the choices and separate the choices by using 'or'.")

    @commands.command()
    async def emojify(self, ctx, *, text):
        """"Emojifies the message that was sent. Converts letters and numbers to discord emojis
        and sends the translated response back. """
        if len(text) > 50:
            return
        numbers = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four",
                   "5": "five", "6": "six", "7": "seven",
                   "8": "eight", "9": "nine"}
        converted = []
        for letter in text.lower():
            if letter.isdecimal():
                converted.append(f":{numbers.get(letter)}:")
            elif letter.isalpha():
                converted.append(f":regional_indicator_{letter}:")
            else:
                converted.append(letter)
        await ctx.send(' '.join(converted))


def setup(bot):
    bot.add_cog(misc(bot))
