import psycopg2
import utils.default

from utils.config import Config

config = Config.from_env()

db_host = config.db_host
db_name = config.db_name
db_user = config.db_user
db_password = config.db_password



def init_db(bot):
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

    for guild in bot.guilds:
        c.execute('INSERT INTO logging (guild_id) VALUES (%s) ON CONFLICT DO NOTHING', (guild.id,))
        c.execute('INSERT INTO dailycat (guild_id) VALUES (%s) ON CONFLICT DO NOTHING', (guild.id,))

    conn.commit()
    conn.close()