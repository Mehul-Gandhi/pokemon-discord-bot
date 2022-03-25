import discord, random, os, asyncio, time
from discord.ext import commands
import discord.ext.commands
import datetime, asyncpg
from cogs.pokemon import pokemon
from asyncio import sleep
from main import client

p = pokemon(client)


class games(commands.Cog):
    """A class containing games to play."""

    def __init__(self, bot):
        self.bot = bot
        self.guess = {}  # number guessing game
        self.correct_ans = {}
        self.hang = {}  # hangman
        self.lives = {}  # hangman
        self.letters = {}

    @commands.command(aliases=['8ball', "8b"])
    async def _8ball(self, ctx, *, question):
        """Ask the magical 8ball your question."""
        await p.reward(ctx.author.id, 1)
        responses = ["It is certain :8ball:",
                     "It is decidedly so :8ball:",
                     "Without a doubt :8ball:",
                     "Yes, definitely :8ball:",
                     "You may rely on it :8ball:",
                     "As I see it, yes :8ball:",
                     "Most likely :8ball:",
                     "Outlook good :8ball:",
                     "Yes :8ball:",
                     "Signs point to yes :8ball:",
                     "Reply hazy try again :8ball:",
                     "Ask again later :8ball:",
                     "Better not tell you now :8ball:",
                     "Cannot predict now :8ball:",
                     "Concentrate and ask again :8ball:",
                     "Don't count on it :8ball:",
                     "My reply is no :8ball:",
                     "My sources say no :8ball:",
                     "Outlook not so good :8ball:",
                     "Very doubtful :8ball:"]
        if 'love' in question:
            await ctx.send("Love is a figure of one's imagination :confused: ")
        else:
            await ctx.send(f'Question: {question}\nAnswer: {random.choice(responses)}')

    @_8ball.error
    async def _8ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please say the question.")

    @commands.command(aliases=['coin', 'gamble'])
    async def flip(self, ctx, number=None):
        """Flips a coin and you either double or lose your gald. Returns either heads or tails
        randomly. Awards user with double the bet if outcome is heads. Example: !flip 5"""
        user = await self.bot.pg_con.fetch("SELECT gald FROM users WHERE id = $1", ctx.author.id)

        await p.reward(ctx.author.id, 1)
        if number is None:
            await ctx.send("Please specify the amount of gald to bet.")
            raise AssertionError("Unspecified amount of gald to bet.")
        if int(number) < 0:
            await ctx.send("You must bet a positive value.")
            raise AssertionError('Cannot bet negative gald.')
        if int(number) > 50:
            await ctx.send("You must bet a number between 1 and 50.")
            raise AssertionError("Cannot bet more than 50 gald.")
        if user[0]['gald'] < int(number):
            await ctx.send("You do not have enough gald to give :frowning: ")
            return
        number = int(number)

        answers = ['heads', 'heads', 'heads', 'tails', 'tails', 'tails', 'tails', 'tails', 'tails',
                   'heads']  # odds of doubling are 40%
        rand = random.choice(answers)
        if rand == 'heads':
            await p.reward(ctx.author.id, int(number))
            await p.reward(779219727582756874, -int(number))
            await ctx.send("*flips a coin* **" + str(rand) + "**! You have won " + str(int(number)) + " gald!")
        if rand != 'heads':
            await ctx.send("*flips a coin* **" + str(rand) + "**! You lost " + str(int(number * 1)) + " gald!")
            await p.reward(ctx.author.id, -int(number))
            await p.reward(779219727582756874, int(number))

    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def lottery(self, ctx, bet):
        """Try your chance at winning the lottery. The odds are 1/100.
        If the user wins, they earn 90 times the original bet."""
        assert int(bet) > 0
        if int(bet) > 50:
            await ctx.send("Bet must be less than or equal to 50 gald.")
            assert int(bet) <= 50
        bet = int(bet)
        x = random.randint(1, 100)
        if x == 1:
            await p.reward(ctx.author.id, bet * 90)
            await ctx.send("Congratulations " + str(
                ctx.author.display_name) + " you won a winning lottery ticket and earned " + str(
                bet * 90) + " gald! :partying_face:")
        else:
            await p.reward(ctx.author.id, -int(bet))
            await p.reward(779219727582756874, bet)
            await ctx.send("Bummer " + str(
                ctx.author.display_name) + ", you did not win a winning lottery ticket :frowning: ")

    @lottery.error
    async def lottery_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error)
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'You are on cooldown; you can use .unpack again in {round(error.retry_after, 2)} seconds')

    @commands.command(aliases=['pick'])
    async def guess(self, ctx, n=100):
        """Number guessing game. Guess a number between 1 and n."""
        n = int(n)
        print(self.guess)
        if n < 10:
            await ctx.send("The domain of the number to guess (n) must be 10 or greater.")
            raise AssertionError("Number to guess is too small.")
        if n > 10000:
            await ctx.send("The domain of the number to guess (n) is too high.")
            raise AssertionError("Number to guess is too high.")
        if ctx.channel.id not in self.guess:
            self.guess[ctx.channel.id] = False
        if self.guess[ctx.channel.id] == False:
            self.guess[ctx.channel.id] = True
            while self.guess[ctx.channel.id] == True:
                current_game = False  # makes sure two games aren't playing at the same time
                await ctx.send(f"Hello {ctx.guild.name}! I'm thinking of a number between 1 and " + str(
                    n) + ". You are given 10 tries to find the number. Good luck!")
                secretNumber = random.randint(1, n)
                print(secretNumber)

                def check(message):
                    return message.channel == ctx.channel and message.content.isdigit()

                for guessesTaken in range(0, 10):
                    msg2 = await self.bot.wait_for('message', check=check)
                    guess = int(msg2.content)
                    if guess < secretNumber:
                        await ctx.send("Your guess is too low! " + str(abs(guessesTaken - 9)) + " guesses left.")
                        await p.reward("{.author.id}".format(msg2), 1)
                    elif guess > secretNumber:
                        await ctx.send("Your guess is too high! " + str(abs(guessesTaken - 9)) + " guesses left.")
                        await p.reward("{.author.id}".format(msg2), 1)
                    else:
                        if n == 100:
                            self.guess[ctx.channel.id] = False
                            await ctx.send(
                                f"Congrats! You correctly guessed the number " + str(secretNumber) + " in " + str(
                                    guessesTaken + 1) + " guesses! You gained 20 gald.")
                            await p.reward("{.author.id}".format(msg2), 20)
                            return
                        if n >= 1000:
                            self.guess[ctx.channel.id] = False
                            await ctx.send(
                                f"Congrats! You correctly guessed the number " + str(secretNumber) + " in " + str(
                                    guessesTaken + 1) + " guesses! You gained 40 gald.")
                            await p.reward("{.author.id}".format(msg2), 40)
                            return
                        if n == 10:
                            self.guess[ctx.channel.id] = False
                            await ctx.send(
                                f"Congrats! You correctly guessed the number " + str(secretNumber) + " in " + str(
                                    guessesTaken + 1) + " guesses! You gained 5 gald.")
                            await p.reward("{.author.id}".format(msg2), 5)
                            return
                        if 10 < n < 200:
                            self.guess[ctx.channel.id] = False
                            await ctx.send(
                                f"Congrats! You correctly guessed the number " + str(secretNumber) + " in " + str(
                                    guessesTaken + 1) + " guesses! You gained 10 gald.")
                            await p.reward(ctx.author.id, 10)
                        else:  # n is between 200 and 9999
                            self.guess[ctx.channel.id] = False
                            await ctx.send(
                                f"Congrats! You correctly guessed the number " + str(secretNumber) + " in " + str(
                                    guessesTaken + 1) + " guesses! You gained 30 gald.")
                            await p.reward("{.author.id}".format(msg2), 30)
                else:
                    self.guess[ctx.channel.id] = False
                    await ctx.send(
                        f" :pensive: Sorry, you took too many guesses. The number I was thinking of was {secretNumber}")
                    await p.reward("{.author.id}".format(msg2), 2)
                    return

    #######################
    ####SLOT MACHINE#######
    #######################

    def slot(self, common=True, uncommon=False, rare=False):
        if common and uncommon == False and not rare:
            voltorb = {'emote': '<a:voltorb:864011674972848159>', 'value': -10}
            magikarp = {'emote': '<a:magikarp:864011673735659541>', 'value': 1}
            ditto = {'emote': '<a:ditto:864011673567363082>', 'value': 5}
            pidgey = {'emote': '<a:pidgey:864011673304170536>', 'value': 2}
            mrmime = {'emote': '<a:mr:864011677119676426>', 'value': 5}
            psyduck = {'emote': '<a:psyduck:864011675505524766>', 'value': 3}
            cyndaquil = {'emote': '<a:cyndaquil:864011830346776586>', 'value': 5}
            jigglypuff = {'emote': '<a:jigglypuff:864011674406748161>', 'value': 5}
            natu = {'emote': '<a:natu:864011674440171560>', 'value': 7}
            print('value of x', common)
            if common % 2 == 0:
                mons = [psyduck, ditto, pidgey]  # , mrmime, psyduck, cyndaquil,#jigglypuff, voltorb, ditto]
            elif 0 < common < 40:
                mons = [mrmime, cyndaquil]
            elif 40 < common < 60:
                mons = [voltorb, jigglypuff]
            elif 60 < common < 80:
                mons = [magikarp, ditto, natu]
            else:
                mons = [magikarp]

        elif common == 0 and uncommon == True and not rare:
            rowlet = {'emote': '<a:rowlet:864011675119386628>', 'value': 15}
            mareep = {'emote': '<a:mareep:864011677228597279>', 'value': 17}
            eevee = {'emote': '<a:eevee:864011673542066187>', 'value': 20}
            marill = {'emote': '<a:marill:864011675556249600>', 'value': 15}
            slowbro = {'emote': '<a:slowbro:864011677828513852>', 'value': 15}
            mudkip = {'emote': '<a:mudkip:864011675618377778>', 'value': 15}
            dratini = {'emote': '<a:dratini:864000092477587477>', 'value': 25}
            lilligant = {'emote': '<a:lilligant:864011676755820546>', 'value': 25}
            drifblim = {'emote': '<a:drifblim:864014121858891796>', 'value': 25}
            snorlax = {'emote': '<a:snorlax:864011677494542367>', 'value': 25}
            eldegoss = {'emote': '<a:eldegoss:864014806229975041>', 'value': 25}
            mons = [dratini, lilligant, eevee]  # mareep, eevee, marill, slowbro, mudkip, dratini
            # , lilligant, drifblim, snorlax, eldegoss]
        elif common == 0 and uncommon == False and rare:
            charizard = {'emote': '<a:charizard:864000092666724363>', 'value': 30}
            pikachu = {'emote': '<a:pikachu:864000092231041024>', 'value': 35}
            goldmagikarp = {'emote': '<a:goldmagikarp:864011673102057512>', 'value': 100}
            dragonite = {'emote': '<a:dragonite:864000093014851594>', 'value': 30}
            if rare == 69:  # jackpot
                mons = [goldmagikarp]
            elif rare % 2 == 0:
                mons = [charizard, pikachu, goldmagikarp, dragonite]
            else:
                mons = [charizard, pikachu, goldmagikarp]
        # mons = [voltorb, magikarp, ditto, pidgey, mrmime, psyduck, cyndaquil,
        #         jigglypuff, rowlet, natu, mareep, eevee, marill, slowbro, mudkip, dratini
        #         , lilligant, drifblim, snorlax, eldegoss, charizard, pikachu, goldmagikarp]
        return random.choice(mons)

    @commands.command()
    async def roll(self, ctx):
        """Roll the slot machine. Earn gald if three in a row of a certain pokemon. Not completed."""
        user = await client.pg_con.fetchrow("SELECT * FROM users WHERE id = $1", ctx.author.id)

        if user['gald'] < 10:
            await ctx.send("You do not have enough gald. (5 gald needed to roll)")
            return
        await p.reward(ctx.author.id, -5)
        message = await ctx.send(
            f"<a:cycle:864023184947675166> <a:cycle:864023184947675166> <a:cycle:864023184947675166>\n"
            f"<a:cycle:864023184947675166> <a:cycle:864023184947675166> <a:cycle:864023184947675166>\n"
            f"<a:cycle:864023184947675166> <a:cycle:864023184947675166> <a:cycle:864023184947675166>")
        first = [{'emote': '<a:cycle:864023184947675166>', 'value': 0},
                 {'emote': '<a:cycle:864023184947675166>', 'value': 0},
                 {'emote': '<a:cycle:864023184947675166>', 'value': 0}]
        second = [{'emote': '<a:cycle:864023184947675166>', 'value': 0},
                  {'emote': '<a:cycle:864023184947675166>', 'value': 0},
                  {'emote': '<a:cycle:864023184947675166>', 'value': 0}]
        third = [{'emote': '<a:cycle:864023184947675166>', 'value': 0},
                 {'emote': '<a:cycle:864023184947675166>', 'value': 0},
                 {'emote': '<a:cycle:864023184947675166>', 'value': 0}]
        slot_results_pic = [self.slot(), self.slot(), self.slot()]
        x = random.randint(1, 100)
        z = random.randint(1, 100)
        for i in range(0, len(slot_results_pic)):
            await asyncio.sleep(1.0)
            first[i] = self.slot(x, False, 0)
            second[i] = self.slot(0, True, 0)
            third[i] = self.slot(0, False, z)
            new_slot_embed = None

            slot_results_str, slot_results_str2, slot_results_str3 = "", "", ""
            for j in range(0, len(first)):
                slot_results_str += f"{first[j]['emote']} "
            for j in range(0, len(first)):
                slot_results_str2 += f"{second[j]['emote']} "
            for j in range(0, len(first)):
                slot_results_str3 += f"{third[j]['emote']} "
            # new_slot_embed = discord.Embed(title="**Slot Machine**", description = f"{slot_results_str}")
            await message.edit(content=f"{slot_results_str}\n"
                                       f"{slot_results_str2}\n"
                                       f"{slot_results_str3}")
        if all(x == first[0] for x in first):
            await ctx.send(
                "Congrats " + str(ctx.author.display_name) + "!" + " You won " + str(first[0]['value']) + " gald!")
            await p.reward(ctx.author.id, first[0]['value'])
        if all(x == second[0] for x in second):
            await ctx.send(
                "Congrats " + str(ctx.author.display_name) + "!" + " You won " + str(second[0]['value']) + " gald!")
            await p.reward(ctx.author.id, second[0]['value'])
        if all(x == third[0] for x in third):
            await ctx.send(
                "Congrats " + str(ctx.author.display_name) + "!" + " You won " + str(third[0]['value']) + " gald!")
            await p.reward(ctx.author.id, third[0]['value'])
            # await sent_embed.edit(embed=new_slot_embed)

    @commands.command()
    @commands.cooldown(3, 300, commands.BucketType.user)
    async def rps(self, ctx):
        """Play rock, paper, scissors with Dragonite! """
        rpsGame = ['fire', 'water', 'grass']
        await ctx.send(f"Fire, water, or grass? Choose wisely...")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.lower() in rpsGame

        user_choice = (await self.bot.wait_for('message', check=check)).content

        comp_choice = random.choice(rpsGame)
        if user_choice.lower() == 'fire':
            if comp_choice == 'fire':
                await p.reward(ctx.author.id, 1)

                await p.reward(779219727582756874, 1)

                await ctx.send(
                    f'Well, that was bizarre. We tied. :smirk: \nYour choice: {user_choice}\nMy choice: {comp_choice}')
            elif comp_choice == 'water':
                await p.reward(ctx.author.id, -5)

                await p.reward(779219727582756874, 5)

                await ctx.send(
                    f'Nice try, but I won that time!! :blush: Drago stole 5 gald from you. \nYour choice: {user_choice}\nMy choice: {comp_choice}')
            elif comp_choice == 'grass':
                await p.reward(ctx.author.id, 15)

                await p.reward(779219727582756874, -15)

                await ctx.send(
                    f"Aw, you beat me. :frowning: It won't happen again! You won 15 gald.\nYour choice: {user_choice}\nMy choice: {comp_choice}")

        elif user_choice.lower() == 'water':
            if comp_choice == 'grass':
                await p.reward(ctx.author.id, -5)

                await p.reward(779219727582756874, 5)

                await ctx.send(
                    f'HAHA! Grass absorbs water! :upside_down: Drago stole 5 gald from you. \nYour choice: {user_choice}\nMy choice: {comp_choice}')
            elif comp_choice == 'water':
                await p.reward(ctx.author.id, 1)

                await p.reward(779219727582756874, 1)

                await ctx.send(
                    f'Oh, wacky. :pensive: We just tied.\nYour choice: {user_choice}\nMy choice: {comp_choice}')
            elif comp_choice == 'fire':
                await p.reward(ctx.author.id, 15)

                await p.reward(779219727582756874, -15)
                await ctx.send(
                    f"Aw man, you actually managed to beat me. :laughing: I'm soaked! You won 15 gald. \nYour choice: {user_choice}\nMy choice: {comp_choice}")

        elif user_choice.lower() == 'grass':
            if comp_choice == 'fire':
                await p.reward(ctx.author.id, -5)

                await p.reward(779219727582756874, 5)

                await ctx.send(
                    f'HAHA!! I JUST BLAZED YOU UP!! :smiling_face_with_3_hearts: Drago stole 5 gald from you. \nYour choice: {user_choice}\nMy choice: {comp_choice}')
            elif comp_choice == 'water':
                await p.reward(ctx.author.id, 15)

                await p.reward(779219727582756874, -15)
                await ctx.send(
                    f'Bummer. >: | :pensive: You won 15 gald. \nYour choice: {user_choice}\nMy choice: {comp_choice}')
            elif comp_choice == 'grass':
                await p.reward(ctx.author.id, 1)

                await p.reward(779219727582756874, 1)
                await ctx.send(
                    f"Oh well, we tied. :stuck_out_tongue: \nYour choice: {user_choice}\nMy choice: {comp_choice}")

    @rps.error
    async def rps_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'You are on cooldown; you can use .rps again in {round(error.retry_after, 2)} seconds')
            await p.reward(ctx.author.id, 1)

    #############
    ##HANGMAN####
    #############

    @commands.command(aliases=['hang', 'h'])
    async def hangman(self, message):
        """A game of hangman where there are 8 lives to guess the correct Pokemon."""
        ctx = message
        if ctx.channel.id in self.hang and self.hang[ctx.channel.id]:  # if a game is in session, return
            return
        answer = self.rand_who()
        answer_list = [character for character in answer]
        display = [":regional_indicator_" + str(character) + ":" for character in answer]
        correct = " ".join(display)
        await ctx.send("I have started a new pokemon hangman game :smile: Use ,h <letter to guess> to guess a letter!")
        # await ctx.send(correct)
        print(answer)
        print(answer_list)
        blanks = [':blue_square:'] * len(answer)
        await ctx.send(" ".join(blanks))
        self.hang[ctx.channel.id] = True
        self.lives[ctx.channel.id] = 8
        self.letters[ctx.channel.id] = []
        while self.hang[ctx.channel.id] == True:
            def loser(m):
                nonlocal message
                # print(m.content.lower())
                channel = message.channel
                if 'i quit' in m.content.lower() and m.author == message.author:  # only the person that started the game can quit the game, otherwise wait for 120 second timeout or win game
                    return 'Lose'
                if m.content.lower().startswith(',hang') or m.content.lower().startswith(
                        ',hangman') or m.content.lower().startswith(',h'):
                    guess = m.content.lower()
                    # print(list(guess))
                    autowin = all([elem in list(guess) for elem in answer_list])
                    # print(autowin)
                    if autowin == True:
                        return 'Autowin'
                    elif ',hangman' in m.content.lower() and len(m.content.lower()) > 8:
                        guess = guess[-1]
                    elif ',hang' in m.content.lower() and len(m.content.lower()) > 5:
                        guess = guess[-1]
                    elif ',h' in m.content.lower() and len(m.content.lower()) < 5:
                        guess = guess[-1]
                    if len(guess) > 1:
                        return
                    attempt = guess in answer_list and guess not in self.letters[ctx.channel.id]
                    attempt2 = guess in self.letters[ctx.channel.id]
                    if m.content.lower() == 'i give up' and m.channel == channel:
                        return 'Lose'
                    elif attempt == False and attempt2 == False and m.channel == channel:
                        return ('Bad', guess)
                    elif attempt == True and m.channel == channel:
                        return ('Win', [i for i, x in enumerate(answer_list) if x == str(guess)])
                    elif attempt2 == True and m.channel == channel:
                        return 'Already'
                else:  # message needs to start with .hang or .hangman
                    return

            try:
                msg2 = await self.bot.wait_for('message', check=loser,
                                               timeout=120)  # the game will reset after 240 seconds.
            except asyncio.TimeoutError:
                self.hang[ctx.channel.id] = False
                self.lives[ctx.channel.id] = 8
                self.letters[ctx.channel.id] = []
                return
            if loser(msg2) == "Already":
                await ctx.send("That letter has already been guessed!")
            if loser(msg2) == "Autowin":
                lst = []
                for elem in answer_list:
                    if elem == '-' or elem == ':':
                        lst.append(elem)
                    elif elem == '2':
                        lst.append(":two:")
                    else:
                        lst.append(":regional_indicator_" + elem + ":")
                lst = " ".join(lst)
                await ctx.send(lst)
                await ctx.send("Congratulations :smile: {.author.display_name}".format(
                    msg2) + " has correctly guessed the word with " + str(
                    abs(self.lives[ctx.channel.id])) + " lives remaining and has earned 20 gald!")
                await p.reward("{.author.id}".format(msg2), 20, True)
                self.hang[ctx.channel.id] = False
                self.lives[ctx.channel.id] = 8
                self.letters[ctx.channel.id] = []
            if loser(msg2)[0] == 'Bad':
                self.lives[ctx.channel.id] -= 1
                if self.lives[ctx.channel.id] != 0:
                    self.letters[ctx.channel.id].append(loser(msg2)[1])
                    await ctx.send("Incorrect guess. You have " + str(self.lives[ctx.channel.id]) + " lives remaining!")
                else:
                    await ctx.send("You ran out of guesses!" + " The correct answer was " + str(correct) + " !")
                    self.lives[ctx.channel.id] = 8
                    self.hang[ctx.channel.id] = False
                    self.letters[ctx.channel.id] = []
            if loser(msg2)[0] == 'Win':
                await p.reward("{.author.id}".format(msg2), 2, True)
                for elem in loser(msg2)[1]:
                    if answer_list[elem] == '-' or answer_list[elem] == ":":
                        blanks[elem] = str(answer_list[elem])
                    elif answer_list[elem] == '2':
                        blanks[elem] = ":two:"
                    else:
                        blanks[elem] = ':regional_indicator_' + str(answer_list[elem]) + ":"
                if ":blue_square:" not in blanks:
                    await ctx.send(" ".join(blanks))
                    await ctx.send("Congratulations :smile: {.author.display_name}".format(
                        msg2) + " has correctly guessed the word with " + str(
                        abs(self.lives[ctx.channel.id])) + " lives remaining and has earned 20 gald!")
                    await p.reward("{.author.id}".format(msg2), 20, True)
                    self.hang[ctx.channel.id] = False
                    self.lives[ctx.channel.id] = 8
                    self.letters[ctx.channel.id] = []
                else:
                    # await ctx.send(correct)
                    await ctx.send("Correct guess :smile: ")
                    await ctx.send(" ".join(blanks))
            elif loser(msg2) == 'Lose':
                self.hang[ctx.channel.id] = False
                self.letters[ctx.channel.id] = []
                self.lives[ctx.channel.id] = 8
                channel = message.channel
                await channel.send("Bummer :disappointed: {.author.display_name}".format(
                    msg2) + '... The correct answer was ' + str(
                    correct) + ". {.author.display_name}".format(msg2) + " lost 10 gald.")
                await p.reward("{.author.id}".format(msg2), -10, True)

    @commands.command()
    async def spin(self, ctx):
        """Spins a bottle and randomly lands on someone in the server."""
        await p.reward(ctx.author.id, 1)
        tag = [779219727582756874]  # there is a chance for bottle to land on Dragonite
        for member in ctx.guild.members:
            if member.status is not discord.Status.offline and not member.bot:
                tag.append(member.id)
        x = random.choice(tag)  # This is the user id of the person
        y = await ctx.author.guild.fetch_member(x)  # this is the user tag of the person
        await ctx.send("Spins a bottle and it lands on " + str(y))
        
    def rand_who(self):  # for the who function
        with open("scramble.txt", "r") as file:
            allText = file.read()
            words = list(map(str, allText.split()))

            # print random string
            return random.choice(words)

def setup(bot):
    bot.add_cog(games(bot))
