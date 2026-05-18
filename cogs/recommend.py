import discord
from discord.ext import commands
from discord import app_commands


class Recommend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="recommend", description="Get an AI-powered K-Drama recommendation")
    @app_commands.describe(prompt="Your mood or a drama you liked (e.g. 'something sad and romantic')")
    async def recommend(self, interaction: discord.Interaction, prompt: str):
        # Phase 4: will connect to Claude API
        embed = discord.Embed(
            title="🤖 AI Recommendation — Coming Soon",
            description=f"Finding the perfect drama for: **{prompt}**...\n\nThis feature is being built in Phase 4!",
            color=discord.Color.pink()
        )
        embed.set_footer(text="OST Bot • Phase 4: Claude AI Integration")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Recommend(bot))
