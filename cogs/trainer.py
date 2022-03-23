import discord, random, os, asyncio, time
from discord.ext import commands
import discord.ext.commands
import datetime, asyncpg
from cogs.pokemon import pokemon
from asyncio import sleep
from main import client
import pypokedex
import pokebase as pb

p = pokemon(client)


class trainer(commands.Cog):
    """A class containing commands on catching other people (Pokemon) on a guild.
    The maximum amount of Pokemon any trainer can own is 3 Pokemon."""

    def __init__(self, bot):
        self.bot = bot

    async def capture(self, trainerid, memberid, guildid):
        """A helper function that adds a discord member to a trainer's team.
        Each Pokemon team is unique to a guild. """
        user = await self.bot.pg_con.fetch("SELECT * FROM trainer WHERE trainer = $1 and guild = $2", trainerid,
                                           guildid)
        if user[0]['mon1'] == None:
            await self.bot.pg_con.execute("UPDATE trainer SET mon1 = $1 WHERE trainer = $2 and guild = $3", memberid,
                                          trainerid, guildid)  # updates gald by one
        elif user[0]['mon2'] == None:
            await self.bot.pg_con.execute("UPDATE trainer SET mon2 = $1 WHERE trainer = $2 and guild = $3",
                                          memberid, trainerid, guildid)
        elif user[0]['mon3'] == None:
            await self.bot.pg_con.execute("UPDATE trainer SET mon3 = $1 WHERE trainer = $2 and guild = $3",
                                          memberid, trainerid, guildid)

    def type_of_ball(self, pokeball):
        if pokeball is None or 'poke' in pokeball:
            return 'pball'
        if 'great' in pokeball:
            return 'gball'
        if 'ultra' in pokeball:
            return 'uball'
        if 'master' in pokeball:
            return 'mball'

    @commands.command()
    async def catch(self, ctx, pokeball=None, *, member: discord.Member):
        """Catch a person from the server. Example <prefix>catch pokeball Dragonite
        The bot cannot be captured. Only one person can have another member on their team.
        Every discord member can have a max of 3 pokemon on their team per guild."""
        if member.id == 779219727582756874:  # cannot catch the bot
            embed = discord.Embed(description="blocked the pokeball!", color=0xe67e22)
            embed.set_image(
                url="https://i.gifer.com/KgXd.gif")
            # embed.set_thumbnail(url = member.avatar)
            embed.set_author(name=member.name, icon_url=member.avatar_url)
            await ctx.send(embed=embed)
            return
        print(member)
        await p.reward(ctx.author.id, 1)
        await p.reward(member.id, 0, True)
        user = await self.bot.pg_con.fetch("SELECT * FROM trainer WHERE trainer = $1 and guild = $2", ctx.author.id,
                                           ctx.guild.id)
        if not user:
            await self.bot.pg_con.execute("INSERT INTO trainer (trainer, guild) VALUES ($1, $2) ", ctx.author.id,
                                          ctx.guild.id)
            user = await self.bot.pg_con.fetch("SELECT * FROM trainer WHERE trainer = $1 and guild = $2", ctx.author.id,
                                               ctx.guild.id)
        memberinfo = await self.bot.pg_con.fetch("SELECT * FROM trainer WHERE trainer = $1 and guild = $2", member.id,
                                                 ctx.guild.id)
        if not memberinfo:
            await self.bot.pg_con.execute("INSERT INTO trainer (trainer, guild) VALUES ($1, $2) ", member.id,
                                          ctx.guild.id)
            memberinfo = await self.bot.pg_con.fetch("SELECT * FROM trainer WHERE trainer = $1 and guild = $2",
                                                     member.id, ctx.guild.id)
        if member == ctx.author:  # People can't catch themselves.
            await ctx.send("You cannot catch yourself.")
            raise AssertionError("Cannot catch yourself.")
        # checks if the pokemon is already caught by another trainer
        caught = await self.bot.pg_con.fetch(
            "SELECT exists (SELECT trainer FROM trainer WHERE (mon1 = $1 or mon2= $1 or mon3 = $1) and guild = $2 LIMIT 1)",
            member.id, ctx.guild.id)
        if caught[0]['exists'] == True:
            trainer = await self.bot.pg_con.fetch(
                "(SELECT trainer FROM trainer WHERE (mon1 = $1 or mon2= $1 or mon3 = $1) and guild = $2 LIMIT 1)",
                member.id, ctx.guild.id)
            trainercopy = trainer[0]['trainer']
            try:
                trainer = await ctx.author.guild.fetch_member(trainer[0]['trainer'])
                if trainer != ctx.author:
                    await ctx.send(str(member.display_name) + " is already caught by " + str(trainer))
                else:
                    await ctx.send("You already caught " + str(member.display_name) + " :laughing: ")
                raise AssertionError("Cannot be caught.")

            except:
                # if owner of the pokemon left the server, the pokemon is released.
                await self.bot.pg_con.execute("DELETE FROM trainer where trainer = $1 and guild = $2",
                                              trainercopy, ctx.guild.id)
        pokeball = self.type_of_ball(pokeball.lower())
        ball = await self.bot.pg_con.fetch("SELECT * FROM users WHERE id = $1", ctx.author.id)
        if ball[0][str(pokeball)] == 0:
            await ctx.send("You do not have enough specified pokeballs.")
            return
        if user[0]['mon1'] != None and user[0]['mon2'] != None and user[0]['mon3'] != None:
            await ctx.send("You cannot own more than 3 pokemon.")
            raise AssertionError("Cannot own more than three pokemon")
        else:
            await self.useitem(ctx.author.id, pokeball)
            if pokeball == 'pball':
                ans = [0, 0, 0, 0, 1]
                message = 'pokeball'
            elif pokeball == 'gball':
                ans = [0, 0, 0, 0, 0, 0, 1, 1, 1, 1]
                message = 'great ball'
            elif 'uball' in pokeball:
                ans = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1]
                print('ultra ball')
                message = 'ultra ball'

            elif 'mball' in pokeball:
                ans = [1]
                print('master ball')
                message = 'master ball'
            rand = random.choice(ans)
            print(rand)
            if rand == 0 and message == 'pokeball':
                embed = discord.Embed(description="broke free from the pokeball!", color=0xe67e22)
                embed.set_image(
                    url="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT3gnMPZARwIlWsJlAVt9MJoeU8-KCWb_HRAg&usqp=CAU")
                # embed.set_thumbnail(url = member.avatar)
                embed.set_author(name=member.name, icon_url=member.avatar_url)
                await ctx.send(embed=embed)
            if rand == 1 and message == 'pokeball':
                await self.capture(ctx.author.id, member.id, ctx.guild.id)
                embed = discord.Embed(description="was successfully caught in a pokeball!",
                                      color=0xe67e22)
                embed.set_image(url="https://i.gifer.com/MfJw.gif")
                # embed.set_thumbnail(url = member.avatar)
                embed.set_author(name=member.name, icon_url=member.avatar_url)
                await ctx.send(embed=embed)
            if rand == 0 and message == 'great ball':
                embed = discord.Embed(description="broke free from the great ball!", color=0xe67e22)
                embed.set_image(url="https://i.pinimg.com/originals/60/c4/35/60c4358f352422caf6967ca9df6c2a37.jpg")
                # embed.set_thumbnail(url = member.avatar)
                embed.set_author(name=member.name, icon_url=member.avatar_url)
                await ctx.send(embed=embed)
                # await ctx.send(member.display_name + " broke free from the great ball!" + " https://i.pinimg.com/originals/60/c4/35/60c4358f352422caf6967ca9df6c2a37.jpg")
            if rand == 1 and message == 'great ball':
                await self.capture(ctx.author.id, member.id, ctx.guild.id)
                embed = discord.Embed(description="was successfully caught in a great ball!",
                                      color=0xe67e22)
                embed.set_image(url="http://pa1.narvii.com/6171/65bffc98a772fbe267b94f63e3f025a1881abf20_00.gif")
                # embed.set_thumbnail(url = member.avatar)
                embed.set_author(name=member.name, icon_url=member.avatar_url)
                await ctx.send(embed=embed)
                # await ctx.send("Successfully caught " + member.display_name + " in a great ball." + " http://pa1.narvii.com/6171/65bffc98a772fbe267b94f63e3f025a1881abf20_00.gif")
            if rand == 1 and message == 'ultra ball':
                await self.capture(ctx.author.id, member.id, ctx.guild.id)
                embed = discord.Embed(description="was successfully caught in a great ball!",
                                      color=0xe67e22)
                embed.set_image(url="https://thumbs.gfycat.com/TimelyIncomparableBlackfish-size_restricted.gif")
                # embed.set_thumbnail(url = member.avatar)
                embed.set_author(name=member.name, icon_url=member.avatar_url)
                await ctx.send(embed=embed)
                # await ctx.send("Successfully caught " + member.display_name + " in an ultra ball." + " https://thumbs.gfycat.com/TimelyIncomparableBlackfish-size_restricted.gif")
            if rand == 0 and message == 'ultra ball':
                embed = discord.Embed(description="broke free from the ultra ball!", color=0xe67e22)
                embed.set_image(
                    url="http://24.media.tumblr.com/a1c8db14b9de538dd8297cfc1fa88d7e/tumblr_mu9lgwULFW1r84emlo1_500.gif")
                # embed.set_thumbnail(url = member.avatar)
                embed.set_author(name=member.name, icon_url=member.avatar_url)
                await ctx.send(embed=embed)
                # await ctx.send(member.display_name + " broke free from the ultra ball!" + " http://24.media.tumblr.com/a1c8db14b9de538dd8297cfc1fa88d7e/tumblr_mu9lgwULFW1r84emlo1_500.gif")
            if rand == 1 and message == 'master ball':
                await self.capture(ctx.author.id, member.id, ctx.guild.id)
                embed = discord.Embed(description="was successfully caught in a master ball!",
                                      color=0xe67e22)
                embed.set_image(
                    url="https://d1fs8ljxwyzba6.cloudfront.net/assets/editorial/2018/11/pokemon-lets-go-mewtwo-master-ball.jpg")
                # embed.set_thumbnail(url = member.avatar)
                embed.set_author(name=member.name, icon_url=member.avatar_url)
                await ctx.send(embed=embed)
                # await ctx.send("Successfully caught " + member.display_name + " in a master ball." + " https://d1fs8ljxwyzba6.cloudfront.net/assets/editorial/2018/11/pokemon-lets-go-mewtwo-master-ball.jpg")

    @catch.error
    async def catch_error(self, ctx, error):
        if isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Bad argument. Please use .catch <pokeball> <user>")
            await p.reward(ctx.author.id, 1)
        else:
            raise error

    ############
    ####PARTY###
    ############
    @commands.command()
    async def party(self, ctx, *, member: discord.Member = None):
        """Displays the Pokemon that the trainer has in their party."""
        await p.reward(ctx.author.id, 1)
        member = ctx.author if member is None else member
        await p.reward(member.id, 0, True)
        trainer = await self.bot.pg_con.fetch("SELECT * FROM trainer WHERE trainer = $1 and guild = $2", member.id,
                                              ctx.guild.id)
        if not trainer:
            await self.bot.pg_con.execute("INSERT INTO trainer (trainer, guild) VALUES ($1, $2) ", member.id,
                                          ctx.guild.id)
            trainer = await self.bot.pg_con.fetch("SELECT * FROM trainer WHERE trainer = $1 and guild = $2", member.id,
                                                  ctx.guild.id)
        in_party = [trainer[0][x] for x in range(1, len(trainer[0]) - 1)]
        in_party = [x for x in in_party if x != None]
        if not in_party:
            await ctx.send(str(member.display_name) + " does not own any Pokemon.")
            raise AssertionError(str(member.display_name) + " does not own any Pokemon.")
        else:

            cur_page = 0
            guild = self.bot.get_guild(ctx.guild.id)  # need to change this later
            pokemon = guild.get_member(
                in_party[cur_page])  # if a pokemon is no longer in the server, the pokemon is removed from the party
            try:
                if pokemon.display_name is None:
                    print('pass')
            except:
                await self.bot.pg_con.execute(
                    "UPDATE trainer SET mon" + str(cur_page + 1) + " = null WHERE trainer = $1 and guild = $2",
                    member.id, ctx.guild.id)
                await ctx.send("Pokemon error. Try again.")
                return

            pages = len(in_party)
            embed = discord.Embed(title=str(member.display_name) + "'s " + "Party:", color=0xe67e22)
            embed.add_field(name=str(pokemon.display_name), value=f"Page {cur_page + 1}/{pages}",
                            inline=False)  # value = str(sorted(keys))
            target = pokemon
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
            embed.set_image(url=pokemon.avatar_url)

            message = await ctx.send(embed=embed)
            # getting the message object for editing and reacting

            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
                # This makes sure nobody except the command sender can interact with the "menu"

            while True:  # and i < 50:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                    # waiting for a reaction to be added - times out after x seconds, 60 in this
                    # example

                    if str(reaction.emoji) == "▶️" and cur_page + 1 != pages:
                        cur_page += 1
                        pokemon = guild.get_member(in_party[
                                                       cur_page])  # if a pokemon is no longer in the server, the pokemon is removed from the party
                        try:
                            if pokemon.display_name is None:
                                print('pass')
                        except:
                            await self.bot.pg_con.execute("UPDATE trainer SET mon" + str(
                                cur_page + 1) + " = null WHERE trainer = $1 and guild = $2", member.id, ctx.guild.id)
                            await ctx.send("Pokemon error. Try again.")
                            return
                        embed = discord.Embed(title=str(member.display_name) + "'s " + "Party:", color=0xe67e22)
                        embed.add_field(name=str(pokemon.display_name), value=f"Page {cur_page + 1}/{pages}",
                                        inline=False)  # value = str(sorted(keys))
                        target = pokemon
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
                        embed.set_image(url=pokemon.avatar_url)
                        await message.edit(embed=embed)
                        # await message.remove_reaction(reaction, user)
                    elif str(reaction.emoji) == "◀️" and cur_page + 1 > 1:
                        cur_page -= 1
                        pokemon = guild.get_member(
                            in_party[
                                cur_page])  # if a pokemon is no longer in the server, the pokemon is removed from the party
                        try:
                            if pokemon.display_name == None:
                                print('pass')
                        except:
                            await self.bot.pg_con.execute("UPDATE trainer SET mon" + str(
                                cur_page + 1) + " = null WHERE trainer = $1 and guild = $2", member.id, ctx.guild.id)
                            await ctx.send("Pokemon error. Try again.")
                            return
                        embed = discord.Embed(title=str(member.display_name) + "'s " + "Party:", color=0xe67e22)
                        embed.add_field(name=str(pokemon.display_name), value=f"Page {cur_page + 1}/{pages}",
                                        inline=False)  # value = str(sorted(keys))
                        target = pokemon
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
                        embed.set_image(url=pokemon.avatar_url)
                        await message.edit(embed=embed)

                    else:
                        await message.remove_reaction(reaction, user)
                        # removes reactions if the user tries to go forward on the last page or
                        # backwards on the first page
                except asyncio.TimeoutError:
                    break

    ############
    ##OWNER#####
    ############

    @commands.command(aliases=['trainer'])
    async def owner(self, ctx, *, member: discord.Member = None):
        """ Displays who owns a specific Pokemon. """
        member = ctx.author if member is None else member
        await p.reward(ctx.author.id, 1)
        await p.reward(member.id, 0, True)
        trainer = await self.bot.pg_con.fetch(
            "SELECT trainer FROM trainer WHERE (mon1 = $1 or mon2 = $1 or mon3 = $1) and guild = $2", member.id,
            ctx.guild.id)
        if not trainer:
            await ctx.send(str(member.display_name) + " does not have a trainer :frowning: ")
        try:
            pokemon = ctx.guild.get_member(trainer[0]['trainer'])
        except:
            # handles when a trainer left the server and deletes that trainer from the database, thereby freeing all
            # pokemon that the trainer owned
            await self.bot.pg_con.execute("DELETE FROM trainer where trainer = $1 and guild = $2",
                                          trainer[0]['trainer'], ctx.guild.id)
            await ctx.send(str(
                member.display_name) + "does not have a trainer :frowning: This message might mean that the trainer "
                                       "has left the server and that the database has now been updated to reflect "
                                       "this.")
            return

        target = pokemon
        embed = discord.Embed(title=str(member.display_name) + "'s " + "Owner:", color=0xe67e22)
        embed.add_field(name=str(pokemon.display_name), value="ID: " + str(target.id)
                        , inline=False)  # value = str(sorted(keys))
        fields = [("Name", str(target), True),
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
        embed.set_thumbnail(url=pokemon.avatar_url)

        message = await ctx.send(embed=embed)

    @commands.command()
    async def release(self, ctx, *, member: discord.Member):
        """ Release a Pokemon from your party back into the wild. """
        # await p.reward(ctx.author.id, 1)
        trainer = await self.bot.pg_con.fetch(
            "SELECT trainer FROM trainer WHERE (mon1 = $1 or mon2 = $1 or mon3 = $1) and guild = $2", member.id,
            ctx.guild.id)
        if not trainer:
            await ctx.send(str(member.display_name) + " does not have a trainer.")
            return
        trainerid = trainer[0]['trainer']
        if trainerid != ctx.author.id:
            await ctx.send("You do not own this Pokemon.")
        else:
            trainer = await self.bot.pg_con.fetch(
                "SELECT * FROM trainer WHERE (mon1 = $1 or mon2 = $1 or mon3 = $1) and guild = $2", member.id,
                ctx.guild.id)
            if trainer[0]['mon1'] == member.id:
                await self.bot.pg_con.execute("UPDATE trainer SET mon1 = null where trainer = $1 and guild = $2",
                                              ctx.author.id, ctx.guild.id)
            elif trainer[0]['mon2'] == member.id:
                await self.bot.pg_con.execute("UPDATE trainer SET mon2 = null where trainer = $1 and guild = $2",
                                              ctx.author.id, ctx.guild.id)
            elif trainer[0]['mon3'] == member.id:
                await self.bot.pg_con.execute("UPDATE trainer SET mon3 = null where trainer = $1 and guild = $2",
                                              ctx.author.id, ctx.guild.id)
            embed = discord.Embed(description="was succesfully released into the wild!", color=0xe67e22)
            embed.set_image(
                url="https://i.pinimg.com/originals/c4/7b/3c/c47b3c1aa200fbd0054e71580884aed4.gif")
            embed.set_author(name=member.display_name, icon_url=member.avatar_url)
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(trainer(bot))
