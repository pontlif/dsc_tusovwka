import disnake
from peewee import *
from disnake.ext import commands
from playhouse.sqlite_ext import JSONField

###################################################################################
###################################################################################
###################################################################################

intents = disnake.Intents.all()
intents.members = True  # Включение намерений для работы с членами сервера
intents.messages = True  # Если нужен доступ к сообщениям
intents.guilds = True    # Для работы с серверами
intents.guild_messages = True  # Для доступа к сообщениям в каналах
bot = commands.Bot("!", sync_commands_debug=True, intents=intents)
db = SqliteDatabase('svr.db')


class SERVERMODEL(Model):
    class Meta:
        database = db


class Users(SERVERMODEL):
    """Таблица пользователей."""
    id = AutoField(primary_key=True)  # Автоинкрементный ID
    discord_id = IntegerField(null=True)  # Discord ID пользователя
    support_cooldown = DateTimeField(null=True)  # Время последного обращения в поддержку
    report_cooldown = DateTimeField(null=True)  # Время последней жалобы

    def warns(self):
        """Полученные предупреждения."""
        return Warns.select().where(Warns.user == self)

    def tickets(self):
        """Созданные обращения."""
        return Tickets.select().where(Tickets.creator == self)


class Warns(SERVERMODEL):
    """Таблица предупреждений."""
    id = AutoField(primary_key=True)  # Автоинкрементный ID
    moderator = ForeignKeyField(Users, backref='issued_warns', on_delete='CASCADE')  # Кто выдал предупреждение
    user = ForeignKeyField(Users, backref='received_warns', on_delete='CASCADE')  # Кому выдано предупреждение
    reason = TextField()  # Причина предупреждения
    create_date = DateTimeField()  # Дата и время выдачи


class Tickets(SERVERMODEL):
    """Таблица обращений."""
    id = AutoField(primary_key=True)  # Автоинкрементный ID
    creator = ForeignKeyField(Users, backref='created_tickets', on_delete='CASCADE')  # Кто создал обращение
    create_date = DateTimeField()  # Дата и время создания обращения
    status = TextField()  # Статус обращения (например, 'open', 'closed')
    start_msg = IntegerField()  # Содержание обращения
    thread = IntegerField()  # ID ветки обращения


Tickets.create_table()
Users.create_table()
Warns.create_table()


###################################################################################
###################################################################################
###################################################################################


mfdb = SqliteDatabase('mafia.db')


class BaseModel(Model):
    class Meta:
        database = mfdb


class Mafia(BaseModel):
    id = AutoField()

    # регистрация
    reg_open = DateTimeField()
    reg_duration = IntegerField()  # in seconds
    reg_close = DateTimeField(null=True)  # после reg_duration или если набрались люди
    min_players = IntegerField()
    max_players = IntegerField()
    password = TextField(null=True)  # for private games

    game_start = DateTimeField(null=True)
    game_finish = DateTimeField(null=True)

    # настройки времени этапов
    day_mode = TextField()  # day_duration and vote_duration progress mode, user defined
    day_duration = IntegerField(null=True)  # in seconds
    night_duration = IntegerField()  # in seconds, user defined
    vote_duration = IntegerField(null=True)  # in seconds

    # игроки и роли
    game_creator = IntegerField()  # discord id
    used_roles = JSONField(null=True)  # [role_name]
    players = JSONField()  # [discord_id : role_name]
    dead_players = JSONField(null=True)  # [discord_id]
    alive_players = JSONField(null=True)  # [discord_id]
    mafia_list = JSONField(null=True)  # [discord_id]
    # current day
    voted_already = JSONField(null=True)  # [discord_id]

    # прочее
    admin_key = TextField()  # key/token for admin access to game settings
    players_list = TextField()  # str for registration embed
    reg_msg_id = IntegerField(null=True)
    mf_msg_id = IntegerField(null=True)  # discord id (int)
    status = TextField() # game stage
    action_history = TextField(null=True)  # action list
    crush_status = TextField(null=True, default="Crush me")  # param for crushed def
    game_thread = IntegerField(null=True)  # Game thread id
    night_count = IntegerField(default=0)  # Счетчик ночей
    day_count = IntegerField(default=0)  # Счетчик дней
    voice_num = IntegerField()  # счетчик потоков
    open_roles = TextField(null=True, default="NO")
    info_history = TextField(null=True) # info of real voice_num + 'id = <@id>'


class Players(BaseModel):
    player_id = IntegerField()
    status = TextField()
    role = TextField(null=True)
    game = IntegerField(null=True)
    voted = IntegerField(null=True, default=0) # за кого проголосовал
    crazy_role = TextField(null=True)
    msg_id = IntegerField(null=True)
    turn = IntegerField(null=True)
    turn_check = TextField(null=True)
    rating = IntegerField(default=350)
    win_results = JSONField(null=True)
    lose_results = JSONField(null=True)
    unban_time = DateTimeField(null=True)


Mafia.create_table()
Players.create_table()
