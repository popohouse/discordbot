import asyncpg

from utils.config import Config

config = Config.from_env()

db_host = config.postgres_host
db_name = config.postgres_name
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

async def removed_while_offline(bot):
    conn = await asyncpg.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

    # Get a list of guild IDs from the database
    rows = await conn.fetch('SELECT guild_id FROM logging')
    db_guild_ids = [row['guild_id'] for row in rows]
    # Get a list of guild IDs that the bot is currently a member of
    bot_guild_ids = [guild.id for guild in bot.guilds]
    # Find guild IDs that are in the database but not in the bot's current guilds
    removed_guild_ids = set(db_guild_ids) - set(bot_guild_ids)
    # Delete data for removed guilds
    for guild_id in removed_guild_ids:
        await conn.execute('DELETE FROM logging WHERE guild_id = $1', guild_id)
        await conn.execute('DELETE FROM dailycat WHERE guild_id = $1', guild_id)
    

    await conn.close()



async def on_guild_remove(guild):
    conn = await asyncpg.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )


    await conn.execute('DELETE FROM logging WHERE guild_id = $1', guild.id)
    await conn.execute('DELETE FROM dailycat WHERE guild_id = $1', guild.id)

    await conn.close()

async def on_guild_join(guild):
    conn = await asyncpg.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )

    await conn.execute('INSERT INTO logging (guild_id) VALUES ($1) ON CONFLICT DO NOTHING', guild.id)
    await conn.execute('INSERT INTO dailycat (guild_id) VALUES ($1) ON CONFLICT DO NOTHING', guild.id)

    await conn.close()

    