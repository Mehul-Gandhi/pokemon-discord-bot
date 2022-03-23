import discord, random, os, asyncio, time
from discord.ext import commands
import discord.ext.commands
import datetime, asyncpg
from cogs.pokemon import pokemon
from main import client

p = pokemon(client)  # used to award gald to trainers


class information(commands.Cog):
    """A class containing commands about users or the guild."""

    def __init__(self, bot):
        self.bot = bot
        self.love = {}  # a dictionary used for lovecalc command

    @commands.command()
    async def about(self, ctx):
        """Returns information about this bot. """
        await p.reward(ctx.author.id, 1)
        embed = discord.Embed(title="Who Am I?", color=discord.Color.orange())
        embed.add_field(name="Description",
                        value="Hello. My name is Drago and I am a high school teenager! "
                              + "My interests include watching anime and walking my dog Sablé !",
                        inline=False)
        embed.add_field(name="Total Servers", value=str(len(self.bot.guilds)))
        embed.add_field(name="Creator", value="Satella#4021")
        embed.timestamp = datetime.datetime.utcnow()
        bot_avatar = ctx.guild.get_member(779219727582756874)
        embed.set_thumbnail(
            url=bot_avatar.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, *, avamember: discord.Member = None):
        """Displays the avatar for the specified user."""
        await p.reward(ctx.author.id, 1)
        avamember = ctx.author if avamember is None else avamember
        userAvatarUrl = avamember.avatar_url
        embed = discord.Embed(title=str(avamember.display_name) + "'s avatar :smile: ", color=discord.Colour.orange())
        embed.set_image(url=userAvatarUrl)
        await ctx.send(embed=embed)

    @commands.command()
    async def info(self, ctx, *, target: discord.Member = None):
        """Returns information about a discord member, the target."""
        if target is None:
            target = ctx.author
        await p.reward(ctx.author.id, 1)
        embed = discord.Embed(title="User information",
                              colour=discord.Color.orange(),
                              timestamp=datetime.datetime.utcnow())

        embed.set_thumbnail(url=target.avatar_url)

        fields = [("Name", str(target), True),
                  ("ID", target.id, True),
                  ("Bot?", target.bot, True),
                  ("Top role", target.top_role.mention, True),
                  ("Status", str(target.status).title(), True),
                  ("Activity",
                   f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}",
                   True),
                  ("Joined Discord on", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                  ("Joined Server on", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), True),
                  ("Boosted?", bool(target.premium_since), True)]

        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)

    @info.error
    async def info_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('I could not find that member...')
            await p.reward(ctx.author.id, 1)

    @commands.command()
    async def serverinfo(self, ctx):
        """Returns information about the guild the user is currently using
        the command in."""
        await p.reward(ctx.author.id, 1)
        role_count = len(ctx.guild.roles)
        list_of_bots = [bot.mention for bot in ctx.guild.members if bot.bot]
        staff_roles = ["Owner", "Head Dev", "Dev", "Head Admin", "Admins", "Moderators", "Community Helpers", "Members"]
        embed2 = discord.Embed(timestamp=ctx.message.created_at, color=discord.Color.orange())
        embed2.add_field(name='Name', value=f"{ctx.guild.name}")
        embed2.add_field(name='Highest role', value=ctx.guild.roles[-2])
        embed2.add_field(name="Server Owner", value=f"{ctx.guild.owner}")
        embed2.add_field(name="Server ID", value=f"{ctx.guild.id}")

        for r in staff_roles:
            role = discord.utils.get(ctx.guild.roles, name=r)
            if role:
                members = '\n'.join([member.name for member in role.members]) or "None"
                embed2.add_field(name=role.name, value=members)
        online = 0
        server = ctx.message.guild
        channel_count = len([x for x in server.channels if type(x) == discord.channel.TextChannel])
        for i in server.members:
            if str(i.status) == 'online' or str(i.status) == 'idle' or str(i.status) == 'dnd':
                online += 1
        embed2.add_field(name='Currently Online', value=online)
        embed2.add_field(name='Text Channels', value=str(channel_count))
        embed2.add_field(name='Number of roles', value=str(role_count))
        embed2.add_field(name='Number Of Members', value=ctx.guild.member_count)
        embed2.add_field(name='Bots:', value=(', '.join(list_of_bots)))
        embed2.add_field(name='Created At', value=ctx.guild.created_at.__format__('%A, %d. %B %Y @ %H:%M:%S'))
        embed2.set_thumbnail(url=ctx.guild.icon_url)
        embed2.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed2.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar_url)
        await ctx.send(embed=embed2)

    @commands.command()
    async def channelinfo(self, ctx, *, channel: int = None):
        """Shows channel information."""
        await p.reward(ctx.author.id, 1)
        if not channel:
            channel = ctx.message.channel
        else:
            channel = self.bot.get_channel(channel)
        data = discord.Embed()
        if hasattr(channel, 'mention'):
            data.description = "**Information about Channel:** " + channel.mention
        if hasattr(channel, 'changed_roles'):
            if len(channel.changed_roles) > 0:
                data.color = discord.Colour.green() if channel.changed_roles[
                    0].permissions.read_messages else discord.Colour.red()
        if isinstance(channel, discord.TextChannel):
            _type = "Text"
        elif isinstance(channel, discord.VoiceChannel):
            _type = "Voice"
        else:
            _type = "Unknown"
        data.add_field(name="Type", value=_type)
        data.add_field(name="ID", value=channel.id, inline=False)
        if hasattr(channel, 'position'):
            data.add_field(name="Position", value=channel.position)
        if isinstance(channel, discord.VoiceChannel):
            if channel.user_limit != 0:
                data.add_field(name="User Number", value="{}/{}".format(len(channel.voice_members), channel.user_limit))
            else:
                data.add_field(name="User Number", value="{}".format(len(channel.voice_members)))
            userlist = [r.display_name for r in channel.members]
            if not userlist:
                userlist = "None"
            else:
                userlist = "\n".join(userlist)
            data.add_field(name="Users", value=userlist)
            data.add_field(name="Bitrate", value=channel.bitrate)
        elif isinstance(channel, discord.TextChannel):
            try:
                pins = await channel.pins()
                data.add_field(name="Pins", value=len(pins), inline=True)
            except discord.Forbidden:
                pass
            data.add_field(name="Members", value="%s" % len(channel.members))
            if channel.topic:
                data.add_field(name="Topic", value=channel.topic, inline=False)
            hidden = []
            allowed = []
            for role in channel.changed_roles:
                if role.permissions.read_messages is True:
                    if role.name != "@everyone":
                        allowed.append(role.mention)
                elif role.permissions.read_messages is False:
                    if role.name != "@everyone":
                        hidden.append(role.mention)
            if len(allowed) > 0:
                data.add_field(name='Allowed Roles ({})'.format(len(allowed)), value=', '.join(allowed), inline=False)
            if len(hidden) > 0:
                data.add_field(name='Restricted Roles ({})'.format(len(hidden)), value=', '.join(hidden), inline=False)
        if channel.created_at:
            data.set_footer(text=("Created on {} ({} days ago)".format(channel.created_at.strftime("%d %b %Y %H:%M"), (
                        ctx.message.created_at - channel.created_at).days)))
        await ctx.send(embed=data)

    @commands.command()
    async def avi(self, ctx, msg: str = None):
        """Retrieve server avatar image link."""
        await p.reward(ctx.author.id, 1)
        if msg:
            server, found = self.find_server(msg)
            if not found:
                return await ctx.send(server)
        else:

            try:
                server = ctx.message.guild
                em = discord.Embed(title=server.name, timestamp=ctx.message.created_at, color=discord.Color.orange())
                em.set_image(url=server.icon_url)
                await ctx.send(embed=em)
            except:
                await ctx.send(self.bot.bot_prefix + server.icon_url)

    @commands.command()
    async def lovecalc(self, ctx, p1: discord.Member, p2: discord.Member):
        """Returns the percentage of love between p1 and p2. Stores this
        percentage in a dictionary to not appear random, but the
        percentage resets when the bot resets. """
        await p.reward(ctx.author.id, 1)
        x = random.randint(0, 100)
        number = p1.id + p2.id
        if number not in self.love:
            self.love[number] = x
        em = discord.Embed(color=discord.Color.orange())
        em.add_field(name="The love between " + str(p1.display_name) + " and " + str(p2.display_name) + " is ",
                     value=str(self.love[number]) + "%")
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(information(bot))
