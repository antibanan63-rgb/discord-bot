import discord
from discord.ext import commands
import asyncio
import os
import collections
import aiohttp

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ Error: Token is missing!")
    exit()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.bans = True
intents.webhooks = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

ALLOWED_USER_IDS = [1461150056915796153]

# Tracking dictionaries for security systems
message_history = collections.defaultdict(list)
ban_history = collections.defaultdict(list)
channel_delete_history = collections.defaultdict(list)
role_delete_history = collections.defaultdict(list)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("🔒 System V6 Ultimate Active: Anti-Nuke, Anti-Spam & Security Shields Online! 🛡️")

# ==================== AUTO-ANTIBOT SYSTEM ====================
@bot.event
async def on_member_join(member):
    if member.bot:
        if member.id not in ALLOWED_USER_IDS:
            try:
                await member.ban(reason="Anti-Bot Security: Unauthorized bot entry blocked.")
                print(f"🚨 Banned unauthorized bot automatically: {member.name} ({member.id})")
            except Exception as e:
                print(f"❌ Failed to ban bot {member.name}: {e}")

# ==================== ANTI-WEBHOOK SYSTEM ====================
@bot.event
async def on_webhooks_update(channel):
    try:
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            await webhook.delete(reason="Anti-Webhook Security: Unauthorized webhook creation blocked.")
            print(f"🚨 Deleted unauthorized webhook in channel: {channel.name}")
    except Exception as e:
        print(f"❌ Failed to delete webhook: {e}")

# ==================== ANTI-MASS BAN SYSTEM ====================
@bot.event
async def on_member_ban(guild, user):
    try:
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            moderator = entry.user
            if moderator.id in ALLOWED_USER_IDS or moderator.bot:
                return

            current_time = asyncio.get_event_loop().time()
            ban_history[moderator.id] = [t for t in ban_history[moderator.id] if current_time - t < 5.0]
            ban_history[moderator.id].append(current_time)

            if len(ban_history[moderator.id]) >= 3:
                try:
                    await guild.ban(moderator, reason="Anti-Nuke Security: Mass banning detected!")
                    print(f"🚨 Anti-Nuke Triggered: Banned mass-banner {moderator.name}")
                except Exception as e:
                    print(f"❌ Failed to ban mass-banner: {e}")
    except Exception as e:
        pass

# ==================== ANTI-MASS CHANNEL DELETE SYSTEM ====================
@bot.event
async def on_guild_channel_delete(channel):
    try:
        guild = channel.guild
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            moderator = entry.user
            if moderator.id in ALLOWED_USER_IDS or moderator.bot:
                return

            current_time = asyncio.get_event_loop().time()
            channel_delete_history[moderator.id] = [t for t in channel_delete_history[moderator.id] if current_time - t < 5.0]
            channel_delete_history[moderator.id].append(current_time)

            if len(channel_delete_history[moderator.id]) >= 2:
                try:
                    await guild.ban(moderator, reason="Anti-Nuke Security: Mass channel deletion detected!")
                except Exception as e:
                    pass
    except Exception as e:
        pass

# ==================== ANTI-MASS ROLE DELETE SYSTEM ====================
@bot.event
async def on_guild_role_delete(role):
    try:
        guild = role.guild
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            moderator = entry.user
            if moderator.id in ALLOWED_USER_IDS or moderator.bot:
                return

            current_time = asyncio.get_event_loop().time()
            role_delete_history[moderator.id] = [t for t in role_delete_history[moderator.id] if current_time - t < 5.0]
            role_delete_history[moderator.id].append(current_time)

            if len(role_delete_history[moderator.id]) >= 2:
                try:
                    await guild.ban(moderator, reason="Anti-Nuke Security: Mass role deletion detected!")
                except Exception as e:
                    pass
    except Exception as e:
        pass

# ==================== ANTI-SPAM SYSTEM ====================
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        await bot.process_commands(message)
        return

    if message.author.id in ALLOWED_USER_IDS or message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return

    author_id = message.author.id
    current_time = asyncio.get_event_loop().time()

    message_history[author_id] = [t for t in message_history[author_id] if current_time - t < 3.0]
    message_history[author_id].append(current_time)

    if len(message_history[author_id]) >= 5:
        try:
            await message.channel.purge(limit=6, check=lambda m: m.author.id == author_id)
            await message.guild.ban(message.author, reason="Anti-Spam Security: Sponging / Spamming detected.")
            warning_msg = await message.channel.send(f"🚨 **Anti-Spam Triggered:** {message.author.mention} was automatically **banned** for spamming!")
            await asyncio.sleep(5)
            await warning_msg.delete()
            del message_history[author_id]
            return
        except Exception as e:
            pass

    await bot.process_commands(message)

# ==================== COMMAND CENTER PANEL ====================
@bot.command(name="commands")
async def custom_commands(ctx):
    embed = discord.Embed(
        title="⚡ ROOT CONTROL // SYSTEM V6",
        description="> **Welcome to the ultimate system panel.** Total server security & dominance activated.",
        color=discord.Color.from_rgb(138, 43, 226)
    )
    
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
    
    embed.add_field(
        name="🛠️ **GENERAL & UTILITY**",
        value="```yaml\n!commands, !ping, !avatar, !serveravatar, !roleinfo, !embed, !poll, !membercount, !clear, !serverinfo, !userinfo, !gift, !webhook\n```",
        inline=False
    )
    
    embed.add_field(
        name="🛡️ **MODERATION & SECURITY**",
        value="```yaml\n!ban, !unban, !kick, !warn, !giverole, !lock, !unlock, !lockdown, !slowmode, !ka, !anti-on, !deleteall\n```",
        inline=False
    )
    
    embed.set_footer(
        text=f"Requested by {ctx.author.name} | Security Active 🟢", 
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None
    )
    
    await ctx.send(embed=embed)

# ==================== OWNER-LOCKED SECURITY CHECK COMMAND ====================
@bot.command(name="anti-on")
async def anti_on_status(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.send("❌ **Access Denied:** Owner permission required for this command.")
        return

    embed = discord.Embed(
        title="🛡️ SECURITY SYSTEMS STATUS",
        description="Here is the current operational status of the server defense shields:",
        color=discord.Color.green()
    )
    embed.add_field(name="🤖 Anti-Bot Shield", value="🟢 **ACTIVE**\n> Automatically bans unauthorized bots.", inline=False)
    embed.add_field(name="🔗 Anti-Webhook Shield", value="🟢 **ACTIVE**\n> Automatically deletes malicious webhooks.", inline=False)
    embed.add_field(name="⚡ Anti-Spam Shield", value="🟢 **ACTIVE**\n> Automatically bans rapid spammers.", inline=False)
    embed.add_field(name="🚨 Anti-Mass Ban Shield", value="🟢 **ACTIVE**\n> Bans members mass-banning users.", inline=False)
    embed.add_field(name="🧹 Anti-Mass Delete Shield", value="🟢 **ACTIVE**\n> Bans members mass-deleting channels/roles.", inline=False)
    
    embed.set_footer(text=f"Checked by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
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

@bot.command(name="gift")
async def gift_command(ctx, member: discord.Member = None):
    target = member or ctx.author
    gift_gif = "https://cdn.discordapp.com/attachments/1543690530582691850/1543694170491719752/1f825152819d7f3576c3dfbf1c810cbe.gif?ex=6a97c6fa&is=6a96757a&hm=e315f42a1f335c3fef18b245c162a2f1d29c65f2fa43000d4f82322b3d407ca4&"
    embed = discord.Embed(
        title="🎁 SPECIAL GIFT RECEIVED!",
        description=f"A special package has been delivered to {target.mention}!",
        color=discord.Color.from_rgb(255, 105, 180)
    )
    embed.set_image(url=gift_gif)
    await ctx.send(embed=embed)

# ==================== WEBHOOK COMMAND ====================
@bot.command(name="webhook")
@commands.has_permissions(administrator=True)
async def send_webhook(ctx, url: str, *, message: str):
    await ctx.message.delete()
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(url, session=session)
        try:
            await webhook.send(content=message, username="Root Control System", avatar_url=bot.user.avatar.url if bot.user.avatar else None)
            await ctx.send("✅ Webhook message sent successfully!", delete_after=5)
        except Exception as e:
            await ctx.send(f"❌ Failed to send webhook: `{e}`", delete_after=5)

# ==================== MODERATION & SECURITY COMMANDS ====================
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    ban_gif = "https://cdn.discordapp.com/attachments/1543270990962753576/1544243621107212308/8a36885c2659fed6316e5645c7b4afae.gif?ex=6a97cc71&is=6a967af1&hm=9761a8180d9fdb5df3247d6d35b12207e04c80766e360d846fe800ca66fdfb3c&"
    embed = discord.Embed(
        title="🔨 USER TERMINATED (BANNED)",
        description=f"**User:** {member.mention}\n**Reason:** `{reason}`\n**Moderator:** {ctx.author.mention}",
        color=discord.Color.red()
    )
    embed.set_image(url=ban_gif)
    await ctx.send(embed=embed)

@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban_member(ctx, user_id: int):
    try:
        user = discord.Object(id=user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"🔓 Unbanned user ID **{user_id}** successfully.")
    except discord.NotFound:
        await ctx.send("❌ User not found in ban list or invalid ID.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: `{e}`")

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
async def kick_all_voice(ctx):
    if not ctx.author.voice or not ctx.author.voice.channel:
        embed_err = discord.Embed(
            title="❌ ERROR",
            description="You must be in a voice channel to use this command!",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed_err)
        return
        
    channel = ctx.author.voice.channel
    member_count = len(channel.members)
    
    ka_gif = "https://cdn.discordapp.com/attachments/1543270990962753576/1544253396675203102/1f825152819d7f3576c3dfbf1c810cbe.gif?ex=6a97d58c&is=6a96840c&hm=7d42ff83542aeb38a1ef030e6698301b9c0b88f7bfcd3f89e1577ec093fe5f7e&"
    
    embed = discord.Embed(
        title="👢 VOICE CHANNEL EVACUATED",
        description=f"**Channel:** `{channel.name}`\n**Evacuated Members:** `{member_count}`\n**Executor:** {ctx.author.mention}",
        color=discord.Color.from_rgb(138, 43, 226)
    )
    embed.set_image(url=ka_gif)
    await ctx.send(embed=embed)
    
    for member in channel.members:
        await member.move_to(None)

@bot.command(name="deleteall")
async def delete_all_protocol(ctx):
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.send("❌ **Access Denied:** Owner permission required for this protocol.")
        return
    await ctx.send("⚠️ **Absolute Server Protocol Initiated...** (Safety safeguard: channels protected)")

bot.run(TOKEN)
