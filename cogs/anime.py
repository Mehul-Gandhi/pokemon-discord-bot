import discord
from discord.ext import commands
import random
import os
import asyncio
import discord.ext.commands
import time
import datetime
from jikanpy import Jikan
from pathlib import Path
from cogs.pokemon import pokemon
import asyncpg

jikan = Jikan()  # for anime searching


async def create_db_pool():
    client.pg_con = await asyncpg.create_pool(database='postgres', user='postgres', password='Mehul09!')


intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix='.', case_insensitive=True, help_command=None, intents=intents)

p = pokemon(client)  # used for awarding gald to members.


class anime(commands.Cog):
    """A class containing anime commands. """

    def __init__(self, bot):
        self.bot = bot
        self.current_year = 2022  # used to show how long ago an anime was aired.

    @commands.command()
    async def anime(self, ctx, *, message):
        """Searches information about an anime from MyAnimeList. """
        await p.reward(ctx.author.id, 1)
        id = jikan.search('anime', str(message))['results'][0]['mal_id']
        anime = jikan.anime(str(id))
        lst = []
        for i in range(0, len(anime['genres'])):
            lst.append(anime['genres'][i]['name'])
        genres = ", ".join(lst)
        embed = discord.Embed(title=str(anime['title']), description=str(anime['url']), color=discord.Color.orange())
        embed.add_field(name=" MAL Score", value=anime['score'], inline=True)
        embed.add_field(name="Ranking", value="#" + str(anime['rank']), inline=True)
        embed.add_field(name="Format", value=anime['type'], inline=True)
        embed.add_field(name="Anime Source", value=anime['source'], inline=True)
        embed.add_field(name="Episodes", value=anime['episodes'], inline=True)
        embed.add_field(name="Status", value=anime['status'], inline=True)
        embed.add_field(name="Air Date", value=anime['aired']['string'], inline=True)
        embed.add_field(name="Genres", value=str(genres), inline=True)
        embed.add_field(name="Aired", value=str(self.current_year
                                                - anime['aired']['prop']['to']['year']) + " years ago",
                        inline=True)
        if len(anime['synopsis']) > 1024:
            embed.add_field(name="Synopsis", value=anime['synopsis'][:1024], inline=False)
            embed.add_field(name="** **", value=anime['synopsis'][1024:], inline=False)
        else:
            embed.add_field(name="Synopsis", value=anime['synopsis'], inline=False)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_thumbnail(url=str(anime['image_url']))
        await ctx.send(embed=embed)

    @commands.command()
    async def baka(self, message, *, member: discord.Member):
        """Call a user a baka. Displays a random pat picture or gif."""
        await p.reward(message.author.id, 1)
        baka_list = ['https://tenor.com/view/tales-of-xilia-gif-10176908',
                     'https://media.tenor.com/images/38fff1193d3535d83a3e4d73f032ef61/tenor.gif',
                     'https://media.tenor.com/images/4e548e93b7e5f0842578a755472796ee/tenor.gif',
                     'https://media.tenor.com/images/52ebe3c79f0eb104f0eb6e4abd70a4a4/tenor.gif',
                     'https://media2.giphy.com/media/11jPPp3IdY1wEU/giphy.gif',
                     'https://media.tenor.com/images/9305f7da173a0790953e87f7709aeba1/tenor.gif',
                     'https://i.kym-cdn.com/photos/images/newsfeed/001/028/204/4d9.gif',
                     'https://media.tenor.com/images/5dece08ee566262a54aa8e62ae915f2d/tenor.gif',
                     'https://media.tenor.com/images/b7d47594e641c4c7082a61de70d461d0/tenor.gif',
                     'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/7bb9f2f8-d65e-4538-a5b2-1493ee7070a8/d8kqa2t-d74f18b1-f698-4fc8-9282-e6bebcb66b01.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzdiYjlmMmY4LWQ2NWUtNDUzOC1hNWIyLTE0OTNlZTcwNzBhOFwvZDhrcWEydC1kNzRmMThiMS1mNjk4LTRmYzgtOTI4Mi1lNmJlYmNiNjZiMDEuZ2lmIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.ZNqnq1n7PwR11fYhhVaWjcGUjpmfF67Kuqiir_F8Gu8',
                     'https://data.whicdn.com/images/250233242/original.gif',
                     'https://thumbs.gfycat.com/IdealGlassBlackcrappie-size_restricted.gif',
                     'https://i.pinimg.com/originals/82/49/91/82499189c7b367709facc96d83c76ca9.gif',
                     'https://i.pinimg.com/originals/c1/f2/21/c1f2211cf5de352d22f13ea9c621b345.gif',
                     'http://pa1.narvii.com/6214/d4af083af5f98b224d2a2ee85e5b0fdeff4eeadb_00.gif',
                     'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/dcd07180-642e-40c6-9a8f-3b413c5bae09/d9gfrhl-d1b27270-3333-4912-b9f3-5e12d08772a3.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2RjZDA3MTgwLTY0MmUtNDBjNi05YThmLTNiNDEzYzViYWUwOVwvZDlnZnJobC1kMWIyNzI3MC0zMzMzLTQ5MTItYjlmMy01ZTEyZDA4NzcyYTMuZ2lmIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.0lXUEX0H3gXYOetQV5LU8IZYpE00C6Fs3Gfgj9a5OMk',
                     'https://64.media.tumblr.com/91f4123a95706c9662ef363f32fb1f1e/tumblr_nu3r9sPE3k1qa94xto1_500.gif',
                     'https://media.tenor.com/images/4f032a0a3c1432f0ec43acfa8a5b0515/tenor.gif',
                     'https://media.tenor.com/images/307b2d83684874e43cce17ac48d8f90b/tenor.gif',
                     'https://c-sg.smule.com/rs-s77/arr/13/0f/296ae559-1e48-4877-b8e2-ade4639f8030_1024.jpg',
                     'http://i.imgur.com/rhP3Vof.gif',
                     'https://media1.tenor.com/images/7e86d21525bd3de8ecf65c84cec1e882/tenor.gif?itemid=17737654',
                     'http://24.media.tumblr.com/tumblr_m36jurSwDT1qb6m0to2_250.gif',
                     'https://i.imgur.com/sWPnHMR.gif?noredirect',
                     'https://thumbs.gfycat.com/DirtyFastFinnishspitz-max-1mb.gif',
                     'https://media.tenor.com/images/537888875d8f533aeb4c8451a6cadbb5/tenor.gif',
                     'https://i.imgur.com/kSzJs14.gif', 'https://media1.giphy.com/media/60VC6fZJecyR2/giphy.gif',
                     'https://media.tenor.com/images/7bb29245de5cfb4154ec37dd962a4491/tenor.gif',
                     'https://64.media.tumblr.com/b22d1209ab2ebdc60cc5ad183bca3ca4/577be750c1473a5c-7e/s500x750/b6d3ceffac29b127183b8de429c8ce0cd20b4a3d.gif',
                     'https://slm-assets.secondlife.com/assets/15264589/view_large/maxresdefault.jpg?1476216728',
                     'https://pbs.twimg.com/media/ETzcowuX0AEUEy-.jpg',
                     'https://www.dictionary.com/e/wp-content/uploads/2018/09/baka-3-265x300.png',
                     'https://cdn141.picsart.com/336684352066203.jpg?type=webp&to=crop&r=1280',
                     'https://thumbs.gfycat.com/CapitalDarlingBlackcrappie-size_restricted.gif',
                     'https://media1.tenor.com/images/99ed452a33c03a91c37083df7eb2419f/tenor.gif?itemid=5586968',
                     'https://thumbs.gfycat.com/EarlyVelvetyKouprey-size_restricted.gif',
                     'https://i.pinimg.com/originals/97/04/cb/9704cba1bd3cd847d07b782d6ef7b598.gif',
                     'https://image.myanimelist.net/ui/OK6W_koKDTOqqqLDbIoPAmHwK2TVANJVq1q9zZxiy1w'
                     ]
        embed = discord.Embed(
            title=f"{message.author.display_name}" + " calls " + str(member.display_name) + " a... um... baka!",
            color=discord.Colour.orange())
        embed.set_image(url=str(random.choice(baka_list)))
        await message.channel.send(embed=embed)

    @baka.error
    async def baka_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the member to call a baka.")
        else:
            raise error

    @commands.command()
    async def hug(self, message, *, member: discord.Member):
        """Hug a user of your choice. Displays a random pat picture or gif."""
        await p.reward(message.author.id, 1)
        hug_list = ['https://i.gifer.com/8WPN.gif',
                    'https://media1.tenor.com/images/201176ed6c3480a1ac7f542a4b255f0f/tenor.gif?itemid=15793171',
                    'https://data.whicdn.com/images/203829122/original.gif', 'https://i.gifer.com/RziH.gif',
                    'https://i.imgur.com/cZWWATV.gif'
                    'https://i.pinimg.com/originals/85/72/a1/8572a1d1ebaa45fae290e6760b59caac.gif',
                    'https://i.gifer.com/2QEa.gif',
                    'https://gifimage.net/wp-content/uploads/2017/06/anime-hug-gif-10.gif',
                    'https://cdn.nekos.life/hug/hug_059.gif', 'https://cdn.nekos.life/hug/hug_022.gif',
                    'https://cdn.nekos.life/hug/hug_074.gif',
                    'https://media1.tenor.com/images/9b3415c97b63be1f1818e05d199d68bb/tenor.gif?itemid=21131180',
                    'https://media1.tenor.com/images/1d94b18b89f600cbb420cce85558b493/tenor.gif?itemid=15942846',
                    'https://i.pinimg.com/originals/8d/ab/29/8dab296aed2cbe25af8ebb4703517356.gif',
                    'https://i.imgur.com/r9aU2xv.gif?noredirect',
                    'https://thumbs.gfycat.com/BlueDecimalAardwolf-max-1mb.gif',
                    'http://25.media.tumblr.com/tumblr_ma7l17EWnk1rq65rlo1_500.gif',
                    'https://media1.giphy.com/media/lrr9rHuoJOE0w/giphy.gif',
                    'https://thumbs.gfycat.com/BountifulElderlyCusimanse-max-1mb.gif',
                    'https://i.imgur.com/nrdYNtL.gif',
                    'https://1.bp.blogspot.com/-JUqgHJmjyDs/YG76cI82URI/AAAAAAAAD_w/0QtzGkpiel0OlTVEdRCDLmK5Ot46rEq8QCLcBGAsYHQ/s300/romantic%2Banime%2Bhug%2Bgif1.gif',
                    'https://i.pinimg.com/originals/f0/2c/7e/f02c7e8d52dac534526dbb86ccc5289e.gif',
                    'https://thumbs.gfycat.com/FrenchShimmeringAmericanmarten-size_restricted.gif',
                    'https://i0.wp.com/2.bp.blogspot.com/-XPqck-C979s/V-QbRIOoqbI/AAAAAAAADzM/seUBJKyKCiQ5W2kScB627WjcKU5Pq1VKwCLcB/s400/chuunibyou.gif?resize=582%2C294&ssl=1',
                    'https://i.imgur.com/IAxUnda.gif',
                    'https://media1.tenor.com/images/201176ed6c3480a1ac7f542a4b255f0f/tenor.gif?itemid=15793171',
                    'https://i.imgur.com/oltglhh.gif', 'https://media3.giphy.com/media/wnsgren9NtITS/giphy.gif',
                    'https://66.media.tumblr.com/5dfb67d0a674fe5f81950478f5b2d4ed/tumblr_ofd4e2h8O81ub9qlao1_400.gif',
                    'https://media1.tenor.com/images/506aa95bbb0a71351bcaa753eaa2a45c/tenor.gif?itemid=7552075',
                    'https://i0.wp.com/media1.tenor.com/images/ba2328b7fb5d0998deb7e06600089709/tenor.gif?itemid=7552072?resize=91,91',
                    'https://acegif.com/wp-content/gif/anime-hug-81.gif', 'https://i.imgur.com/GuADSLm.gif',
                    'https://i.pinimg.com/originals/b6/2f/04/b62f047f8ed11b832cb6c0d8ec30687b.gif',
                    'https://data.whicdn.com/images/224946029/original.gif',
                    'http://38.media.tumblr.com/35eac6c8d6de05b24ebd554fef7efeae/tumblr_njuitaR85p1u03j02o1_500.gif',
                    'https://acegif.com/wp-content/gif/anime-hug-70.gif',
                    'https://media1.giphy.com/media/qscdhWs5o3yb6/200.gif',
                    'https://media.giphy.com/media/VGACXbkf0AeGs/giphy.gif',
                    'https://image.myanimelist.net/ui/OK6W_koKDTOqqqLDbIoPAsfebnwTQs0RbMdOSZzLrcA',
                    'https://i.imgur.com/ntqYLGl.gif', 'https://i.gifer.com/8VnY.gif',
                    'https://i.imgur.com/3OzmqMS.gif',
                    'https://i.pinimg.com/originals/9e/37/86/9e378638db8cc4d64f54e8bb9e924c3e.gif',
                    'https://i.pinimg.com/originals/2a/e8/ac/2ae8ac3752d66e8aad046d9f0d35710a.gif',
                    'https://i.pinimg.com/originals/b3/3d/60/b33d604c507568fb402062c13594182d.gif',
                    'https://media2.giphy.com/media/ShAchOHe38Aak/200.gif',
                    'https://data.whicdn.com/images/315778649/original.gif',
                    'https://data.whicdn.com/images/189855245/original.gif',
                    'https://media.tenor.com/images/6deb677d1a080655e2c916452e4b6ba5/tenor.gif',
                    'https://media1.tenor.com/images/6a7055a00a2e37f9c128042203754e2e/tenor.gif?itemid=17890770',
                    'https://i.imgur.com/WO9Dmt7.gif',
                    'https://i.pinimg.com/originals/7b/eb/ba/7bebba13758d93b089b3ee500345499c.gif',
                    'https://i.pinimg.com/originals/78/02/3f/78023f02117db3a10dda46e2bea6647e.gif',
                    'https://media.tenor.com/images/7e166af8ae4d55c69b8ec4a4943b7269/tenor.gif',
                    'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/80ff523f-ff84-457d-a547-464588d3a3d3/db7jelh-5ffbc5af-fbe7-4645-85db-0482f97e016b.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcLzgwZmY1MjNmLWZmODQtNDU3ZC1hNTQ3LTQ2NDU4OGQzYTNkM1wvZGI3amVsaC01ZmZiYzVhZi1mYmU3LTQ2NDUtODVkYi0wNDgyZjk3ZTAxNmIuZ2lmIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.6cfnrROTxU7OzVDW4RXoFruZfRAYW_5zf4jPQ41dJ5M',
                    'https://i2.wp.com/media.giphy.com/media/5eyhBKLvYhafu/giphy.gif',
                    'https://i.pinimg.com/originals/38/35/d9/3835d9d60de188693efa3adbed685519.gif',
                    'https://thumbs.gfycat.com/AmazingAcclaimedDoe-size_restricted.gif',
                    'https://64.media.tumblr.com/7e758a0cae0b15d892166879e0e8982d/tumblr_n64z9xBrSN1qckvvzo1_250.gif',
                    'https://68.media.tumblr.com/24d0574a8f7f03fc73db6a0194cc0cb4/tumblr_op6gauJW141ru0b90o3_r1_500.gif',
                    'https://cutewallpaper.org/21/anime-boy-hugging-crying-girl/Anime-Couple-Cry-Favim-Com-GIF.gif',
                    'https://cutewallpaper.org/21/anime-boy-hugging-crying-girl/Girl-boy-hug-GIFs-Get-the-best-GIF-on-GIPHY.gif',
                    'https://64.media.tumblr.com/d1aee4d23527d2909f684055edb03de6/tumblr_ph50ooR8th1qc4uvwo1_540.gif',
                    'https://giphy.com/gifs/hug-3ZnBrkqoaI2hq',
                    'https://images-ext-1.discordapp.net/external/w0g0ptHOm2meCJUJ4-iDJogzsYFz7pCxcTktDykaAvM/https/cdn.nekos.life/hug/hug_002.gif']
        embed = discord.Embed(
            title=f"{message.author.display_name}" + " hugs " + str(member.display_name) + "!",
            color=discord.Colour.orange())
        embed.set_image(url=str(random.choice(hug_list)))
        await message.channel.send(embed=embed)

    @hug.error
    async def hug_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the member to hug.")
            await p.reward(ctx.author.id, 1)
        else:
            raise error

    @commands.command(aliases=['kissy'])
    async def kiss(self, message, *, member: discord.Member):
        """Kiss a user of your choice. Displays a random kiss picture or gif."""
        await p.reward(message.author.id, 1)
        kiss_list = ['https://cdn.nekos.life/kiss/kiss_065.gif',
                     'https://acegif.com/wp-content/uploads/anime-kiss-6.gif',
                     'https://media1.tenor.com/images/5cf6c2fef93911111538d837ec71c24c/tenor.gif?itemid=5448064',
                     'https://media3.giphy.com/media/CzCi6itPr3yBa/giphy.gif',
                     'https://i2.wp.com/nileease.com/wp-content/uploads/2020/08/a38e2494f071e28c7e5872d5d0e5272e.gif?fit=360%2C190&ssl=1',
                     'https://i.pinimg.com/originals/bf/fb/80/bffb8052cdfd5785cb03cba8788aee30.gif',
                     'https://www.icegif.com/wp-content/uploads/anime-kiss-icegif.gif',
                     'https://media1.tenor.com/images/ee88010c910818d2705bbfaeb26e0a91/tenor.gif?itemid=12192868',
                     'https://thumbs.gfycat.com/GeneralCourageousAnt-size_restricted.gif',
                     'https://i.makeagif.com/media/12-12-2013/5cKn2y.gif',
                     'http://giphygifs.s3.amazonaws.com/media/bm2O3nXTcKJeU/giphy.gif',
                     'https://i1.wp.com/novocom.top/image/bWVkalwaHkWEuZ2lwaHkuY29t/media/Z2sivLSfN8FH2/giphy.gif',
                     'https://quotesblog.net/wp-content/uploads/2018/08/good-night-kiss-animated-gifs.gif',
                     'https://cdn.myanimelist.net/s/common/uploaded_files/1483588705-b321623c459d2a7001761459d2c8707a.gif',
                     'https://thepantlessanimeblogger.files.wordpress.com/2012/12/campione2.gif',
                     'https://lh3.googleusercontent.com/proxy/PyV5AuOoZopLvfv0t2P1aoKJo3wtNxFrLzUcEuSmr_zDLJJltXErjGjnv7RqZncFLnDgj-7YXGlLPOqW52a2vMDHZBUp3oy0VAsJibd6XcVpaOv03vIlHWcKc70A',
                     'https://i1.wp.com/nileease.com/wp-content/uploads/2020/05/0c2c7fd8bd626d50254e71c839761eb6.gif?fit=500%2C270&ssl=1',
                     'https://cutewallpaper.org/21/anime-kiss-pic/Anime-Kiss-GIF-Anime-Kiss-Cute-Discover-Share-GIFs.gif',
                     'https://i.imgur.com/lmY5soG.gif',
                     'https://cdn.myanimelist.net/s/common/uploaded_files/1483589844-8d0395a7386d12026399620c087f4b97.gif',
                     'https://gifimage.net/wp-content/uploads/2017/09/anime-french-kiss-gif-10.gif',
                     'http://31.media.tumblr.com/ea7842aad07c00b098397bf4d00723c6/tumblr_n570yg0ZIv1rikkvpo1_500.gif',
                     'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/58d633b1-a100-4b5e-9ee6-5de8b4e6736b/d51m084-5c922e42-bcfe-4a8b-b826-72f381e9aa43.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOiIsImlzcyI6InVybjphcHA6Iiwib2JqIjpbW3sicGF0aCI6IlwvZlwvNThkNjMzYjEtYTEwMC00YjVlLTllZTYtNWRlOGI0ZTY3MzZiXC9kNTFtMDg0LTVjOTIyZTQyLWJjZmUtNGE4Yi1iODI2LTcyZjM4MWU5YWE0My5naWYifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6ZmlsZS5kb3dubG9hZCJdfQ.uR8R3luJzBzx3EFLsouIWK4Cm7EXZL97fvg3vS7zh7Q',
                     'https://i0.wp.com/media1.tenor.com/images/558f63303a303abfdddaa71dc7b3d6ae/tenor.gif',
                     'https://thumbs.gfycat.com/InsecureHarmfulBrahmancow-size_restricted.gif',
                     'https://thumbs.gfycat.com/MiserlySpectacularAustraliancurlew-small.gif',
                     'https://31.media.tumblr.com/52e2cd6735ac92efb15be079fc06fe3b/tumblr_msr6hvvRY61sh31wjo1_500.gif',
                     'https://thumbs.gfycat.com/EmbarrassedImportantImpala-max-1mb.gif',
                     'https://i.imgur.com/06EyL6L.gif',
                     'https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/917ca7eb-672e-46fe-b0b2-253dbe3a41fc/dasbj5r-910436e0-aacd-430b-a58c-954240190ab2.gif?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOiIsImlzcyI6InVybjphcHA6Iiwib2JqIjpbW3sicGF0aCI6IlwvZlwvOTE3Y2E3ZWItNjcyZS00NmZlLWIwYjItMjUzZGJlM2E0MWZjXC9kYXNiajVyLTkxMDQzNmUwLWFhY2QtNDMwYi1hNThjLTk1NDI0MDE5MGFiMi5naWYifV1dLCJhdWQiOlsidXJuOnNlcnZpY2U6ZmlsZS5kb3dubG9hZCJdfQ.dBRJVXEmQNWpQYHMSzbwPgBgGE-ipksliWz1SL8EMbg',
                     'https://media.tenor.com/images/5bb0b88a4a01658375125e95a67ba3cd/tenor.gif',
                     'https://qph.fs.quoracdn.net/main-qimg-8c1ee5cd9dc548573732ee462c265a88',
                     'https://i.pinimg.com/originals/97/5d/8f/975d8fde407fd4d5e3a6c0304dd8108e.jpg',
                     'https://data.whicdn.com/images/36114520/original.gif',
                     'https://thumbs.gfycat.com/ColorlessOffbeatFirebelliedtoad-max-1mb.gif',
                     'https://64.media.tumblr.com/7b789c7e72e0e3eebf36a8d754345022/tumblr_p84hwd32EK1xrpawgo1_500.gif',
                     'https://media1.tenor.com/images/95f098bb029ec124a57bafab4156eddf/tenor.gif?itemid=7903397',
                     'http://31.media.tumblr.com/9d316d8626f805b4bdcc6861dc3f90bb/tumblr_mi0ttkIIYD1rmmu90o1_500.gif',
                     'https://64.media.tumblr.com/949d2455a6eac0d545ec38e5c5789779/tumblr_msdc0jZ0cu1rx1dfqo4_r1_500.gif',
                     'https://image.myanimelist.net/ui/OK6W_koKDTOqqqLDbIoPAs6bUva3M1cTgCysDcbLx8A',
                     'https://media.tenor.com/images/36c9fc3da0078091447fa8b09f9bb9cf/tenor.gif',
                     'https://i.pinimg.com/originals/28/6b/02/286b029f0288bc65d732ef183b0c5e09.gif',
                     'http://33.media.tumblr.com/b629bff97b83d1af1f51351508eac339/tumblr_nie6nraDpz1repwszo1_500.gif',
                     'https://media0.giphy.com/media/NoEwwH3GKdBRu/giphy.gif',
                     'http://25.media.tumblr.com/695899f9ebc047f0eaea7dcb9073a4ee/tumblr_mutdm4io4p1rl5wfro1_500.gif',
                     'https://data.whicdn.com/images/317413883/original.gif',
                     'https://i.kym-cdn.com/photos/images/newsfeed/001/284/304/568.gif',
                     'https://acegif.com/wp-content/uploads/anime-kiss-11.gif',
                     'https://cutewallpaper.org/21/cute-anime-kiss/Anime-Kiss-GIF-Anime-Kiss-Cute-Discover-and-Share-GIFs.gif',
                     'https://i.pinimg.com/originals/0d/14/34/0d1434d7b1ba471f103aed7d689dbffe.jpg',
                     'https://static.wikia.nocookie.net/yuripedia/images/8/80/Tumblr_m9kzpwuiNw1r2pvg2o1_500.gif/revision/latest/top-crop/width/300/height/300?cb=20170809130833',
                     'http://cdn.lowgif.com/small/30877125909adb31-.gif',
                     'https://media1.tenor.com/images/8a47f33179692c1a3e3cf8a12324b93b/tenor.gif?itemid=5047638',
                     'https://media1.giphy.com/media/cnf7omAIsmYmI/giphy.gif',
                     'https://i.pinimg.com/originals/d1/85/e3/d185e322bf1aed4d7ff79a6990960798.jpg',
                     'https://i.pinimg.com/originals/c0/98/26/c098260664a2902fb8348a9a0babf1d6.gif',
                     'https://cdn.nekos.life/kiss/kiss_085.gif', 'https://cdn.nekos.life/kiss/kiss_132.gif',
                     'https://i.imgur.com/0WWWvat.gif',
                     'https://68.media.tumblr.com/2bbeb57901f4a62bc8bc268d8122db9a/tumblr_okry1lbeWq1qcsnnso1_540.gif',
                     'https://64.media.tumblr.com/57b20ba6706550faba1e5329003b1eb8/tumblr_inline_nsl3adaWjs1t6pb44_500.gif',
                     'http://i.skyrock.net/5079/88775079/pics/3174561165_1_11_1IKppSSS.gif',
                     'http://pa1.narvii.com/5805/c7cbd97fd0862a6e7debd33382d62995bdc2ef58_00.gif',
                     'https://tenor.com/view/golden-time-anime-kiss-couple-lovers-gif-6155670',
                     ]
        embed = discord.Embed(
            title=f"{message.author.display_name}" + " kisses " + str(member.display_name) + "!",
            color=discord.Colour.orange())
        embed.set_image(url=str(random.choice(kiss_list)))
        await message.channel.send(embed=embed)

    @kiss.error
    async def kiss_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the member to kiss.")
            await p.reward(ctx.author.id, 1)
        else:
            raise error

    @commands.command()
    async def punch(self, message, *, member: discord.Member):
        """ Punch a user of your choice. The owner of the bot and the bot itself is immune. A user
        also cannot punch themselves. Displays a random anime punch gif. """
        await p.reward(message.author.id, 1)
        if member.id in [779219727582756874, 203020214332424192, message.author.id, 254833853112254464]:  # the bot,
            # owner of the bot, and person using the command cannot be punched.
            punch_list = ['https://i.gifer.com/AU8y.gif',
                          'https://thumbs.gfycat.com/WealthyImpressionableAfricanparadiseflycatcher-size_restricted.gif',
                          'http://images5.fanpop.com/image/photos/31500000/Kyon-tries-to-punch-Haruhi-kyon-the-melancholy-of-haruhi-suzumiya-31501828-500-236.gif']
            embed = discord.Embed(
                title=f"{message.author.display_name}" + " fails to punch " + str(member.display_name) + "!",
                color=discord.Colour.orange())
            embed.set_image(url=str(random.choice(punch_list)))
            await message.channel.send(embed=embed)
            return
        else:

            punch_list = [
                'https://64.media.tumblr.com/0f4967894329b0cdd7244e47a6b942d7/2effa07e7133756d-2f/s540x810/e3255b8a2ea984f453d82e1c593c0e45de0c07cb.gifv',
                'https://static.fjcdn.com/gifs/10_c4f7c4_5455970.gif',
                'https://cdn59.picsart.com/176248934001202.gif?to=min&r=640',
                'https://i.imgur.com/AQ1fSJG.gif',
                'https://pokemonmeme.com/uploads/images/SvmG8Nu2E.gif',
                'https://64.media.tumblr.com/83269e6a7c3f8f34ed63d401ee669615/tumblr_nw8dknZUiD1uhun7jo1_400.gif',
                'https://i.pinimg.com/originals/f3/ec/8c/f3ec8c256cb22279c14bfdc48c92e5ab.gif',
                'https://media1.tenor.com/images/7a582f32ef2ed527c0f113f81a696ae3/tenor.gif?itemid=5012021',
                'https://i.imgur.com/f2kkp3L.gif?noredirect',
                'https://i.gifer.com/BlpF.gif', 'https://i.makeagif.com/media/4-26-2014/r6PZtn.gif',
                'https://i.imgur.com/5zzymRM.gif',
                'https://i.gifer.com/Aq6y.gif',
                'https://gifimage.net/wp-content/uploads/2017/09/anime-punching-gif-6.gif',
                'https://japanpowered.com/media/images//dandy-punch.gif',
                'https://thumbs.gfycat.com/FlusteredHalfKitty-max-1mb.gif',
                'https://i.pinimg.com/originals/8a/ab/09/8aab09880ff9226b1c73ee4c2ddec883.gif',
                'https://media3.giphy.com/media/xUO4t2gkWBxDi/giphy.gif',
                'https://i.gifer.com/9eUJ.gif',
                'https://3.bp.blogspot.com/-f2C5CBKw05A/W95nlOPZ4HI/AAAAAAABXVo/eU16NRt_qQIh64c3AvSScDYuRL2H6lAegCKgBGAs/s1600/Omake%2BGif%2BAnime%2B-%2BFairy%2BTail%2BFinal%2BSeason%2B-%2BEpisode%2B282%2B-%2BLucy%2BPunch.gif',
                'https://i.kym-cdn.com/photos/images/newsfeed/001/856/131/1af.gif',
                'https://thumbs.gfycat.com/IllinformedRipeFlounder-size_restricted.gif',
                'https://i.gifer.com/9aKB.gif',
                'https://i2.wp.com/myotakuworld.com/wp-content/uploads/2020/06/Eren-Punch%E2%80%99s-Titan-1.gif?resize=400%2C225&ssl=1',
                'https://3.bp.blogspot.com/-IvE6RqOlJYI/WcdL3KhiyLI/AAAAAAAA8JU/EtPkrIF-rKsIwCRYc3V7qY5lhaw_YI8PACKgBGAs/s1600/Omake%2BGif%2BAnime%2B-%2BBoku%2Bno%2BHero%2BAcademia%2B-%2BEpisode%2B37%2B-%2BAll%2BMight%2BGut%2BPunches%2BBakugo.gif',
                'https://i.kym-cdn.com/photos/images/original/001/891/647/e2c.gif',
                'https://thumbs.gfycat.com/EmbellishedImmenseGavial-max-1mb.gif',
                'https://gifimage.net/wp-content/uploads/2017/09/anime-punch-gif-4.gif', 'https://i.gifer.com/1ZXu.gif']
            embed = discord.Embed(
                title=f"{message.author.display_name}" + " punches " + str(member.display_name) + "!",
                color=discord.Colour.orange())
            embed.set_image(url=str(random.choice(punch_list)))
            await message.channel.send(embed=embed)

    @punch.error
    async def punch_error(self, ctx, error):
        await ctx.send(error)
        await p.reward(ctx.author.id, 1)

    @commands.command(aliases=['headpat', 'pet'])
    async def pat(self, message, *, member: discord.Member):
        """Pat a user of your choice. Displays a random pat picture or gif."""
        await p.reward(message.author.id, 1)
        pat_list = ['https://tenor.com/view/tales-of-zestiria-edna-tales-of-series-to-z-seraph-gif-13986621',
                    'https://i.pinimg.com/originals/d7/c3/26/d7c326bd43776f1e0df6f63956230eb4.gif',
                    'https://media.tenor.com/images/ad8357e58d35c1d63b570ab7e587f212/tenor.gif',
                    'https://thumbs.gfycat.com/FlimsyDeafeningGrassspider-small.gif',
                    'https://media2.giphy.com/media/ARSp9T7wwxNcs/200.gif',
                    'https://media.tenor.com/images/a671268253717ff877474fd019ef73e9/tenor.gif',
                    'https://i.pinimg.com/originals/ec/b8/7f/ecb87fb2827a022884d5165046f6608a.gif',
                    'https://media3.giphy.com/media/SSPW60F2Uul8OyRvQ0/giphy.gif',
                    'https://66.media.tumblr.com/1c433aeea03d0fcee34c22696ba1307b/tumblr_osl1kmMWL91qbvovho1_400.gif',
                    'https://i.imgur.com/WyMHuyL.gif',
                    'https://media.tenor.com/images/1d37a873edfeb81a1f5403f4a3bfa185/tenor.gif',
                    'https://i.gifer.com/FJyk.gif',
                    'https://64.media.tumblr.com/acab0232bfb5cfd5d2d45e55e9dae898/tumblr_pbxhq7GyIf1th206io1_500.gif',
                    'https://external-preview.redd.it/K_B_wuNrhb-8-Tj3JI4Mx7DhgFugx8pz-JNqeRLoNtM.gif?s=df8ffc7e6c6b94a814aa6fdab6995824c3760157',
                    'https://s3-us-west-2.amazonaws.com/megumi.img/zr1Anime-%D0%93%D0%B8%D1%84%D0%BA%D0%B8-Anime-Gochuumon-wa-Usagi-Desu-ka-2599036.gif',
                    'https://thumbs.gfycat.com/BlushingDeepBlacknorwegianelkhound-small.gif',
                    'http://31.media.tumblr.com/38c5c052568dd814453de3775fcf106c/tumblr_nmd3kqYBmW1sgsmuuo4_1280.gif',
                    'https://i0.wp.com/31.media.tumblr.com/2c546e729c79debbb9a04facff52b921/tumblr_n50nf50jj21qbvovho1_500.gif?resize=650,400',
                    'https://kiwifarms.net/attachments/giphy-gif.982897/',
                    'https://steamuserimages-a.akamaihd.net/ugc/924798830218951772/28C3FD3D1D3F4DD9869CCEF58AC6C10CA8BC6046/',
                    'https://64.media.tumblr.com/1e92c03121c0bd6688d17eef8d275ea7/tumblr_pjgkb7Q1oi1ubu1ls_500.gif',
                    'https://i.imgur.com/IrNCWmy.gif',
                    'https://external-preview.redd.it/wbwazGu1XEeZ24nZzxWbnON7B1XrGAl8upuQRbvckAA.gif?s=3bccfbf2db571a2d65a6b1b92042b11338010854',
                    'https://66.media.tumblr.com/4ef8168ef51016e8a68ef976f9b3ff4b/tumblr_inline_p0rnklDObz1t3nyud_540.gif',
                    'https://i.imgur.com/yLOONqZ.gif',
                    'https://external-preview.redd.it/Iap8keoY3p2PQxrhVmJ3u9fJDDOrk1BZK0vXHoJMGiE.png?auto=webp&s=371be57496b62f213da48d7587f2b44a8d34a33f',
                    'https://i.pinimg.com/originals/90/c5/6f/90c56fd0c24ef9152bba28f01946bee1.gif',
                    'https://media.tenor.com/images/385a8d13c1ee5213e560e07d12320d02/tenor.gif',
                    'https://cdn140.picsart.com/309124704046201.gif?to=min&r=640',
                    'https://g.redditmedia.com/5ia6JIfCxcOId2-UibSdkSEeTVW-dUQ8p2xC0Jqa124.gif?fm=mp4&mp4-fragmented=false&s=3cc3ca58c2d1c325ee1280801139c3a7',
                    'https://i.pinimg.com/originals/c2/23/2a/c2232aec426d8b5e85e026cbca410463.gif',
                    'https://i.pinimg.com/originals/d7/c3/26/d7c326bd43776f1e0df6f63956230eb4.gif',
                    'https://64.media.tumblr.com/8fe0b57291325eb914f608c4e4d7e2bc/tumblr_pas1yvkR181s878hio1_500.gif',
                    'https://i.imgur.com/Aq8ycyH.gif', 'https://i.imgur.com/V5olXAS.gif',
                    'https://i.pinimg.com/originals/57/e9/82/57e98242606d651cc992b9525d3de2d8.gif',
                    'https://thumbs.gfycat.com/DamagedLameAntelope-max-1mb.gif',
                    'https://thumbs.gfycat.com/ThriftyCorruptAmericanpainthorse-small.gif',
                    'https://lh4.googleusercontent.com/proxy/fRrpUjIfZeR0v144cOR0QQMT4Wa3ERJNAEvZkZQwMRUyWV2ROE5qBub_tl8uHfs_NxE=s0-d',
                    'https://memestatic.fjcdn.com/gifs/Reverse+headpats_04c996_6522036.gif',
                    'https://thumbs.gfycat.com/NauticalDampJerboa-max-1mb.gif',
                    'http://s3.amazonaws.com/katsunews/6712fcce-be89-40f3-9ee9-473123d7d951.gif',
                    'https://lh3.googleusercontent.com/proxy/_UPSaqjqWySrAEQ46PwXmSzzJgJXbAvKbLBUSDfnGz004OH8fAhtpsOzNPg1H6fXdOY=s0-d',
                    'https://media1.tenor.com/images/b5c3570b91d657a75160056dda054291/tenor.gif?itemid=19736277',
                    'https://i.pinimg.com/originals/a7/92/b6/a792b6741bda0bbe76c91f0f26b34949.gif',
                    'https://cdn.nekos.life/pat/pat_031.gif', 'https://cdn.nekos.life/pat/pat_016.gif',
                    'https://tenor.com/view/anime-anime-head-rub-anime-head-pat-anime-couple-anime-snuggle-gif-16085314',
                    'https://tenor.com/view/nagi_no_asukara-nagi-manaka-head-pat-gif-8841561',
                    'https://tenor.com/view/kaede-azusagawa-kaede-gif-head-headpat-gif-13284057',
                    'https://tenor.com/view/anime-sleep-sleepy-head-pat-gif-15779012',
                    'https://tenor.com/view/charlotte-pat-blush-embarrassed-shy-gif-5081286',
                    'https://tenor.com/view/pat-gif-12018805', 'https://cdn.nekos.life/pat/pat_067.gif',
                    'https://i.pinimg.com/originals/be/75/ff/be75ff9f2ba20efb4dbda09c62802b39.gif',
                    'https://cdn.nekos.life/pat/pat_057.gif', 'http://i.giphy.com/tOOybDwi1EaEo.gif',
                    'https://steamuserimages-a.akamaihd.net/ugc/313367221053828170/930858D44B0730EF680DA1A4BF74800BB65A5BFC/',
                    'https://64.media.tumblr.com/df818117d19236a459c61b4f29c80152/881ae79913db7c30-d7/s400x600/aaeae652bf0c99ea5bdae465e529ce91afbe9e78.gif']
        embed = discord.Embed(
            title=f"{message.author.display_name}" + " pats " + str(member.display_name) + "!",
            color=discord.Colour.orange())
        embed.set_image(url=str(random.choice(pat_list)))
        await message.channel.send(embed=embed)

    @pat.error
    async def pat_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please specify the member to pat.")
            await p.reward(ctx.author.id, 1)
        else:
            raise error


client.loop.run_until_complete(create_db_pool())


def setup(bot):
    bot.add_cog(anime(bot))
