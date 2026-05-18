import discord
from discord.ext import commands
from discord import app_commands
from database import add_to_watchlist, get_watchlist, remove_from_watchlist


class Watchlist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    watchlist_group = app_commands.Group(
        name="watchlist",
        description="Manage your K-Drama watchlist"
    )

    @watchlist_group.command(name="add", description="Add a drama to your watchlist")
    @app_commands.describe(drama="Name of the K-Drama to add")
    async def watchlist_add(self, interaction: discord.Interaction, drama: str):
        user_id = str(interaction.user.id)
        added = add_to_watchlist(user_id, drama)

        if added:
            embed = discord.Embed(
                title="✅ Added to Watchlist",
                description=f"**{drama}** has been added to your watchlist!",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="⚠️ Already in Watchlist",
                description=f"**{drama}** is already in your watchlist.",
                color=discord.Color.orange()
            )

        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    @watchlist_group.command(name="show", description="View your watchlist")
    async def watchlist_show(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        dramas = get_watchlist(user_id)

        if not dramas:
            embed = discord.Embed(
                title="📋 Your Watchlist",
                description="Your watchlist is empty! Use `/watchlist add` to add dramas.",
                color=discord.Color.pink()
            )
        else:
            drama_list = "\n".join(
                [f"{i+1}. **{drama[0]}**" for i, drama in enumerate(dramas)]
            )
            embed = discord.Embed(
                title=f"📋 {interaction.user.display_name}'s Watchlist",
                description=drama_list,
                color=discord.Color.pink()
            )
            embed.set_footer(text=f"{len(dramas)} drama(s) saved")

        await interaction.response.send_message(embed=embed)

    @watchlist_group.command(name="remove", description="Remove a drama from your watchlist")
    @app_commands.describe(drama="Name of the K-Drama to remove")
    async def watchlist_remove(self, interaction: discord.Interaction, drama: str):
        user_id = str(interaction.user.id)
        removed = remove_from_watchlist(user_id, drama)

        if removed:
            embed = discord.Embed(
                title="🗑️ Removed from Watchlist",
                description=f"**{drama}** has been removed from your watchlist.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="❌ Not Found",
                description=f"**{drama}** wasn't found in your watchlist.",
                color=discord.Color.red()
            )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Watchlist(bot))
