import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.spotify import search_ost


class OST(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ost", description="Get the Spotify soundtrack for a K-Drama")
    @app_commands.describe(drama="Name of the K-Drama to get the OST for")
    async def ost(self, interaction: discord.Interaction, drama: str):
        await interaction.response.defer()

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, search_ost, drama)

            if not result:
                embed = discord.Embed(
                    title="❌ OST Not Found",
                    description=(
                        f"Couldn't find a Spotify OST for **{drama}**.\n"
                        "Try the full drama title or check the spelling."
                    ),
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return

            # Build track list
            track_lines = []
            for i, track in enumerate(result["tracks"], 1):
                name = track["name"]
                artist = track["artist"]
                url = track["url"]
                if url:
                    track_lines.append(f"`{i}.` [{name}]({url})\n　　*{artist}*")
                else:
                    track_lines.append(f"`{i}.` {name}\n　　*{artist}*")

            tracks_str = "\n".join(track_lines) if track_lines else "Track list unavailable."

            # Emoji badge
            type_badge = "💿 Album" if result["type"] == "album" else "🎵 Playlist"

            embed = discord.Embed(
                title=f"🎵 {result['title']}",
                url=result["url"],
                description=tracks_str,
                color=discord.Color.green()
            )

            embed.add_field(
                name="🎤 Artist",
                value=result["artist"] or "Various Artists",
                inline=True
            )
            embed.add_field(
                name="📅 Year",
                value=result["release_date"],
                inline=True
            )
            embed.add_field(
                name="🎶 Total Tracks",
                value=str(result["total_tracks"]),
                inline=True
            )
            embed.add_field(
                name=type_badge,
                value=f"[Open in Spotify ↗]({result['url']})",
                inline=False
            )

            if result["poster"]:
                embed.set_thumbnail(url=result["poster"])

            embed.set_footer(text=f"OST Bot • Showing top 5 tracks  |  Try /recommend for AI drama picks!")

            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"[OST Cog] Error: {e}")
            embed = discord.Embed(
                title="⚠️ Something went wrong",
                description="Couldn't reach Spotify right now. Try again in a moment.",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(OST(bot))
