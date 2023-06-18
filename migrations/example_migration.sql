-- Example script for database migration when bot is updated, used as base for new migrations scripts

--- Naming scheme of files should be as follows `migrate_002.sql` would be script responsible for migrating from version 1 to 2



CREATE TABLE IF NOT EXISTS PlaceHolderTable (
    guild_id BIGINT PRIMARY KEY,
    channel_id BIGINT,
    user_id BIGINT
);

-- Update the 'schema_version' relevant version
UPDATE schema_version SET version = 2;