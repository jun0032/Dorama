import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.mdl import search_drama


class Drama(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="drama", description="Look up a K-Drama on MyDramaList")
    @app_commands.describe(name="Name of the K-Drama to search for")
    async def drama(self, interaction: discord.Interaction, name: str):
        # Defer so Discord doesn't time out while we scrape
        await interaction.response.defer()

        try:
            # Run the blocking scrape in a thread so the bot doesn't freeze
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, search_drama, name)

            if not result:
                embed = discord.Embed(
                    title="❌ Drama Not Found",
                    description=(
                        f"Couldn't find **{name}** on MyDramaList.\n"
                        "Try a different spelling or the full title."
                    ),
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return

            # Build the embed
            genres_str = " • ".join(result["genres"]) if result["genres"] else "N/A"
            stars = _rating_to_stars(result["rating"])

            embed = discord.Embed(
                title=result["title"],
                url=result["url"],
                description=result["synopsis"],
                color=discord.Color.pink()
            )

            embed.add_field(
                name="⭐ Rating",
                value=f"{result['rating']}/10  {stars}",
                inline=True
            )
            embed.add_field(
                name="🎬 Episodes",
                value=result["episodes"],
                inline=True
            )
            embed.add_field(
                name="📅 Year",
                value=result["year"],
                inline=True
            )
            embed.add_field(
                name="🎭 Genres",
                value=genres_str,
                inline=False
            )
            embed.add_field(
                name="🌏 Country",
                value=result["country"],
                inline=True
            )

            if result["poster"]:
                embed.set_thumbnail(url=result["poster"])

            embed.set_footer(text="OST Bot • Data from MyDramaList  |  Try /ost to get the soundtrack!")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"[Drama Cog] Error: {e}")
            embed = discord.Embed(
                title="⚠️ Something went wrong",
                description="Couldn't reach MyDramaList right now. Try again in a moment.",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed)


def _rating_to_stars(rating_str: str) -> str:
    """Convert a numeric rating to a simple star display."""
    try:
        rating = float(rating_str)
        filled = round(rating / 2)  # out of 5
        return "⭐" * filled + "☆" * (5 - filled)
    except (ValueError, TypeError):
        return ""


async def setup(bot):
    await bot.add_cog(Drama(bot))
