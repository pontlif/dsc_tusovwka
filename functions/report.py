from init import bot, Users
from variables import ADM_REPORTS, servers, year1970
import disnake
from disnake import TextInputStyle, TextInput
from disnake.ext import commands
# from disnake.ext.commands import
import datetime


class ReportModal(disnake.ui.Modal):
    def __init__(self, user: disnake.Member):
        self.user = user  # Сохраняем пользователя как атрибут модального окна
        components = [
            disnake.ui.TextInput(
                label="Жалоба",
                placeholder="Подробно опиши нарушение, рекомендуем сослаться на пункт(ы)",
                custom_id="complaint",
                style=disnake.TextInputStyle.paragraph,
                min_length=12,
                max_length=3750
            ),
        ]
        super().__init__(
            title=f"Пожаловаться на {user.display_name}",
            custom_id="report",
            components=components,
        )

    # Обработка ответа, после отправки модального окна
    async def callback(self, inter: disnake.ModalInteraction):
        channel = await bot.fetch_channel(ADM_REPORTS)
        complaint = inter.text_values["complaint"]

        await channel.send(
            f"# НОВАЯ ЖАЛОБА[!](https://goo.su/diuFu/)\n"
            f"**-------------------------------------**\n"
            f"{complaint}\n\n"
            f"**-------------------------------------**\n"
            f"**Поступила от: <@{inter.author.id}> **\n"
            f"**Обвиняемый: <@{self.user.id}> **\n"
            f"**-------------------------------------**\n"
            f"/warn - выдать предупреждение\n"
            f"/mute - выдать мьют\n"
            f"/ban - выдать бан\n"
        )
        Users.update(report_cooldown=datetime.datetime.now()).where(Users.discord_id == inter.author.id).execute()
        await inter.send('## Жалоба отправлена', ephemeral=True)


@bot.slash_command(description='Пожаловать на пользователя', guild_ids=[servers], name="report")
async def report(inter, user: disnake.Member = commands.Param(description="Выбери пользователя, на которого хотите пожаловаться")):
    people = Users.get_or_none(discord_id=inter.author.id)
    if user.id == inter.author.id:
        await inter.send(
            f"## Пожаловаться на себя нельзя. <:a_focus:1257120519875072091>",
            ephemeral=True)
        return
    if user.bot:
        await inter.send(
            f"## Пожаловаться на бота нельзя. <:a_focus:1257120519875072091>",
            ephemeral=True)
        return
    if people is None:
        people = Users.create(discord_id=inter.author.id)
    if (people.report_cooldown is None) or (people.report_cooldown + datetime.timedelta(minutes=45) < datetime.datetime.now()):
        await inter.response.send_modal(modal=ReportModal(user))
    else:
        cooldown = people.report_cooldown + datetime.timedelta(minutes=45)
        await inter.send(
            f"### Ты недавно уже писал жалобу. Следующую можно будет только через <t:{round((cooldown - year1970).total_seconds())}:R>",
            ephemeral=True)