CREATE TABLE IF NOT EXISTS leveling (
    guild_id BIGINT,
    user_id BIGINT,
    xp BIGINT,
    PRIMARY KEY (guild_id, user_id)
);

UPDATE schema_version set version = 2;