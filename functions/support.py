from init import bot, Users, Tickets
import disnake
from variables import *
from disnake import TextInputStyle


support_cooldown = {}


class SupportModal(disnake.ui.Modal):
    def __init__(self):
        # Детали модального окна и его компонентов
        components = [
            disnake.ui.TextInput(
                label="Обращение",
                placeholder="",
                custom_id="ticket",
                style=TextInputStyle.paragraph,
                min_length=12,
                max_length=3750
            ),
        ]
        super().__init__(
            title="Создание обращения",
            custom_id="create_ticket",
            components=components,
        )

    # Обработка ответа, после отправки модального окна
    async def callback(self, inter: disnake.ModalInteraction):
        channel = await bot.fetch_channel(ADM_PUBLIC)
        support_ticket = await channel.create_thread(
            name="Обращение {}".format(inter.author.global_name),
            type=disnake.ChannelType.private_thread,
            invitable=False
        )
        Users.update(support_cooldown=datetime.datetime.now()).where(Users.discord_id == inter.author.id).execute()
        await support_ticket.add_user(inter.author)
        await inter.send('Обращение создано -<#{}>'.format(support_ticket.id), ephemeral=True)
        embed = disnake.Embed(timestamp=datetime.datetime.now(),
                              description="# ОБРАЩЕНИЕ: \n \n" + inter.data.components[0]["components"][0]["value"],
                              color=disnake.Colour.green())
        embed.add_field(name="Создатель обращения", value=f"<@{inter.author.id}>", inline=False)
        start_msg = await support_ticket.send(embed=embed, components=[
            disnake.ui.Button(label="Закрыть обращение", style=disnake.ButtonStyle.red,
                              custom_id="close_support_ticket")])
        Tickets.create(
            thread=support_ticket.id, creator=inter.author.id, status="Open", create_date=datetime.datetime.now(),
            start_msg=start_msg.id)
        await support_ticket.send(f"-# <@&{POLICE}>, <@&{ADMIN}>")


@bot.slash_command(description='Отправляет сообщение для приема обращений', guild_ids=[servers])
async def support(inter):
    support_open = open("documents/support.txt", "r", encoding="utf-8")
    support_text = support_open.read()
    await inter.send(
        support_text,
        components=[disnake.ui.Button(label="Создать обращение", style=disnake.ButtonStyle.success,
                                      custom_id="create_support_ticket")])


@bot.listen("on_button_click")
async def support_listen(inter: disnake.MessageInteraction):
    if inter.component.custom_id not in ["create_support_ticket", "close_support_ticket", ]:
        return
    if inter.component.custom_id == "create_support_ticket":
        people = Users.get_or_none(discord_id=inter.author.id)
        if people is None:
            people = Users.create(discord_id=inter.author.id)
        if (people.support_cooldown is None) or (people.support_cooldown + datetime.timedelta(minutes=45) < datetime.datetime.now()):
            await inter.response.send_modal(modal=SupportModal())
        else:
            cooldown = people.support_cooldown + datetime.timedelta(minutes=45)
            await inter.send(
                f"Ты недавно уже создавал обращение в поддержку. Следующее можно будет только через <t:{round((cooldown - year1970).total_seconds())}:R>",
                ephemeral=True)
    if inter.component.custom_id == "close_support_ticket":
        guild = bot.get_guild(servers)
        people = guild.get_member(inter.author.id)
        people_in_table = Users.get_or_none(discord_id=inter.author.id)
        ticket_in_table = Tickets.get(start_msg=inter.message.id)
        if people_in_table == None:
            Users.create(discord_id=inter.author.id)
        if ((guild.get_role(OWNER)) in people.roles) or (inter.author.id == ticket_in_table.creator):
            thread = inter.channel
            await inter.send(f'# ОБРАЩЕНИЕ БЫЛО ЗАКРЫТО\n-# Закрыто: <@{inter.author.id}>')
            Tickets.update(status="Close").where(Tickets.start_msg == inter.message.id).execute()
            await thread.edit(locked=True, archived=True)
        else:
            await inter.send(f"Закрыть обращение может только <@&{OWNER}> и создатель обращения", ephemeral=True)
