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


class tcg(commands.Cog):
    """A class containing the Pokemon Trading Card Game (TCG)."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tcg(self, ctx):
        """The user adds themselves to the tcg database in PostgreSQL. If the user is already in the database,
        the tcg command will then server as a help command listing the commands associated with this TCG. """
        await p.reward(ctx.author.id, 1)

        tcg = await self.bot.pg_con.fetch("SELECT * FROM tcg WHERE userid = $1", ctx.author.id)
        if not tcg:
            await self.bot.pg_con.execute("INSERT INTO tcg (userid, pid, amount) VALUES ($1, 25, 1) ", ctx.author.id)
            await ctx.send(str(ctx.author.display_name) + " has been successfully added to the tcg database.")
        else:
            embed = discord.Embed(title="**Trading Card Game**",
                                  description="Try to collect all the cards! (List of commands)",
                                  color=discord.Color.orange())
            embed.add_field(name="**.tcg**", value="Shows this help command.")
            embed.add_field(name="**.gald**", value="Check the completion of your TCG journey.")
            embed.add_field(name="**.unpack**", value="Unpack a random card from the TCG for 10 gald.")
            embed.add_field(name="**.cards**", value="Check the cards that a player in the TCG owns.")
            embed.add_field(name="**.dex**", value="Shows pokedex information on a Pokemon.")
            embed.add_field(name="**.trade**", value="Give a Pokemon card to another user in the TCG database.")
            embed.add_field(name="**.amount**", value="Shows how many Pokemon cards a user owns of a specific Pokemon.")
            await ctx.send(embed=embed)

    @commands.command()
    async def trade(self, ctx, number: int, pokemon, *, member: discord.Member):
        """Give a pokemon card to another discord member. """
        assert number > 0
        assert member != ctx.author, await ctx.send("You cannot trade cards with yourself :frowning: ")
        try:
            pokemon = pypokedex.get(name=pokemon)
        except:
            pokemon = pypokedex.get(dex=pokemon)
        trader = await self.bot.pg_con.fetch("SELECT * FROM tcg WHERE userid = $1 and pid = $2", ctx.author.id,
                                             pokemon.dex)
        if not trader:
            await ctx.send("You are not in the tcg database. Do .tcg to add yourself to the database.")
            return
        if int(trader[0]['amount']) < number:
            await ctx.send(
                f"You do not have enough {pokemon.name.capitalize()} cards to trade. (You have {trader[0]['amount']} total {pokemon.name.capitalize()}.)")
            return
        receiver = await self.bot.pg_con.fetch("SELECT * FROM tcg WHERE userid = $1", member.id)
        if not receiver:
            await ctx.send(
                f"{member.display_name} is not in the tcg database. Have them do .tcg to add themselves to the database.")
            return
        receiver = await self.bot.pg_con.fetch("SELECT * FROM tcg WHERE userid = $1 and pid = $2", member.id,
                                               pokemon.dex)
        if not receiver:
            receiver = await self.bot.pg_con.execute("INSERT INTO tcg VALUES ($1, $2, $3) ", member.id, pokemon.dex, 0)
            receiver = await self.bot.pg_con.fetch("SELECT * FROM tcg WHERE userid = $1 and pid = $2", member.id,
                                                   pokemon.dex)
        await self.bot.pg_con.execute("UPDATE tcg SET amount = $2 WHERE userid = $3 and pid = $1", pokemon.dex,
                                      trader[0]['amount'] - 1, ctx.author.id)  # updates amount by one
        await self.bot.pg_con.execute("UPDATE tcg SET amount = $2 WHERE userid = $3 and pid = $1", pokemon.dex,
                                      receiver[0]['amount'] + 1, member.id)
        await ctx.send(
            f"You have successfully given {member.display_name} {number} {pokemon.name.capitalize()} cards :smile: ")

    @commands.command()
    async def amount(self, ctx, pokemon, *, member: discord.Member = None):
        """Check how many Pokemon cards of a certain pokemon that a discord member owns."""
        member = ctx.author if member is None else member
        try:
            pokemon = pypokedex.get(name=pokemon)
        except:
            pokemon = pypokedex.get(dex=pokemon)
        trader = await self.bot.pg_con.fetch("SELECT * FROM tcg WHERE userid = $1 and pid = $2", member.id, pokemon.dex)
        if not trader:
            await ctx.send(f"{member.display_name} has 0 {pokemon.name.capitalize()} cards.")
        else:
            await ctx.send(f" {member.display_name} has {trader[0]['amount']} {pokemon.name.capitalize()} cards.")

    @commands.command()
    @commands.cooldown(random.randint(1, 3), random.randint(1, 600), commands.BucketType.user)
    async def unpack(self, ctx):
        """To unpack a card, it costs 10 gald. The user receives a random card where every Pokemon is
        equally likely to be received. The objective of the Pokemon TCG is to collect them all! """
        tcg = await self.bot.pg_con.fetch("SELECT * FROM tcg WHERE userid = $1", ctx.author.id)
        if not tcg:
            await ctx.send("You are not in the tcg database. Do .tcg to add yourself to the database.")
            return
        user = await self.bot.pg_con.fetch("SELECT gald FROM users WHERE id = $1", ctx.author.id)
        if user[0]['gald'] < 10:
            await ctx.send("You do not have enough gald to give :frowning: (10 gald needed to unpack)")
            return
        await p.reward(ctx.author.id, -10)
        await p.reward(779219727582756874, 10, True)

        x = random.randint(1, 898)
        if 0 < x < 152:
            booster = 'Generation 1'
        elif 152 <= x < 252:
            booster = 'Generation 2'
        elif 252 <= x < 387:
            booster = 'Generation 3'
        elif 387 <= x <= 493:
            booster = 'Generation 4'
        elif 494 <= x <= 649:
            booster = 'Generation 5'
        elif 650 <= x <= 721:
            booster = "Generation 6"
        elif 721 <= x <= 809:
            booster = 'Generation 7'
        else:
            booster = "Generation 8"
        pokemon = pypokedex.get(dex=x)
        types = ", ".join(pokemon.types)
        card = await self.bot.pg_con.fetch("SELECT * FROM tcg WHERE userid = $1 and pid = $2", ctx.author.id, x)
        if not card:
            await self.bot.pg_con.execute("INSERT INTO tcg VALUES ($1, $2, $3) ", ctx.author.id, x, 1)
        else:
            await self.bot.pg_con.execute("UPDATE tcg SET amount = $2 WHERE userid = $3 and pid = $1", x,
                                          card[0]['amount'] + 1, ctx.author.id)  # updates amount by one
        embed = discord.Embed(title=f"Booster Box: {booster}",
                              description=f"{ctx.author.display_name} opened their box for 10 gald and received card  ``` {x}/898```",
                              color=discord.Color.orange())

        embed.add_field(name=f" #{x} {pokemon.name.capitalize()}",
                        value=f"``` {types.capitalize()} ```")
        embed.set_thumbnail(url=ctx.author.avatar_url)
        num = pokemon.dex
        if int(num) >= 100:
            number = str(pokemon.dex)
        elif int(num) >= 10:
            number = "0" + str(pokemon.dex)
        else:
            number = "0" + "0" + str(pokemon.dex)
        embed.set_image(url="https://www.serebii.net/pokemon/art/" + str(number) + ".png")
        await ctx.send(embed=embed)

    @unpack.error
    async def unpack_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"Sorry {ctx.author.display_name}, :slight_frown: you have no more booster cards left to unpack...")
            await p.reward(ctx.author.id, 1)

    @commands.command(aliases=['deck', 'card'])
    async def cards(self, ctx, member: discord.Member = None, cur_page=None):
        """Browse through the list of cards that a member has in their collection.
        cur_page is an option parameter that can start the search from page cur_page.
        """
        await p.reward(ctx.author.id, 1)
        member = ctx.author if member is None else member
        tcg = await self.bot.pg_con.fetch("SELECT * FROM tcg WHERE userid = $1", member.id)
        if not tcg:
            await ctx.send(str(member.display_name) + " is not in the TCG database :frowning: ")
            return
        entries = [tcg[x]['pid'] for x in range(len(tcg))]  # pokemon collected by dex number
        total = [tcg[x]['amount'] for x in range(len(tcg))]  # amount of pokemon collected
        entries, total = zip(
            *sorted(zip(entries, total)))  # sorted the pokemon collected and amount through zip function
        # await ctx.send(entries)
        # await ctx.send(total)

        pages = len(entries)
        if cur_page == None:
            cur_page = 0
        else:
            cur_page = int(cur_page) - 1
        pokemon = pypokedex.get(dex=entries[cur_page])
        embedVar = discord.Embed(title=str(member.display_name) + "'s Pokedex: " + pokemon.name.capitalize(),
                                 color=0xe67e22)
        embedVar.add_field(name="Weight", value=str(pokemon.weight / 10) + " kg",
                           inline=True)  # value = str(sorted(keys))
        embedVar.add_field(name="Height", value=str(pokemon.height / 10) + " meters", inline=True)
        embedVar.add_field(name="ID", value="#" + str(pokemon.dex), inline=True)
        embedVar.add_field(name="Amount Owned", value=total[cur_page], inline=False)
        embedVar.add_field(name="Pages", value=str(cur_page + 1) + "/" + str(pages))
        embedVar.timestamp = datetime.datetime.utcnow()
        num = pokemon.dex
        if int(num) >= 100:
            number = str(pokemon.dex)
        elif int(num) >= 10:
            number = "0" + str(pokemon.dex)
        else:
            number = "0" + "0" + str(pokemon.dex)
        embedVar.set_image(url="https://www.serebii.net/pokemon/art/" + str(number) + ".png")
        # await ctx.send("https://www.serebii.net/pokedex-swsh/icon/" + str(number) + ".png")
        message = await ctx.send(embed=embedVar)
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
                    pokemon = pypokedex.get(dex=entries[cur_page])
                    embedVar = discord.Embed(
                        title=str(member.display_name) + "'s Pokedex: " + pokemon.name.capitalize(),
                        color=0xe67e22)
                    embedVar.add_field(name="Weight", value=str(pokemon.weight / 10) + " kg",
                                       inline=True)  # value = str(sorted(keys))
                    embedVar.add_field(name="Height", value=str(pokemon.height / 10) + " meters", inline=True)
                    embedVar.add_field(name="ID", value="#" + str(pokemon.dex), inline=True)
                    embedVar.add_field(name="Amount Owned", value=total[cur_page], inline=False)
                    embedVar.timestamp = datetime.datetime.utcnow()
                    num = pokemon.dex
                    if int(num) >= 100:
                        number = str(pokemon.dex)
                    elif int(num) >= 10:
                        number = "0" + str(pokemon.dex)
                    else:
                        number = "0" + "0" + str(pokemon.dex)
                    embedVar.set_image(url="https://www.serebii.net/pokemon/art/" + str(number) + ".png")
                    embedVar.add_field(name="Pages", value=str(cur_page + 1) + "/" + str(pages))

                    await message.edit(embed=embedVar)
                    # await message.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "◀️" and cur_page + 1 > 1:
                    cur_page -= 1
                    pokemon = pypokedex.get(dex=entries[cur_page])
                    embedVar = discord.Embed(
                        title=str(member.display_name) + "'s Pokedex: " + pokemon.name.capitalize(),
                        color=0xe67e22)
                    embedVar.add_field(name="Weight", value=str(pokemon.weight / 10) + " kg",
                                       inline=False)  # value = str(sorted(keys))
                    embedVar.add_field(name="Height", value=str(pokemon.height / 10) + " meters", inline=True)
                    embedVar.add_field(name="ID", value="#" + str(pokemon.dex), inline=True)
                    embedVar.add_field(name="Amount Owned", value=total[cur_page], inline=False)
                    embedVar.timestamp = datetime.datetime.utcnow()
                    embedVar.add_field(name="Pages", value=str(cur_page + 1) + "/" + str(pages))
                    num = pokemon.dex
                    if int(num) >= 100:
                        number = str(pokemon.dex)
                    elif int(num) >= 10:
                        number = "0" + str(pokemon.dex)
                    else:
                        number = "0" + "0" + str(pokemon.dex)
                    embedVar.set_image(url="https://www.serebii.net/pokemon/art/" + str(number) + ".png")
                    await message.edit(embed=embedVar)

                else:
                    pass
                    # await message.remove_reaction(reaction, user)
                    # removes reactions if the user tries to go forward on the last page or
                    # backwards on the first page
            except asyncio.TimeoutError:
                break

def setup(bot):
    bot.add_cog(tcg(bot))