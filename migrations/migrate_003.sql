CREATE TABLE IF NOT EXISTS leveling (
    guild_id BIGINT,
    role_id BIGINT,
    levelreq BIGINT,
    PRIMARY KEY (guild_id, role_id, levelreq)
);

UPDATE schema_version set version = 3;