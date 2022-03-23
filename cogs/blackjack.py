import discord
from discord.ext import commands
import random
import os
import asyncio
from asyncio import sleep
import discord.ext.commands
import time
import datetime, asyncpg
from random import sample
########
from discord.utils import get
import PIL
from PIL import Image

intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix=',', case_insensitive=True, help_command=None, intents=intents)


class CardGames(commands.Cog):
    """A discord blackjack game that uses cards from Tales of Vesperia."""

    def __init__(self, bot):
        self.bot = bot
        self.games = {}  # A dictionary that contains the active channels currently
        # playing a blackjack game. Key is the channel id and value is the discord user id.

    @commands.command()
    async def bj(self, ctx):
        """Blackjack game. The player can either hit or stay. Beat the dealer's score.
        The dealer stops hitting once their total score is 17 or above. If any player
        has a score above 21, they automatically bust. Uses cards from Tales of Vesperia."""
        file = discord.File("cards/player.jpg")
        if ctx.channel.id in self.games:
            if self.games[ctx.channel.id] != ctx.author.id:  # if a game is in session, return
                return
            else:
                if ctx.message.content == ".bj":  # if a game is in session, remind the player to make a choice.
                    await ctx.send("Please select .bj hit or .bj stay")
        else:
            self.games[ctx.channel.id] = ctx.author.id
            deck = Deck()  # create a deck that is utilized between the player and the AI
            player = Player(deck, ctx.author.id)
            AI = Player(deck, 0)
            for i in range(0, 2):  # both the player and the dealer start off with two cards.
                player.draw()
                AI.draw()
            self.saveCardPicture(player.notSortedCardPaths())
            embed = discord.Embed(title=f" {ctx.author.display_name} started a game of blackjack!", description=
            f"Select either <prefix>bj hit or <prefix>bj stay", colour=discord.Color.red())
            embed.set_image(url="attachment://cards/player.jpg")
            await ctx.send(file=file, embed=embed)  # showcases the first card and the back of the 2nd card for the
            # opponent.
            embed = discord.Embed(title=f"Dragonite's Cards:", colour=discord.Color.red())
            self.saveCardPicture([AI.cards[0].getPath(), "cards/back.png"])
            file = discord.File("cards/player.jpg")
            embed.set_thumbnail(url="attachment://cards/player.jpg")
            await ctx.send(file=file, embed=embed)
            while self.games[ctx.channel.id]:  # while the game is not over
                def playerBust():
                    """A helper method that decides if the game is over for the player."""
                    return player.score > 21

                def gameOver():
                    """A helper method that decides if the game is over."""
                    if AI.score > 21:
                        return "Dragonite busts!"
                    if AI.score == 21:
                        return "Dragonite gets a blackjack!"
                    if AI.score == player.score:
                        return "Push"
                    if AI.score > player.score:
                        return "Dragonite wins!"
                    if 16 < AI.score < player.score:
                        return f"{ctx.author.display_name} wins!"
                    return "null"

                def check(m):
                    """Performs a check for await. The author of the message being
                    checked must be the same author as the person who sent the message.
                    """
                    if m.author == ctx.author:
                        if ".bj i quit" in m.content.lower():
                            return 'Lose'
                        elif '.bj stay' in m.content.lower():
                            return 'stay'
                        elif '.bj hit' in m.content.lower():
                            return 'hit'

                try:
                    msg2 = await self.bot.wait_for('message', check=check,
                                                   timeout=30)  # the game will reset after 30 seconds.
                    file = discord.File("cards/player.jpg")
                except asyncio.TimeoutError:
                    del self.games[ctx.channel.id]
                    return
                if check(msg2) == "hit":
                    player.draw()
                    self.saveCardPicture(player.notSortedCardPaths())
                    if not playerBust():
                        embed = discord.Embed(title=f"{ctx.author.display_name}", colour=discord.Color.red())
                        embed.set_image(url="attachment://cards/player.jpg")
                        await ctx.send(file=file, embed=embed)
                    else:
                        embedPlayer = discord.Embed(title=f"{ctx.author.display_name} busts!\n", description=
                        f"\nScore: {player.score}",
                                                    colour=discord.Color.red())
                        embedPlayer.set_image(url="attachment://cards/player.jpg")
                        await ctx.send(file=file, embed=embedPlayer)
                        file = discord.File("cards/player.jpg")
                        self.saveCardPicture(AI.notSortedCardPaths())
                        embedAI = discord.Embed(title=f"Dragonite", description=f"Score: {AI.score}",
                                                colour=discord.Color.red())
                        embedAI.set_image(url="attachment://cards/player.jpg")
                        await ctx.send(file=file, embed=embedAI)
                        del self.games[ctx.channel.id]  # resets the game dictionary so that a new game can begin
                        return
                elif check(msg2) == 'stay':
                    while gameOver() == "null":  # The AI will keep drawing cards until the game is not over.
                        AI.draw()
                    self.saveCardPicture(AI.notSortedCardPaths())
                    embed = discord.Embed(title=f"{gameOver()}",
                                          description=f"{ctx.author.display_name}'s score: {player.score}\n" +
                                                      f"Dragonite's score: {AI.score}", color=discord.Color.red())
                    embed.set_image(url="attachment://cards/player.jpg")
                    await ctx.send(file=file, embed=embed)
                    del self.games[ctx.channel.id]
                    return
                elif check(msg2) == '.bj i quit':
                    await ctx.send("Game over! You backed out!")
                    del self.games[ctx.channel.id]
                    return
                else:
                    return  # message needs to start with .bj

    def saveCardPicture(self, cardList):
        """A helper function that generates a picture saved at
        cards/player.jpg based on the pictures inputted in the cardList."""
        images = [Image.open(x) for x in
                  cardList]  # for every card in the deck, showcase the card in the picture to send.
        widths, heights = zip(*(i.size for i in images))
        total_width = sum(widths)
        max_height = max(heights)
        new_im = Image.new("RGB", (total_width, max_height))
        x_offset = 0
        for im in images:
            new_im.paste(im, (x_offset, 0))
            x_offset += im.size[0]
        new_im.save('cards/player.jpg')

    @commands.command()
    async def poker(self, ctx):
        """A poker game based on Five-Card Draw. A player can swap a card by clicking on the
        corresponding button labeled 1 through 5 and subsequently click the check mark to
        swap the selected cards. If a player receives at least One Pair, they have the
        option to 'Double their Bet.' In this minigame, the player is given a card and
        predicts whether the next card will be higher or lower than the current card
        in terms of value. The cards are drawn without replacement until one session
         of the game concludes. """
        if ctx.channel.id in self.games:  # if a game is in session, return
            if self.games[ctx.channel.id] != ctx.author.id:
                return
        else:
            self.games[ctx.channel.id] = ctx.author.id
            deck = Deck()  # create a deck that the player utilizes.
            player = Player(deck, ctx.author.id)
            for i in range(0, 5):
                player.draw()
            self.saveCardPicture(player.notSortedCardPaths())
            message = await ctx.send(f"Which cards to swap?\n" + f"{ctx.author.display_name}'s cards:")
            await ctx.send(file=discord.File("cards/player.jpg"))
            choices = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "✅"]
            for choice in choices:
                await message.add_reaction(choice)
            emoji_list = [False, False, False, False, False]

            def check(reaction, user):
                """Adds valid emojis that have been reacted to a queue,
                which will process the cards to swap later."""
                if user == ctx.author:
                    if str(reaction.emoji) != "✅":
                        if str(reaction.emoji) in choices:
                            if str(reaction.emoji) not in emoji_list:
                                emoji_list[choices.index(str(reaction.emoji))] = str(reaction.emoji)
                            elif str(reaction.emoji) in emoji_list:
                                emoji_list[choices.index(str(reaction.emoji))] = str(reaction.emoji)
                    return user == ctx.author and str(reaction.emoji) == "✅"
                # This makes sure nobody except the command sender can interact with the "menu"

            def cardPayout():
                frequency = {}
                suits = {}
                for card in player.cards:
                    if card.getName() == "Ace":  # adjust the Ace value
                        card.value = 11
                for elem in player.cards:
                    if elem.getName() not in frequency:
                        frequency[elem.getName()] = 1
                    else:
                        frequency[elem.getName()] += 1

                    if elem.getSuit() not in suits:
                        suits[elem.getSuit()] = 1
                    else:
                        suits[elem.getSuit()] += 1

                # Royal Flush
                def royalHelper():
                    if all([x.getSuit() == player.cards[0].suit for x in
                            player.cards]):  # if all cards have the same suit
                        royal_flush = ["10", "Jack", "King", "Queen", "Ace"]
                        for card in player.cards:
                            if card.getSuit() in royal_flush:
                                royal_flush.remove(card.getSuit())
                            if len(royal_flush) == 0:
                                return "Royal Flush!"

                if len(suits) == 1:
                    if royalHelper() is not None:
                        return "Royal Straight Flush"
                else:
                    royalHelper()
                # Straight Flush
                if len(suits) == 1:
                    result = self.flush(player)
                    if result is not None:
                        return f"Straight {result}"
                # Four of A Kind
                if 4 in frequency.values():
                    return "Four of a Kind!"
                # Full House
                elif len(frequency) == 2:
                    return "Full House!"
                elif len(suits) == 1:
                    return "Flush!"
                # Straight
                elif self.flush(player) is not None:
                    return "Straight"
                # Three of a Kind
                elif 3 in frequency.values():
                    return "Three of a Kind!"
                elif len(frequency) == 3:
                    return "Two Pair!"
                elif len(frequency) == 4:
                    return "One Pair."
                else:
                    return "No Pair."

            while True:
                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=check)
                except asyncio.TimeoutError:
                    del self.games[ctx.channel.id]
                    return
                for i in range(len(emoji_list)):
                    if emoji_list[i]:
                        player.swapCard(i)
                self.saveCardPicture(player.notSortedCardPaths())
                await ctx.send("Swapped cards: ")
                await ctx.send(file=discord.File("cards/player.jpg"))
                result = cardPayout()
                await ctx.send(result)
                if result in ["No Pair.", "One Pair."]:
                    del self.games[ctx.channel.id]
                    return
                choices = ["✅", "❎"]
                message = await ctx.send("Double bet?")
                for choice in choices:
                    await message.add_reaction(choice)

                def doubleBet(reaction, user):
                    """A helper function that determines whether
                    or not the player decides to double the bet
                    based on the reacted emoji. """
                    if user == ctx.author:
                        if str(reaction.emoji) in choices:
                            if str(reaction.emoji) == "✅":
                                return "Double"
                            else:
                                return "Game Over"

                try:
                    reaction, user = await self.bot.wait_for("reaction_add", timeout=10, check=doubleBet)
                except asyncio.TimeoutError:
                    del self.games[ctx.channel.id]
                    return
                if doubleBet(reaction, user) == "Double":
                    await self.doubleBet(ctx, player)
                else:
                    del self.games[ctx.channel.id]
                    return

    async def doubleBet(self, ctx, player):
        """A function that allows a player to double their bet
        up to 10 times, which is also based on Tales of Vesperia."""
        gameOver = False
        counter = 0
        for i in range(0, 4):
            player.cards.pop()
        self.saveCardPicture(player.notSortedCardPaths())
        message = await ctx.send(file=discord.File("cards/player.jpg"))

        def highOrLow(reaction, user):
            """Determines whether or not the game is over
             and calculates if the next drawn card is higher
             or lower than the current card."""
            nonlocal gameOver
            nonlocal counter
            if ctx.author == user and str(reaction.emoji) in ["🇭", "🇱"]:
                counter += 1
                if str(reaction.emoji) == "🇭":
                    if player.cards[0].worth <= player.cards[1].worth:
                        return "Bet Doubled!"
                    else:
                        gameOver = True
                        return "Game Over!"
                elif str(reaction.emoji) == "🇱":
                    if player.cards[0].worth >= player.cards[1].worth:
                        return "Bet Doubled!"
                    else:
                        gameOver = True
                        return "Game Over!"

        def continueGame(reaction, user):
            """Returns true if and only if the user decides
            to continue doubling their bet."""
            if ctx.author == user and str(reaction.emoji) in ["✅", "❎"]:
                return str(reaction.emoji) == "✅"

        while not gameOver and counter <= 10:
            player.draw()
            for choice in ["🇭", "🇱"]:
                await message.add_reaction(choice)
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30, check=highOrLow)
                try:
                    await message.clear_reactions()
                except:
                    pass
            except asyncio.TimeoutError:
                del self.games[ctx.channel.id]
                return
            self.saveCardPicture([player.cards[0].getPath(), player.cards[1].getPath()])
            file = discord.File("cards/player.jpg")
            embed = discord.Embed(color=discord.Color.red())
            embed.set_image(url="attachment://cards/player.jpg")
            message = await ctx.send(file=file, embed=embed)
            if not highOrLow(reaction, user) == "Bet Doubled!":
                await ctx.send(content="Game Over!")
                del self.games[ctx.channel.id]
                return
            message = await ctx.send(f"Bet doubled! Double Bet? Active Card: {player.cards[1].getName()} " +
                                     f"{player.cards[1].getSuit()}")
            for choice in ["✅", "❎"]:
                await message.add_reaction(choice)
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=15, check=continueGame)
                try:
                    await message.clear_reactions()
                except:
                    pass
            except asyncio.TimeoutError:
                del self.games[ctx.channel.id]
                return
            if not continueGame(reaction, user):
                del self.games[ctx.channel.id]
                return
            player.cards.pop(0)

    def flush(self, player):
        """Checks if the current deck contains an instance of
        a flush. A flush is a hand that contains five cards all
        of the same suit, not all of sequential rank. """
        temp = sorted(player.cards, key=lambda x: x.worth)
        cardCheck = iter(sorted(player.cards, key=lambda x: x.worth))
        expectedValue = min(player.cards, key=lambda x: x.worth).worth
        expectedCard = "Jack"
        totalFlush = 0
        for card in cardCheck:
            if card.getName() == "Ace" and expectedValue == 14:
                expectedValue = 2
                totalFlush += 1
            elif card.worth < 10:
                if expectedValue != card.value:
                    break
                expectedValue = card.value + 1
                totalFlush += 1
            elif card.getName() == "10":
                if expectedValue != card.value:
                    break
                expectedValue = 11
                totalFlush += 1
                expectedCard = "Jack"
            else:
                if expectedValue != card.worth:
                    break
                if expectedCard == card.getName() == "Jack":
                    expectedCard = "Queen"
                    totalFlush += 1
                    expectedValue = 12
                    continue
                elif expectedCard == "Queen" == card.getName():
                    expectedCard = "King"
                    totalFlush += 1
                    expectedValue = 13
                    continue
                elif expectedCard == "King" == card.getName():
                    expectedCard = "Ace"
                    totalFlush += 1
                    expectedValue = 14
                    continue
        if totalFlush == 5:
            return "Flush!"
        else:
            return None


class Player:
    """A class representing the player in a game of poker or blackjack.
    Cards is a list of cards currently in the player's hand. discordID is
    the player's ID. """
    def __init__(self, deck, discordID):
        self.cards = []
        self.deck = deck
        self.score = 0
        self.id = discordID

    def draw(self):
        """Draws a card from the deck. Updates the player's score,
        used in blackjack."""
        self.cards.append(self.deck.deck.pop())
        self.score = self.score + self.cards[-1].value
        self.updateAce()

    def updateAce(self):
        """If an Ace is in the player's hand, update the player's score
        if it would benefit the player. """
        if self.score > 21:
            for elem in self.cards:
                if elem.card == "Ace" and elem.value == 11:
                    elem.value = 1
                    self.score = self.score - 10

    def cards(self):
        return self.cards

    def notSortedCardPaths(self):
        """Returns a list of paths used for sending
        a picture of cards on Discord. """
        return [x.path for x in self.cards]

    def cardPaths(self):
        sort = sorted([x for x in self.cards], key=lambda x: x.worth)
        return [x.path for x in sort]

    def swapCard(self, i):
        """Remove a card from the player's hand at index i and replaces
        it with a card from the Deck."""
        self.cards[i] = self.deck.deck.pop()


class Deck:
    """Generates a deck of 52 shuffled cards."""
    def __init__(self):
        self.deck = self.generateDeck()
        random.shuffle(self.deck)

    def generateDeck(self):
        """There are 13 types of cards and 4 types of suits."""
        deck = []
        total = 0
        for i in range(0, 13):
            card = self.computeCardType(i)

            value = 11 if i == 0 else i + 1 if i < 10 else 10

            deck.append(Card(card, "Heart", value, total))
            total += 1
            deck.append(Card(card, "Club", value, total))
            total += 1
            deck.append(Card(card, "Diamond", value, total))
            total += 1
            deck.append(Card(card, "Spade", value, total))
            total += 1

        return deck

    def computeCardType(self, i):
        lst = ["Ace", "2", "3", "4", "5",
               "6", "7", "8", "9", "10",
               "Jack", "Queen", "King"]
        return lst[i]

    def getCardString(self, i):
        """Useful for debugging."""
        card = self.deck[i].card
        suit = self.deck[i].suit
        value = self.deck[i].value
        return f"Card: {card}\n" \
               f"Suit: {suit}\n" \
               f"Value: {value}"

    def getCard(self, i):
        return self.deck[i]


class Card:
    """The card is the type of card. Ex: Ace, two, three, King, Queen Jack.
    The suit is Hearts, Clubs, Diamonds, or Spades.
    The value is an integer between 1-10. """

    def __init__(self, card, suit, value, total):
        self.card = card
        self.suit = suit
        self.value = value
        self.path = self.generatePath(total)
        self.worth = 11 if self.card == "Jack" else 12 if self.card == "Queen" else 13 if self.card == "King" else 14 if self.card == "Ace" else self.value

    def getName(self):
        return self.card

    def getSuit(self):
        return self.suit

    def getValue(self):
        return self.value

    def getPath(self):
        return self.path

    def generatePath(self, total):
        return f"cards/{total}.png"


def setup(bot):
    bot.add_cog(CardGames(bot))
