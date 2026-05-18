import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from database import init_db

load_dotenv()
init_db()

# Bot setup with all intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


@bot.tree.command(name="ping", description="Check if the bot is alive")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot is online and running.\n**Latency:** {latency}ms",
        color=discord.Color.pink()
    )
    embed.set_footer(text="OST Bot • K-Drama & Music")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="help", description="See all available commands")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎵 OST Bot — Commands",
        description="Your K-Drama & soundtrack companion.",
        color=discord.Color.pink()
    )
    embed.add_field(
        name="/ping",
        value="Check if the bot is online",
        inline=False
    )
    embed.add_field(
        name="/drama [name]",
        value="Look up a K-Drama — rating, episodes, genres, streaming info",
        inline=False
    )
    embed.add_field(
        name="/ost [drama name]",
        value="Get the soundtrack for a drama with a Spotify link",
        inline=False
    )
    embed.add_field(
        name="/recommend [mood or drama]",
        value="Get an AI-powered drama recommendation + its OST",
        inline=False
    )
    embed.add_field(
        name="/watchlist add [drama]",
        value="Save a drama to your personal watchlist",
        inline=False
    )
    embed.add_field(
        name="/watchlist show",
        value="View your saved dramas",
        inline=False
    )
    embed.set_footer(text="OST Bot • More features coming soon 🌸")
    await interaction.response.send_message(embed=embed)


async def load_cogs():
    """Load all cogs from the cogs directory."""
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"✅ Loaded cog: {filename}")
            except Exception as e:
                print(f"❌ Failed to load cog {filename}: {e}")


async def main():
    async with bot:
        await load_cogs()
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("❌ DISCORD_TOKEN not found in .env file")
        await bot.start(token)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
