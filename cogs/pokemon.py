import discord
from discord.ext import commands
import pokebase as pb
import pypokedex
import random
import os
import asyncio
from asyncio import sleep
import discord.ext.commands
import time
import datetime, asyncpg
from random import sample

### For Undo/Redo of TicTacToe ###
from collections import deque
import copy

###FOR ANIME.PY####
from pathlib import Path
from discord_slash import SlashCommand  # Importing the newly installed library.
from discord_slash import cog_ext, SlashContext

intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix=',', case_insensitive=True, help_command=None, intents=intents)


async def create_db_pool():
    client.pg_con = await asyncpg.create_pool(database='postgres', user='postgres', password='Mehul09!')


class pokemon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lst = {}  # will ensure only one game is running at a time in a server and channel for pguess
        self.who = {}  # scramble
        self.mons = {}  # scramble
        self.correct_ans = {}
        self.hang = {}  # hangman
        self.lives = {}  # hangman
        self.letters = {}


    async def reward(self, memberid, newxp, awarded=False):
        """Rewards discord members experience points. Adds the member to the
        PostgreSQL database if they are not already in the database. """
        if type(memberid) != int:
            memberid = int(memberid)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE id = $1", memberid)
        if not user:
            await self.bot.pg_con.execute("INSERT INTO users (id, usage, gald) VALUES ($1, 0, 0) ", memberid)
        user = await self.bot.pg_con.fetchrow("SELECT * FROM users WHERE id = $1", memberid)
        # print(user)
        # print(user[1])
        await self.bot.pg_con.execute("UPDATE users SET gald = $1 WHERE id = $2 ", user['gald'] + newxp,
                                      memberid)  # updates gald by one

        if not awarded:  # does not increase command usage by one if awarded gald
            await self.bot.pg_con.execute("UPDATE users SET usage = $1 WHERE id = $2 ", user['usage'] + 1,
                                          memberid)  # updates usage by one
            await self.bot.pg_con.execute("UPDATE users SET total = $1 WHERE id = $2 ", user['total'] + abs(newxp),
                                          memberid)  # changes experience points and level
        if user['gald'] < 0:
            await self.bot.pg_con.execute("UPDATE users SET gald = $1 WHERE id = $2 ", 0,
                                          memberid)  # handles negative gald and brings it back to zero

    @client.command()
    @commands.is_owner()
    async def award(self, ctx, newxp: int, *, member: discord.Member):
        """The owner of the bot can award a discord member experience points."""
        newxp = int(newxp)
        await self.reward(member.id, newxp, True)
        await ctx.send("Successfully awarded " + str(newxp) + " gald to " + str(member.display_name) + " !")

    @commands.command(aliases=['gald'])
    async def xp(self, ctx, *, member: discord.Member = None):
        """Returns information about a member's level, experience points, gald,
        command usage, trainer status, and the number of pokemon cards the member
        owns. """
        member = ctx.author if member is None else member
        await self.reward(ctx.author.id, 1)

        await self.reward(member.id, 0, True)

        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE id = $1", member.id)
        tcg = await self.bot.pg_con.fetch("SELECT * FROM tcg WHERE userid = $1", member.id)

        embed = discord.Embed(color=discord.Color.orange(), timestamp=ctx.message.created_at)
        embed.set_author(name=member.display_name)
        embed.set_thumbnail(url=member.avatar_url)
        if tcg:
            percentage = round(len(tcg) / 898 * 100, 2)
            if percentage < 1:
                rank = "```Newbie Trainer```"
            elif percentage < 10:
                rank = "```Beginner Trainer```"
            elif percentage < 15:
                rank = "```Standard Trainer```"
            elif percentage < 25:
                rank = "```Bronze Level Trainer```"
            elif percentage < 40:
                rank = "```Silver Level Trainer```"
            elif percentage < 50:
                rank = "```Gold Level Trainer```"
            elif percentage < 65:
                rank = "```Advanced Trainer```"
            elif percentage < 80:
                rank = "```Gym Leader```"
            elif percentage < 100:
                rank = "```Elite Four Member```"
            elif percentage == 100:
                rank = "```Pokemon Master!```"
            embed.add_field(name="Trainer Status", value=rank, inline=False)
        if member.id == 779219727582756874:
            embed.add_field(name="Trainer Status",
                            value=" :star: "'```Kawaii Master```' + " :star: ")  # title exclusively for Dragonite
        rank = await self.bot.pg_con.fetch(
            "SELECT rownumber from (SELECT id = $1 as x, RANK () OVER (ORDER BY total DESC) rownumber FROM users ) t where x is true",
            member.id)
        embed.add_field(name="Rank", value=f"**#{rank[0]['rownumber']}**", inline=False)
        embed.add_field(name="Level", value=user[0]['level'], inline=True)
        embed.add_field(name="EXP", value=user[0]['total'], inline=True)
        embed.add_field(name='Gald', value=user[0]['gald'], inline=True)
        embed.add_field(name='Command Usage', value=user[0]['usage'], inline=True)
        if tcg:
            embed.add_field(name="Cards", value=str(len(tcg)) + "/898 cards found!" + " (" + str(percentage) + "%)",
                            inline=False)
        growth = lambda n: ((n ** 3 * (100 - n)) / 50) / 3 if n < 100 else float(
            'inf')  # 200K exp needed for level 100 based on erratic level up
        embed.set_footer(text=f"{int(growth(user[0]['level']) - user[0]['total'])} exp needed to next level!")
        await ctx.send(embed=embed)

    @commands.command()
    async def give(self, ctx, xp, *, member: discord.Member = None):
        """Give another member experience points. Experience points given cannot be negative."""
        assert member is not None, await ctx.send('Please specify a member to give gald to :frowning: ')
        assert member != ctx.author, await ctx.send("You cannot give gald to yourself :frowning: ")
        xp = int(xp)
        assert xp > 0
        user = await self.bot.pg_con.fetch("SELECT gald FROM users WHERE id = $1", ctx.author.id)
        if user[0]['gald'] < xp:
            await ctx.send("You do not have enough gald to give :frowning: ")
            return
        await self.reward(member.id, xp, True)
        await self.reward(ctx.author.id, -xp)
        await ctx.send("You have successfully given " + str(xp) + " gald to " + str(member.display_name) + " :smile:")

    @give.error
    async def give_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the person to give gald to.")

    @commands.command(aliases=['dex', 'mon'])
    async def pokemon(self, ctx, message):
        """Returns information about a pokemon from the pokedex.
        The variable message can  be either the pokemon name or
        the national pokedex number of the pokemon. """
        await self.reward(ctx.author.id, 3)

        try:
            pokemon = pypokedex.get(dex=message.lower())
        except:
            pokemon = pypokedex.get(name=message.lower())

        abilities = []

        for i in range(0, len(pokemon.abilities)):
            abilities.append(pokemon.abilities[i].name)
        abilities = ", ".join(abilities)
        all_types = pokemon.types

        types = ", ".join(all_types)

        embed = discord.Embed(title=str(pokemon.name.capitalize()) + " #" + str(pokemon.dex),
                              description="Types: " + str(types.capitalize()),
                              color=discord.Color.red())  # = description="Height: " + str(pokemon.height / 10) + " meters")
        embed.add_field(name="**Height**", value=str(pokemon.height / 10) + " meters")
        embed.add_field(name="Weight", value=str(pokemon.weight / 10) + " kilograms")
        embed.add_field(name="Abilities", value=str(abilities.capitalize()))
        stats = pokemon.base_stats
        embed.add_field(name="Base Stats", value='*hp/atk/def/sp.atk/sp.def/speed:* ' + str(stats.hp) + "/" + str(
            stats.attack) + "/" + str(stats.defense) + "/"
                                                 + str(stats.sp_atk) + "/" + str(stats.sp_def) + "/" + str(stats.speed))
        num = pokemon.dex
        if int(num) >= 100:
            number = str(pokemon.dex)
        elif int(num) >= 10:
            number = "0" + str(pokemon.dex)
        else:
            number = "0" + "0" + str(pokemon.dex)
        embed.set_thumbnail(url="https://www.serebii.net/pokemon/art/" + str(number) + ".png")
        # embed.set_thumbnail(url=s1.url)

        await ctx.send(embed=embed)

    #################################
    ##POKEMON SCRAMBLE GAME (WHO)####
    #################################

    def rand_who(self):  # for the who function
        """Returns a random pokemon from the scramble.txt text file."""
        with open("scramble.txt", "r") as file:
            allText = file.read()
            words = list(map(str, allText.split()))

            # print random string
            return random.choice(words)

    def shuffle_mons(self, mons):  # for the who function
        """Randomly shuffles the letters in a word. """
        result = [''.join(sample(ele, len(ele))) for ele in mons]
        result = " ".join(result)
        return str(result)

    @client.command(aliases=['w', 'who'])
    async def scramble(self, message, number=1):
        """Randomly scrambles number pokemon. The goal of the scramble game is to guess
        the names of the Pokemon that are scrambled to earn gald. """
        ctx = message
        if number <= 0:
            return
        if number > 8 and message.author.id != 203020214332424192:
            await channel.send("Pokemon to guess must be less than 8.")
            return
        if ctx.channel.id not in self.who:
            self.who[ctx.channel.id] = False

        if not self.who[ctx.channel.id]:
            self.who[ctx.channel.id] = True
            self.mons[ctx.channel.id] = []
            self.correct_ans[ctx.channel.id] = []
            channel = message.channel
            for i in range(0, number):
                self.mons[ctx.channel.id].append(self.rand_who())
            xp = number * 10
            if 'pikachu' in self.mons[ctx.channel.id]:
                xp += 25
            if 'dragonite' in self.mons[ctx.channel.id]:
                xp += 50
            if 'mew' in self.mons[ctx.channel.id]:
                xp += 100
            if 'cyndaquil' in self.mons[ctx.channel.id]:
                xp += 25
            if 'eldegoss' in self.mons[ctx.channel.id]:
                xp += 30
            if 'missingno.' in self.mons[ctx.channel.id]:
                xp = 150
            self.correct_ans[ctx.channel.id].append(" ".join(self.mons[ctx.channel.id]))
            # await channel.send(correct_ans)
            await channel.send("I have scrambled a Pokemon(s): " + self.shuffle_mons(self.mons[ctx.channel.id]))
            print(xp)
            print(self.correct_ans[ctx.channel.id])
            correct_ans = " ".join(self.correct_ans[ctx.channel.id])

            # await ctx.send(correct_ans)
            def loser(m):
                if m.content.lower() == 'i give up' and m.channel == channel:
                    return 'Lose'
                elif m.content.lower() == str(correct_ans) and m.channel == channel:
                    return 'Win'

            try:
                msg2 = await self.bot.wait_for('message', check=loser,
                                               timeout=240)  # the game will reset after 240 seconds.
            except asyncio.TimeoutError:
                self.who[ctx.channel.id] = False
                return
            if loser(msg2) == 'Win':
                self.who[ctx.channel.id] = False
                print("{.author.id}".format(msg2))
                await self.reward("{.author.id}".format(msg2), xp)

                await channel.send("Correct :smile: {.author.display_name}".format(msg2) + "! The answer was " + str(
                    correct_ans.title()) + ". I have given you " + str(
                    xp) + " gald.")  # .author gives the discord ID, whereas #.author.nick gives the nickname of the user.
            elif loser(msg2) == 'Lose':
                self.who[ctx.channel.id] = False
                await channel.send(
                    "Bummer :disappointed: {.author.display_name}".format(msg2) + '... The correct answer was ' + str(
                        correct_ans.title()) + ". {.author.display_name}".format(msg2) + " lost 10 gald.")
                await self.reward("{.author.id}".format(msg2), -10)

        elif ctx.channel.id in self.who:
            await self.reward(message.author.id, 1)

            channel = message.channel
            await channel.send(
                "Hey, a game is already in session. The pokemon are: " + self.shuffle_mons(self.mons[ctx.channel.id]))

    #############
    ## SHOP #####
    #############
    @commands.command()
    async def buy(self, ctx, item, amount=1):
        """Buy an item from AntLionMan's shop. Dragonite bot earns the profit. """
        amount = int(amount)
        assert amount > 0, await ctx.send('r u dumb')  # can't buy negative amount of items
        await self.reward(ctx.author.id, 1)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE id = $1", ctx.author.id)
        # gald, uball, mball, arrows, bombs
        shop = ['pokeball', 'poke', 'pball', 'gball' 'great', 'greatball', 'uball', 'ultra', 'ultraball', 'mball',
                'master', 'masterball'
            , 'arrow', 'arrows', 'bomb', 'bombs', 'freedom']
        if 'lottery' in item.lower() or 'ticket' in item.lower():
            await ctx.send("Use <prefix>lottery <amount to bet> instead :smile: ")
            return
        elif 'unpack' in item.lower() or 'card' in item.lower():
            await ctx.send("Use <prefix>unpack instead :smile: ")
            return
        if item.lower() not in shop:
            await ctx.send("Item does not exist in shop")
            return
        if item.lower() == 'pokeball' or item.lower() == 'poke' or item.lower() == 'pball':
            item = 'pball'
            temp = 'pokeball'
            cost = 20
        elif item.lower() == 'gball' or 'great' in item.lower():
            item, temp = 'gball', 'greatball'
            cost = 40
        elif 'ultra' in item.lower() or item.lower() == 'uball':
            item, temp = 'uball', 'ultraball'
            cost = 80
        elif item.lower() == 'mball' or 'master' in item.lower():
            item, temp = 'mball', 'masterball'
            cost = 550
        elif 'arrow' in item.lower():
            item, temp = 'arrows', 'arrow'
            cost = 20
        elif 'bomb' in item.lower():
            item = 'bomb'
            temp = 'bomb'
            cost = 50
        elif 'freedom' in item.lower():  #####FREEDOM####
            user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE id = $1", ctx.author.id)

            trainer = await self.bot.pg_con.fetch(
                "SELECT trainer FROM trainer WHERE (mon1 = $1 or mon2 = $1 or mon3 = $1) and guild = $2", ctx.author.id,
                ctx.guild.id)
            if not trainer:
                await ctx.send(str(ctx.author.display_name) + " does not have a trainer :frowning: ")
                return
            if user[0]['gald'] < 600:
                await ctx.send("You do not have enough gald to be freed (600 gald required) :frowning: ")
                return
            memberid = ctx.author.id
            guildid = ctx.guild.id
            trainer = await self.bot.pg_con.fetch(
                "SELECT * FROM trainer WHERE (mon1 = $1 or mon2 = $1 or mon3 = $1) and guild = $2", int(memberid),
                int(guildid))
            owner = trainer[0]['trainer']
            trainer = [trainer[0][x] for x in range(1, len(trainer[0]) - 1)]
            mon = [trainer.index(x) for x in trainer if x == ctx.author.id][0]
            await ctx.send(mon)

            # await ctx.send(owner)
            if mon == 0:
                await self.bot.pg_con.execute("UPDATE trainer SET mon1 = $1 WHERE trainer = $2 and guild = $3 ", None,
                                              owner, ctx.guild.id)  # updates gald by one
            elif mon == 1:
                await self.bot.pg_con.execute("UPDATE trainer SET mon2 = $1 WHERE trainer = $2 and guild = $3 ", None,
                                              owner, ctx.guild.id)  # updates gald by one
            elif mon == 2:
                await self.bot.pg_con.execute("UPDATE trainer SET mon3 = $1 WHERE trainer = $2 and guild = $3 ", None,
                                              owner, ctx.guild.id)  # updates gald by one
            owner = ctx.guild.get_member(owner)
            embed = discord.Embed(title="You have successfully been freed from " + str(owner.display_name),
                                  description="** **", color=discord.Color.orange())
            embed.set_image(
                url="https://i.gifer.com/CztY.gif")
            await ctx.send(embed=embed)
            await self.reward(ctx.author.id, -600, True)
            return

        async def update(item, amount, cost):
            """Updates the user's inventory. Checks if the purchase is valid first. """
            nonlocal temp
            assert user[0]['gald'] >= cost * amount, await ctx.send(
                "You do not have enough gald :frowning: " + str(cost * amount) + " gald required!")
            if str(item) == 'mball':
                assert amount <= 2, await ctx.send("You cannot own more than 2 master balls.")
                assert user[0]['mball'] + amount <= 2, await ctx.send("You cannot own more than 2 master balls.")
                assert user[0]['gald'] - (cost * amount) >= 0, await ctx.send("You do not have enough gald :frowning: ")
            await self.bot.pg_con.execute("UPDATE users SET gald = $1 WHERE id = $2 ", user[0]['gald'] - cost * amount,
                                          ctx.author.id)  # takes away money
            await self.bot.pg_con.execute("UPDATE users SET " + str(item) + " = $1 WHERE id = $2 ",
                                          user[0][str(item)] + amount, ctx.author.id)  # awards user the bought item
            await ctx.send("You have successfully bought " + str(amount) + " " + str(temp) + "s for " + str(
                cost * amount) + " gald :smile: ")

        await update(item, amount, cost)


    @buy.error
    async def buy_error(self, ctx, error):
        await self.reward(ctx.author.id, 1)
        if isinstance(error, commands.BadArgument):
            await ctx.send(
                "Bad argument. Please use .buy <item> <amount>. Don't separate 'poke and ball' into two words.")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the item to buy.")

    ###########
    ##SHOP#####
    ###########
    @commands.command(aliases=['items', 'store'])
    async def shop(self, ctx):
        """ Displays information about the items in AntLionMan's shop. """
        await self.reward(ctx.author.id, 1)
        embed = discord.Embed(title="AntLionMan's Shop", color=discord.Color.orange(),
                              description="YOU GIVE GALD AND ME BE HAPPY!!!")
        embed.add_field(name="Pokeballs", value="20 Gald")
        embed.add_field(name="Great Balls", value="40 Gald")
        embed.add_field(name="Ultra Balls", value="80 Gald", )
        embed.add_field(name="Master Balls", value="550 Gald")
        embed.add_field(name="Bombs", value="50 Gald")
        embed.add_field(name="Arrows", value="20 Gald")
        embed.add_field(name="Lottery Ticket", value="1-50 Gald")
        embed.add_field(name="Unpack a Pokemon Card", value="10 Gald")
        embed.add_field(name="Freedom (Frees you from trainer)", value="600 Gald", inline=False)
        embed.add_field(name="** ** ",
                        value=":money_with_wings: Use .buy <item> <amount> to purchase an item and support "
                              "AntLionMan! :money_with_wings: ")
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/822331074276229161/843390164118274088/antlionman.jpg")
        await ctx.send(embed=embed)

    #############
    ####BAG#####
    ############

    @commands.command(aliases=['balls', 'inventory', 'pokeballs'])
    async def bag(self, ctx, *, member: discord.Member = None):
        """ Displays how many items a user has in their bag. """
        member = ctx.author if member == None else member
        await self.reward(member.id, 0, True)  # ensures member is in the database
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE id = $1", member.id)
        embed = discord.Embed(title=str(member.display_name) + "'s Inventory", color=discord.Color.orange())
        embed.add_field(name="Pokeballs", value=user[0]['pball'])
        embed.add_field(name="Great Balls ", value=user[0]['gball'])
        embed.add_field(name="Ultra Balls ", value=user[0]['uball'], inline=True)
        embed.add_field(name="Master Balls ", value=user[0]['mball'], inline=True)
        embed.add_field(name="Bombs", value=user[0]['bomb'], inline=True)
        embed.add_field(name="Arrows", value=user[0]['arrows'], inline=True)
        ball_list = [
            "https://static.wikia.nocookie.net/pokemon/images/8/87/Pok%C3%A9_Ball.png/revision/latest?cb=20200918005128",
            "https://static.wikia.nocookie.net/pokemon/images/a/ac/Great_Ball_Artwork.png/revision/latest?cb=20200918010231",
            "https://www.pinclipart.com/picdir/middle/84-843046_ultra-ball-pokemon-png-clipart.png",
            "https://media.karousell.com/media/photos/products/2019/12/31/master_ball_pokemon_sword_and_shield_masterball_1577726001_28ef8f31.jpg",
            'https://static.wikia.nocookie.net/ssb/images/8/8d/Bob-OmbWiiU.png/revision/latest?cb=20140409201131',
            'https://st.depositphotos.com/1024768/3004/v/950/depositphotos_30040639-stock-illustration-bow-and-arrow-clip-art.jpg']
        embed.set_thumbnail(url=random.choice(ball_list))
        await ctx.send(embed=embed)

    async def useitem(self, memberid, item):
        """A helper function that decreases a user's specific item by one in the database."""
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE id = $1", memberid)
        await self.bot.pg_con.execute("UPDATE users SET " + str(item) + " = $1 WHERE id = $2 ", user[0][str(item)] - 1,
                                      memberid)

    @commands.command()
    # @commands.cooldown(2, 600, commands.BucketType.user)
    async def bomb(self, ctx, *, member: discord.Member = None):
        """Bomb a user. This user lose a random amount of gald and you gain that gald."""
        await self.reward(ctx.author.id, 1)
        await self.reward(member.id, 0, True)  # ensures member is in the user database
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE id = $1", ctx.author.id)
        memberinfo = await self.bot.pg_con.fetch("SELECT * FROM users WHERE id = $1", member.id)
        print(user[0]['bomb'])
        print(memberinfo[0]['gald'])
        if member == None:
            await ctx.send("Please specify a member to bomb.")
            return
        if member.id == ctx.author.id:
            await ctx.send("Cannot bomb yourself.")
            return
        if user[0]['bomb'] < 1:
            await ctx.send("You do not own any bombs.")
            return
        if memberinfo[0]['gald'] == 0:
            lost_gald = 0
        elif memberinfo[0]['gald'] > 0:
            lost_gald = float('inf')
            while memberinfo[0]['gald'] < lost_gald:
                ans = [0, 5, 10, 10, 10, 20, 20, 30, 30, 40, 40, 50, 60, 70, 80, 90, 100, 20, 30, 30, 40, 40, 30, 20,
                       10,
                       30,
                       30, 20, 20, 20, 10, 10, 20, 20, 30, 30, 30]
                lost_gald = random.choice(ans)
        sound = ['BAM', 'BOOM', 'KAPOW']
        emojis = [':smile:', ':joy:', ':upside_down:', ':smiley:', ':stuck_out_tongue:', ':smiling_imp:',
                  ':exploding_head:', ':smiley_cat:', ":smile:"]
        await self.reward(member.id, -lost_gald, True)  # member selected loses gald
        print('pass')
        await self.reward(ctx.author.id, lost_gald, True)  # user picks up the gald
        await self.useitem(ctx.author.id, 'bomb')  # updates the user's number of bombs in their bag
        await ctx.send(str(random.choice(
            sound)) + " " + member.display_name + " has been bombed by " + ctx.author.display_name + " and has lost " + str(
            lost_gald) + " gald! " + str(random.choice(emojis)) + " " + str(
            ctx.author.display_name) + ' picks up the gald.')

    @bomb.error
    async def bombs_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'You are on cooldown; you can bomb someone again in {round(error.retry_after, 2)} seconds')
            await self.reward(ctx.author.id, 1)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the member to bomb")
            reward(1, ctx.author.id)

    @client.command()
    async def arrow(self, ctx):
        """Randomly shoots an arrow at someone who is online in the guild this command is used in.
        This random person loses a tiny amount of gald. """
        await self.reward(ctx.author.id, 1)
        user = await self.bot.pg_con.fetch("SELECT * FROM users WHERE id = $1", ctx.author.id)
        if user[0]['arrows'] < 1:
            await ctx.send("You do not own any arrows.")
            return
        tag = [779219727582756874]  # there is a chance to hit the Dragonite bot
        # for guild in self.bot.guilds: #this line  will try to shoot someone across servers so don't use this
        for member in ctx.guild.members:
            'THIS IF STATEMENT IS HOW THE ARROW FUNCTION WORKS AND FILTERS WHO CAN GET HIT.'
            if member.status is not discord.Status.offline and not member.bot:  # to restrict to people in the gald system, add "and str(member.id) in gald". to restrict to people with gald add "and gald[str(member.id)] >0
                tag.append(member.id)
        id = random.choice(tag)  # This is the user id of the person
        # print(id)
        tag = await ctx.author.guild.fetch_member(id)
        await self.reward(id, 0, True)  # ensures the member getting hit is in the gald database
        memberinfo = await self.bot.pg_con.fetch("SELECT * FROM users WHERE id = $1", id)
        print(memberinfo)
        await self.useitem(ctx.author.id, 'arrows')
        if memberinfo[0]['gald'] == 0:
            await ctx.send(str(tag) + " has been shot by " + str(ctx.author.display_name) + ".")
            return
        if str(id) == '779219727582756874':
            await ctx.send(" :angry: YOU SHOT ME! Dragonite steals 30 of your gald.")
            await self.reward(ctx.author.id, -30)
            await self.reward(779219727582756874, 30, True)
            return
        if id == ctx.author.id:
            await ctx.send("You shoot yourself and lose 20 gald :frowning: ")
            await self.reward(ctx.author.id, -20)
            return
        else:
            xp = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            xp_to_lose = random.choice(xp)
            await self.reward(ctx.author.id, xp_to_lose)
            await ctx.send(str(tag) + " has been shot by " + str(ctx.author.display_name) + " and loses " + str(
                xp_to_lose) + " gald.")



    #############################
    ## WHO'S THAT POKEMON#######
    ## POKEMON GUESSING GAME####
    ############################

    @commands.command(aliases=['pg'])
    @commands.cooldown(5, 5, commands.BucketType.user)
    async def pguess(self, ctx):
        """Guess the name of a Pokemon through a picture or a gif."""
        await self.reward(ctx.author.id, 1)

        if ctx.channel.id not in self.lst:
            self.lst[ctx.channel.id] = False
        elif ctx.channel.id in self.lst:
            if self.lst[ctx.channel.id] == True:
                return

        if self.lst[ctx.channel.id] == False:
            self.lst[ctx.channel.id] = True
            choices = ['pokemon/pokemon/main-sprites/crystal/animated/',
                       'pokemon/pokemon/main-sprites/crystal/back/',
                       'pokemon/pokemon/main-sprites/black-white/', 'pokemon/pokemon/main-sprites/black-white/',
                       'pokemon/pokemon/main-sprites/black-white/', 'pokemon/pokemon/main-sprites/shinyback/'
                , 'pokemon/pokemon/main-sprites/back/', 'pokemon/pkmn/pokemon/FRLG/FRLG/',
                       'pokemon/pkmn/pokemon/mystery/mystery2/portraits/',
                       'pokemon/pkmn/pokemon/Trozei/',
                       'pokemon/pokemon/main-sprites/black-white/']  # 'pokemon/main-sprites/yellow/gbc/',
            x = random.choice(choices)
            filename = random.choice(os.listdir(str(x)))
            file = discord.File(str(x) + str(filename), filename=filename)
            responses = ["Who's that Pokemon?"]
            embed = discord.Embed(title=str(random.choice(responses)), color=discord.Colour.orange())
            embed.set_image(url="attachment://" + str(filename))
            await ctx.send(file=file, embed=embed)
            if '.png' in filename:
                num = filename.replace(".png", "")
            if '.gif' in filename:
                num = filename.replace(".gif", "")
            if '.PNG' in filename:
                num = filename.replace(".PNG", "")
            pokemon = pypokedex.get(dex=int(num))
            print(pokemon.name)
            channel = ctx.channel

            def check(m):
                # print(m.content.lower())
                if m.content.lower() == str(pokemon.name) and m.channel == channel:
                    return 'Win'

            try:
                msg2 = await self.bot.wait_for('message', check=check,
                                               timeout=15)  # the game will reset after 240 seconds.
            except asyncio.TimeoutError:
                self.lst[ctx.channel.id] = False
                # print(self.lst)
                await channel.send(
                    "Bummer :disappointed: " + str(ctx.author.display_name) + ". The correct answer was " + str(
                        pokemon.name.capitalize()))
                await self.reward(ctx.author.id, 1)
                return
            if check(msg2) == 'Win':
                await channel.send(
                    "Correct :smile: {.author.display_name}".format(msg2) + "! The answer was " + str(
                        pokemon.name.capitalize()) + ". I have given you " + str(5) + " gald.")
                await self.reward("{.author.id}".format(msg2), 5)
                self.lst[ctx.channel.id] = False
                # print(self.lst)
                print(self.lst)
            elif check(msg2) == 'Lose':
                await channel.send(
                    "Bummer :disappointed: {ctx.author.display_name}".format(
                        msg2) + '... The correct answer was ' + str(
                        pokemon.name.capitalize()))
                self.lst[ctx.channel.id] = False

    @pguess.error
    async def pguess_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'You are on cooldown; you can use .pguess again in {round(error.retry_after, 2)} seconds')
        else:
            await ctx.send(error)




client.loop.run_until_complete(create_db_pool())


def setup(bot):
    bot.add_cog(pokemon(bot))
