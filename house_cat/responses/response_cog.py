import discord
import discord.ext.commands as commands
from .response_builder import ResponseBuilder
from .poll import Poll
from .thesaurus import thesaurus
from . import magic8ball
from util import logger
import random


class ResponseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.response_builder = ResponseBuilder()

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if len(message.content) > 0:
            if message.content[0] == "$":
                logger.log_command(message, message.content)
                return
        chance_of_reaction = 0.005
        if not isinstance(message.channel, discord.DMChannel):
            if message.channel.permissions_for(message.guild.me).add_reactions:
                if random.random() < chance_of_reaction:
                    await message.add_reaction("❤")
        if message.author == self.bot.user:
            return

    @commands.command(name="poll")
    async def poll(self, ctx, *args):
        if len(args) == 0:
            embed = discord.Embed(title="",
                                  description="Use `poll \"Question\" \"Option 1\" \"Option 2\"` to create a poll. "
                                              "You may add more than 2 options (up to 9). Use $help for more info.",
                                  color=self.bot.color)
            await ctx.send(embed=embed)
            return
        try:
            poll = Poll(ctx, *args)
            await poll.poll()
        except (IndexError, ValueError) as e:
            await ctx.send(str(e))

    @commands.command(name="thesaurize")
    async def thesaurize(self, ctx, *args):
        response = await thesaurus.convert(ctx)
        if len(response) > 0:
            embed = discord.Embed(title="", description=response, color=self.bot.color)
            await ctx.send(embed=embed)

    @commands.command(name="magic8ball", aliases=["8ball"])
    async def magic_8_ball(self, ctx, *args):
        response = magic8ball.get_response()
        embed = discord.Embed(title="", description=response['text'], color=response['color'])
        await ctx.send(embed=embed)

    @commands.command(name="stats")
    async def stats(self, ctx, *args):
        if await self.bot.is_owner(ctx.author):
            guilds = list(self.bot.guilds)
            user_count = str(len(self.bot.users))
            latency = str(self.bot.latency)

            embed = discord.Embed(title="Bot stats", description="", color=self.bot.color)
            embed.add_field(name="Number of guilds:", value=str(len(guilds)), inline=False)
            embed.add_field(name="User Count:", value=user_count, inline=False)
            embed.add_field(name="Latency:", value=latency, inline=False)

            await ctx.send(embed=embed)

    @commands.command(name="help", aliases=["commands", "housecat"])
    async def help(self, ctx, *args):
        embed = discord.Embed(title="",
                              description="Please visit http://housecat.altskop.com/commands to view the list of all commands."
                              , color=self.bot.color)
        await ctx.send(embed=embed)
