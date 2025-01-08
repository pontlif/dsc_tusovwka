from init import bot
from variables import *


@bot.slash_command(description="Повторная верификация", guild_ids=[servers])
async def verify(inter):
    await inter.response.defer(ephemeral=True)
    guild = bot.get_guild(servers)
    role = guild.get_role(VERIFY)

    if role is None:
        await inter.send("Роль верификации устарела.", ephemeral=True)
    for member in guild.members:
        await member.add_roles(role)

    await inter.send("Все участники должны заново пройти верификацию", ephemeral=True)
