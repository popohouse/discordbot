from utils.config import Config

config = Config.from_env()


async def create_tables(bot):
    async with bot.pool.acquire() as conn:
        # Define current version of schema here
        expected_version = 1
        schema_version_exists = await conn.fetchval('''
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_name = 'schema_version'
            )
        ''')
        if not schema_version_exists:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS logging (
                    guild_id BIGINT PRIMARY KEY,
                    channel_id BIGINT,
                    log_deleted_messages BOOLEAN,
                    log_edited_messages BOOLEAN,
                    log_nickname_changes BOOLEAN,
                    log_member_join_leave BOOLEAN,
                    log_member_kick BOOLEAN,
                    log_member_ban_unban BOOLEAN,
                    log_automod_actions BOOLEAN,
                    log_role_user_update BOOLEAN,
                    log_user_vc_update BOOLEAN,
                    log_user_vc_action BOOLEAN,
                    log_onboarding_accept BOOLEAN,
                    log_role_update BOOLEAN,
                    log_channel_update BOOLEAN,
                    log_expression_update BOOLEAN,
                    log_invite_update BOOLEAN,
                    log_server_update BOOLEAN,
                    modlogchannel_id BIGINT
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
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS birthday_extras(
                guild_id BIGINT PRIMARY KEY,
                channel_id BIGINT,
                role_id BIGINT
                    )
                ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS auto_responses(
                id SERIAL PRIMARY KEY,
                guild_id BIGINT NOT NULL,
                triggers TEXT[] NOT NULL,
                response TEXT NOT NULL,
                ping BOOLEAN,
                deletemsg BOOLEAN,
                selfdelete INT,
                ignoreroles BIGINT[],
                UNIQUE (guild_id, triggers, response)
                    )
                ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS stickyposts(
                id SERIAL PRIMARY KEY,
                guild_id BIGINT NOT NULL,
                channel_id BIGINT NOT NULL,
                stickypost TEXT,
                message_id BIGINT,
                UNIQUE (guild_id, channel_id)
                    )
                ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS warnings(
                id SERIAL PRIMARY KEY,
                guild_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                mod_id BIGINT NOT NULL,
                reason TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                UNIQUE (guild_id, user_id, reason, timestamp)
                    )
                ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS notes(
                id SERIAL PRIMARY KEY,
                guild_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                mod_id BIGINT NOT NULL,
                note TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                UNIQUE (guild_id, user_id, note, timestamp)
                    )
                ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS reportchannel(
                guild_id BIGINT PRIMARY KEY,
                channel_id BIGINT NOT NULL,
                role_id BIGINT
                    )
                ''')
            await conn.execute('''CREATE TABLE schema_version (version INT NOT NULL)''')
            await conn.execute('INSERT INTO schema_version (version) VALUES ($1)', expected_version)
        else:
            stored_version = await conn.fetchval('SELECT version FROM schema_version')
            if stored_version == expected_version:
                return
            if stored_version < expected_version:
                # Please actually add here, and remove the return statement simply here as place holder currently
                # Also have it work through migrations in case of multiple schema updates
                return
            # Hey future me please add better error handling in case of users having issues with schema updates.
            raise ValueError('Invalid schema version detected')


async def populate_tables(bot):
    async with bot.pool.acquire() as conn:
        for guild in bot.guilds:
            await conn.execute('INSERT INTO logging (guild_id) VALUES ($1) ON CONFLICT DO NOTHING', guild.id)
            await conn.execute('INSERT INTO dailycat (guild_id) VALUES ($1) ON CONFLICT DO NOTHING', guild.id)