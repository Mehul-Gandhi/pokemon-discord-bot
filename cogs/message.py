import discord, random, os, asyncio, time
from discord.ext import commands
import discord.ext.commands
import datetime, asyncpg
from cogs.pokemon import pokemon
from asyncio import sleep
from main import client


p = pokemon(client)


class message(commands.Cog):
    """A class containing commands allowing to message another discord members.
    The remind commands uses PostgreSQL."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['alarm'])
    async def reminder(self, ctx, time: int, *, message):
        """Sends a reminder to the user after time minutes. Pings the user
        with the specified message."""
        await p.reward(ctx.author.id, 1)
        await ctx.send("I will remind you the message in " + str(time) + " minutes.")
        await sleep(60 * time)
        await ctx.send(f'{ctx.author.mention}' + " , you sent yourself a reminder saying: " + str(message))

    @commands.command()
    async def dm(self, ctx, member: discord.Member = None, *, message):
        """Private messages a user the message sent."""
        await p.reward(ctx.author.id, 1)
        print(member)
        await member.send(f'{ctx.author}' + ' sent you a message saying: ' + message)
        await ctx.send(":white_check_mark: Sent!")

    @commands.command(aliases=['remind'])
    async def rm(self, ctx, member: discord.Member = None, *, message):
        """Reminds a user the message sent. The maximum messages a user can have in
        their inbox is 10. The next time a user posts something, the bot reminds the
        user the message unless the user has nrm toggled."""
        assert len(message) < 300, await ctx.send("The given message is too long to send :frowning: ")
        assert len(message) > 0, await ctx.send("The given message is too short to send :frowning:")
        await p.reward(ctx.author.id, 1)
        member = ctx.author if member is None else member
        user = await self.bot.pg_con.fetch("SELECT * FROM message WHERE id = $1", member.id)
        usage = await self.bot.pg_con.fetch("SELECT * from tusage where cmd = $1", 'rm')
        if not user:
            await self.bot.pg_con.execute("INSERT INTO message (id) VALUES ($1) ", member.id)
            user = await self.bot.pg_con.fetch("SELECT * FROM message WHERE id = $1", member.id)
        if len(user[0]['msg']) > 9:
            await ctx.send("The user's inbox is full :frowning: ")
            return
        if ctx.author.id in user[0]['blocks']:
            await ctx.send(f"{member.display_name} has you blocked :frowning: ")
            return
        rm_number = usage[0]['usage'] + 1
        message_to_send = f"{ctx.author}  sent you a message saying: ** {message}  **  (reminder #{rm_number}) [change this alert with the nrm command]"
        await self.bot.pg_con.execute("UPDATE message SET msg = array_append (msg, $1) where id = $2", message_to_send,
                                      member.id)
        await self.bot.pg_con.execute("UPDATE tusage SET usage = $1 where cmd = $2", rm_number,
                                      'rm')  # reminder message number
        await ctx.send(f"I will remind {member.display_name} the message :smile: ")

    @commands.command()
    async def read(self, ctx):
        """The user reads the messages in their inbox, usually if nrm is toggled on."""
        await p.reward(ctx.author.id, 1)
        user = await self.bot.pg_con.fetch("SELECT * FROM message WHERE id = $1", ctx.author.id)  # member.id)
        message = user[0]['msg']
        if not user or not message:
            await ctx.send("You do not have any messages in your inbox.")
            return
        length = len(message)
        await self.bot.pg_con.execute("UPDATE message SET msg = array_remove (msg, $1) where id = $2", message[0],
                                      ctx.author.id)
        await self.bot.pg_con.execute("UPDATE message SET archive = array_append (archive, $1) where id = $2",
                                      message[0], ctx.author.id)  # stores all messages in the archive
        await ctx.send(f" {ctx.author.mention}, {message[0]}. You have {length - 1} messages remaining in your inbox.")

    @rm.error
    async def rm_error(self, ctx, error):  # Returns an error when a member cannot be found.
        if isinstance(error, commands.BadArgument):
            await ctx.send('I could not find that user.')
            await p.reward(ctx.author.id, 1)

    @commands.command()
    async def block(self, ctx, *, member: discord.Member):
        """Block a member from allowing them to send messages to you. """
        await p.reward(ctx.author.id, 1)
        assert member.id != 203020214332424192, await ctx.send(
            "You cannot block this user.")  # people cannot block the user Satella#4021
        user = await self.bot.pg_con.fetch("SELECT * FROM message WHERE id = $1", ctx.author.id)  # member.id)
        if member.id not in user[0]['blocks']:
            await self.bot.pg_con.execute("UPDATE message SET blocks = array_append (blocks, $1) where id = $2",
                                          member.id, ctx.author.id)
            await ctx.send(
                f"I have successfully blocked {member.display_name} from sending you remind messages :smile: ")
        else:
            await self.bot.pg_con.execute("UPDATE message SET blocks = array_remove (blocks, $1) where id = $2",
                                          member.id, ctx.author.id)
            await ctx.send(
                f"I have successfully unblocked {member.display_name} from sending you remind messages :smile: ")

    @commands.command()
    async def blocks(self, ctx):
        """Showcases the list of people the user has blocked. """
        await p.reward(ctx.author.id, 1)
        user = await self.bot.pg_con.fetch("SELECT blocks FROM message WHERE id = $1", ctx.author.id)  # member.id)
        if not user or not user[0]['blocks']:
            await ctx.send(f"{ctx.author.display_name}, you do not have anyone blocked.")
            return
        lst = []
        for item in user[0]['blocks']:
            lst.append(ctx.guild.get_member(item).name)
        rv = ", ".join(lst)
        await ctx.send(f"{ctx.author.display_name}, you have blocked: {rv} ({len(lst)} blocks total)")

    @commands.command()
    async def nrm(self, ctx):
        """If nrm is toggled on, remind messages won't be shown automatically. Instead,
        the user must use the read command to read messages that are sent to their inbox. """
        await p.reward(ctx.author.id, 1)
        user = await self.bot.pg_con.fetch("SELECT nrm FROM message WHERE id = $1", ctx.author.id)
        if not user:
            await self.bot.pg_con.execute("INSERT INTO message (id, nrm) VALUES ($1, True) ", member.id)
            await ctx.send(f"{ctx.author.display_name}, you have turned off automatic reminds.")
        if not user[0]['nrm']:  # automatic reminds are currently on and will be off
            await self.bot.pg_con.execute("UPDATE message SET nrm = $1 where id = $2", True, ctx.author.id)
            await ctx.send(f"{ctx.author.display_name}, you have turned off automatic reminds.")
        elif user[0]['nrm']:
            await self.bot.pg_con.execute("UPDATE message SET nrm = $1 where id = $2", False, ctx.author.id)
            await ctx.send(f"{ctx.author.display_name}, you have turned on automatic reminds.")


def setup(bot):
    bot.add_cog(message(bot))
