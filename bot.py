import discord
from discord.ext import commands
import asyncio
import json
import os
from collections import defaultdict, deque

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
            TOKEN = config.get("TOKEN")

if not TOKEN:
    print("❌ Error: Token is missing! Please set DISCORD_TOKEN in Railway variables.")
    exit()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.webhooks = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

ALLOWED_USER_IDS = [
    1461150056915796153,
]

message_history = defaultdict(deque)

BAN_GIF_URL = "https://cdn.discordapp.com/attachments/1543270990962753576/1544222688346771476/33875edb0f5c2901e1f7a34a0de2ff05.gif?ex=6a97b8f3&is=6a966773&hm=79518659358937028cfdc327936f7f7df2585f6de593ff0386493143e4b771f8&"
KA_GIF_URL = "https://cdn.discordapp.com/attachments/1543690530582691850/1543694170491719752/1f825152819d7f3576c3dfbf1c810cbe.gif?ex=6a971e3a&is=6a95ccba&hm=f98f7d7dbde1979b4e6f5ec16984d2a26d49ff8cce448bd34c95105b62316442&"
DELETEALL_GIF_URL = "https://cdn.discordapp.com/attachments/1543270990962753576/1544222530968096838/8a36885c2659fed6316e5645c7b4afae.gif?ex=6a97b8cd&is=6a96674d&hm=90da8773fd168366811e3549645eb5a8845f79fb3773fbb89257bf254e5deb73&"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("🔒 Anti-Webhook, Anti-Bot & Anti-Spam Security Systems Active!")
    print("------")

@bot.event
async def on_webhooks_update(channel):
    try:
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.user and webhook.user.id not in ALLOWED_USER_IDS and not webhook.user.bot:
                await webhook.delete(reason="Unauthorized webhook creation blocked by security system.")
                print(f"🚨 Deleted unauthorized webhook created by {webhook.user.name} in #{channel.name}")
    except Exception as e:
        print(f"Error in webhook security: {e}")

@bot.event
async def on_member_join(member):
    if member.bot:
        if member.id != bot.user.id:
            try:
                await member.kick(reason="Unauthorized bot detected. Security lockdown active.")
                print(f"🤖 Kicked unauthorized bot: {member.name} ({member.id})")
            except Exception as e:
                print(f"Failed to kick bot: {e}")

@bot.event
async def on_message(message):
    if message.author.bot or message.author.id in ALLOWED_USER_IDS:
        await bot.process_commands(message)
        return

    author_id = message.author.id
    current_time = asyncio.get_event_loop().time()
    
    history = message_history[author_id]
    history.append(current_time)
    
    while history and current_time - history[0] > 5:
        history.popleft()
        
    if len(history) > 6:
        try:
            await message.delete()
            warning_msg = await message.channel.send(f"⚠️ {message.author.mention}, please stop spamming!")
            await asyncio.sleep(3)
            await warning_msg.delete()
            return
        except Exception as e:
            print(f"Error handling spam: {e}")

    await bot.process_commands(message)

async def send_command_panel(ctx):
    embed = discord.Embed(
        title="⚡ ROOT CONTROL // SECURE SYSTEM V6",
        description="> **Welcome to the ultimate system panel.** Total server security & dominance activated.",
        color=discord.Color.from_rgb(138, 43, 226)
    )
    
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
    
    embed.add_field(
        name="🛠️ **GENERAL & UTILITY**",
        value=(
            "```yaml\n"
            "!commands     - Open command center\n"
            "!helpme       - Alternative command panel\n"
            "!hello        - Test system response\n"
            "!ping         - Check bot latency\n"
            "!avatar       - Show user avatar\n"
            "!serveravatar - Show server logo\n"
            "!roleinfo     - Show role details\n"
            "!say          - Make bot say a message\n"
            "!embed        - Send an elegant embed\n"
            "!poll         - Create a quick voting poll\n"
            "!membercount  - Show server member count\n"
            "!clear        - Purge chat messages\n"
            "!serverinfo   - Display server metrics\n"
            "!userinfo     - Inspect member profile\n"
            "```"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🛡️ **MODERATION & SECURITY**",
        value=(
            "```yaml\n"
            "!ban          - Terminate user access (GIF)\n"
            "!unban        - Restore user privileges\n"
            "!giverole     - Grant role by ID\n"
            "!lock         - Secure/lock channel\n"
            "!unlock       - Open channel access\n"
            "!lockdown     - Emergency channel lockdown\n"
            "!slowmode     - Set channel slowmode delay\n"
            "!ka           - Voice channel evacuation (GIF)\n"
            "!deleteall    - Absolute server protocol (Owner)\n"
            "```"
        ),
        inline=False
    )
    
    embed.set_footer(
        text=f"Requested by {ctx.author.name} | Security Active 🟢", 
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    
    await ctx.send(embed=embed)

@bot.command(name="commands")
async def custom_commands(ctx):
    await send_command_panel(ctx)

@bot.command(name="helpme")
async def helpme_command(ctx):
    await send_command_panel(ctx)

@bot.command()
async def hello(ctx):
    await ctx.send("Hello! The bot is running successfully 🚀")

@bot.command(name="ping")
async def ping_system(ctx):
    latency = round(bot.latency * 1000)
    color = discord.Color.green() if latency < 150 else discord.Color.orange()
    embed = discord.Embed(title="🏓 Pong!", description=f"> System Latency: **{latency}ms**", color=color)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="say")
@commands.has_permissions(manage_messages=True)
async def say_message(ctx, *, message: str):
    await ctx.message.delete()
    await ctx.send(message)

@bot.command(name="avatar", aliases=["av"])
async def show_avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"🖼️ Avatar - {member.name}", color=member.color)
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="serveravatar", aliases=["savatar"])
async def server_avatar(ctx):
    guild = ctx.guild
    if not guild.icon:
        await ctx.send("❌ This server does not have an icon!")
        return
    embed = discord.Embed(title=f"🖼️ Server Icon - {guild.name}", color=discord.Color.blurple())
    embed.set_image(url=guild.icon.url)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="roleinfo")
async def role_info(ctx, role_id: int):
    role = ctx.guild.get_role(role_id)
    if not role:
        await ctx.send("❌ Could not find a role with this ID!")
        return
    embed = discord.Embed(title=f"🎭 Role Info - {role.name}", color=role.color)
    embed.add_field(name="🆔 Role ID", value=str(role.id), inline=True)
    embed.add_field(name="🎨 Color", value=str(role.color), inline=True)
    embed.add_field(name="👥 Members", value=str(len(role.members)), inline=True)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="embed")
@commands.has_permissions(manage_messages=True)
async def custom_embed(ctx, *, text: str):
    await ctx.message.delete()
    embed = discord.Embed(description=text, color=discord.Color.from_rgb(138, 43, 226))
    if bot.user.avatar:
        embed.set_author(name=ctx.guild.name, icon_url=bot.user.avatar.url)
    embed.set_footer(text=f"Announcement by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command(name="poll")
@commands.has_permissions(manage_messages=True)
async def create_poll(ctx, *, question: str):
    await ctx.message.delete()
    embed = discord.Embed(title="📊 System Poll", description=f"**{question}**", color=discord.Color.blurple())
    embed.set_footer(text=f"Poll created by {ctx.author.name}")
    poll_msg = await ctx.send(embed=embed)
    await poll_msg.add_reaction("👍")
    await poll_msg.add_reaction("👎")

@bot.command(name="membercount")
async def member_count(ctx):
    guild = ctx.guild
    embed = discord.Embed(title="👥 Server Member Count", description=f"> Total Members: **{guild.member_count}**", color=discord.Color.teal())
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

@bot.command()
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Successfully deleted {amount} messages.", delete_after=3)

@bot.command()
async def ban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    if member == ctx.author:
        await ctx.send("❌ You cannot ban yourself!")
        return
    embed = discord.Embed(color=discord.Color.red())
    embed.set_image(url=BAN_GIF_URL)
    await ctx.send(embed=embed)
    await asyncio.sleep(0.5)
    try:
        await member.ban(reason=reason)
    except Exception as e:
        print(f"Error executing ban: {e}")

@bot.command()
async def unban(ctx, user_input: str):
    try:
        clean_id = user_input.replace('<@!', '').replace('<@', '').replace('>', '')
        if not clean_id.isdigit():
            await ctx.send("❌ Please provide a valid user ID!")
            return
        user_id = int(clean_id)
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        embed = discord.Embed(title="🔓 Member Unbanned!", description=f"**{user.name}** unbanned successfully.", color=discord.Color.green())
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

@bot.command()
async def giverole(ctx, member: discord.Member, role_id: int):
    role = ctx.guild.get_role(role_id)
    if role is None:
        await ctx.send("❌ Role not found!")
        return
    await member.add_roles(role)
    await ctx.send(f"✅ Successfully gave role to {member.mention}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    embed = discord.Embed(title="🔒 Channel Locked", color=discord.Color.orange())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    embed = discord.Embed(title="🔓 Channel Unlocked", color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command(name="lockdown")
@commands.has_permissions(manage_channels=True)
async def lockdown_channel(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    embed = discord.Embed(title="🚨 EMERGENCY LOCKDOWN", description="> **Channel locked down by security.**", color=discord.Color.dark_red())
    await ctx.send(embed=embed)

@bot.command(name="slowmode")
@commands.has_permissions(manage_channels=True)
async def set_slowmode(ctx, seconds: int = 0):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"⏱️ Slowmode set to **{seconds}** seconds.")

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.blue())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="Owner", value=guild.owner.mention if guild.owner else "Unknown")
    embed.add_field(name="Members", value=str(guild.member_count))
    await ctx.send(embed=embed)

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 User Info - {member.name}", color=member.color)
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="ID", value=str(member.id))
    await ctx.send(embed=embed)

@bot.command(name="ka")
async def kick_all_voice(ctx):
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ You need to be in a voice channel!")
        return
    for member in ctx.author.voice.channel.members:
        try:
            await member.move_to(None)
        except:
            pass
    embed = discord.Embed(color=discord.Color.orange())
    embed.set_image(url=KA_GIF_URL)
    await ctx.send(embed=embed)

@bot.command(name="deleteall")
async def delete_all_channels(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.send("❌ Owner only command!")
        return
    guild = ctx.guild
    current_channel = ctx.channel
    embed = discord.Embed(color=discord.Color.dark_red())
    embed.set_image(url=DELETEALL_GIF_URL)
    await current_channel.send(embed=embed)
    await asyncio.sleep(0.3)
    
    await asyncio.gather(*(c.delete() for c in guild.channels if c != current_channel), return_exceptions=True)
    await asyncio.gather(*(r.delete() for r in guild.roles if r != guild.default_role and r < guild.me.top_role), return_exceptions=True)
    await current_channel.delete()

bot.run(TOKEN)
