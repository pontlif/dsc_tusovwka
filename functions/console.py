from variables import *
import disnake
from init import bot
from functions.mafia import Mfinfo_modal, Mfstop_modal


@bot.slash_command(guild_ids=[servers], description="Консоль")
async def cmd(inter, command=disnake.ext.commands.Param(name='command', description='Консольная команда')):
    command = command.lower()
    guild = bot.get_guild(servers)
    member = guild.get_member(inter.author.id)
    user = bot.get_user(inter.author.id)
    CLASSIS_CHAT = bot.get_guild(1139692253762297896)
    CLASSIS_CHAT = CLASSIS_CHAT.get_channel(CHAT)
    # school_179_th = CLASSIS_CHAT.get_thread(SCHOOL_179_THREAD)
    # school_444_th = CLASSIS_CHAT.get_thread(SCHOOL_444_THREAD)
    # school_1514_th = CLASSIS_CHAT.get_thread(SCHOOL_1514_THREAD)
    if (command == "transgender"):
        guild = bot.get_guild(servers)
        man_role = guild.get_role(MAN)
        fem_role = guild.get_role(FEM)
        if ((bot.get_guild(servers)).get_role(MAN)) in inter.author.roles:
            member = guild.get_member(inter.author.id)
            await member.remove_roles(man_role)
            await member.add_roles(fem_role)
            await inter.send(f"Теперь ты <@&{FEM}>", ephemeral=True)
        else:
            member = guild.get_member(inter.author.id)
            await member.remove_roles(fem_role)
            await member.add_roles(man_role)
            await inter.send(f"Теперь ты <@&{MAN}>",ephemeral=True)
    elif (command == "valorant"):
        valorant_role = guild.get_role(VALORANT)
        valorant_th = CLASSIS_CHAT.get_thread(VALORANT_THREAD)
        if ((bot.get_guild(servers)).get_role(VALORANT)) in inter.author.roles:
            await valorant_th.remove_user(user)
            await member.remove_roles(valorant_role)
            await inter.send(f"Роль <@&{VALORANT}> снята",ephemeral=True)
        else:
            await member.add_roles(valorant_role)
            await valorant_th.add_user(user)
            await inter.send(f"Роль <@&{VALORANT}> добавлена",ephemeral=True)
    elif (command == "cs"):
        cs_role = guild.get_role(CS)
        cs_th = CLASSIS_CHAT.get_thread(CS_THREAD)
        if ((bot.get_guild(servers)).get_role(CS)) in inter.author.roles:
            await cs_th.remove_user(user)
            await member.remove_roles(cs_role)
            await inter.send(f"Роль <@&{CS}> снята",ephemeral=True)
        else:
            await member.add_roles(cs_role)
            await cs_th.add_user(user)
            await inter.send(f"Роль <@&{CS}> добавлена",ephemeral=True)
    elif (command == "minecraft"):
        minecraft_role = guild.get_role(MINECRAFT)
        minecraft_th = CLASSIS_CHAT.get_thread(MINECRAFT_THREAD)
        if ((bot.get_guild(servers)).get_role(MINECRAFT)) in inter.author.roles:
            await minecraft_th.remove_user(user)
            await member.remove_roles(minecraft_role)
            await inter.send(f"Роль <@&{MINECRAFT}> снята",ephemeral=True)
        else:
            await member.add_roles(minecraft_role)
            await minecraft_th.add_user(user)
            await inter.send(f"Роль <@&{MINECRAFT}> добавлена",ephemeral=True)
    elif (command == "stalcraft"):
        stalcraft_role = guild.get_role(STALCRAFT)
        stalcraft_th = CLASSIS_CHAT.get_thread(STALCRAFT_THREAD)
        if ((bot.get_guild(servers)).get_role(STALCRAFT)) in inter.author.roles:
            await stalcraft_th.remove_user(user)
            await member.remove_roles(stalcraft_role)
            await inter.send(f"Роль <@&{STALCRAFT}> снята",ephemeral=True)
        else:
            await member.add_roles(stalcraft_role)
            await stalcraft_th.add_user(user)
            await inter.send(f"Роль <@&{STALCRAFT}> добавлена",ephemeral=True)
    elif (command == "verify"):
        guild = bot.get_guild(servers)
        verify_role = guild.get_role(VERIFY)
        member = guild.get_member(inter.author.id)
        await member.add_roles(verify_role)
    elif (command == "board"):
        board_role = guild.get_role(BOARD)
        board_th = CLASSIS_CHAT.get_thread(BOARD_THREAD)
        if ((bot.get_guild(servers)).get_role(BOARD)) in inter.author.roles:
            await board_th.remove_user(user)
            await member.remove_roles(board_role)
            await inter.send(f"Роль <@&{BOARD}> снята",ephemeral=True)
        else:
            await member.add_roles(board_role)
            await board_th.add_user(user)
            await inter.send(f"Роль <@&{BOARD}> добавлена",ephemeral=True)
    elif (command == "mfstop"):
        await inter.response.send_modal(modal=Mfstop_modal())
    elif (command == "mfdocs"):
        mfdocs_open = open("documents/mafia_docs.txt", "r", encoding="utf-8")
        mfdocs_txt = mfdocs_open.read()
        embed = disnake.Embed(description=mfdocs_txt, color=disnake.Colour.from_rgb(0, 255, 213),
                              timestamp=datetime.datetime.now())
        await inter.send(embed=embed, ephemeral=True)
    elif (command == "cmd") or (command == "commands") or (command == "command") or (command == "list"):
        commands_list_open = open("documents/commands_list.txt", "r", encoding="utf-8")
        commands_list_txt = commands_list_open.read()
        await inter.send(f"{commands_list_txt}",ephemeral=True)
    elif (command == "mfinfo"):
        await inter.response.send_modal(modal=Mfinfo_modal())
    elif command == "rules":
        guild = bot.get_guild(servers)
        owner_role = guild.get_role(OWNER)
        if owner_role not in inter.author.roles:
            await inter.send("## В доступе отказано", ephemeral=True)
            return
        rules_open = open("documents/rules.txt", "r", encoding="utf-8")
        rules_txt = rules_open.read()
        embed = disnake.Embed(description=rules_txt, color=disnake.Colour.from_rgb(0, 255, 213),
                              timestamp=datetime.datetime.now())
        embed.set_footer(text="Вступили в силу")
        chat = inter.channel
        await chat.send(embed=embed)
        await inter.send("Готово!", ephemeral=True)
    elif command == "guide":
        guild = bot.get_guild(servers)
        owner_role = guild.get_role(OWNER)
        if owner_role not in inter.author.roles:
            await inter.send("## В доступе отказано", ephemeral=True)
            return
        guide_open = open("documents/guide.txt", "r", encoding="utf-8")
        guide_txt = guide_open.read()
        embed = disnake.Embed(description=guide_txt, color=disnake.Colour.from_rgb(255, 132, 0), )
        chat = inter.channel
        await chat.send(embed=embed)
        await inter.send("Готово!", ephemeral=True)
    elif command == "lofi":
        guild = bot.get_guild(servers)
        owner_role = guild.get_role(OWNER)
        if owner_role not in inter.author.roles:
            await inter.send("## В доступе отказано", ephemeral=True)
            return
        lofi_open = open("documents/lofi.txt", "r", encoding="utf-8")
        lofi_txt = lofi_open.read()
        embed = disnake.Embed(description=lofi_txt, color=disnake.Colour.from_rgb(255, 132, 0), )
        chat = inter.channel
        await chat.send(embed=embed, components=[
            disnake.ui.Button(label="Jazz", style=disnake.ButtonStyle.primary, custom_id="lofi_jazz"),
            disnake.ui.Button(label="Classic", style=disnake.ButtonStyle.gray, custom_id="lofi_classic"),
            disnake.ui.Button(label="Stop", style=disnake.ButtonStyle.danger, custom_id="lofi_stop"),])
        await inter.send('Готово!', ephemeral=True)
    else:
        await inter.send(f"Команды ***{command}*** несуществует!", ephemeral=True)
