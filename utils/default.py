import time
import discord
import traceback
from io import BytesIO
from datetime import timedelta

def traceback_maker(err, advance: bool = True) -> str:
    """A way to debug your code anywhere"""
    _traceback = "".join(traceback.format_tb(err.__traceback__))
    error = f"```py\n{_traceback}{type(err).__name__}: {err}\n```"
    return error if advance else f"{type(err).__name__}: {err}"


def timetext(name) -> str:
    """Timestamp, but in text form"""
    return f"{name}_{int(time.time())}.txt"


def date(
    target, clock: bool = True,
    ago: bool = False, only_ago: bool = False
) -> str:
    """Converts a timestamp to a Discord timestamp format"""
    if isinstance(target, (float,int)):
        unix = int(target)
    else:
        unix = int(time.mktime(target.timetuple()))
    timestamp = f"<t:{unix}:{'f' if clock else 'D'}>"
    if ago:
        timestamp += f" (<t:{unix}:R>)"
    if only_ago:
        timestamp = f"<t:{unix}:R>"
    return timestamp


def responsible(target: discord.Member, reason: str) -> str:
    """Default responsible maker targeted to find user in AuditLogs"""
    responsible = f"[ {target} ]"
    if not reason:
        return f"{responsible} no reason given..."
    return f"{responsible} {reason}"


def actionmessage(case: str, mass: bool = False) -> str:
    """Default way to present action confirmation in chat"""
    output = f"**{case}** the user"

    if mass:
        output = f"**{case}** the IDs/Users"

    return f"✅ Successfully {output}"


async def pretty_results(
    ctx, filename: str = "Results",
    resultmsg: str = "Here's the results:", loop: list = None
) -> None:
    """A prettier way to show loop results"""
    if not loop:
        return await ctx.send("The result was empty...")

    pretty = "\r\n".join([f"[{str(num).zfill(2)}] {data}" for num, data in enumerate(loop, start=1)])

    if len(loop) < 15:
        return await ctx.send(f"{resultmsg}```ini\n{pretty}```")

    data = BytesIO(pretty.encode('utf-8'))
    await ctx.send(
        content=resultmsg,
        file=discord.File(
            data,
            filename=timetext(filename.title())
        )
    )

def format_time(duration: timedelta) -> str:
    total_seconds = int(duration.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0:
        parts.append(f"{seconds}s")
    
    formatted_duration = ' '.join(parts)
    return formatted_duration