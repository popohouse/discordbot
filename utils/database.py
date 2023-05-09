import psycopg2

from utils.config import Config

config = Config.from_env()

db_host = config.db_host
db_name = config.db_name
db_user = config.db_user
db_password = config.db_password

def create_tables():
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    c = conn.cursor()

    c.execute('''
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
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS dailycat (
            guild_id BIGINT PRIMARY KEY,
            channel_id BIGINT,
            post_time TEXT
        )
    ''')

    conn.commit()
    conn.close()


def populate_tables(bot):
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    c = conn.cursor()

    for guild in bot.guilds:
        c.execute('INSERT INTO logging (guild_id) VALUES (%s) ON CONFLICT DO NOTHING', (guild.id,))
        c.execute('INSERT INTO dailycat (guild_id) VALUES (%s) ON CONFLICT DO NOTHING', (guild.id,))

    conn.commit()
    conn.close()

def removed_while_offline(bot):
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    c = conn.cursor()
    # Get a list of guild IDs from the database
    c.execute('SELECT guild_id FROM logging')
    db_guild_ids = [row[0] for row in c.fetchall()]
    # Get a list of guild IDs that the bot is currently a member of
    bot_guild_ids = [guild.id for guild in bot.guilds]
    # Find guild IDs that are in the database but not in the bot's current guilds
    removed_guild_ids = set(db_guild_ids) - set(bot_guild_ids)
    # Delete data for removed guilds
    for guild_id in removed_guild_ids:
        c.execute('DELETE FROM logging WHERE guild_id = %s', (guild_id,))
        c.execute('DELETE FROM dailycat WHERE guild_id = %s', (guild_id,))
    
    conn.commit()
    conn.close()



async def on_guild_remove(guild):
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    c = conn.cursor()

    c.execute('DELETE FROM logging WHERE guild_id = %s', (guild.id,))
    c.execute('DELETE FROM dailycat WHERE guild_id = %s', (guild.id,))

    conn.commit()
    conn.close()

async def on_guild_join(guild):
    conn = psycopg2.connect(
        host=db_host,
        database=db_name,
        user=db_user,
        password=db_password
    )
    c = conn.cursor()

    c.execute('INSERT INTO logging (guild_id) VALUES (%s) ON CONFLICT DO NOTHING', (guild.id,))
    c.execute('INSERT INTO dailycat (guild_id) VALUES (%s) ON CONFLICT DO NOTHING', (guild.id,))

    conn.commit()
    conn.close()

    