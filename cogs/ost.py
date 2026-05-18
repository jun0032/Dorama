import discord
from discord.ext import commands
from discord import app_commands


class OST(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ost", description="Get the soundtrack for a K-Drama")
    @app_commands.describe(drama="Name of the K-Drama to get the OST for")
    async def ost(self, interaction: discord.Interaction, drama: str):
        # Phase 3: will connect to Spotify API
        embed = discord.Embed(
            title="🎵 OST Lookup — Coming Soon",
            description=f"Finding the soundtrack for **{drama}**...\n\nThis feature is being built in Phase 3!",
            color=discord.Color.pink()
        )
        embed.set_footer(text="OST Bot • Phase 3: Spotify Integration")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(OST(bot))
