import discord
from discord.ext import commands
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ Error: Token is missing!")
    exit()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

ALLOWED_USER_IDS = [1461150056915796153]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("🔒 System V6 Active & All Advanced Security Commands Loaded!")

# ==================== COMMAND CENTER PANEL ====================
@bot.command(name="commands")
async def custom_commands(ctx):
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
            "!ping         - Check bot latency\n"
            "!avatar       - Show user avatar\n"
            "!serveravatar - Show server logo\n"
            "!roleinfo     - Show role details\n"
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
            "!ban          - Terminate user (GIF)\n"
            "!unban        - Restore user privileges\n"
            "!kick         - Kick member from server\n"
            "!warn         - Issue a formal warning\n"
            "!giverole     - Grant role by ID\n"
            "!lock         - Secure/lock channel\n"
            "!unlock       - Open channel access\n"
            "!lockdown     - Emergency channel lockdown\n"
            "!slowmode     - Set channel slowmode\n"
            "!ka           - Voice channel evacuation\n"
            "!deleteall    - Absolute server protocol\n"
            "```"
        ),
        inline=False
    )
    
    embed.set_footer(
        text=f"Requested by {ctx.author.name} | Security Active 🟢", 
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    
    await ctx.send(embed=embed)

# ==================== GENERAL & UTILITY COMMANDS ====================
@bot.command(name="ping")
async def ping_system(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: **{latency}ms**")

@bot.command(name="avatar")
async def user_avatar(ctx, member: discord.Member = None):
    target = member or ctx.author
    embed = discord.Embed(title=f"🖼️ {target.name}'s Avatar", color=discord.Color.purple())
    if target.avatar:
        embed.set_image(url=target.avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="serveravatar")
async def server_avatar(ctx):
    if not ctx.guild.icon:
        await ctx.send("❌ No server icon!")
        return
    embed = discord.Embed(title=f"🖼️ {ctx.guild.name} Icon", color=discord.Color.blurple())
    embed.set_image(url=ctx.guild.icon.url)
    await ctx.send(embed=embed)

@bot.command(name="roleinfo")
async def role_info(ctx, role: discord.Role):
    embed = discord.Embed(title=f"📌 Role: {role.name}", color=role.color)
    embed.add_field(name="ID", value=role.id, inline=True)
    embed.add_field(name="Members", value=len(role.members), inline=True)
    embed.add_field(name="Color", value=str(role.color), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="embed")
async def send_embed(ctx, title: str, *, message: str):
    await ctx.message.delete()
    embed = discord.Embed(title=title, description=message, color=discord.Color.purple())
    await ctx.send(embed=embed)

@bot.command(name="poll")
async def create_poll(ctx, *, question: str):
    await ctx.message.delete()
    embed = discord.Embed(title="📊 SYSTEM POLL", description=question, color=discord.Color.dark_purple())
    poll_msg = await ctx.send(embed=embed)
    await poll_msg.add_reaction("👍")
    await poll_msg.add_reaction("👎")

@bot.command(name="membercount")
async def member_count(ctx):
    await ctx.send(f"👥 Total Members in **{ctx.guild.name}**: `{ctx.guild.member_count}`")

@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🧹 Successfully cleared `{amount}` messages!")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command(name="serverinfo")
async def server_info(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 {guild.name} Information", color=discord.Color.dark_purple())
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 Owner", value=guild.owner, inline=True)
    embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
    embed.add_field(name="📅 Created On", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    await ctx.send(embed=embed)

@bot.command(name="userinfo")
async def user_info(ctx, member: discord.Member = None):
    target = member or ctx.author
    embed = discord.Embed(title=f"👤 User Info: {target.name}", color=target.color)
    if target.avatar:
        embed.set_thumbnail(url=target.avatar.url)
    embed.add_field(name="ID", value=target.id, inline=True)
    embed.add_field(name="Joined Server", value=target.joined_at.strftime("%Y-%m-%d") if target.joined_at else "Unknown", inline=True)
    embed.add_field(name="Account Created", value=target.created_at.strftime("%Y-%m-%d"), inline=True)
    await ctx.send(embed=embed)

# ==================== MODERATION & SECURITY COMMANDS ====================
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"🔨 Banned **{member.name}** | Reason: `{reason}`\nhttps://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif")

@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban_member(ctx, *, user_name):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = user_name.split('#') if '#' in user_name else (user_name, None)
    for ban_entry in banned_users:
        user = ban_entry.user
        if user.name == member_name:
            await ctx.guild.unban(user)
            await ctx.send(f"🔓 Unbanned **{user.name}** successfully.")
            return
    await ctx.send("❌ User not found in ban list.")

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick_member(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"👢 Kicked **{member.name}** | Reason: `{reason}`")

@bot.command(name="warn")
@commands.has_permissions(kick_members=True)
async def warn_member(ctx, member: discord.Member, *, reason="No reason provided"):
    embed = discord.Embed(
        title="⚠️ SYSTEM WARNING",
        description=f"**Member:** {member.mention}\n**Moderator:** {ctx.author.mention}\n**Reason:** `{reason}`",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)
    try:
        await member.send(f"⚠️ You have been warned in **{ctx.guild.name}** for: `{reason}`")
    except discord.Forbidden:
        pass

@bot.command(name="giverole")
@commands.has_permissions(manage_roles=True)
async def give_role(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"✅ Added role **{role.name}** to **{member.name}**.")

@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def lock_channel(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Channel has been locked successfully.")

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def unlock_channel(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Channel has been unlocked.")

@bot.command(name="lockdown")
@commands.has_permissions(administrator=True)
async def lockdown_server(ctx):
    for channel in ctx.guild.text_channels:
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🚨 **EMERGENCY LOCKDOWN ACTIVATED:** All text channels have been locked!")

@bot.command(name="slowmode")
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int = 0):
    await ctx.channel.edit(slowmode_delay=seconds)
    if seconds == 0:
        await ctx.send("⚡ Slowmode has been **disabled**.")
    else:
        await ctx.send(f"⏳ Slowmode set to **{seconds}** seconds.")

@bot.command(name="ka")
@commands.has_permissions(move_members=True)
async def kick_all_voice(ctx):
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ You must be in a voice channel!")
        return
    channel = ctx.author.voice.channel
    for member in channel.members:
        await member.move_to(None)
    await ctx.send(f"👢 Evacuated all members from voice channel: **{channel.name}**")

@bot.command(name="deleteall")
async def delete_all_protocol(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.send("❌ **Access Denied:** Owner permission required for this protocol.")
        return
    await ctx.send("⚠️ **Absolute Server Protocol Initiated...** (Safety safeguard: channels protected)")

bot.run(TOKEN)
