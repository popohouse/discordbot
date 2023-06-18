from dataclasses import dataclass
from dotenv import dotenv_values


@dataclass
class Config:
    """This class is used to store the bot's configuration.
    You can load it from a dictionary or from a .env file (recommended).
    By default in this Discord bot template, we use from_env classmethod.
    """
    discord_token: str
    discord_prefix: str
    discord_owner_id: int
    discord_join_message: str

    postgres_host: str
    postgres_database: str
    postgres_user: str
    postgres_password: str

    poe_token: str

    kutt_token: str
    kutt_host: str

    @classmethod
    def from_dict(self, **kwargs) -> "Config":
        """Create a Config object from a dictionary."""
        kwargs_overwrite = {}

        for k, v in kwargs.items():
            new_key = k.lower()

            if v.isdigit():
                kwargs_overwrite[new_key] = int(v)
            else:
                kwargs_overwrite[new_key] = v

        return Config(**kwargs_overwrite)

    @classmethod
    def from_env(self, filename: str = ".env") -> "Config":
        """Create a Config object from a .env file."""
        return Config.from_dict(**dotenv_values(filename))