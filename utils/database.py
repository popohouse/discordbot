import sqlite3


def init_db(bot):
    conn = sqlite3.connect('data/MeowMix.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS logging (
            guild_id INTEGER PRIMARY KEY,
            channel_id INTEGER,
            log_deleted_messages BOOLEAN,
            log_edited_messages BOOLEAN,
            log_nickname_changes BOOLEAN,
            log_member_join_leave BOOLEAN,
            log_member_kick BOOLEAN,
            log_member_ban_unban BOOLEAN
        )
    ''')
    
    for guild in bot.guilds:
        c.execute('INSERT OR IGNORE INTO logging (guild_id) VALUES (?)', (guild.id,))

    conn.commit()
    conn.close()