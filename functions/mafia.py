import disnake
from init import Players, bot, Mafia
from variables import *
import asyncio
import random
from disnake.ext import commands
import string
from disnake import TextInputStyle, TextInput

roles = ["doctor", "detective", "mafia", "people", "people", "people", "baby", "people", "mafia", "police", "people",
         "crazy", "people", "thief", "mafia", "people"]

win_count = {"mafia": 0, "people": 0, "doctor": 0, "detective": 0, "baby": 0, "police": 0, "crazy": 0, "thief": 0}
mafia_room_0_id = 1289351607238262844


class Mfstop_modal(disnake.ui.Modal):
    def __init__(self):
        # Детали модального окна и его компонентов
        components = [
            disnake.ui.TextInput(
                label="Номер игры",
                placeholder="",
                custom_id="mfgame.id",
                style=TextInputStyle.short,
                min_length=1,
                max_length=7
            ),
            disnake.ui.TextInput(
                label="ADMIN KEY",
                placeholder="",
                custom_id="mfgame.admin_key",
                style=TextInputStyle.short, min_length=24, max_length=24, required=False)
        ]
        super().__init__(
            title="Остановить игру в мафию",
            custom_id="mf_stop",
            components=components,
        )

    # Обработка ответа, после отправки модального окна
    async def callback(self, inter: disnake.ModalInteraction):
        mfgame_id = inter.data.components[0]["components"][0]["value"]
        mfgame = Mafia.get_or_none(id=mfgame_id)
        guild = bot.get_guild(servers)
        OWNER_ROLE = guild.get_role(OWNER)
        if mfgame == None:
            await inter.send("Такой игры нет!", ephemeral=True)
        if (OWNER_ROLE not in inter.author.roles) and (inter.data.components[1]["components"][0]["value"] != mfgame.admin_key):
            await inter.send("## В доступе отказано", ephemeral=True)
            return
        else:
            if mfgame.status == "Stoped":
                await inter.send("Игра уже остановлена!", ephemeral=True)
            elif mfgame.status == "Finished":
                await inter.send("Игра уже закончилась!", ephemeral=True)
            elif mfgame.status == "Crushed":
                await inter.send("Эта игра была крашнута!", ephemeral=True)
            elif mfgame.status == "Players < Minimal_players":
                await inter.send("Эта игра не была запущена из-за малого количества игроков", ephemeral=True)
            elif (mfgame.status == "Registration_open") or (mfgame.status == "Registration_private_open"):
                Mafia.update(status="Stoped").where(Mafia.id == mfgame.id).execute()
                await inter.send("Регистрация на игру остановлена!", ephemeral=True)
                await mafia_stop(mfgame, "Registration")
            else:
                Mafia.update(status="Stoped").where(Mafia.id == mfgame.id).execute()
                await inter.send("Игра остановлена!", ephemeral=True)
                await mafia_stop(mfgame, "night")


###################################################################################
###################################################################################
###################################################################################


class Mfinfo_modal(disnake.ui.Modal):
    def __init__(self):
        # Детали модального окна и его компонентов
        components = [
            disnake.ui.TextInput(
                label="Номер игры",
                placeholder="",
                custom_id="mfgame.id",
                style=TextInputStyle.short,
                min_length=1,
                max_length=7
            ),
            disnake.ui.TextInput(
                label="ADMIN KEY",
                placeholder="",
                custom_id="mfgame.admin_key",
                style=TextInputStyle.short, min_length=24, max_length=24, required=False)
        ]
        super().__init__(
            title="Получить информацию о игре",
            custom_id="mf_stop",
            components=components,
        )

    # Обработка ответа, после отправки модального окна
    async def callback(self, inter: disnake.ModalInteraction):
        mfgame_id = inter.data.components[0]["components"][0]["value"]
        mfgame = Mafia.get_or_none(id=mfgame_id)
        guild = bot.get_guild(servers)
        OWNER_ROLE = guild.get_role(OWNER)
        if mfgame is None:
            await inter.send("Такой игры нет!", ephemeral=True)
            return
        if (OWNER_ROLE not in inter.author.roles) and (inter.data.components[1]["components"][0]["value"] != mfgame.admin_key):
            await inter.send("## В доступе отказано", ephemeral=True)
            return
        colour = disnake.Colour.default()
        times_embed = disnake.Embed(description="## TIMES:", colour=colour)
        times_embed.add_field(
            name="REG_OPEN", value=f"<t:{round(((mfgame.reg_open - year1970).total_seconds()))}:R>",
            inline=False)
        if mfgame.reg_close is not None:
            times_embed.add_field(name="REG_CLOSE", value=f"<t:{round(((mfgame.reg_close - year1970).total_seconds()))}:R>", inline=False)
        else:
            times_embed.add_field(name="REG_CLOSE",value="NONE",inline=False)
        if mfgame.game_start is not None:
            times_embed.add_field(name="GAME_START", value=f"<t:{round(((mfgame.game_start - year1970).total_seconds()))}:R>", inline=False)
        else:
            times_embed.add_field(name="GAME_START", value="NONE", inline=False)
        if mfgame.game_finish is not None:
            times_embed.add_field(name="GAME_FINISH", value=f"<t:{round(((mfgame.game_finish - year1970).total_seconds()))}:R>", inline=False)
        else:
            times_embed.add_field(name="GAME_FINISH", value="NONE", inline=False)

        durations_embed = disnake.Embed(description="## DURATIONS:", colour=colour)
        durations_embed.add_field(name="REG_DURATION", value=mfgame.reg_duration, inline=False)
        if mfgame.day_duration is not None:
            durations_embed.add_field(name="DAY_DURATION", value=mfgame.day_duration, inline=False)
        else:
            durations_embed.add_field(name="DAY_DURATION", value="NONE", inline=False)
        durations_embed.add_field(name="NIGHT_DURATION", value=mfgame.night_duration, inline=False)
        if mfgame.vote_duration is not None:
            durations_embed.add_field(name="VOTE_DURATION", value=mfgame.vote_duration, inline=False)
        else:
            durations_embed.add_field(name="VOTE_DURATION", value="NONE", inline=False)

        info_embed = disnake.Embed(description="## INFO:", colour=colour)
        info_embed.add_field(name="ID", value=mfgame.id, inline=False)
        if mfgame.password is not None:
            info_embed.add_field(name="PASSWORD", value=mfgame.password, inline=False)
        else:
            info_embed.add_field(name="PASSWORD", value="NONE", inline=False)
        info_embed.add_field(name="DAY_MODE", value=mfgame.day_mode, inline=False)
        info_embed.add_field(name="GAME_CREATOR", value=mfgame.game_creator, inline=False)
        info_embed.add_field(name="ADMIN_KEY", value=mfgame.admin_key, inline=False)
        info_embed.add_field(name="STATUS", value=mfgame.status, inline=False)
        info_embed.add_field(name="CRUSH_STATUS", value=mfgame.crush_status, inline=False)
        info_embed.add_field(name="OPEN_ROLES", value=mfgame.open_roles, inline=False)
        info_embed.add_field(name="VOICE_NUM", value=mfgame.voice_num, inline=False)

        ids_embed = disnake.Embed(description="## IDS:", colour=colour)
        ids_embed.add_field(name="REG_MSG_ID", value=mfgame.reg_msg_id, inline=False)
        if mfgame.mf_msg_id is not None:
            ids_embed.add_field(name="MF_MSG_ID", value=mfgame.mf_msg_id, inline=False)
        else:
            ids_embed.add_field(name="MF_MSG_ID", value="NONE", inline=False)
        if mfgame.game_thread is not None:
            ids_embed.add_field(name="GAME_THREAD", value=mfgame.game_thread, inline=False)
        else:
            ids_embed.add_field(name="GAME_THREAD", value="NONE", inline=False)

        players_roles_embed = disnake.Embed(description="## PLAYERS AND ROLES:", colour=colour)
        players_roles_embed.add_field(name="MIN_PLAYERS", value=mfgame.min_players, inline=False)
        players_roles_embed.add_field(name="MAX_PLAYERS", value=mfgame.max_players, inline=False)
        if mfgame.used_roles is not None:
            roles_txt = ""
            for role in mfgame.used_roles:
                roles_txt += f"{role}\n"
            players_roles_embed.add_field(name="USED_ROLES", value=roles_txt, inline=False)
        else:
            players_roles_embed.add_field(name="USED_ROLES", value="NONE", inline=False)
        players_txt = ""
        players_dict = (mfgame.players).copy()
        players = list(players_dict.keys())
        for player in players:
            players_txt += f"{player} : {players_dict.get(player)}\n"
        players_roles_embed.add_field(name="PLAYERS", value=players_txt, inline=False)
        if mfgame.dead_players is not None:
            dead_players_txt = ""
            for dead_player in mfgame.dead_players:
                dead_players_txt += f"{dead_player}\n"
            players_roles_embed.add_field(name="DEAD_PLAYERS", value=dead_players_txt, inline=False)
        else:
            players_roles_embed.add_field(name="DEAD_PLAYERS", value="NONE", inline=False)
        if mfgame.alive_players is not None:
            alive_players_txt = ""
            for alive_player in mfgame.alive_players:
                alive_players_txt += f"{alive_player}\n"
            players_roles_embed.add_field(name="ALIVE_PLAYERS", value=alive_players_txt, inline=False)
        else:
            players_roles_embed.add_field(name="ALIVE_PLAYERS", value="NONE", inline=False)

        if mfgame.mafia_list is not None:
            mafia_list_txt = ""
            for alive_player in mfgame.mafia_list:
                mafia_list_txt += f"{alive_player}\n"
            players_roles_embed.add_field(name="MAFIA_LIST", value=mafia_list_txt, inline=False)
        else:
            players_roles_embed.add_field(name="MAFIA_LIST", value="NONE", inline=False)

        if mfgame.voted_already is not None:
            if len(mfgame.voted_already) == 0:
                players_roles_embed.add_field(name="VOTED_ALREADY", value="[]", inline=False)
            else:
                voted_already_txt = ""
                for voter in mfgame.voted_already:
                    voted_already_txt += f"{voter}\n"
                players_roles_embed.add_field(name="VOTED_ALREADY", value=voted_already_txt, inline=False)
        else:
            players_roles_embed.add_field(name="VOTED_ALREADY", value="NONE", inline=False)
        players_roles_embed.add_field(name="PLAYERS_LIST", value=mfgame.players_list, inline=False)

        count_embed = disnake.Embed(description="## COUNTS:", colour=colour)
        count_embed.add_field(name="NIGHT_COUNT", value=mfgame.night_count, inline=False)
        count_embed.add_field(name="DAY_COUNT", value=mfgame.day_count, inline=False)

        reference_embed = disnake.Embed(description="## REFERENCE:", colour=colour)
        for player in players:
            reference_embed.add_field(name=player, value=f"<@{player}>", inline=False)

        action_history_embed = disnake.Embed(description=f"## ACTION_HISTORY\n\n\n{mfgame.action_history}", colour=colour)
        if mfgame.action_history is not None:
            action_history_embed = disnake.Embed(description=f"## ACTION_HISTORY\n\n\n{mfgame.action_history}", colour=colour)
        else:
            action_history_embed = disnake.Embed(description=f"## ACTION_HISTORY\nNONE", colour=colour)
        await inter.send(f"# ИНФОРМАЦИЯ О ИГРЕ #{mfgame.id}",embeds=[info_embed, count_embed, ids_embed, times_embed, durations_embed, players_roles_embed, reference_embed, action_history_embed], ephemeral=True)


###################################################################################
###################################################################################
###################################################################################


class PasswordModal(disnake.ui.Modal):
    def __init__(self):
        # Детали модального окна и его компонентов
        components = [
            disnake.ui.TextInput(
                label="Введи пароль к приватной игре",
                placeholder="Например, 12345678",
                custom_id="password_field",
                style=TextInputStyle.short,
                min_length=8,
                max_length=8
            ),
        ]
        super().__init__(
            title="Регистрация в приватную игру мафии",
            custom_id="password_check",
            components=components,
        )

    # Обработка ответа, после отправки модального окна
    async def callback(self, inter: disnake.ModalInteraction):
        mfgame = Mafia.get(Mafia.reg_msg_id == inter.message.id)
        member = Players.get_or_none(Players.player_id == inter.author.id)
        if member is None:
            Players.create(player_id=inter.author.id, status="not_played",win_results=win_count, lose_results=win_count)
        if inter.data.components[0]["components"][0]["value"] == mfgame.password:
            players = (mfgame.players).copy()
            players[inter.author.id] = None
            Players.update(status='played',game=mfgame.id).where(Players.player_id == inter.author.id).execute()
            Mafia.update(players_list=mfgame.players_list + f"\n-# <@{inter.author.id}>", players=players).where(mfgame).execute()
            mfgame = Mafia.get(Mafia.reg_msg_id == inter.message.id)
            guild = bot.get_guild(servers)
            mafia_chat_object = await guild.fetch_channel(MAFIA)
            chat_object = await mafia_chat_object.fetch_message(mfgame.reg_msg_id)
            embed = disnake.Embed(
                description=f"# МАФИЯ #{mfgame.id}\n## Начало через: <t:{round(((mfgame.reg_open + datetime.timedelta(seconds=mfgame.reg_duration) - year1970).total_seconds()))}:R>\n## Игроки:\n{mfgame.players_list}",
            )

            embed.set_image(url=mf_img_logo)
            embed.add_field(name="Участвует:", value=len(mfgame.players), inline=True)
            embed.add_field(name="Минимум:", value=mfgame.min_players, inline=True)
            embed.add_field(name="Максимум:", value=mfgame.max_players, inline=True)
            if mfgame.open_roles == "NO":
                open_roles_embed_txt = "Роли засекречены"
            elif mfgame.open_roles == "YES" and mfgame.max_players < 12:
                open_roles_embed_txt = "Роли не засекречены"
            else:
                open_roles_embed_txt = "Роли не засекречены (если меньше 12 игроков)"
            embed.add_field(name="Настройки:",
                            value=f"Скорость дня: {mfgame.day_mode}\nДлительность ночи: {mfgame.night_duration} секунд\n{open_roles_embed_txt}",
                            inline=False)
            await inter.send("## Теперь ты участвуешь!", ephemeral=True)
            overwrite_voice = disnake.PermissionOverwrite(speak=True, connect=True, view_channel=True)
            guild = bot.get_guild(servers)
            crt_member = guild.get_member(inter.author.id)
            mfgame = Mafia.get(Mafia.id == mfgame.id)
            mafia_room = mfgame.voice_num
            if mafia_room == 1:
                mafia_room = await bot.fetch_channel(MAFIA_ROOM_1)
            if mafia_room == 2:
                mafia_room = await bot.fetch_channel(MAFIA_ROOM_2)
            if mafia_room == 3:
                mafia_room = await bot.fetch_channel(MAFIA_ROOM_3)
            await mafia_room.set_permissions(target=crt_member, overwrite=overwrite_voice)
            if mfgame.max_players > len(mfgame.players):
                embed.set_default_colour(disnake.Colour.yellow())
                await chat_object.edit(embed=embed, components=[disnake.ui.Button(label="Участвовать", style=disnake.ButtonStyle.success,custom_id="join_private")])
            else:
                Mafia.update(reg_close=datetime.datetime.now(), game_start=datetime.datetime.now()+datetime.timedelta(seconds=30)).where(mfgame).execute()
                mfgame = Mafia.get(Mafia.id == mfgame.id)
                embed.set_default_colour(disnake.Colour.from_rgb(255, 255, 255))
                await chat_object.edit(embed=embed, components=[
                    disnake.ui.Button(label="Участвовать", disabled=True, style=disnake.ButtonStyle.success, custom_id="join_private")])
        else:
            await inter.send("## Неправильный пароль",ephemeral=True)

# 6 игроков - Доктор, Детектив, Мафия, 3 Мирных
# 7 игроков - Доктор, Детектив, Мафия, Красотка, 3 Мирных
# 8 игроков - Доктор, Детектив, Мафия, Красотка, 4 Мирных
# 9 игроков - Доктор, Детектив, 2 Мафии, Красотка, 3 Мирных
# 10 игроков - Доктор, Детектив, 2 Мафии, Красотка, Полицейский, 3 Мирных
# 11 игроков - Доктор, Детектив, 2 Мафии, Красотка, Полицейский, 4 Мирных
# 12 игроков - Доктор, Детектив, 2 Мафии, Красотка, Полицейский, Сумасшедший, 4 Мирных
# 13 игроков - Доктор, Детектив, 2 Мафии, Красотка, Полицейский, Сумасшедший, 5 Мирных
# 14 игроков - Доктор, Детектив, 2 Мафии, Красотка, Полицейский, Сумасшедший, Вор, 5 Мирных
# 15 игроков - Доктор, Детектив, 3 Мафии, Красотка, Полицейский, Сумасшедший, Вор, 5 Мирных
# 16 игроков - Доктор, Детектив, 3 Мафии, Красотка, Полицейский, Сумасшедший, Вор, 6 Мирных


async def mafia_night(mfgame):
    mafia_check_finish = False

    class DoctorSelectMenu(disnake.ui.StringSelect):
        def __init__(self):
            doctor = Players.get((Players.game == mfgame.id) & (Players.role == "doctor"))
            patients = (mfgame.alive_players).copy()
            if doctor.turn is not None:
                if doctor.turn in patients:
                    patients.remove(doctor.turn)
            options = []
            for patient in patients:
                guild = bot.get_guild(servers)
                patient_nick = guild.get_member(int(patient))
                patient_nick = patient_nick.nick
                if patient_nick is None:
                    patient_nick = bot.get_user(int(patient))
                    patient_nick = patient_nick.global_name
                option = disnake.SelectOption(label=patient_nick, value=patient)
                options = [option] + options
            super().__init__(
                placeholder="Кого лечить?",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            if mafia_check_finish == False:
                player_info = Players.get(Players.player_id == inter.author.id)
                mfgame = Mafia.get(Mafia.id == player_info.game)
                msg = bot.get_message(player_info.msg_id)
                await inter.send(f"## Ты вылечил этой ночью <@{self.values[0]}>")
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(url=mf_img_night)
                embed.add_field(name="Роль:", value="Доктор", inline=True)
                embed.add_field(name="Вылечил:", value=f"<@{self.values[0]}>", inline=True)
                await msg.edit(embed=embed, view=disnake.ui.View())
                Players.update(turn=self.values[0], turn_check="Yes").where(Players.player_id == inter.author.id).execute()
            else:
                await inter.send(f"## Ход не засчитан, попробуй еще раз")

    class SendDoctorMenu(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(DoctorSelectMenu())

    class DetectiveSelectMenu(disnake.ui.StringSelect):
        def __init__(self):
            patients = (mfgame.alive_players).copy()
            detective = Players.get((Players.game == mfgame.id) & (Players.role == "detective"))
            patients.remove(detective.player_id)
            options = []
            for patient in patients:
                guild = bot.get_guild(servers)
                patient_nick = guild.get_member(patient)
                patient_nick = patient_nick.nick
                if patient_nick == None:
                    patient_nick = bot.get_user(patient)
                    patient_nick = patient_nick.global_name
                option = disnake.SelectOption(label=patient_nick, value=patient)
                options = [option] + options
            super().__init__(
                placeholder="Кого проверить?",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            if mafia_check_finish == False:
                player_info = Players.get(Players.player_id == inter.author.id)
                mfgame = Mafia.get(Mafia.id == player_info.game)
                msg = bot.get_message(player_info.msg_id)
                await inter.send(f"## Ты проверил этой ночью <@{self.values[0]}>")
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(
                    url=mf_img_night)
                embed.add_field(name="Роль:", value="Детектив", inline=True)
                embed.add_field(name="Проверил:", value=f"<@{self.values[0]}>", inline=True)
                embed.add_field(name="Результат:", value=f"Придет рано утром", inline=False)
                await msg.edit(embed=embed, view=disnake.ui.View())
                Players.update(turn=self.values[0], turn_check = "Yes").where(Players.player_id == inter.author.id).execute()
            else:
                await inter.send(f"## Ход не засчитан, попробуй еще раз")

    class SendDetectiveMenu(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(DetectiveSelectMenu())

    class BabySelectMenu(disnake.ui.StringSelect):
        def __init__(self):
            baby = Players.get((Players.game == mfgame.id) & (Players.role == "baby"))
            patients = (mfgame.alive_players).copy()
            if baby.turn != None:
                if baby.turn in patients:
                    patients.remove(baby.turn)
            options = []
            patients.remove(int(baby.player_id))
            for patient in patients:
                guild = bot.get_guild(servers)
                patient_nick = guild.get_member(int(patient))
                patient_nick = patient_nick.nick
                if patient_nick == None:
                    patient_nick = bot.get_user(int(patient))
                    patient_nick = patient_nick.global_name
                option = disnake.SelectOption(label=patient_nick, value=patient)
                options = [option] + options
            super().__init__(
                placeholder="Кого пригласить в гости?",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            if mafia_check_finish == False:
                player_info = Players.get(Players.player_id == inter.author.id)
                mfgame = Mafia.get(Mafia.id == player_info.game)
                msg = bot.get_message(player_info.msg_id)
                await inter.send(f"## Ты пригласил в гости <@{self.values[0]}>")
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(
                    url=mf_img_night)
                embed.add_field(name="Роль:", value="Красотка", inline=True)
                embed.add_field(name="Пригласил в гости:", value=f"<@{self.values[0]}>", inline=True)
                await msg.edit(embed=embed, view=disnake.ui.View())
                Players.update(turn=self.values[0], turn_check = "Yes").where(Players.player_id == inter.author.id).execute()
            else:
                await inter.send(f"## Ход не засчитан, попробуй еще раз")

    class SendBabyMenu(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(BabySelectMenu())

    class PoliceSelectMenu(disnake.ui.StringSelect):
        def __init__(self):
            police = Players.get((Players.game == mfgame.id) & (Players.role == "police"))
            patients = (mfgame.alive_players).copy()
            if police.turn != None:
                if police.turn in patients:
                    patients.remove(police.turn)
            options = []
            patients.remove(police.player_id)
            for patient in patients:
                guild = bot.get_guild(servers)
                patient_nick = guild.get_member(int(patient))
                patient_nick = patient_nick.nick
                if patient_nick == None:
                    patient_nick = bot.get_user(int(patient))
                    patient_nick = patient_nick.global_name
                option = disnake.SelectOption(label=patient_nick, value=patient)
                options = [option] + options
            super().__init__(
                placeholder="Кого задержать?",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            if mafia_check_finish == False:
                player_info = Players.get(Players.player_id == inter.author.id)
                mfgame = Mafia.get(Mafia.id == player_info.game)
                msg = bot.get_message(player_info.msg_id)
                await inter.send(f"## Ты задержал <@{self.values[0]}>, он более не может ходить")
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(
                    url=mf_img_night)
                embed.add_field(name="Роль:", value="Полицейский", inline=True)
                embed.add_field(name="Задержан:", value=f"<@{self.values[0]}>", inline=True)
                await msg.edit(embed=embed, view=disnake.ui.View())
                Players.update(turn=self.values[0], turn_check = "Yes").where(Players.player_id == inter.author.id).execute()
            else:
                await inter.send(f"## Ход не засчитан, попробуй еще раз")

    class SendPoliceMenu(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(PoliceSelectMenu())

    class ThiefSelectMenu(disnake.ui.StringSelect):
        def __init__(self):
            thief = Players.get((Players.game == mfgame.id) & (Players.role == "thief"))
            patients = (mfgame.alive_players).copy()
            options = []
            patients.remove(thief.player_id)
            for patient in patients:
                guild = bot.get_guild(servers)
                patient_nick = guild.get_member(int(patient))
                patient_nick = patient_nick.nick
                if patient_nick == None:
                    patient_nick = bot.get_user(int(patient))
                    patient_nick = patient_nick.global_name
                option = disnake.SelectOption(label=patient_nick, value=patient)
                options = [option] + options
            super().__init__(
                placeholder="Чью роль украсть?",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            if mafia_check_finish == False:
                player_info = Players.get(Players.player_id == inter.author.id)
                mfgame = Mafia.get(Mafia.id == player_info.game)
                msg = bot.get_message(player_info.msg_id)
                await inter.send(f"## Ты украл роль <@{self.values[0]}>")
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(
                    url=mf_img_night)
                embed.add_field(name="Роль:", value="Вор", inline=True)
                embed.add_field(name="Роль украдена у:", value=f"<@{self.values[0]}>", inline=True)
                embed.add_field(name="Полученная роль:", value=f"Будет получена рано утром", inline=False)
                await msg.edit(embed=embed, view=disnake.ui.View())
                Players.update(turn=self.values[0], turn_check = "Yes").where(Players.player_id == inter.author.id).execute()
            else:
                await inter.send(f"## Ход не засчитан, попробуй еще раз")

    class SendThiefMenu(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(ThiefSelectMenu())

    class MafiaSelectMenu(disnake.ui.StringSelect):
        def __init__(self):
            patients = (mfgame.alive_players).copy()
            mafia_list = mfgame.mafia_list
            for mafia in mafia_list:
                if mafia in patients:
                    patients.remove(mafia)
            options = []
            for patient in patients:
                guild = bot.get_guild(servers)
                patient_nick = guild.get_member(int(patient))
                patient_nick = patient_nick.nick
                if patient_nick == None:
                    patient_nick = bot.get_user(int(patient))
                    patient_nick = patient_nick.global_name
                option = disnake.SelectOption(label=patient_nick, value=patient)
                options = [option] + options
            super().__init__(
                placeholder="Кого убить?",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            if mafia_check_finish == False:
                player_info = Players.get(Players.player_id == inter.author.id)
                mfgame = Mafia.get(Mafia.id == player_info.game)
                msg = bot.get_message(player_info.msg_id)
                await inter.send(f"## Ты убил <@{self.values[0]}>")
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(
                    url=mf_img_night)
                embed.add_field(name="Роль:", value="Мафия", inline=True)
                mafia_alive_list = set(mfgame.alive_players).intersection(mfgame.mafia_list)
                mafia_alive_pl_list = ""
                for mafia_alive_pl in mafia_alive_list:
                    mafia_alive_pl_list = mafia_alive_pl_list + f"<@{mafia_alive_pl}>\n"
                embed.add_field(name="Состав мафии:", value=f"{len(mafia_alive_list)}\n{mafia_alive_pl_list}", inline=False)
                embed.add_field(name="Убит:", value=f"<@{self.values[0]}>", inline=False)
                await msg.edit(embed=embed, view=disnake.ui.View())
                Players.update(turn=self.values[0], turn_check = "Yes").where(Players.player_id == inter.author.id).execute()
            else:
                await inter.send(f"## Ход не засчитан, попробуй еще раз")

    class SendMafiaMenu(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(MafiaSelectMenu())

    class PoliceCRZSelectMenu(disnake.ui.StringSelect):
        def __init__(self):
            crazy = Players.get((Players.game == mfgame.id) & (Players.role == "crazy"))
            patients = (mfgame.alive_players).copy()
            if crazy.turn != None:
                if crazy.turn in patients:
                    patients.remove(crazy.turn)
            options = []
            patients.remove(crazy.player_id)
            for patient in patients:
                guild = bot.get_guild(servers)
                patient_nick = guild.get_member(int(patient))
                patient_nick = patient_nick.nick
                if patient_nick == None:
                    patient_nick = bot.get_user(int(patient))
                    patient_nick = patient_nick.global_name
                option = disnake.SelectOption(label=patient_nick, value=patient)
                options = [option] + options
            super().__init__(
                placeholder="Кого задержать?",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            if mafia_check_finish == False:
                player_info = Players.get(Players.player_id == inter.author.id)
                mfgame = Mafia.get(Mafia.id == player_info.game)
                msg = bot.get_message(player_info.msg_id)
                await inter.send(f"## Ты задержал <@{self.values[0]}>, он более не может ходить")
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(
                    url=mf_img_night)
                embed.add_field(name="Роль:", value="Полицейский", inline=True)
                embed.add_field(name="Задержан:", value=f"<@{self.values[0]}>", inline=True)
                await msg.edit(embed=embed, view=disnake.ui.View())
                Players.update(turn=self.values[0], turn_check="Yes").where(Players.player_id == inter.author.id).execute()
            else:
                await inter.send(f"## Ход не засчитан, попробуй еще раз")

    class SendPoliceCRZMenu(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(PoliceCRZSelectMenu())

    class BabyCRZSelectMenu(disnake.ui.StringSelect):
        def __init__(self):
            crazy = Players.get((Players.game == mfgame.id) & (Players.role == "crazy"))
            patients = (mfgame.alive_players).copy()
            if crazy.turn != None:
                if crazy.turn in patients:
                    patients.remove(crazy.turn)
            options = []
            patients.remove(crazy.player_id)
            for patient in patients:
                guild = bot.get_guild(servers)
                patient_nick = guild.get_member(int(patient))
                patient_nick = patient_nick.nick
                if patient_nick == None:
                    patient_nick = bot.get_user(int(patient))
                    patient_nick = patient_nick.global_name
                option = disnake.SelectOption(label=patient_nick, value=patient)
                options = [option] + options
            super().__init__(
                placeholder="Кого пригласить в гости?",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            if mafia_check_finish is False:
                player_info = Players.get(Players.player_id == inter.author.id)
                mfgame = Mafia.get(Mafia.id == player_info.game)
                msg = bot.get_message(player_info.msg_id)
                await inter.send(f"## Ты пригласил в гости <@{self.values[0]}>")
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(
                    url=mf_img_night)
                embed.add_field(name="Роль:", value="Красотка", inline=True)
                embed.add_field(name="Пригласил в гости:", value=f"<@{self.values[0]}>", inline=True)
                await msg.edit(embed=embed, view=disnake.ui.View())
                Players.update(turn=self.values[0], turn_check="Yes").where(Players.player_id == inter.author.id).execute()
            else:
                await inter.send(f"## Ход не засчитан, попробуй еще раз")

    class SendBabyCRZMenu(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(BabyCRZSelectMenu())

    class DoctorCRZSelectMenu(disnake.ui.StringSelect):
        def __init__(self):
            crazy = Players.get((Players.game == mfgame.id) & (Players.role == "crazy"))
            patients = (mfgame.alive_players).copy()
            if crazy.turn is not None:
                if crazy.turn in patients:
                    patients.remove(crazy.turn)
            options = []
            patients.remove(crazy.player_id)
            for patient in patients:
                guild = bot.get_guild(servers)
                patient_nick = guild.get_member(int(patient))
                patient_nick = patient_nick.nick
                if patient_nick is None:
                    patient_nick = bot.get_user(int(patient))
                    patient_nick = patient_nick.global_name
                option = disnake.SelectOption(label=patient_nick, value=patient)
                options = [option] + options
            super().__init__(
                placeholder="Кого лечить?",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            if mafia_check_finish is False:
                player_info = Players.get(Players.player_id == inter.author.id)
                mfgame = Mafia.get(Mafia.id == player_info.game)
                msg = bot.get_message(player_info.msg_id)
                await inter.send(f"## Ты вылечил этой ночью <@{self.values[0]}>")
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(
                    url=mf_img_night)
                embed.add_field(name="Роль:", value="Доктор", inline=True)
                embed.add_field(name="Вылечил:", value=f"<@{self.values[0]}>", inline=True)
                await msg.edit(embed=embed, view=disnake.ui.View())
                Players.update(turn=self.values[0], turn_check="Yes").where(Players.player_id == inter.author.id).execute()
            else:
                await inter.send(f"## Ход не засчитан, попробуй еще раз")

    class SendDoctorCRZMenu(disnake.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(DoctorCRZSelectMenu())


























































    # НОЧЬ

    mfgame = Mafia.get(Mafia.id == mfgame.id)
    if mfgame.status == "Stoped":
        return
    game_thread = await bot.fetch_channel(mfgame.game_thread)
    old_game_history = str(mfgame.action_history)
    night_num = mfgame.night_count + 1
    new_game_history = old_game_history + f"\n\n``Ночь #{night_num}:``"
    Mafia.update(
        action_history=new_game_history,
        night_count=night_num, voted_already=[]).where(Mafia.id == mfgame.id).execute()
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    alive_players = (mfgame.alive_players).copy()
    alive_players_list = ""
    for alive_player in alive_players:
        alive_players_list = alive_players_list + f"<@{alive_player}>\n"
    embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Игроки:\n{alive_players_list}", color=disnake.Colour.dark_blue())
    embed.set_footer(text=f"Игра #{mfgame.id}")
    embed.add_field(name="Игроков осталось:", value=len(alive_players), inline=True)
    embed.set_image(url=mf_img_night)
    if mfgame.voice_num == 1:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_1)
    elif mfgame.voice_num == 2:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_2)
    else:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_3)
    overwrite_voice = disnake.PermissionOverwrite(speak=False, connect=True, view_channel=True)
    # overwrite_voice2 = disnake.PermissionOverwrite(speak=False, connect=False, view_channel=False)
    mafia_room_0 = await bot.fetch_channel(mafia_room_0_id)
    night_members = []
    for night_mmbr in mfgame.alive_players:
        guild = bot.get_guild(servers)
        crt_member = guild.get_member(night_mmbr)
        night_members.append(night_mmbr)
        await mafia_room.set_permissions(target=crt_member, overwrite=overwrite_voice)
        mafia_room = await bot.fetch_channel(mafia_room.id)
        mafia_room_members = mafia_room.members
        if crt_member in mafia_room_members:
            # await mafia_room_0.set_permissions(target=crt_member, overwrite=overwrite_voice)
            await crt_member.move_to(channel=mafia_room_0)
            await crt_member.move_to(channel=mafia_room)
            # await mafia_room_0.set_permissions(target=crt_member, overwrite=overwrite_voice2)
    await game_thread.edit(locked=True)
    await game_thread.send(embed=embed)
    night_over = datetime.datetime.now() + datetime.timedelta(seconds=mfgame.night_duration)
    night_over_embed = round((night_over - year1970).total_seconds())
    for alive_player in alive_players:
        mfgame = Mafia.get(Mafia.id == mfgame.id)
        embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>", color=disnake.Colour.dark_blue())
        embed.set_image(
            url=mf_img_night)
        embed.set_footer(text=f"Игра #{mfgame.id}")
        player_info = Players.get(Players.player_id == alive_player)
        user = bot.get_user(int(alive_player))
        if player_info.role == "doctor":
            embed.add_field(name="Роль:", value="Доктор", inline=False)
            view = SendDoctorMenu()
            msg = await user.send(embed=embed, view=view)
            Players.update(msg_id=msg.id).where(Players.player_id == alive_player).execute()
        if player_info.role == "detective":
            view = SendDetectiveMenu()
            embed.add_field(name="Роль:", value="Детектив", inline=False)
            msg = await user.send(embed=embed, view=view)
        if player_info.role == "mafia":
            view = SendMafiaMenu()
            embed.add_field(name="Роль:", value="Мафия", inline=False)
            # mafia_alive_list = set(mfgame.alive_players).intersection(mfgame.mafia_list)
            mafia_alive_list = []
            for mafia123 in mfgame.mafia_list:
                if mafia123 in mfgame.alive_players:
                    mafia_alive_list.append(mafia123)
            mafia_alive_pl_list = ""
            for mafia_alive_pl in mafia_alive_list:
                mafia_alive_pl_list = mafia_alive_pl_list + f"<@{mafia_alive_pl}>\n"
            embed.add_field(name="Состав мафии:", value=f"{len(mafia_alive_list)}\n{mafia_alive_pl_list}", inline=False)
            msg = await user.send(embed=embed, view=view)
        if player_info.role == "people":
            embed.add_field(name="Роль:", value="Мирный житель", inline=False)
            msg = await user.send(embed=embed)
        if player_info.role == "baby":
            view = SendBabyMenu()
            embed.add_field(name="Роль:", value="Красотка", inline=False)
            msg = await user.send(embed=embed, view=view)
        if player_info.role == "police":
            view = SendPoliceMenu()
            embed.add_field(name="Роль:", value="Полицейский", inline=False)
            await user.send(embed=embed, view=view)
        if player_info.role == "crazy":
            if player_info.crazy_role == "doctor":
                view = SendDoctorCRZMenu()
                embed.add_field(name="Роль:", value="Доктор", inline=False)
                msg = await user.send(embed=embed, view=view)
            if player_info.crazy_role == "baby":
                view = SendBabyCRZMenu()
                embed.add_field(name="Роль:", value="Красотка", inline=False)
                msg = await user.send(embed=embed, view=view)
            if player_info.crazy_role == "police":
                view = SendPoliceCRZMenu()
                embed.add_field(name="Роль:", value="Полицейский", inline=False)
                msg = await user.send(embed=embed, view=view)
        if player_info.role == "thief":
            embed.add_field(name="Роль:", value="Вор", inline=False)
            view = SendThiefMenu()
            msg = await user.send(embed=embed, view=view)
        Players.update(msg_id=msg.id, turn_check=None).where(Players.player_id == alive_player).execute()
    night_over_timer = night_over - datetime.datetime.now()
    await asyncio.sleep(round(night_over_timer.total_seconds()))
    night_check_finish = True
    police_player = Players.get_or_none(
        (Players.role == "police") & (Players.game == mfgame.id) & (Players.status == "played"))
    doctor_player = Players.get_or_none(
        (Players.role == "doctor") & (Players.game == mfgame.id) & (Players.status == "played"))
    baby_player = Players.get_or_none(
        (Players.role == "baby") & (Players.game == mfgame.id) & (Players.status == "played"))
    detective_player = Players.get_or_none(
        (Players.role == "detective") & (Players.game == mfgame.id) & (Players.status == "played"))
    thief_player = Players.get_or_none(
        (Players.role == "thief") & (Players.game == mfgame.id) & (Players.status == "played"))
    crazy_player = Players.get_or_none(
        (Players.role == "crazy") & (Players.game == mfgame.id) & (Players.status == "played"))
    mafia_list = mfgame.mafia_list
    police_turn = None
    baby_turn = None
    mafia_turn = None
    detective_turn = None
    doctor_turn = None
    thief_turn = None
    crazy_turn = None
    police_afk = ""
    baby_afk = ""
    doctor_afk = ""
    detective_afk = ""
    mafia_afk = ""
    thief_afk = ""
    crazy_afk = ""


    # ОБРАБОТЧИК НОЧИ
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    action_history = mfgame.action_history
    if mfgame.status == "Stoped":
        return

    if police_player is not None:
        if police_player.turn_check is None:
            police_turn_list = (mfgame.alive_players).copy()
            police_turn_list.remove(police_player.player_id)
            police_turn = police_player.turn
            if police_turn is not None:
                police_turn_list.remove(police_player.turn)
            turn = random.choices(police_turn_list)
            turn = turn[0]
            Players.update(turn=turn).where(Players.player_id == police_player.player_id).execute()
            msg = police_player.msg_id
            msg = bot.get_message(msg)
            embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                  color=disnake.Colour.dark_blue())
            embed.set_image(
                url=mf_img_night)
            embed.add_field(name="Роль:", value="Полицейский", inline=True)
            embed.add_field(name="Задержан:", value=f"<@{turn}>", inline=True)
            await msg.edit(embed=embed, view=disnake.ui.View())
            police_turn = turn
            police_afk = bot_emoji
        else:
            police_turn = police_player.turn



    if baby_player is not None:
        if baby_player.turn_check is None:
            baby_turn_list = (mfgame.alive_players).copy()
            baby_turn_list.remove(baby_player.player_id)
            baby_turn = baby_player.turn
            if baby_turn is not None:
                baby_turn_list.remove(baby_player.turn)
            turn = random.choices(baby_turn_list)
            turn = turn[0]
            Players.update(turn=turn).where(Players.player_id == baby_player.player_id).execute()
            msg = baby_player.msg_id
            msg = bot.get_message(msg)
            embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                  color=disnake.Colour.dark_blue())
            embed.set_image(
                url=mf_img_night)
            embed.add_field(name="Роль:", value="Красотка", inline=True)
            embed.add_field(name="Пригласила в гости:", value=f"<@{turn}", inline=True)
            await msg.edit(embed=embed, view=disnake.ui.View())
            baby_turn = turn
            baby_afk = bot_emoji
        else:
            baby_turn = baby_player.turn

    mafia_turn_check = None
    mafia_player = None
    for mafia in mafia_list:
        if (mafia in mfgame.alive_players) and (mafia_turn_check is None) and (mafia != police_turn):
            mafia_turn_check = "Yes"
            mafia_player = Players.get(Players.player_id == mafia)
            if mafia_player.turn_check is None:
                mafia_turn_list = mfgame.alive_players.copy()
                for mafia_pl in mafia_list:
                    if mafia_pl in mafia_turn_list:
                        mafia_turn_list.remove(mafia_pl)
                turn = random.choices(mafia_turn_list)
                turn = turn[0]
                Players.update(turn=turn).where(Players.player_id == mafia_player.player_id).execute()
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(
                    url=mf_img_night)
                embed.add_field(name="Роль:", value="Мафия", inline=True)
                # mafia_alive_list = set(mfgame.alive_players).intersection(mfgame.mafia_list)
                mafia_alive_list = []
                for mafia345 in mfgame.mafia_list:
                    if mafia345 in mfgame.alive_players:
                        mafia_alive_list = mafia_alive_list + [mafia345]
                mafia_alive_pl_list = ""
                for mafia_alive_pl in mafia_alive_list:
                    mafia_alive_pl_list = mafia_alive_pl_list + f"<@{mafia_alive_pl}>\n"
                embed.add_field(name="Состав мафии:", value=f"{len(mafia_alive_list)}\n{mafia_alive_pl_list}",inline=False)
                embed.add_field(name="Убит:", value=f"<@{turn}>", inline=False)
                msg = mafia_player.msg_id
                msg = bot.get_message(msg)
                await msg.edit(embed=embed, view=disnake.ui.View())
                mafia_turn = turn
                mafia_afk = bot_emoji
            else:
                mafia_turn = mafia_player.turn

    if doctor_player is not None:
        if doctor_player.turn_check is None:
            doctor_turn_list = (mfgame.alive_players).copy()
            doctor_turn_list.remove(doctor_player.player_id)
            doctor_turn = doctor_player.turn
            if doctor_turn is None:
                turn = random.choices(doctor_turn_list)
                turn = turn[0]
                Players.update(turn=turn).where(Players.player_id == doctor_player.player_id).execute()
            else:
                doctor_turn_list.remove(doctor_player.turn)
                turn = random.choices(doctor_turn_list)
                turn = turn[0]
                Players.update(turn=turn).where(Players.player_id == doctor_player.player_id).execute()
            msg = doctor_player.msg_id
            msg = bot.get_message(msg)
            embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                  color=disnake.Colour.dark_blue())
            embed.set_image(
                url=mf_img_night)
            embed.add_field(name="Роль:", value="Доктор", inline=True)
            embed.add_field(name="Вылечил:", value=f"<@{turn}", inline=True)
            await msg.edit(embed=embed, view=disnake.ui.View())
            doctor_turn = turn
            doctor_afk = bot_emoji
        else:
            doctor_turn = doctor_player.turn

    if thief_player is not None:
        if thief_player.turn_check is None:
            thief_turn_list = (mfgame.alive_players).copy()
            thief_turn_list.remove(thief_player.player_id)
            thief_turn = thief_player.turn
            if thief_turn is None:
                turn = random.choices(thief_turn_list)
                turn = turn[0]
                Players.update(turn=turn).where(Players.player_id == thief_player.player_id).execute()
            else:
                thief_turn_list.remove(thief_player.turn)
                turn = random.choices(thief_turn_list)
                turn = turn[0]
                Players.update(turn=turn).where(Players.player_id == thief_player.player_id).execute()
            msg = thief_player.msg_id
            msg = bot.get_message(msg)
            embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                  color=disnake.Colour.dark_blue())
            embed.set_image(
                url=mf_img_night)
            embed.add_field(name="Роль:", value="Вор", inline=True)
            embed.add_field(name="Роль украдена у:", value=f"<@{turn}>", inline=True)
            embed.add_field(name="Полученная роль:", value=f"Будет получена рано утром", inline=False)
            await msg.edit(embed=embed, view=disnake.ui.View())
            thief_turn = turn
            thief_afk = bot_emoji
        else:
            thief_turn = thief_player.turn

    crazy_role = None
    if crazy_player != None:
        crazy_role = crazy_player.crazy_role
        if crazy_player.turn_check == None:
            crazy_turn_list = (mfgame.alive_players).copy()
            turn = crazy_player.turn
            if turn != None:
                crazy_turn_list.remove(crazy_player.turn)
            if (crazy_player.crazy_role == "baby") or (crazy_player.crazy_role == "police"):
                crazy_turn_list.remove(crazy_player.player_id)
            turn = random.choices(crazy_turn_list)
            turn = turn[0]
            Players.update(turn=turn).where(Players.player_id == crazy_player.player_id).execute()
            msg = crazy_player.msg_id
            msg = bot.get_message(msg)
            if crazy_player.crazy_role == "doctor":
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(url=mf_img_night)
                embed.add_field(name="Роль:", value="Доктор", inline=True)
                embed.add_field(name="Вылечил:", value=f"<@{turn}>", inline=True)
            if crazy_player.crazy_role == "police":
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(url=mf_img_night)
                embed.add_field(name="Роль:", value="Полицейский", inline=True)
                embed.add_field(name="Задержан:", value=f"<@{turn}>", inline=True)
            if crazy_player.crazy_role == "baby":
                embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>",
                                      color=disnake.Colour.dark_blue())
                embed.set_image(url=mf_img_night)
                embed.add_field(name="Роль:", value="Красотка", inline=True)
                embed.add_field(name="Пригласила в гости:", value=f"<@{turn}>", inline=True)
            await msg.edit(embed=embed, view=disnake.ui.View())
            crazy_turn = turn
            crazy_afk = bot_emoji
        else:
            crazy_turn = crazy_player.turn
    if detective_player is not None:
        if detective_player.turn_check is None:
            detective_turn_list = (mfgame.alive_players).copy()
            detective_turn_list.remove(detective_player.player_id)
            turn = random.choices(detective_turn_list)
            turn = turn[0]
            embed = disnake.Embed(
                description=f"# Ночь #{night_num}\n## Закончится <t:{night_over_embed}:R>", 
                color=disnake.Colour.dark_blue())
            embed.set_image(url=mf_img_night)
            embed.add_field(name="Роль:", value="Детектив", inline=True)
            embed.add_field(name="Проверил:", value=f"<@{turn}>", inline=True)
            embed.add_field(name="Результат:", value=f"Придет рано утром",inline=False)
            msg = detective_player.msg_id
            msg = bot.get_message(msg)
            detective_turn = turn
            detective_afk = bot_emoji
            await msg.edit(embed=embed, view=disnake.ui.View())
        else:
            detective_turn = detective_player.turn

    # обработчик всех ходов
    # [role]_player - строка в Players / None
    # [role]_turn - id игрока / None
    # action_history - история игры
    if police_turn is not None:
        police_turn_people = Players.get(Players.player_id == police_turn)
        if (police_turn_people.role == "people") or (police_turn_people.role == "crazy"):
            result_emoji = no_emoji
        else:
            result_emoji = yes_emoji
        action_history += f"\n-# <:police:1279123991826796564><@{police_player.player_id}> задержал <@{police_turn}>{result_emoji}{police_afk}"
        embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Законичалась", color=disnake.Colour.dark_blue())
        embed.set_image(url=mf_img_night)
        embed.add_field(name="Роль:", value="Полицейский", inline=True)
        embed.add_field(name="Задержан:", value=f"<@{police_turn}>", inline=True)
        msg = police_player.msg_id
        msg = bot.get_message(msg)
        await msg.edit(embed=embed, view=disnake.ui.View())
        user = bot.get_user(police_turn)
        await user.send("## Полицейский задержал тебя этой ночью!")
    if baby_turn is not None:
        baby_turn_people = Players.get(Players.player_id == baby_turn)
        if baby_player.player_id == police_turn:
            police_emoji = stop_emoji
            Players.update(turn=None).where(Players.player_id == baby_player.player_id).execute()
        else:
            police_emoji = ""
        if baby_turn == mafia_turn:
            result_emoji = yes_emoji
        else:
            result_emoji = no_emoji
        if result_emoji == yes_emoji:
            action_history += f"\n-# <:baby:1279126735119716460><@{baby_player.player_id}> забрала в гости <@{baby_turn}>{result_emoji}{police_emoji}{baby_afk}"
        else:
            action_history += f"\n-# <:baby:1279126735119716460><@{baby_player.player_id}> пригласила в гости <@{baby_turn}>{result_emoji}{police_emoji}{baby_afk}"
        embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Законичалась", color=disnake.Colour.dark_blue())
        embed.set_image(url=mf_img_night)
        embed.add_field(name="Роль:", value="Красотка", inline=True)
        embed.add_field(name="Пригласила в гости:", value=f"<@{baby_turn}>{police_emoji}", inline=True)
        msg = baby_player.msg_id
        msg = bot.get_message(msg)
        await msg.edit(embed=embed, view=disnake.ui.View())
    killed = None
    after_mafia_killed = []
    if mafia_turn is not None:
        if mafia_player.player_id == police_turn:
            police_emoji = stop_emoji
            Players.update(turn=None).where(Players.player_id == mafia_player.player_id).execute()
        else:
            police_emoji = ""
        result_emoji = ""
        baby_check = False
        embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Закончилась",
                              color=disnake.Colour.dark_blue())
        embed.set_image(url=mf_img_night)
        embed.add_field(name="Роль:", value="Мафия", inline=True)
        # mafia_alive_list = set(mfgame.alive_players).intersection(mfgame.mafia_list)
        mafia_alive_list = []
        for mafia in mfgame.mafia_list:
            if mafia in mfgame.alive_players:
                mafia_alive_list = mafia_alive_list + [mafia]
        mafia_alive_pl_list = ""
        for mafia_alive_pl in mafia_alive_list:
            mafia_alive_pl_list = mafia_alive_pl_list + f"<@{mafia_alive_pl}>\n"
        embed.add_field(name="Состав мафии:", value=f"{len(mafia_alive_list)}\n{mafia_alive_pl_list}", inline=False)
        embed.add_field(name="Убит:", value=f"<@{mafia_turn}>", inline=False)
        if baby_player is not None:
            if police_turn == baby_player.player_id:
                baby_turn_stoped = True
            else:
                baby_turn_stoped = False
        else:
            baby_turn_stoped = False
        if (baby_turn_stoped is False) and (baby_player is not None):
            if mafia_turn == baby_turn:
                result_emoji = no_emoji
            elif mafia_turn == baby_player.player_id:
                result_emoji = yes_emoji
                baby_check = True
                if doctor_turn == baby_player.player_id:
                    killed = [baby_turn]
                elif doctor_turn == baby_turn:
                    killed = [baby_player.player_id]
                else:
                    killed = [baby_turn, baby_player.player_id]
                    random.shuffle(killed)
            elif (mafia_turn == doctor_turn) and (mafia_turn != baby_player.player_id):
                result_emoji = no_emoji
            else:
                result_emoji = yes_emoji
                killed = [mafia_turn]
        else:
            if mafia_turn == doctor_turn:
                result_emoji = no_emoji
            else:
                result_emoji = yes_emoji
                killed = [mafia_turn]
        if baby_check is False:
            action_history += f"\n-# <:mafia:1279146979481489429><@{mafia_player.player_id}> убил <@{mafia_turn}>{result_emoji}{police_emoji}{mafia_afk}"
        else:
            action_history += f"\n-# <:mafia:1279146979481489429><@{mafia_player.player_id}> убил <@{mafia_turn}> и <@{baby_turn}>{result_emoji}{police_emoji}{mafia_afk}"
        mfgame_2 = Mafia.get(Mafia.id == mfgame.id)
        after_mafia_killed = (mfgame_2.alive_players).copy()
        msg = mafia_player.msg_id
        msg = bot.get_message(msg)
        await msg.edit(embed=embed)
        if killed is not None:
            for abcdefg in killed:
                if abcdefg in after_mafia_killed:
                    after_mafia_killed.remove(abcdefg)
        msg = mafia_player.msg_id
        msg = bot.get_message(msg)
        await msg.edit(embed=embed)
    if doctor_turn != None:
        if doctor_player.player_id == police_turn:
            police_emoji = stop_emoji
            Players.update(turn=None).where(Players.player_id == doctor_player.player_id).execute()
        else:
            police_emoji = ""
        if baby_player != None:
            if doctor_turn == mafia_turn:
                result_emoji = yes_emoji
            elif (doctor_turn == baby_turn) and (mafia_turn == baby_player.player_id):
                result_emoji = yes_emoji
            else:
                result_emoji = no_emoji
        else:
            if doctor_turn  == mafia_turn:
                result_emoji = yes_emoji
            else:
                result_emoji = no_emoji
        if result_emoji == yes_emoji:
            action_history += f"\n-# <:doctor:1279169650344857731><@{doctor_player.player_id}> воксресил <@{doctor_turn}>{result_emoji}{police_emoji}{doctor_afk}"
        else:
            action_history += f"\n-# <:doctor:1279169650344857731><@{doctor_player.player_id}> полечил <@{doctor_turn}>{result_emoji}{police_emoji}{doctor_afk}"
        embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Законичалась", color=disnake.Colour.dark_blue())
        embed.set_image(
            url=mf_img_night)
        embed.add_field(name="Роль:", value="Доктор", inline=True)
        embed.add_field(name="Вылечил:", value=f"<@{doctor_turn}>{police_emoji}", inline=True)
        msg = doctor_player.msg_id
        msg = bot.get_message(msg)
        await msg.edit(embed=embed, view=disnake.ui.View())
    if detective_turn != None:
        if detective_player.player_id == police_turn:
            police_emoji = stop_emoji
            Players.update(turn=None).where(Players.player_id == detective_player.player_id).execute()
        else:
            police_emoji = ""
        if detective_turn in mafia_list:
            result_emoji = yes_emoji
        else:
            result_emoji = no_emoji
        if result_emoji == yes_emoji:
            action_history += f"\n-# <:detective:1279204298248683614><@{detective_player.player_id}> нашел мафию <@{detective_turn}>{result_emoji}{police_emoji}{detective_afk}"
        else:
            action_history += f"\n-# <:detective:1279204298248683614><@{detective_player.player_id}> проверил <@{detective_turn}>{result_emoji}{police_emoji}{detective_afk}"
        embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Законичалась", color=disnake.Colour.dark_blue())
        embed.set_image(
            url=mf_img_night)
        embed.add_field(name="Роль:", value="Детектив", inline=True)
        embed.add_field(name="Проверил:", value=f"<@{detective_turn}>{police_emoji}", inline=True)
        if detective_player.player_id == police_turn:
            embed.add_field(name="Результат:", value=f"Ход задержан полицейским", inline=False)
        else:
            if result_emoji == yes_emoji:
                embed.add_field(name="Результат:", value=f"Обнаружена мафия", inline=False)
            else:
                embed.add_field(name="Результат:", value=f"Мафия НЕ обнаружена", inline=False)
        msg = detective_player.msg_id
        msg = bot.get_message(msg)
        await msg.edit(embed=embed, view=disnake.ui.View())
    if crazy_turn != None:
        if crazy_player.player_id == police_turn:
            police_emoji = stop_emoji
            Players.update(turn=None).where(Players.player_id == crazy_player.player_id).execute()
        else:
            police_emoji = ""
        if crazy_role == "doctor":
            if baby_player != None:
                if doctor_turn == mafia_turn:
                    result_emoji = yes_emoji
                elif (doctor_turn == baby_turn) and (mafia_turn == baby_player.player_id):
                    result_emoji = yes_emoji
                else:
                    result_emoji = no_emoji
            else:
                if doctor_turn == mafia_turn:
                    result_emoji = yes_emoji
                else:
                    result_emoji = no_emoji
            if result_emoji == yes_emoji:
                action_history += f"\n-# <:crazy:1279205262074445865><@{crazy_player.player_id}> воксресил <@{crazy_turn}>{result_emoji}{police_emoji}{crazy_afk}"
            else:
                action_history += f"\n-# <:crazy:1279205262074445865><@{crazy_player.player_id}> полечил <@{crazy_turn}>{result_emoji}{police_emoji}{crazy_afk}"
            embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Законичалась", color=disnake.Colour.dark_blue())
            embed.set_image(
                url=mf_img_night)
            embed.add_field(name="Роль:", value="Доктор", inline=True)
            embed.add_field(name="Вылечил:", value=f"<@{crazy_turn}>{police_emoji}", inline=True)
            msg = crazy_player.msg_id
            msg = bot.get_message(msg)
            await msg.edit(embed=embed, view=disnake.ui.View())
        if crazy_role == "police":
            crz_police_turn_people = Players.get(Players.player_id == crazy_turn)
            if (crz_police_turn_people.role == "people") or (crz_police_turn_people.role == "crazy"):
                result_emoji = no_emoji
            else:
                result_emoji = yes_emoji
            action_history += f"\n-# <:crazy:1279205262074445865><@{crazy_player.player_id}> задержал <@{crazy_turn}>{result_emoji}{police_emoji}{crazy_afk}"
            embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Законичалась", color=disnake.Colour.dark_blue())
            embed.set_image(
                url=mf_img_night)
            embed.add_field(name="Роль:", value="Полицейский", inline=True)
            embed.add_field(name="Задержан:", value=f"<@{crazy_turn}>", inline=True)
            msg = crazy_player.msg_id
            msg = bot.get_message(msg)
            await msg.edit(embed=embed, view=disnake.ui.View())
        if crazy_role == "baby":
            crz_baby_turn_people = Players.get(Players.player_id == crazy_turn)
            if crazy_turn == mafia_turn:
                result_emoji = yes_emoji
            else:
                result_emoji = no_emoji
            action_history += f"\n-# <:crazy:1279205262074445865><@{crazy_player.player_id}> забрала в гости <@{crazy_turn}>{result_emoji}{police_emoji}{crazy_afk}"
            embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Законичалась", color=disnake.Colour.dark_blue())
            embed.set_image(
                url=mf_img_night)
            embed.add_field(name="Роль:", value="Красотка", inline=True)
            embed.add_field(name="Пригласила в гости:", value=f"<@{crazy_turn}>{police_emoji}", inline=True)
            msg = crazy_player.msg_id
            msg = bot.get_message(msg)
            await msg.edit(embed=embed, view=disnake.ui.View())
    if thief_turn != None:
        embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Законичалась", color=disnake.Colour.dark_blue())
        embed.set_image(
            url=mf_img_night)
        embed.add_field(name="Роль:", value="Вор", inline=True)
        embed.add_field(name="Роль украдена у:", value=f"<@{thief_turn}>", inline=True)
        if thief_player.player_id == police_turn:
            police_emoji = stop_emoji
            Players.update(turn=None).where(Players.player_id == thief_player.player_id).execute()
        else:
            police_emoji = ""
        if thief_player.player_id != police_turn:
            if thief_turn in mafia_list:
                if killed == None:
                    killed = [thief_player.player_id]
                else:
                    killed = killed + [thief_player.player_id]
                result_emoji = no_emoji
                action_history += f"\n-# <:thief:1279486227438899281><@{thief_player.player_id}> пытался украсть роль мафии у <@{thief_turn}>, потому был убит{result_emoji}{police_emoji}{thief_afk}"
            else:
                user = bot.get_user(thief_turn)
                await user.send("## Вор украл твою роль! Теперь ты мирный житель.")
                Players.update(role = "people").where(Players.player_id == thief_turn).execute()
                thief_turn_people = Players.get(Players.player_id == thief_turn)
                if thief_turn_people.role == "crazy":
                    Players.update(role = "crazy", crazy_role=thief_turn_people.crazy_role).where(Players.player_id == thief_player.player_id).execute()
                    embed.add_field(name="Полученная роль:", value=f"{thief_turn_people.crazy_role}", inline=False)
                else:
                    embed.add_field(name="Полученная роль:", value=f"{thief_turn_people.role}", inline=False)
                result_emoji = yes_emoji
                action_history += f"\n-# <:thief:1279486227438899281><@{thief_player.player_id}> украл роль у <@{thief_turn}>{result_emoji}{police_emoji}{thief_afk}"
        else:
            embed.add_field(name="Полученная роль:", value=f"Ход задержан полицейским", inline=False)
            action_history += f"\n-# <:thief:1279486227438899281><@{thief_player.player_id}> пытался украсть роль у <@{thief_turn}>{result_emoji}{police_emoji}{thief_afk}"
        msg = thief_player.msg_id
        msg = bot.get_message(msg)
        await msg.edit(embed=embed, view=disnake.ui.View())
    if killed is not None:
        Mafia.update(alive_players=after_mafia_killed).where(Mafia.id == mfgame.id).execute()
        for kill in killed:
            user = bot.get_user(kill)
            kill_user = Players.get(Players.player_id == kill)
            Players.update(status="died").where(Players.player_id == kill_user.player_id).execute()
            dead_list = mfgame.dead_players
            if dead_list is None:
                dead_list = []
            dead_list = dead_list + [kill]
            Mafia.update(dead_players=dead_list).where(Mafia.id == mfgame.id).execute()
            mfgame = Mafia.get(Mafia.id == mfgame.id)
            await user.send(f"## Ты был убит\nИгра #{mfgame.id}")
    else:
        killed = []
    Mafia.update(action_history=action_history).where(Mafia.id == mfgame.id).execute()
    for people in night_members:
        people_info = Players.get(player_id=people)
        if people_info.role == "people":
            msg = people_info.msg_id
            msg = bot.get_message(msg)
            embed = disnake.Embed(description=f"# Ночь #{night_num}\n## Законичалась", color=disnake.Colour.dark_blue())
            embed.set_image(url=mf_img_night)
            await msg.edit(embed=embed)
    await mafia_day(mfgame, killed)
    return


async def mafia_stop(mfgame, stop_moment):
    mfgame = Mafia.get(id=mfgame.id)
    if stop_moment == "Registration":
        guild = bot.get_guild(servers)
        mafia_chat_object = await guild.fetch_channel(MAFIA)
        msg = await mafia_chat_object.fetch_message(mfgame.reg_msg_id)
        embed = disnake.Embed(
            description=f"# МАФИЯ #{mfgame.id}\n## Игра остановлена\n## Игроки:\n{mfgame.players_list}", )
        embed.set_image(
            url=mf_img_logo)

        embed.add_field(name="Участвует:", value=len(mfgame.players), inline=True)
        embed.add_field(name="Минимум:", value=mfgame.min_players, inline=True)
        embed.add_field(name="Максимум:", value=mfgame.max_players, inline=True)
        if mfgame.open_roles == "YES":
            open_roles_embed_txt = "Роли не засекречены"
        elif mfgame.open_roles == "NO":
            open_roles_embed_txt = "Роли засекречены"
        else:
            open_roles_embed_txt = "Ошибка! error_id = 0008"  # fixme 0008
        embed.add_field(name="Настройки:",
                        value=f"Скорость дня: {mfgame.day_mode}\nДлительность ночи: {mfgame.night_duration} секунд\n{open_roles_embed_txt}",
                        inline=False)
        embed.set_default_colour(disnake.Colour.red())
        await msg.edit(embed=embed, components=[
            disnake.ui.Button(label="Участвовать", style=disnake.ButtonStyle.success,
                              custom_id="join_cl", disabled=True)])
        Mafia.update(crush_status="no", status="Stoped", voice_num=0, game_finish=datetime.datetime.now()).where(Mafia.id == mfgame.id).execute()
        pplstrt = (mfgame.players).copy()
        pplstrt = list(pplstrt.keys())
        for ppl in pplstrt:
            ppl = int(ppl)
            user = bot.get_user(ppl)
            Players.update(status="not_played", role=None, crazy_role=None, turn_check=None, game=0, voted=0, msg_id=None).where(Players.player_id == ppl).execute()
    elif (stop_moment == "day") or (stop_moment == "night") or (stop_moment == "vote"):
        action_history = mfgame.action_history
        action_history += "\n# ИГРА ОСТАНОВЛЕНА"
        game_time_finsih = datetime.datetime.now()
        game_thread = await bot.fetch_channel(mfgame.game_thread)
        await game_thread.edit(locked=True, archived=True)
        if mfgame.voice_num == 1:
            mafia_room = await bot.fetch_channel(MAFIA_ROOM_1)
        elif mfgame.voice_num == 2:
            mafia_room = await bot.fetch_channel(MAFIA_ROOM_2)
        else:
            mafia_room = await bot.fetch_channel(MAFIA_ROOM_3)
        pplstrt = (mfgame.players).copy()
        pplstrt = list(pplstrt.keys())
        overwrite_voice = disnake.PermissionOverwrite(speak=False, connect=False, view_channel=False)
        guild = bot.get_guild(servers)
        await game_thread.edit(locked=True, archived=True)
        players_and_roles = ""
        for player in pplstrt:
            player = int(player)
            crt_member = guild.get_member(player)
            await mafia_room.set_permissions(target=crt_member, overwrite=overwrite_voice)
            mafia_room = await bot.fetch_channel(mafia_room.id)
            mafia_room_members = mafia_room.members
            mafia_room_0 = await bot.fetch_channel(mafia_room_0_id)
            if crt_member in mafia_room_members:
                await crt_member.move_to(channel=mafia_room_0)
                await crt_member.move_to(channel=mafia_room)
            if (mfgame.players).get(f"{player}") == "mafia":
                player_role = "мафия<:mafia:1279146979481489429>"
            elif (mfgame.players).get(f"{player}") == "people":
                player_role = "мирный житель"
            elif (mfgame.players).get(f"{player}") == "police":
                player_role = "полицейский<:police:1279123991826796564>"
            elif (mfgame.players).get(f"{player}") == "baby":
                player_role = "красотка<:baby:1279126735119716460>"
            elif (mfgame.players).get(f"{player}") == "thief":
                player_role = "вор<:thief:1279486227438899281>"
            elif (mfgame.players).get(f"{player}") == "detective":
                player_role = "детектив<:detective:1279204298248683614>"
            elif (mfgame.players).get(f"{player}") == "doctor":
                player_role = "доктор<:doctor:1279169650344857731>"
            else:
                player_role = "сумасшедший<:crazy:1279205262074445865>"
            players_and_roles += f"<@{player}> - {player_role}\n"
        embed1 = disnake.Embed(
            description=f"# Игра остановлена!\n### Игроки:\n{players_and_roles}",
            color=disnake.Colour.purple())
        embed2 = disnake.Embed(description=
                               f"## История игры:\n"
                               f"{bot_emoji} - ход сделан автоматически\n"
                               f"{stop_emoji} - ход отменен полицейским\n"
                               f"{yes_emoji} - успешный ход\n"
                               f"{no_emoji} - неуспешный ход\n"
                               f"{mfgame.action_history}\n"
                               f"## Игра завершена, игра остановлена", color=disnake.Colour.purple())
        mf_msg_id = await game_thread.send(embeds=[embed1, embed2])
        Mafia.update(game_finish=game_time_finsih, mf_msg_id=mf_msg_id.id, crush_status="no", voice_num=0,
                     status="Stoped").where(Mafia.id == mfgame.id).execute()
        for player in pplstrt:
            player = int(player)
            #player_info = Players.get(Players.player_id == player)
            crt_member = guild.get_member(player)
            mfgame = Mafia.get(Mafia.id == mfgame.id)
            Players.update(status="not_played", game=0, role=None, voted=None, turn=None, msg_id=None,
                           crazy_role=None, turn_check=None).where(Players.player_id == player).execute()
            embed = disnake.Embed(
                description=f"## Игра #{mfgame.id} остановлена!",
                color=disnake.Colour.red())
            embed.add_field(name="Подробнее", value=mf_msg_id.jump_url, inline=True)
            user = bot.get_user(crt_member.id)
            await game_thread.add_user(user)
            await user.send(embed=embed)
        await game_thread.edit(locked=True, archived=True)
    else:
        user = bot.get_user(737017177864929370)
        await user.send("ERROR! (error_id == 0007)") #fixme 0007


async def mafia_day(mfgame, killed):
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    if mfgame.status == "Stoped":
        return
    mafia_alive_list = []
    for mafia_plp in mfgame.mafia_list:
        if mafia_plp in mfgame.alive_players:
            mafia_alive_list.append(mafia_plp)
    if len(mafia_alive_list) == 0:
        await mafia_finish(mfgame, winner="people")
        return
    doctor_check = Players.get_or_none((Players.role == "doctor") & (Players.game == mfgame.id) & (Players.status == "played"))
    baby_check = Players.get_or_none((Players.role == "baby") & (Players.game == mfgame.id) & (Players.status == "played"))
    if (len(mafia_alive_list) >= (len(mfgame.alive_players)-len(mafia_alive_list))):
        if (baby_check == None) or (doctor_check == None):
            await mafia_finish(mfgame, winner="mafia")
            return
    day_num = mfgame.day_count + 1
    action_history = mfgame.action_history
    action_history += f"\n\n ``День #{day_num}:``"
    Mafia.update(day_count=day_num, status="Day", action_history=action_history).where(Mafia.id == mfgame.id).execute()
    game_thread = await bot.fetch_channel(mfgame.game_thread)
    colour_embed = disnake.Colour.green()
    if len(killed) != 0:
        colour_embed = disnake.Colour.red()
    kill_embed = disnake.Embed(description=f"## Убиты это ночью:", colour=colour_embed)
    for kill in killed:
        kill_user = bot.get_user(kill)
        if mfgame.open_roles == "YES":
            players_dict = (mfgame.players).copy()
            pl_role123 = players_dict.get(f"{kill}")
            if pl_role123 == "people":
                pl_role123 = "Мирный"
            elif pl_role123 == "mafia":
                pl_role123 = "Мафия"
            elif pl_role123 == "doctor":
                pl_role123 = "Доктор"
            elif pl_role123 == "detective":
                pl_role123 = "Детектив"
            elif pl_role123 == "baby":
                pl_role123 = "Красотка"
            elif pl_role123 == "police":
                pl_role123 = "Полицейский"
            else:
                pl_role123 = "Ошибка! error_id = 0001" #fixme 0001
        else:
            pl_role123 = "Роль засекречена"
        kill_embed.add_field(name=pl_role123, value=f"<@{kill}>", inline=False)
        await game_thread.remove_user(kill_user)
    await game_thread.send(embed=kill_embed)
    if mfgame.voice_num == 1:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_1)
    elif mfgame.voice_num == 2:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_2)
    else:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_3)
    overwrite_voice = disnake.PermissionOverwrite(speak=True, connect=True, view_channel=True)
    for day_mmbr in mfgame.alive_players:
        guild = bot.get_guild(servers)
        crt_member = guild.get_member(day_mmbr)
        await mafia_room.set_permissions(target=crt_member, overwrite=overwrite_voice)
        mafia_room = await bot.fetch_channel(mafia_room.id)
        mafia_room_members = mafia_room.members
        mafia_room_0 = await bot.fetch_channel(mafia_room_0_id)
        if crt_member in mafia_room_members:
            await crt_member.move_to(channel=mafia_room_0)
            await crt_member.move_to(channel=mafia_room)
    alive_players = (mfgame.alive_players).copy()
    alive_players_list = ""
    for alive_player in alive_players:
        alive_players_list = alive_players_list + f"<@{alive_player}>\n"
    if mfgame.day_mode == "Очень быстрый":
        day_duration = 15 + len(mfgame.alive_players) * 25
    elif mfgame.day_mode == "Быстрый":
        day_duration = 20 + len(mfgame.alive_players) * 30
    elif mfgame.day_mode == "Средний":
        day_duration = 30 + len(mfgame.alive_players) * 35
    elif mfgame.day_mode == "Длинный":
        day_duration = 45 + len(mfgame.alive_players) * 40
    elif mfgame.day_mode == "Очень длинный":
        day_duration = 65 + len(mfgame.alive_players) * 55
    else:
        day_duration = 30 + len(mfgame.alive_players) * 35
    Mafia.update(day_duration=day_duration).where(Mafia.id == mfgame.id).execute()
    embed = disnake.Embed(description=f"# День #{day_num}\n## Голосование <t:{round(((datetime.datetime.now() + datetime.timedelta(seconds=day_duration))-year1970).total_seconds())}:R>\n## Игроки:\n{alive_players_list}",
                          color=disnake.Colour.yellow())
    embed.set_footer(text=f"Игра #{mfgame.id}")
    embed.add_field(name="Игроков осталось:", value=len(alive_players), inline=True)
    embed.set_image(
        url=mf_img_day)
    msg = await game_thread.send(embed=embed, components=[
            disnake.ui.Button(label="Перейти к голосованию", style=disnake.ButtonStyle.success,
                              custom_id="start_vote")])
    Mafia.update(mf_msg_id = msg.id).where(Mafia.id == mfgame.id).execute()
    await game_thread.edit(locked=False)
    await asyncio.sleep(day_duration)
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    if mfgame.status == "Day":
        embed = disnake.Embed(
            description=f"# День #{day_num}\n## Голосование началось!\n## Игроки:\n{alive_players_list}",
            color=disnake.Colour.yellow())
        embed.set_footer(text=f"Игра #{mfgame.id}")
        embed.add_field(name="Игроков осталось:", value=len(alive_players), inline=True)
        embed.set_image(
            url=mf_img_day)
        await msg.edit(embed=embed, components=[])
        vote_list = mfgame.alive_players
        await mafia_vote(mfgame, vote_kick_list=vote_list)
    return


@bot.slash_command(description='Выдать бан в мафии', guild_ids=[servers], name="mfban")
async def mfban(inter, user : disnake.User = commands.Param(description="Выбери пользователя, которого надо забанить"), days : int = 0 , hours : int = 0, minutes : int = 0):
    """
                Parameters
                ----------
                user: Пользователь
                days: Дней блокировки
                hours: Часов блокировки
                minutes: Минут блокировки
                """
    unban_time = datetime.datetime.now() + datetime.timedelta(days=days, hours=hours, minutes=minutes)
    in_table = Players.get_or_none(player_id=user.id)
    if in_table is None:
        Players.create(player_id=user.id, status="not_played")
    Players.update(unban_time=unban_time).where(Players.player_id == user.id).execute()
    await inter.send(f"Пользователь <@{user.id}> заблокирован на:\n**{days}** дней\n**{hours}** часов\n**{minutes}** минут",ephemeral=True)


@bot.slash_command(description='Снять бан в мафии', guild_ids=[servers], name="mfunban")
async def mfunban(inter, user : disnake.User = commands.Param(description="Выбери пользователя, которого надо разбанить")):
    in_table = Players.get_or_none(player_id=user.id)
    if in_table is None:
        await inter.send(f"<@{user.id}> не был заблокирован", ephemeral=True)
        return
    if in_table.unban_time < datetime.datetime.now():
        await inter.send(f"<@{user.id}> не был заблокирован", ephemeral=True)
        return
    Players.update(unban_time=None).where(Players.player_id == user.id).execute()
    await inter.send(f"<@{user.id}> разблокирован",ephemeral=True)


@bot.slash_command(description='Получить данные о игроке', guild_ids=[servers], name="mf_pl_info")
async def mf_pl_info(inter, user: disnake.Member = commands.Param(description="Выбери пользователя, о котором хочешь спросить")):
    player = Players.get_or_none(player_id=user.id)
    if player == None:
        await inter.send(f"## <@{user.id}> не представлен в таблице игроков 'Мафии'", ephemeral=True)
        return
    colour = disnake.Colour.default()
    rating_embed = disnake.Embed(description="## RATING:", colour=colour)
    rating_embed.add_field(name="RATING", value=player.rating, inline=False)
    win_dict = player.win_results
    lose_dict = player.lose_results
    roles = list(win_dict.keys())
    win_txt = ""
    lose_txt = ""
    for role in roles:
        win_txt += f"{role} : {win_dict.get(role)}\n"
        lose_txt += f"{role} : {lose_dict.get(role)}\n"
    rating_embed.add_field(name="WIN_RESULTS", value=win_txt, inline=False)
    rating_embed.add_field(name="LOSE_RESULTS", value=lose_txt, inline=False)

    info_embed = disnake.Embed(description="## INFO:", colour=colour)
    info_embed.add_field(name="PLAYER_ID", value=player.player_id, inline=False)
    info_embed.add_field(name="STATUS", value=player.status, inline=False)
    info_embed.add_field(name="GAME", value=player.game, inline=False)
    if player.unban_time == None:
        info_embed.add_field(name="UNBAN_TIME", value="NONE", inline=False)
    else:
        info_embed.add_field(name="UNBAN_TIME", value=f"<t:{round(((player.unban_time - year1970).total_seconds()))}:R>",
                             inline=False)

    game_embed = disnake.Embed(description="## GAME:", colour=colour)
    if player.game is not None:
        game_embed.add_field(name="GAME", value=player.game, inline=False)
    else:
        game_embed.add_field(name="GAME", value="NONE", inline=False)



    if player.role is not None:
        game_embed.add_field(name="ROLE", value=player.role, inline=False)
    else:
        game_embed.add_field(name="ROLE", value="NONE", inline=False)




    if player.crazy_role is not None:
        game_embed.add_field(name="CRAZY_ROLE", value=player.crazy_role, inline=False)
    else:
        game_embed.add_field(name="CRAZY_ROLE", value="NONE", inline=False)



    if player.msg_id is not None:
        game_embed.add_field(name="MSG_ID", value=player.msg_id, inline=False)
    else:
        game_embed.add_field(name="MSG_ID", value="NONE", inline=False)



    if player.turn is not None:
        game_embed.add_field(name="TURN", value=player.turn, inline=False)
    else:
        game_embed.add_field(name="TURN", value="NONE", inline=False)

    if player.turn_check is not None:
        game_embed.add_field(name="TURN_CHECK", value=player.turn_check, inline=False)
    else:
        game_embed.add_field(name="TURN_CHECK", value="NONE", inline=False)

    if player.voted is not None:
        game_embed.add_field(name="VOTED", value=player.voted, inline=False)
    else:
        game_embed.add_field(name="VOTED", value="NONE", inline=False)
    await inter.send(f"## Пользователь <@{user.id}> представлен в таблице игроков 'Мафии':", embeds=[info_embed, rating_embed, game_embed], ephemeral=True)




@bot.listen("on_button_click")
async def mafia_game_listen(inter: disnake.MessageInteraction):
    if inter.component.custom_id not in ["start_vote"]:
        return
    mfgame = Mafia.get(Mafia.mf_msg_id == inter.message.id)
    if mfgame.status != "Day":
        await inter.send("Ошибка! error_id = 0005", ephemeral=True) #fixme 0005
        return
    if inter.component.custom_id == "start_vote":
        if inter.author.id not in mfgame.alive_players:
            await inter.send("Ты вообще-то мертвый -_-",ephemeral=True)
            return
        voted_already = mfgame.voted_already
        if voted_already == None:
            voted_already = []
        if inter.author.id in voted_already:
            await inter.send("Ты уже готов к голосованию!",ephemeral=True)
        else:
            voted_already.append(inter.author.id)
            Mafia.update(voted_already=voted_already).where(Mafia.id == mfgame.id).execute()
            if (len(voted_already))/(len(mfgame.alive_players)) > 0.5:
                msg = inter.message
                alive_players = (mfgame.alive_players).copy()
                alive_players_list = ""
                for alive_player in alive_players:
                    alive_players_list = alive_players_list + f"<@{alive_player}>\n"
                embed = disnake.Embed(
                    description=f"# День #{mfgame.day_count}\n## Голосование началось!\n## Игроки:\n{alive_players_list}",
                    color=disnake.Colour.yellow())
                embed.set_footer(text=f"Игра #{mfgame.id}")
                embed.add_field(name="Игроков осталось:", value=len(mfgame.alive_players), inline=True)
                embed.set_image(url=mf_img_day)
                await msg.edit(embed=embed, components=[])
                vote_list = mfgame.alive_players
                await mafia_vote(mfgame, vote_kick_list=vote_list)
                return
            else:
                await inter.send("Теперь ты готов к голосованию!",ephemeral=True)


async def mafia_vote(mfgame, vote_kick_list):
    Mafia.update(status="vote", voted_already=[]).where(Mafia.id == mfgame.id).execute()
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    if mfgame.status == "Stoped":
        return
    if mfgame.voice_num == 1:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_1)
    elif mfgame.voice_num == 2:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_2)
    else:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_3)
    overwrite_voice = disnake.PermissionOverwrite(speak=False, connect=True, view_channel=True)
    for day_mmbr in mfgame.alive_players:
        guild = bot.get_guild(servers)
        crt_member = guild.get_member(day_mmbr)
        await mafia_room.set_permissions(target=crt_member, overwrite=overwrite_voice)
        mafia_room = await bot.fetch_channel(mafia_room.id)
        mafia_room_members = mafia_room.members
        mafia_room_0 = await bot.fetch_channel(mafia_room_0_id)
        if crt_member in mafia_room_members:
            await crt_member.move_to(channel=mafia_room_0)
            await crt_member.move_to(channel=mafia_room)
    game_thread = await bot.fetch_channel(mfgame.game_thread)
    await game_thread.edit(locked=True)
    candidats_list = ""
    for candidat in vote_kick_list:
        candidats_list += f"<@{candidat}>\n"
    embed = disnake.Embed(
        description=f"# Голосование.\n### Выбери кого линчевать(убить):",
        color=disnake.Colour.yellow())
    embed.add_field(name="Игроков осталось:", value=len(mfgame.alive_players), inline=False)
    embed.add_field(name="Кандидаты:", value=candidats_list)
    embed.add_field(name="Времени отведено:", value=f"35 секунд", inline=False)
    await game_thread.send(embed=embed)

    class VoteMenu(disnake.ui.StringSelect):
        def __init__(self, crt_member, mfgame_id):
            mfgame = Mafia.get(Mafia.id == mfgame_id)
            patients = vote_kick_list.copy()
            if crt_member.id in patients:
                patients.remove(crt_member.id)
            options = []
            for patient in patients:
                guild = bot.get_guild(servers)
                patient_nick = guild.get_member(int(patient))
                patient_nick = patient_nick.nick
                if patient_nick == None:
                    patient_nick = bot.get_user(int(patient))
                    patient_nick = patient_nick.global_name
                option = disnake.SelectOption(label=patient_nick, value=patient)
                options = options + [option]
            super().__init__(
                placeholder="Пропуск голосования",
                min_values=1,
                max_values=1,
                options=options,
            )

        async def callback(self, inter: disnake.MessageInteraction):
            player_info = Players.get(Players.player_id == inter.author.id)
            mfgame = Mafia.get(Mafia.id == player_info.game)
            if mfgame.status == "vote":
                action_history = mfgame.action_history
                action_history += f"\n-# <@{player_info.player_id}> голосует за <@{self.values[0]}>"
                Mafia.update(action_history=action_history).where(Mafia.id == mfgame.id).execute()
                msg = bot.get_message(player_info.msg_id)
                await inter.send(f"## Ты проголосвал за <@{self.values[0]}>")
                Players.update(voted=self.values[0]).where(Players.player_id == player_info.player_id).execute()
                embed = disnake.Embed(
                    description=f"# Голосование.\n### Выбери кого линчевать(убить):",
                    color=disnake.Colour.yellow())
                embed.set_footer(text=f"Игра #{mfgame.id}")
                embed.add_field(name="Проголосовал за:", value=f"<@{self.values[0]}>", inline=True)
                embed.add_field(name="Игроков осталось:", value=len(mfgame.alive_players), inline=False)
                await msg.edit(embed=embed, view=disnake.ui.View())
            else:
                if mfgame.status == "Stoped":
                    await inter.send("## Эта игра была остановлена!")
                    msg = inter.message
                    embed = disnake.Embed(
                        description=f"# Голосование\n### Выбери кого линчевать(убить):",
                        color=disnake.Colour.yellow())
                    embed.set_footer(text=f"Игра #{mfgame.id}")
                    embed.add_field(name="Игроков осталось:", value=len(mfgame.alive_players), inline=True)
                    embed.add_field(name="Проголосовал за:", value=f"Пропуск", inline=True)
                    await msg.edit(embed=embed, view=None)
                elif mfgame.status == "Crushed":
                    await inter.send("## Эта игра была крашнута!")
                    msg = inter.message
                    embed = disnake.Embed(
                        description=f"# Голосование\n### Выбери кого линчевать(убить):",
                        color=disnake.Colour.yellow())
                    embed.set_footer(text=f"Игра #{mfgame.id}")
                    embed.add_field(name="Игроков осталось:", value=len(mfgame.alive_players), inline=True)
                    embed.add_field(name="Проголосовал за:", value=f"Пропуск", inline=True)
                    await msg.edit(embed=embed, view=None)
    class SendVoteMenu(disnake.ui.View):
        def __init__(self, votemenu: VoteMenu):
            super().__init__()
            self.add_item(votemenu)


    for day_mmbr in mfgame.alive_players:
        crt_member = bot.get_user(day_mmbr)
        lcl_vote_menu = VoteMenu(crt_member=crt_member, mfgame_id=mfgame.id)
        send_vote_menu = SendVoteMenu(votemenu=lcl_vote_menu)



        embed = disnake.Embed(
            description=f"# Голосование\n### Выбери кого линчевать(убить):",
            color=disnake.Colour.yellow())
        embed.set_footer(text=f"Игра #{mfgame.id}")
        embed.add_field(name="Игроков осталось:", value=len(mfgame.alive_players), inline=True)
        msg_id = await crt_member.send(embed=embed, view=send_vote_menu)
        Players.update(msg_id=msg_id.id, voted=0).where(Players.player_id==crt_member.id).execute()
    await asyncio.sleep(35)
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    for day_mmbr2 in mfgame.alive_players:
        day_mmbr2_in_Players = Players.get(Players.player_id == day_mmbr2)
        msg = bot.get_message(day_mmbr2_in_Players.msg_id)
        if (day_mmbr2_in_Players.voted == 0) or (day_mmbr2_in_Players.voted == None):
            embed = disnake.Embed(
                description=f"# Голосование\n### Выбери кого линчевать(убить):",
                color=disnake.Colour.yellow())
            embed.set_footer(text=f"Игра #{mfgame.id}")
            embed.add_field(name="Игроков осталось:", value=len(mfgame.alive_players), inline=True)
            embed.add_field(name="Проголосовал за:", value=f"Пропуск", inline=True)
            await msg.edit(embed=embed, view=None)
    vote_list = {"skip":0}
    for mmbr in vote_kick_list:
        vote_list[mmbr] = 0
    for voter in mfgame.alive_players:
        voter = Players.get(Players.player_id == voter)
        if (voter.voted == 0) or (voter.voted == None):
            vote_list["skip"] = vote_list.get("skip") + 1
        else:
            vote_list[voter.voted] = vote_list.get(voter.voted) + 1
    vote_list_finish = [key for key, value in vote_list.items() if value == max(vote_list.values())]
    # vote_list_finish - список кандидатов(включая "skip"), что набрали наибольшее количество голосов.
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    action_history = mfgame.action_history
    mafia_alive_list = []
    for mafia_plp in mfgame.mafia_list:
        if mafia_plp in mfgame.alive_players:
            mafia_alive_list.append(mafia_plp)
    if len(vote_list_finish) == 1:
        if vote_list_finish == ["skip"]:
            embed = disnake.Embed(
                description=f"# Голосование окончено\n## Линчевание отменяется!",
                color=disnake.Colour.red())
            await game_thread.send(embed=embed)
            action_history += f"\n### Линчевание отменено!"
            Mafia.update(action_history=action_history).where(Mafia.id == mfgame.id).execute()
            doctor_check = Players.get_or_none((Players.role == "doctor") & (Players.game == mfgame.id) & (Players.status == "played"))
            baby_check = Players.get_or_none((Players.role == "baby") & (Players.game == mfgame.id) & (Players.status == "played"))
            if (len(mafia_alive_list)+1 == len(mfgame.alive_players)-len(mafia_alive_list)) and (baby_check==None) and (doctor_check==None):
                await mafia_finish(mfgame, winner="mafia")
                return
            await mafia_night(mfgame)

        else:
            for kill in vote_list_finish:
                kill = kill
            user = bot.get_user(kill)
            kill_user = Players.get(Players.player_id == kill)
            Players.update(status="died").where(Players.player_id == kill_user.player_id).execute()
            dead_list = mfgame.dead_players
            if dead_list == None:
                dead_list = []
            dead_list = dead_list + [kill]
            action_history += f"\n### <@{kill}> линчевали"
            alive_players_list = mfgame.alive_players.copy()
            alive_players_list.remove(kill)
            Mafia.update(dead_players=dead_list, action_history=action_history, alive_players=alive_players_list).where(Mafia.id == mfgame.id).execute()
            mfgame = Mafia.get(Mafia.id == mfgame.id)
            await user.send(f"## Тебя линчевали на дневном голсовании!\nИгра #{mfgame.id}")
            if mfgame.open_roles == "YES":
                players_dict = (mfgame.players).copy()
                pl_role123 = players_dict.get(f"{kill}")
                if pl_role123 == "people":
                    pl_role123 = "Мирный"
                elif pl_role123 == "mafia":
                    pl_role123 = "Мафия"
                elif pl_role123 == "doctor":
                    pl_role123 = "Доктор"
                elif pl_role123 == "detective":
                    pl_role123 = "Детектив"
                elif pl_role123 == "baby":
                    pl_role123 = "Красотка"
                elif pl_role123 == "police":
                    pl_role123 = "Полицейский"
                else:
                    pl_role123 = "Ошибка! error_id = 0002" #fixme 0002
            else:
                pl_role123 = "Засекречена"
            embed = disnake.Embed(
                description=f"# Голосование окончено\n## Вешаем <@{kill}>!",
                color=disnake.Colour.yellow())
            embed.add_field(name="Роль:", value=pl_role123, inline=True)
            await game_thread.remove_user(user)
            await game_thread.send(embed=embed)
            doctor_check = Players.get_or_none((Players.role == "doctor") & (Players.game == mfgame.id) & (Players.status == "played"))
            baby_check = Players.get_or_none((Players.role == "baby") & (Players.game == mfgame.id) & (Players.status == "played"))
            mafia_alive_list = []
            for mafia_plp in mfgame.mafia_list:
                if mafia_plp in mfgame.alive_players:
                    mafia_alive_list.append(mafia_plp)
            if len(mafia_alive_list) == 0:
                await mafia_finish(mfgame, winner="people")
                return
            if (len(mafia_alive_list) >= (len(mfgame.alive_players) - len(mafia_alive_list))):
                if (baby_check == None) or (doctor_check == None):
                    await mafia_finish(mfgame, winner="mafia")
                    return
            await mafia_night(mfgame)
    else:
        if len(vote_list_finish) == len(vote_kick_list):
            embed = disnake.Embed(
                description=f"# Голосование окончено\n## Линчевание отменяется!",
                color=disnake.Colour.red())
            await game_thread.send(embed=embed)
            action_history += f"\n### Линчевание отменено!"
            Mafia.update(action_history=action_history).where(Mafia.id == mfgame.id).execute()
            await mafia_night(mfgame)
        else:
            action_history += f"\n ### Голосование перезапуск"
            Mafia.update(action_history=action_history).where(Mafia.id == mfgame.id).execute()
            await mafia_vote(mfgame=mfgame, vote_kick_list=vote_list_finish)

async def mafia_finish(mfgame, winner):
    Mafia.update(status="Finished").where(Mafia.id == mfgame.id).execute()
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    game_time_finsih = datetime.datetime.now()
    game_thread = await bot.fetch_channel(mfgame.game_thread)
    if mfgame.voice_num == 1:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_1)
    elif mfgame.voice_num == 2:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_2)
    else:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_3)
    pplstrt = (mfgame.players).copy()
    pplstrt = list(pplstrt.keys())
    overwrite_voice = disnake.PermissionOverwrite(speak=True, connect=False, view_channel=False)
    guild = bot.get_guild(servers)
    await game_thread.edit(locked=True, archived=True)
    if winner == "mafia":
        txt = "Победила мафия"
    else:
        txt = "Победили мирные"
    players_and_roles = ""
    game_duration = game_time_finsih - mfgame.game_start
    game_duration = game_duration.total_seconds()
    game_duration = round(game_duration)
    game_duration = game_duration // 60
    for player in pplstrt:
        player = int(player)
        player_info = Players.get(Players.player_id == player)
        crt_member = guild.get_member(player)
        await mafia_room.set_permissions(target=crt_member, overwrite=overwrite_voice)
        mafia_room = await bot.fetch_channel(mafia_room.id)
        mafia_room_members = mafia_room.members
        mafia_room_0 = await bot.fetch_channel(mafia_room_0_id)
        if crt_member in mafia_room_members:
            await crt_member.move_to(channel=mafia_room_0)
            await crt_member.move_to(channel=mafia_room)
        if (mfgame.players).get(f"{player}") == "mafia":
            player_role = "мафия<:mafia:1279146979481489429>"
        elif (mfgame.players).get(f"{player}") == "people":
            player_role = "мирный житель"
        elif (mfgame.players).get(f"{player}") == "police":
            player_role = "полицейский<:police:1279123991826796564>"
        elif (mfgame.players).get(f"{player}") == "baby":
            player_role = "красотка<:baby:1279126735119716460>"
        elif (mfgame.players).get(f"{player}") == "thief":
            player_role = "вор<:thief:1279486227438899281>"
        elif (mfgame.players).get(f"{player}") == "detective":
            player_role = "детектив<:detective:1279204298248683614>"
        elif (mfgame.players).get(f"{player}") == "doctor":
            player_role = "доктор<:doctor:1279169650344857731>"
        else:
            player_role = "сумасшедший<:crazy:1279205262074445865>"
        players_and_roles += f"<@{player}> - {player_role}\n"
    embed1 = disnake.Embed(
        description=f"# Игра завершена!\n## {txt}\n### Игроки:\n{players_and_roles}",
        color=disnake.Colour.purple())
    embed2 = disnake.Embed(description=f"## История игры:\n"
                                       f"{bot_emoji} - ход сделан автоматически\n"
                                       f"{stop_emoji} - ход отменен полицейским\n"
                                       f"{yes_emoji} - успешный ход\n"
                                       f"{no_emoji} - неуспешный ход\n"
                                       f"{mfgame.action_history}\n"
                                       f"## Игра завершена, {txt}",
                           color=disnake.Colour.purple())
    embed2.set_footer(text=f"Длительность игры: {game_duration} минут")
    mf_msg_id = await game_thread.send(embeds=[embed1, embed2])
    Mafia.update(game_finish=game_time_finsih, mf_msg_id=mf_msg_id.id, crush_status="no", voice_num=0, status="Finish").where(Mafia.id == mfgame.id).execute()
    for player in pplstrt:
        player = int(player)
        player_info = Players.get(Players.player_id == player)
        crt_member = guild.get_member(player)
        player_role = (mfgame.players).get(f"{player}")
        mfgame = Mafia.get(Mafia.id == mfgame.id)
        if player in mfgame.dead_players:
            user = bot.get_user(crt_member.id)
            await game_thread.add_user(user)
        if player_role == "mafia":
            if winner == "mafia":
                rating_change = 35
                win_check = True
            else:
                rating_change = -10
                win_check = False
        elif (player_role == "people"):
            if winner == "people":
                rating_change = 25
                win_check = True
            else:
                rating_change = -15
                win_check = False
        elif (player_role == "thief"):
            if winner == "people":
                rating_change = 20
                win_check = True
            else:
                rating_change = -15
                win_check = False
        else:
            if winner == "people":
                rating_change = 20
                win_check = True
            else:
                rating_change = -25
                win_check = False
        if win_check == True:
            EmbedColour = disnake.Colour.green()
            EmbedTXT = "Получено:"
            win_results = player_info.win_results
            win_results = win_results.copy()
            win_role_result = win_results.get(player_role)
            win_results[player_role] = win_role_result + 1
            if (player_info.rating + rating_change >= 700):
                result_rating = 700
            else:
                result_rating = player_info.rating + rating_change
            Players.update(rating=result_rating, win_results=win_results).where(Players.player_id == player_info.player_id).execute()
        else:
            EmbedColour = disnake.Colour.red()
            EmbedTXT = "Потеряно:"
            lose_results = player_info.lose_results
            lose_results = lose_results.copy()
            lose_role_result = lose_results.get(player_role)
            lose_results[player_role] = lose_role_result + 1
            if (player_info.rating + rating_change <= 0):
                result_rating = 0
            else:
                result_rating = player_info.rating + rating_change
            Players.update(rating=result_rating, lose_results=lose_results).where(Players.player_id == player_info.player_id).execute()
        Players.update(status="not_played", game=0, role=None, voted=None, turn=None, msg_id=None,crazy_role=None).where(Players.player_id == player).execute()
        embed = disnake.Embed(
            description=f"## Игра #{mfgame.id} завершена! {txt}\n## Рейтинг:",
            color=EmbedColour)
        embed.add_field(name="Было:", value=player_info.rating, inline=True)
        embed.add_field(name=EmbedTXT, value=abs(rating_change), inline=True)
        embed.add_field(name="Стало:", value=result_rating, inline=True)
        embed.add_field(name="Подробнее", value=mf_msg_id.jump_url, inline=True)
        user = bot.get_user(crt_member.id)
        await user.send(embed=embed)
    await game_thread.edit(locked=True, archived=True)

async def mafia_crush(mfgame):
    mfgame = Mafia.get(id=mfgame.id)
    action_history = mfgame.action_history
    action_history += "\n# ИГРА КРАШНУТА"
    game_time_finsih = datetime.datetime.now()
    game_thread = await bot.fetch_channel(mfgame.game_thread)
    if mfgame.voice_num == 1:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_1)
    elif mfgame.voice_num == 2:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_2)
    else:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_3)
    pplstrt = (mfgame.players).copy()
    pplstrt = list(pplstrt.keys())
    overwrite_voice = disnake.PermissionOverwrite(speak=False, connect=False, view_channel=False)
    guild = bot.get_guild(servers)
    await game_thread.edit(locked=True, archived=True)
    players_and_roles = ""
    for player in pplstrt:
        player = int(player)
        crt_member = guild.get_member(player)
        await mafia_room.set_permissions(target=crt_member, overwrite=overwrite_voice)
        mafia_room = await bot.fetch_channel(mafia_room.id)
        mafia_room_members = mafia_room.members
        mafia_room_0 = await bot.fetch_channel(mafia_room_0_id)
        if crt_member in mafia_room_members:
            await crt_member.move_to(channel=mafia_room_0)
            await crt_member.move_to(channel=mafia_room)
        if (mfgame.players).get(f"{player}") == "mafia":
            player_role = "мафия<:mafia:1279146979481489429>"
        elif (mfgame.players).get(f"{player}") == "people":
            player_role = "мирный житель"
        elif (mfgame.players).get(f"{player}") == "police":
            player_role = "полицейский<:police:1279123991826796564>"
        elif (mfgame.players).get(f"{player}") == "baby":
            player_role = "красотка<:baby:1279126735119716460>"
        elif (mfgame.players).get(f"{player}") == "thief":
            player_role = "вор<:thief:1279486227438899281>"
        elif (mfgame.players).get(f"{player}") == "detective":
            player_role = "детектив<:detective:1279204298248683614>"
        elif (mfgame.players).get(f"{player}") == "doctor":
            player_role = "доктор<:doctor:1279169650344857731>"
        else:
            player_role = "сумасшедший<:crazy:1279205262074445865>"
        players_and_roles += f"<@{player}> - {player_role}\n"
    embed1 = disnake.Embed(
        description=f"# Игра крашнута!\n### Игроки:\n{players_and_roles}",
        color=disnake.Colour.purple())
    embed2 = disnake.Embed(
        description=f"## История игры:\n"
                    f"{bot_emoji} - ход сделан автоматически\n"
                    f"{stop_emoji} - ход отменен полицейским\n"
                    f"{yes_emoji} - успешный ход\n"
                    f"{no_emoji} - неуспешный ход\n"
                    f"{mfgame.action_history}\n"
                    f"## Игра завершена, игра крашнута",
        color=disnake.Colour.purple())
    mf_msg_id = await game_thread.send(embeds=[embed1, embed2])
    Mafia.update(game_finish=game_time_finsih, mf_msg_id=mf_msg_id.id, crush_status="no", voice_num=0,
                 status="Crushed").where(Mafia.id == mfgame.id).execute()
    for player in pplstrt:
        player = int(player)
        player_info = Players.get(Players.player_id == player)
        crt_member = guild.get_member(player)
        mfgame = Mafia.get(Mafia.id == mfgame.id)
        Players.update(status="not_played", game=0, role=None, voted=None, turn=None, msg_id=None,
                       crazy_role=None).where(Players.player_id == player).execute()
        embed = disnake.Embed(
            description=f"## Игра #{mfgame.id} крашнута!",
            color=disnake.Colour.red())
        embed.add_field(name="Подробнее", value=mf_msg_id.jump_url, inline=True)
        user = bot.get_user(crt_member.id)
        await game_thread.add_user(user)
        await user.send(embed=embed)
    await game_thread.edit(locked=True, archived=True)
async def mafia_reg_crush(mfgame):
    mfgame = Mafia.get(id=mfgame.id)
    guild = bot.get_guild(servers)
    mafia_chat_object = await guild.fetch_channel(MAFIA)
    msg = await mafia_chat_object.fetch_message(mfgame.reg_msg_id)
    embed = disnake.Embed(
        description=f"# МАФИЯ #{mfgame.id}\n## Игра крашнута\n## Игроки:\n{mfgame.players_list}", )
    embed.set_image(
        url=mf_img_logo)

    embed.add_field(name="Участвует:", value=len(mfgame.players), inline=True)
    embed.add_field(name="Минимум:", value=mfgame.min_players, inline=True)
    embed.add_field(name="Максимум:", value=mfgame.max_players, inline=True)
    if mfgame.open_roles == "YES":
        open_roles_embed_txt = "Роли не засекречены"
    elif mfgame.open_roles == "NO":
        open_roles_embed_txt = "Роли засекречены"
    else:
        open_roles_embed_txt = "Ошибка! error_id = 0009"  # fixme 0009
    embed.add_field(name="Настройки:",
                    value=f"Скорость дня: {mfgame.day_mode}\nДлительность ночи: {mfgame.night_duration} секунд\n{open_roles_embed_txt}",
                    inline=False)
    embed.set_default_colour(disnake.Colour.red())
    await msg.edit(embed=embed, components=[
        disnake.ui.Button(label="Участвовать", style=disnake.ButtonStyle.success,
                          custom_id="join_cl", disabled=True)])
    Mafia.update(crush_status="no", status="Crushed", voice_num=0, ).where(Mafia.id == mfgame.id).execute()
    pplstrt = (mfgame.players).copy()
    pplstrt = list(pplstrt.keys())
    for ppl in pplstrt:
        ppl = int(ppl)
        Players.update(status="not_played", role=None, crazy_role=None, turn_check=None, game=0, voted=0,
                       msg_id=None).where(Players.player_id == ppl).execute()


async def mafia_game(mfgame):
    global roles
    if mfgame.voice_num == 1:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_1)
    if mfgame.voice_num == 2:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_2)
    if mfgame.voice_num == 3:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_3)
    in_voice = mafia_room.members
    for voice_start_mmbr in in_voice:
        pplstrt = (mfgame.players).copy()
        pplstrt = list(pplstrt.keys())
        if f"{voice_start_mmbr.id}" not in pplstrt:
            await voice_start_mmbr.move_to(channel=None)
    if len(mfgame.players) < mfgame.min_players:
        guild = bot.get_guild(servers)
        mafia_chat_object = await guild.fetch_channel(MAFIA)
        chat_object = await mafia_chat_object.fetch_message(mfgame.reg_msg_id)
        embed = disnake.Embed(
            description=f"# МАФИЯ #{mfgame.id}\n## НЕДОСТАТОЧНО ИГРОКОВ\n## Игроки:\n{mfgame.players_list}", )
        embed.set_image(
            url=mf_img_logo)

        embed.add_field(name="Участвует:", value=len(mfgame.players), inline=True)
        embed.add_field(name="Минимум:", value=mfgame.min_players, inline=True)
        embed.add_field(name="Максимум:", value=mfgame.max_players, inline=True)
        if mfgame.open_roles == "YES":
            open_roles_embed_txt = "Роли не засекречены"
        elif mfgame.open_roles == "NO":
            open_roles_embed_txt = "Роли засекречены"
        else:
            open_roles_embed_txt = "Ошибка! error_id = 0003"  #fixme 0003
        embed.add_field(name="Настройки:",
                        value=f"Скорость дня: {mfgame.day_mode}\nДлительность ночи: {mfgame.night_duration} секунд\n{open_roles_embed_txt}",
                        inline=False)
        embed.set_default_colour(disnake.Colour.red())
        await chat_object.edit(embed=embed, components=[
            disnake.ui.Button(label="Участвовать", style=disnake.ButtonStyle.success,
                              custom_id="join_cl", disabled=True)])
        Mafia.update(status="Players < Minimal_players", crush_status="No crush", voice_num=0).where(Mafia.id == mfgame.id).execute()
        pplstrt = (mfgame.players).copy()
        pplstrt = list(pplstrt.keys())
        for player in pplstrt:
            player = int(player)
            Players.update(
                status="not_played", game=0, role=None,
                voted=None, turn=None, msg_id=None, crazy_role=None).where(Players.player_id == player).execute()
        return
    if len(mfgame.players) >= 12:
        roles_open = "NO"
    else:
        roles_open = mfgame.open_roles
    Mafia.update(status="Night", game_start=datetime.datetime.now(), open_roles=roles_open).where(Mafia.id == mfgame.id).execute()
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    roles_pack = roles.copy()
    del roles_pack[len(mfgame.players):16]
    Mafia.update(used_roles=roles_pack).where(Mafia.id == mfgame.id).execute()
    players = (mfgame.players).copy()
    players = list(players.keys())
    alive_players = []
    for alive_player in players:
        alive_player = int(alive_player)
        alive_players = alive_players + [alive_player]
    Mafia.update(alive_players=alive_players).where(Mafia.id == mfgame.id).execute()
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    mafia_players_dict = {}
    for player in players:
        player = int(player)
        player_role = random.choices(roles_pack)
        player_role = player_role[0]
        roles_pack.remove(player_role)
        if player_role == "crazy":
            crazy_roles = ["baby", "doctor", "police"]
            crazy_role = random.choices(crazy_roles)
            crazy_role = crazy_role[0]
            Players.update(role=player_role, crazy_role=crazy_role).where(Players.player_id == player).execute()
        elif player_role == "mafia":
            mafia_list = mfgame.mafia_list
            if mafia_list == None:
                mafia_list = []
            mafia_list = mafia_list + [player]
            Players.update(role=player_role).where(Players.player_id == player).execute()
            Mafia.update(mafia_list=mafia_list).where(Mafia.id == mfgame.id).execute()
            mfgame = Mafia.get(Mafia.id == mfgame.id)
        else:
            Players.update(role=player_role).where(Players.player_id == player).execute()
        mafia_players_dict[player] = player_role


    Mafia.update(players=mafia_players_dict).where(Mafia.id == mfgame.id).execute()
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    channel = await bot.fetch_channel(MAFIA)
    game_thread = await channel.create_thread(
        name="Игра #{}".format(mfgame.id),
        type=disnake.ChannelType.private_thread,
        invitable=False)
    Mafia.update(game_thread = game_thread.id).where(Mafia.id == mfgame.id).execute()
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    guild = bot.get_guild(servers)
    mafia_chat_object = await guild.fetch_channel(MAFIA)
    chat_object = await mafia_chat_object.fetch_message(mfgame.reg_msg_id)
    embed = disnake.Embed(
        description=f"# МАФИЯ #{mfgame.id}\n## ИГРА ЗАПУЩЕНА - <#{game_thread.id}>\nVoice чат: <#{mafia_room.id}>\n## Игроки:\n{mfgame.players_list}", )
    embed.set_image(
        url=mf_img_logo)

    embed.add_field(name="Участвует:", value=len(mfgame.players), inline=True)
    embed.add_field(name="Минимум:", value=mfgame.min_players, inline=True)
    embed.add_field(name="Максимум:", value=mfgame.max_players, inline=True)
    if mfgame.open_roles == "YES":
        open_roles_embed_txt = "Роли не засекречены"
    elif mfgame.open_roles == "NO":
        open_roles_embed_txt = "Роли засекречены"
    else:
        open_roles_embed_txt = "Ошибка! error_id = 0004"  # fixme 0004
    embed.add_field(name="Настройки:",
                    value=f"Скорость дня: {mfgame.day_mode}\nДлительность ночи: {mfgame.night_duration} секунд\n{open_roles_embed_txt}",
                    inline=False)
    embed.set_default_colour(disnake.Colour.from_rgb(255, 255, 255))
    await chat_object.edit(embed=embed, components=[
        disnake.ui.Button(label="Участвовать", style=disnake.ButtonStyle.success,
                          custom_id="join_cl", disabled=True)])
    for player in players:
        player = int(player)
        await game_thread.add_user(bot.get_user(player))
    for player in players:
        player = int(player)
        user = bot.get_user(player)
        mfgame = Mafia.get(Mafia.id == mfgame.id)
        player_info = Players.get(Players.player_id == player)
        embed = disnake.Embed(
            description=f"# МАФИЯ #{mfgame.id}\n## ЧАТ ИГРЫ - <#{game_thread.id}>\n## Игроки:\n{mfgame.players_list}", )
        embed.add_field(name="Voice чат:", value=f"<#{mafia_room.id}>", inline=False)
        if player_info.role == "doctor":
            embed.add_field(name="Роль:", value="Доктор", inline=False)
            embed.add_field(name="Описание:", value="Обладает способностью лечить жителей города. Каждой ночью доктор пытается угадать, в кого стреляла мафия.\nЕсли доктор угадал и «вылечил» жертву мафии, город просыпается без потерь (или с меньшими потерями).\nДоктор не может исцелять одного и того же игрока две ночи подряд.\nПобеждает если в городе не будет мафии", inline=False)
            embed.set_default_colour(disnake.Colour.green())
            embed.set_image(url=mf_img_doctor)
            await user.send(embed=embed)
        if player_info.role == "detective":
            embed.add_field(name="Роль:", value="Детектив", inline=False)
            embed.add_field(name="Описание:", value=f"Обладает способностью проверить жителей города. Каждой ночью детектив пытается угадать, кто является членом мафии.\nЕсли детектив угадал - 'Мафия обнаружена', если нет - 'Мафия НЕ обнаружена'.\nПобеждает если в городе не будет мафии.", inline=False)
            embed.set_default_colour(disnake.Colour.green())
            embed.set_image(url=mf_img_detective)
            await user.send(embed=embed)
        if player_info.role == "mafia":
            embed.add_field(name="Роль:", value="Мафия", inline=False)
            embed.add_field(name="Описание:", value="Просыпается ночью и выбирает жителя города которого убивает. Если есть другой живой член мафии с большим приоритетом, то ход более низких по рангу мафии не учитывается\nПобеждает если гарантираванно может убить весь город.", inline=False)
            embed.add_field(name="Приоритет:", value=((mfgame.mafia_list).index(player_info.player_id))+1, inline=False)
            embed.set_default_colour(disnake.Colour.red())
            embed.set_image(url=mf_img_mafia)
            await user.send(embed=embed)
        if player_info.role == "people":
            embed.add_field(name="Роль:", value="Мирный житель", inline=False)
            embed.add_field(name="Описание:", value="Мирный житель не просыпается ночью. Побеждает если в городе не осталось мафии", inline=False)
            embed.set_default_colour(disnake.Colour.green())
            embed.set_image(url="mf_img_people")
            await user.send(embed=embed)
        if player_info.role == "baby":
            embed.add_field(name="Роль:", value="Красотка", inline=False)
            embed.add_field(name="Описание:", value="Просыпается ночью и выбирает жителя города, которого 'заберет в гости'. Если его попробует убить мафия, то он выживет, но если мафия убьет красотку, то будет убита и красотка, и ее 'гость'.", inline=False)
            embed.set_default_colour(disnake.Colour.green())
            embed.set_image(url=mf_img_baby)
            await user.send(embed=embed)
        if player_info.role == "police":
            embed.add_field(name="Роль:", value="Полицейский", inline=False)
            embed.add_field(name="Описание:", value="Просыпается ночью и выбирает жителя города, которого будет 'дежурить'. Ход этого игрока отменяется", inline=False)
            embed.set_default_colour(disnake.Colour.green())
            embed.set_image(url=mf_img_police)
            await user.send(embed=embed)
        if player_info.role == "crazy":
            if player_info.crazy_role == "doctor":
                embed.add_field(name="Роль:", value="Доктор", inline=False)
                embed.add_field(name="Описание:", value="Обладает способностью лечить жителей города. Каждой ночью доктор пытается угадать, в кого стреляла мафия.\nЕсли доктор угадал и «вылечил» жертву мафии, город просыпается без потерь (или с меньшими потерями).\nДоктор не может исцелять одного и того же игрока две ночи подряд.\nПобеждает если в городе не будет мафии", inline=False)
                embed.set_default_colour(disnake.Colour.green())
                embed.set_image(
                    url=mf_img_doctor)
                await user.send(embed=embed)
            if player_info.crazy_role == "baby":
                embed.add_field(name="Роль:", value="Красотка", inline=False)
                embed.add_field(name="Описание:", value="Просыпается ночью и выбирает жителя города, которого 'заберет в гости'. Если его попробует убить мафия, то он выживет, но если мафия убьет красотку, то будет убита и красотка, и ее 'гость'.", inline=False)
                embed.set_default_colour(disnake.Colour.green())
                embed.set_image(
                    url=mf_img_baby)
                await user.send(embed=embed)
            if player_info.crazy_role == "police":
                embed.add_field(name="Роль:", value="Полицейский", inline=False)
                embed.add_field(name="Описание:", value="Просыпается ночью и выбирает жителя города, которого будет 'дежурить'. Ход этого игрока отменяется", inline=False)
                embed.set_default_colour(disnake.Colour.green())
                embed.set_image(
                    url=mf_img_police)
                await user.send(embed=embed)
        if player_info.role == "thief":
            embed.add_field(name="Роль:", value="Вор", inline=False)
            embed.add_field(name="Описание:", value="Просыпается ночью и выбирает жителя города, чью роль крадет. Выбранный житель становится мирным жителем.\nЕсли вор попытается украсть роль у мафии, то будет убит.", inline=False)
            embed.set_default_colour(disnake.Colour.green())
            embed.set_image(url=mf_img_thief)
            await user.send(embed=embed)
    await mafia_night(mfgame)
    return

@bot.slash_command(guild_ids=[servers], name='mafia')
async def mafia_create(inter: disnake.ApplicationCommandInteraction,
                       min_players_param=disnake.ext.commands.Param(name='min_players', default=6,
                                                                    description='Минимальное количество игроков',
                                                                    choices=["6", "7", "8", "9", "10", "11", "12", "13",
                                                                             "14", "15",
                                                                             "16"]),
                       max_players_param=disnake.ext.commands.Param(name='max_players', default=16,
                                                                    description='Максимальное количество игроков',
                                                                    choices=["6", "7", "8", "9", "10", "11", "12", "13",
                                                                             "14", "15",
                                                                             "16"]),
                       reg_duration_param=disnake.ext.commands.Param(name='reg_timer', default="45s",
                                                                     description='Длительность регистрации',
                                                                     choices=["45s","2 минуты", "3 минуты", "4 минуты",
                                                                              "5 минут", "7 минут"]),
                       day_mode_param=disnake.ext.commands.Param(name='day_timer', default="Средний",
                                                                 description='Скорость дня',
                                                                 choices=["Очень быстрый", "Быстрый", "Средний",
                                                                          "Длинный",
                                                                          "Очень длинный"]),
                       night_duration_param=disnake.ext.commands.Param(name='night_timer', default="60 секунд",
                                                                       description='Длительность ночи',
                                                                       choices=["30 секунд", "60 секунд", "90 секунд",
                                                                                "120 секунд"]),
                       password_param=commands.Param(name="password", description="Пароль приватной игры (необяз.)",
                                                     default='00000000', max_length=8,
                                                     min_length=8),
                       roles_open_param = disnake.ext.commands.Param(name="open_role", default="NO", description="Раскрывать ли роль после смерти", choices=["NO", "YES"])):
    """Создать игру в мафию"""
    #await inter.response.defer(ephemeral=True)
    check_voice_num = Mafia.get_or_none(Mafia.voice_num == 1)
    if check_voice_num != None:
        check_voice_num = Mafia.get_or_none(Mafia.voice_num == 2)
        if check_voice_num != None:
            check_voice_num = Mafia.get_or_none(Mafia.voice_num == 3)
            if check_voice_num != None:
                await inter.send("## Достигнут максимум одновременных игр(3/3)\n### Попробуй позже", ephemeral=True)
                return
            else:
                check_voice_num = 3
        else:
            check_voice_num = 2
    else:
        check_voice_num = 1
    creator = Players.get_or_none(Players.player_id == inter.author.id)
    if creator is None:
        Players.create(player_id=inter.author.id, status="not_played", win_results=win_count, lose_results=win_count)
    creator = Players.get(Players.player_id == inter.author.id)
    min_players_param = int(min_players_param)
    max_players_param = int(max_players_param)
    if min_players_param > max_players_param:
        await inter.send("Минимальное количество игроков больше максимального!(так нельзя)", ephemeral=True)
        return
    unban_time = creator.unban_time
    if unban_time == None:
        unban_time = datetime.datetime.now() - datetime.timedelta(minutes=360)
    if ((creator.status != "not_played") and (creator.status != "died")) or (unban_time > datetime.datetime.now()):
        if unban_time > datetime.datetime.now():
            await inter.send(
                f"Ты забанен в мафии. Попробуй заново <t:{round((unban_time - year1970).total_seconds())}:R>",
                ephemeral=True)
        elif creator.status == "played":
            await inter.send(
                "Ты уже играешь в мафию, дождись ее окнончания или своей смерти в ней, прежде чем начать новую игру!",
                ephemeral=True)

        return
    Players.update(status='played').where(Players.player_id == inter.author.id).execute()
    if reg_duration_param == "2 минуты":
        reg_duration = 2 * 60
    elif reg_duration_param == "3 минуты":
        reg_duration = 3 * 60
    elif reg_duration_param == "4 минуты":
        reg_duration = 4 * 60
    elif reg_duration_param == "5 минут":
        reg_duration = 5 * 60
    elif reg_duration_param == "7 минут":
        reg_duration = 7 * 60
    elif reg_duration_param == "45s":
        reg_duration = 45
    else:
        await inter.send("Недопустимая длительность регистрации!", ephemeral=True)
        return
    if night_duration_param == "30 секунд":
        night_duration = 30
    elif night_duration_param == "60 секунд":
        night_duration = 60
    elif night_duration_param == "90 секунд":
        night_duration = 90
    elif night_duration_param == "120 секунд":
        night_duration = 120
    else:
        await inter.send("Некорректная длительность ночи!", ephemeral=True)
        return
    password = None
    status = "Registration_open"
    if password_param != "00000000":
        password = password_param
        status = "Registration_private_open"
    if min_players_param >= 12:
        roles_open_param = "NO"
    if check_voice_num == 1:
        mafia_room_id = MAFIA_ROOM_1
    elif check_voice_num == 2:
        mafia_room_id = MAFIA_ROOM_2
    else:
        mafia_room_id = MAFIA_ROOM_3
    mfgame = Mafia.create(
        reg_open=datetime.datetime.now(),
        reg_duration=reg_duration,
        min_players=min_players_param,
        max_players=max_players_param,
        password=password,
        day_mode=day_mode_param,
        night_duration=night_duration,
        game_creator=inter.author.id,
        players={inter.author.id: None},
        admin_key=''.join(random.choices(string.ascii_uppercase + string.digits, k=24)),
        players_list=f"-# <@{inter.author.id}>",
        status=status,
        voice_num=check_voice_num, action_history="", open_roles=roles_open_param, info_history=f"Mafia_room(num={check_voice_num}) - <#{mafia_room_id}>\n")
    audit_chat_object = await bot.fetch_channel(1294809285804691466)
    await audit_chat_object.send(f"# ------------\n## Игра #{mfgame.id}\nADMIN_KEY:```{mfgame.admin_key}```\n# ------------")
    Players.update(game=mfgame.id).where(Players.player_id == inter.author.id).execute()
    embed = disnake.Embed(
            description=f"# МАФИЯ #{mfgame.id}\n## Начало <t:{round(((mfgame.reg_open + datetime.timedelta(seconds=mfgame.reg_duration) - year1970).total_seconds()))}:R>\n## Игроки:\n{mfgame.players_list}",)
    embed.set_image(url=mf_img_logo)
    if mfgame.password != None:
        embed.set_default_colour(disnake.Colour.yellow())
    else:
        embed.set_default_colour(disnake.Colour.green())
    embed.add_field(name="Участвует:", value=len(mfgame.players), inline=True)
    embed.add_field(name="Минимум:", value=mfgame.min_players, inline=True)
    embed.add_field(name="Максимум:", value=mfgame.max_players, inline=True)
    if roles_open_param == "NO":
        roles_open_embed_txt = "Роли засекречены"
    elif roles_open_param == "YES" and max_players_param < 12:
        roles_open_embed_txt = "Роли не засекречены"
    else:
        roles_open_embed_txt = "Роли не засекречены (если меньше 12 игроков)"
    embed.add_field(name="Настройки:", value=f"Скорость дня: {day_mode_param}\nДлительность ночи: {night_duration} секунд\n{roles_open_embed_txt}", inline=False)
    chat_object = await bot.fetch_channel(MAFIA)
    await inter.send("Игра создана!", ephemeral=True)
    if check_voice_num == 1:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_1)
    if check_voice_num == 2:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_2)
    if check_voice_num == 3:
        mafia_room = await bot.fetch_channel(MAFIA_ROOM_3)
    overwrite_voice = disnake.PermissionOverwrite(speak=True, connect=True, view_channel=True)
    guild = bot.get_guild(servers)
    crt_member = guild.get_member(inter.author.id)
    await mafia_room.set_permissions(target=crt_member, overwrite=overwrite_voice)
    if mfgame.password != None:
        reg_msg_id_param = await chat_object.send(embed=embed, components=[
            disnake.ui.Button(label="Участвовать", style=disnake.ButtonStyle.success,
                              custom_id="join_private")])
    else:
        reg_msg_id_param = await chat_object.send(embed=embed, components=[
            disnake.ui.Button(label="Участвовать", style=disnake.ButtonStyle.success,
                              custom_id="join")])
    chat_chat_object = await bot.fetch_channel(CHAT)
    await chat_chat_object.send(f"## Новая игра в мафию!\n## {reg_msg_id_param.jump_url}")
    Mafia.update(reg_msg_id=reg_msg_id_param.id).where(Mafia.id == mfgame.id).execute()

    await asyncio.sleep(mfgame.reg_duration)
    mfgame = Mafia.get(Mafia.id == mfgame.id)
    if (mfgame.status == "Registration_open") or (mfgame.status == "Registration_private_open"):
        Mafia.update(reg_close = datetime.datetime.now()).where(Mafia.id == mfgame.id).execute()
        mfgame = Mafia.get(Mafia.id == mfgame.id)
        await mafia_game(mfgame)
        return



@bot.listen("on_button_click")
async def mafia_create_listen(inter: disnake.MessageInteraction):
    if inter.component.custom_id not in ["join", "join_private", ]:
        return
    mfgame = Mafia.get(Mafia.reg_msg_id == inter.message.id)
    if (inter.component.custom_id == "join") or (inter.component.custom_id == "join_private"):
        if mfgame.status == "Stoped":
            await inter.send("## Эта игра была остановлена!",ephemeral=True)
        if mfgame.status == "Crushed":
            await inter.send("## Эта игра была крашнута!",ephemeral=True)
        member = Players.get_or_none(Players.player_id == inter.author.id)
        if member == None:
            Players.create(player_id=inter.author.id, status="not_played", win_results=win_count, lose_results=win_count)
        member = Players.get(player_id=inter.author.id)
        unban_time = member.unban_time
        if unban_time == None:
            unban_time = datetime.datetime.now() - datetime.timedelta(minutes=360)
        if unban_time > datetime.datetime.now():
            await inter.send(f"## Ты забанен в мафии. Попробуй заново <t:{round((unban_time - year1970).total_seconds())}:R>",ephemeral=True)
            return
        elif (Players.get(Players.player_id == inter.author.id)).game == mfgame.id:
            await inter.send("## Ты уже участвуешь!", ephemeral=True)
            return
        elif (Players.get(Players.player_id == inter.author.id)).status == "played" :
            await inter.send("## Ты уже играешь в мафию, дождись ее окнончания или своей смерти в ней, прежде чем присоединиться к другой игре!", ephemeral=True)
            return
        mfgame = Mafia.get(Mafia.id == mfgame.id)
        if mfgame.reg_close != None:
            await inter.send("## Кнопка уже не доступна! (error_id = 0006)",ephemeral=True) #fixme 0006
            return
        if inter.component.custom_id == "join":
            players = (mfgame.players).copy()
            players[inter.author.id] = None
            Players.update(status='played', game=mfgame.id).where(Players.player_id == inter.author.id).execute()
            Mafia.update(players_list=mfgame.players_list + f"\n-# <@{inter.author.id}>", players=players).where(mfgame).execute()
            guild = bot.get_guild(servers)
            mafia_chat_object = await guild.fetch_channel(MAFIA)
            chat_object = await mafia_chat_object.fetch_message(mfgame.reg_msg_id)
            mfgame = Mafia.get(Mafia.reg_msg_id == inter.message.id)
            embed = disnake.Embed(
                description=f"# МАФИЯ #{mfgame.id}\n## Начало <t:{round(((mfgame.reg_open + datetime.timedelta(seconds=mfgame.reg_duration) - year1970).total_seconds()))}:R>\n## Игроки:\n{mfgame.players_list}")
            embed.set_image(url=mf_img_logo)
            embed.add_field(name="Участвует:", value=len(mfgame.players), inline=True)
            embed.add_field(name="Минимум:", value=mfgame.min_players, inline=True)
            embed.add_field(name="Максимум:", value=mfgame.max_players, inline=True)
            if mfgame.open_roles == "NO":
                open_roles_embed_txt = "Роли засекречены"
            elif mfgame.open_roles == "YES" and mfgame.max_players < 12:
                open_roles_embed_txt = "Роли не засекречены"
            else:
                open_roles_embed_txt = "Роли не засекречены (если меньше 12 игроков)"
            embed.add_field(name="Настройки:",
                            value=f"Скорость дня: {mfgame.day_mode}\nДлительность ночи: {mfgame.night_duration} секунд\n{open_roles_embed_txt}",
                            inline=False)
            await inter.send("## Теперь ты участвуешь!", ephemeral=True)
            if mfgame.max_players > len(mfgame.players):
                embed.set_default_colour(disnake.Colour.green())
                await chat_object.edit(embed=embed, components=[disnake.ui.Button(label="Участвовать", style=disnake.ButtonStyle.success,custom_id="join")])
            else:
                Mafia.update(reg_close=datetime.datetime.now(),game_start=datetime.datetime.now() + datetime.timedelta(seconds=30)).where(mfgame).execute()
                mfgame = Mafia.get(Mafia.id == mfgame.id)
                embed.set_default_colour(disnake.Colour.from_rgb(255, 255, 255))
                await chat_object.edit(embed=embed, components=[
                    disnake.ui.Button(label="Участвовать", disabled=True, style=disnake.ButtonStyle.success,
                                      custom_id="join_private")])


        if inter.component.custom_id == "join_private":
            await inter.response.send_modal(modal=PasswordModal())
