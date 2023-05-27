import asyncpg

from utils.config import Config

config = Config.from_env()

db_host = config.postgres_host
db_name = config.postgres_database
db_user = config.postgres_user
db_password = config.postgres_password

async def create_tables():
    conn = await asyncpg.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

    await conn.execute('''
        CREATE TABLE IF NOT EXISTS logging (
            guild_id BIGINT PRIMARY KEY,
            channel_id BIGINT,
            log_deleted_messages BOOLEAN,
            log_edited_messages BOOLEAN,
            log_nickname_changes BOOLEAN,
            log_member_join_leave BOOLEAN,
            log_member_kick BOOLEAN,
            log_member_ban_unban BOOLEAN
        )
    ''')
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS dailycat (
            guild_id BIGINT PRIMARY KEY,
            channel_id BIGINT,
            post_time TEXT
        )
    ''')
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS reaction_roles (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            message_id BIGINT NOT NULL,
            emoji TEXT NOT NULL,
            role_id BIGINT NOT NULL,
            UNIQUE (guild_id, message_id, emoji)
    );
    
    ''')
    await conn.execute(''' 
        CREATE TABLE IF NOT EXISTS timezones (
            user_id BIGINT PRIMARY KEY,
            timezone TEXT NOT NULL
        )
    ''')
    await conn.execute(''' 
        CREATE TABLE IF NOT EXISTS mod_role_id (
            guild_id BIGINT PRIMARY KEY,
            role_id BIGINT NOT NULL
            )
        ''')
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS birthdays (
            guild_id BIGINT NOT NULL,
            user_id BIGINT NOT NULL,
            date DATE NOT NULL,
            PRIMARY KEY (guild_id, user_id)
            )
        ''')
    await conn.execute ('''
    CREATE TABLE IF NOT EXISTS birthday_channels(
        guild_id BIGINT PRIMARY KEY,
        channel_id BIGINT NOT NULL 
            )
        ''')
    await conn.close()


async def populate_tables(bot):
    conn = await asyncpg.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

    for guild in bot.guilds:
        await conn.execute('INSERT INTO logging (guild_id) VALUES ($1) ON CONFLICT DO NOTHING', guild.id)
        await conn.execute('INSERT INTO dailycat (guild_id) VALUES ($1) ON CONFLICT DO NOTHING', guild.id)

    await conn.close()

    