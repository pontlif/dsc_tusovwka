from init import bot
from variables import *
import disnake


@bot.slash_command(description="Раздает роль обновления", guild_ids=[servers])
async def update(
    inter,
        status=disnake.ext.commands.Param(name='on_or_off', description='Выбор', choices=['вкл', 'выкл'])):
    await inter.response.defer(ephemeral=True)
    guild = bot.get_guild(servers)
    role = guild.get_role(UPDATE)
    if status == 'вкл':
        if role is None:
            await inter.send("Роль обновления устарела устарела.", ephemeral=True)
        for member in guild.members:
            await member.add_roles(role)

        await inter.send("Режим обновления включен", ephemeral=True)
    elif status == 'выкл':
        for member in guild.members:
            await member.remove_roles(role)
        await inter.send("Режим обновления выключен")
    else:
        await inter.send("Ошибочка :(")
