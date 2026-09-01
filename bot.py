import discord
from discord.ext import commands
import asyncio
import json
import os
from collections import defaultdict, deque

# Get Token safely from Railway Environment Variables, or fallback to config.json if local
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
            TOKEN = config.get("TOKEN")

if not TOKEN:
    print("❌ Error: Token is missing! Please set DISCORD_TOKEN in Railway variables.")
    exit()

# Bot Configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.webhooks = True # مهم جداً لمراقبة الـ Webhooks

bot = commands.Bot(command_prefix="!", intents=intents)

# Remove the default help command to avoid conflicts
bot.remove_command('help')

# Your User ID allowed to use sensitive commands / bypass security
ALLOWED_USER_IDS = [
    1461150056915796153,
]

# Anti-Spam Storage Dictionary
message_history = defaultdict(deque)

# --------------------------------------------------
# GIFs Configuration (Embed Image URLs)
# --------------------------------------------------
BAN_GIF_URL = "https://cdn.discordapp.com/attachments/1543270990962753576/1544222688346771476/33875edb0f5c2901e1f7a34a0de2ff05.gif?ex=6a97b8f3&is=6a966773&hm=79518659358937028cfdc327936f7f7df2585f6de593ff0386493143e4b771f8&"
KA_GIF_URL = "https://cdn.discordapp.com/attachments/1543690530582691850/1543694170491719752/1f825152819d7f3576c3dfbf1c810cbe.gif?ex=6a971e3a&is=6a95ccba&hm=f98f7d7dbde1979b4e6f5ec16984d2a26d49ff8cce448bd34c95105b62316442&"
DELETEALL_GIF_URL = "https://cdn.discordapp.com/attachments/1543270990962753576/1544222530968096838/8a36885c2659fed6316e5645c7b4afae.gif?ex=6a97b8cd&is=6a96674d&hm=90da8773fd168366811e3549645eb5a8845f79fb3773fbb89257bf254e5deb73&"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("🔒 Anti-Webhook, Anti-Bot & Anti-Spam Security Systems Active!")
    print("------")

# --------------------------------------------------
# 🛡️ SECURITY SYSTEM: Anti-Webhook Creation
# --------------------------------------------------
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

# --------------------------------------------------
# 🛡️ SECURITY SYSTEM: Anti-Unauthorized Bots
# --------------------------------------------------
@bot.event
async def on_member_join(member):
    if member.bot:
        if member.id != bot.user.id:
            try:
                await member.kick(reason="Unauthorized bot detected. Security lockdown active.")
                print(f"🤖 Kicked unauthorized bot: {member.name} ({member.id})")
            except Exception as e:
                print(f"Failed to kick bot: {e}")

# --------------------------------------------------
# 🛡️ SECURITY SYSTEM: Anti-Spam & Rate Limiting
# --------------------------------------------------
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

# --------------------------------------------------
# 1. Commands Menu (!commands & !helpme)
# --------------------------------------------------
async def send_command_panel(ctx):
    embed = discord.Embed(
        title="⚡ ROOT CONTROL // SECURE SYSTEM V5",
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

# --------------------------------------------------
# 2. Hello / Test Command (!hello)
# --------------------------------------------------
@bot.command()
async def hello(ctx):
    """Simple command to check if the bot is working"""
    await ctx.send("Hello! The bot is running successfully 🚀")

# --------------------------------------------------
# 3. Ping Command (!ping)
# --------------------------------------------------
@bot.command(name="ping")
async def ping_system(ctx):
    """Checks the bot's latency"""
    latency = round(bot.latency * 1000)
    color = discord.Color.green() if latency < 150 else discord.Color.orange()
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"> System Latency: **{latency}ms**",
        color=color
    )
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

# --------------------------------------------------
# 4. Say Command (!say)
# --------------------------------------------------
@bot.command(name="say")
@commands.has_permissions(manage_messages=True)
async def say_message(ctx, *, message: str):
    """Makes the bot say a message (Moderators only)"""
    await ctx.message.delete()
    await ctx.send(message)

@say_message.error
async def say_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please provide a message! Example: `!say Hello guys`")

# --------------------------------------------------
# 5. Avatar Command (!avatar)
# --------------------------------------------------
@bot.command(name="avatar", aliases=["av"])
async def show_avatar(ctx, member: discord.Member = None):
    """Displays a user's avatar in high resolution"""
    member = member or ctx.author
    embed = discord.Embed(
        title=f"🖼️ Avatar - {member.name}",
        color=member.color
    )
    embed.set_image(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

# --------------------------------------------------
# 6. Server Avatar Command (!serveravatar)
# --------------------------------------------------
@bot.command(name="serveravatar", aliases=["savatar"])
async def server_avatar(ctx):
    """Displays the server's icon in high resolution"""
    guild = ctx.guild
    if not guild.icon:
        await ctx.send("❌ This server does not have an icon!")
        return

    embed = discord.Embed(
        title=f"🖼️ Server Icon - {guild.name}",
        color=discord.Color.blurple()
    )
    embed.set_image(url=guild.icon.url)
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

# --------------------------------------------------
# 7. Role Info Command (!roleinfo)
# --------------------------------------------------
@bot.command(name="roleinfo")
async def role_info(ctx, role_id: int):
    """Displays detailed information about a role using its ID"""
    role = ctx.guild.get_role(role_id)
    if not role:
        await ctx.send("❌ Could not find a role with this ID!")
        return

    embed = discord.Embed(
        title=f"🎭 Role Info - {role.name}",
        color=role.color
    )
    embed.add_field(name="🆔 Role ID", value=str(role.id), inline=True)
    embed.add_field(name="🎨 Color", value=str(role.color), inline=True)
    embed.add_field(name="👥 Members with Role", value=str(len(role.members)), inline=True)
    embed.add_field(name="📌 Position", value=str(role.position), inline=True)
    embed.add_field(name="🔒 Mentionable", value=str(role.mentionable), inline=True)
    embed.add_field(name="📅 Created On", value=role.created_at.strftime("%Y-%m-%d"), inline=True)
    
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

# --------------------------------------------------
# 8. Custom Embed Maker (!embed)
# --------------------------------------------------
@bot.command(name="embed")
@commands.has_permissions(manage_messages=True)
async def custom_embed(ctx, *, text: str):
    """Makes the bot send an elegant custom embed message"""
    await ctx.message.delete()
    embed = discord.Embed(
        description=text,
        color=discord.Color.from_rgb(138, 43, 226)
    )
    if bot.user.avatar:
        embed.set_author(name=ctx.guild.name, icon_url=bot.user.avatar.url)
    embed.set_footer(text=f"Announcement by {ctx.author.name}")
    await ctx.send(embed=embed)

@custom_embed.error
async def embed_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please provide text for the embed! Example: `!embed Hello everyone!`")

# --------------------------------------------------
# 9. Poll Command (!poll)
# --------------------------------------------------
@bot.command(name="poll")
@commands.has_permissions(manage_messages=True)
async def create_poll(ctx, *, question: str):
    """Creates a quick voting poll with reactions"""
    await ctx.message.delete()
    embed = discord.Embed(
        title="📊 System Poll",
        description=f"**{question}**",
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Poll created by {ctx.author.name}")
    poll_msg = await ctx.send(embed=embed)
    await poll_msg.add_reaction("👍")
    await poll_msg.add_reaction("👎")

@create_poll.error
async def poll_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to create polls!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please provide a question! Example: `!poll Are you ready?`")

# --------------------------------------------------
# 10. Member Count Command (!membercount)
# --------------------------------------------------
@bot.command(name="membercount")
async def member_count(ctx):
    """Displays the total number of members in the server"""
    guild = ctx.guild
    embed = discord.Embed(
        title="👥 Server Member Count",
        description=f"> Total Members in **{guild.name}**: **{guild.member_count}**",
        color=discord.Color.teal()
    )
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

# --------------------------------------------------
# 11. Clear Messages Command (!clear)
# --------------------------------------------------
@bot.command()
async def clear(ctx, amount: int = 5):
    """Deletes a specific number of messages"""
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Successfully deleted {amount} messages.", delete_after=3)

# --------------------------------------------------
# 12. Ban Command (!ban)
# --------------------------------------------------
@bot.command()
async def ban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    """Bans a member and sends its specific GIF via Embed"""
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

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please specify a member to ban! Example: `!ban @user reason`")

# --------------------------------------------------
# 13. Unban Command (!unban)
# --------------------------------------------------
@bot.command()
async def unban(ctx, user_input: str):
    """Unbans a member using either their Mention (@user) or User ID"""
    try:
        clean_id = user_input.replace('<@!', '').replace('<@', '').replace('>', '')
        
        if not clean_id.isdigit():
            await ctx.send("❌ Please provide a valid user mention or User ID! Example: `!unban @user`")
            return

        user_id = int(clean_id)
        user = await bot.fetch_user(user_id)
        
        await ctx.guild.unban(user)
        
        embed = discord.Embed(
            title="🔓 Member Unbanned!",
            description=f"**{user.name}** (`{user.id}`) has been unbanned successfully.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Action by {ctx.author.name}")
        await ctx.send(embed=embed)
        
    except discord.NotFound:
        await ctx.send("❌ Could not find a user with this ID or they are not banned!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

# --------------------------------------------------
# 14. Give Role by ID Command (!giverole)
# --------------------------------------------------
@bot.command()
async def giverole(ctx, member: discord.Member, role_id: int):
    """Gives a role to a member using the Role ID"""
    role = ctx.guild.get_role(role_id)
    if role is None:
        await ctx.send("❌ Could not find a role with this ID!")
        return
    if role >= ctx.me.top_role:
        await ctx.send("❌ This role is higher than or equal to the bot's highest role!")
        return
    await member.add_roles(role)
    await ctx.send(f"✅ Successfully gave the {role.mention} role to {member.mention}")

# --------------------------------------------------
# 15. Lock Channel Command (!lock)
# --------------------------------------------------
@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    """Locks the current channel so members cannot send messages"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    embed = discord.Embed(
        title="🔒 Channel Locked",
        description="This channel has been locked by a moderator.",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed)

@lock.error
async def lock_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")

# --------------------------------------------------
# 16. Unlock Channel Command (!unlock)
# --------------------------------------------------
@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    """Unlocks the current channel"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    embed = discord.Embed(
        title="🔓 Channel Unlocked",
        description="This channel has been unlocked.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@unlock.error
async def unlock_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")

# --------------------------------------------------
# 17. Lockdown Channel Command (!lockdown)
# --------------------------------------------------
@bot.command(name="lockdown")
@commands.has_permissions(manage_channels=True)
async def lockdown_channel(ctx):
    """Activates emergency lockdown on the current channel"""
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    embed = discord.Embed(
        title="🚨 EMERGENCY LOCKDOWN",
        description="> **This channel has been locked down by security protocol.** Please wait for further instructions from moderators.",
        color=discord.Color.dark_red()
    )
    embed.set_footer(text=f"Action by {ctx.author.name}")
    await ctx.send(embed=embed)

@lockdown_channel.error
async def lockdown_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use lockdown!")

# --------------------------------------------------
# 18. Slowmode Command (!slowmode)
# --------------------------------------------------
@bot.command(name="slowmode")
@commands.has_permissions(manage_channels=True)
async def set_slowmode(ctx, seconds: int = 0):
    """Sets the slowmode delay for the current channel"""
    await ctx.channel.edit(slowmode_delay=seconds)
    if seconds == 0:
        await ctx.send("⏱️ Slowmode has been disabled.")
    else:
        await ctx.send(f"⏱️ Slowmode set to **{seconds}** seconds.")

@set_slowmode.error
async def slowmode_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to change slowmode!")

# --------------------------------------------------
# 19. Server Info Command (!serverinfo)
# --------------------------------------------------
@bot.command()
async def serverinfo(ctx):
    """Displays detailed information about the server"""
    guild = ctx.guild
    embed = discord.Embed(
        title=f"📊 {guild.name} - Server Information",
        color=discord.Color.blue()
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
    embed.add_field(name="👥 Members", value=str(guild.member_count), inline=True)
    embed.add_field(name="🆔 Server ID", value=str(guild.id), inline=True)
    embed.add_field(name="💬 Channels", value=str(len(guild.channels)), inline=True)
    embed.add_field(name="🎭 Roles", value=str(len(guild.roles)), inline=True)
    embed.add_field(name="📅 Created On", value=guild.created_at.strftime("%Y-%m-%d %H:%M"), inline=True)
    
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

# --------------------------------------------------
# 20. User Info Command (!userinfo)
# --------------------------------------------------
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    """Displays information about a user"""
    member = member or ctx.author
    embed = discord.Embed(
        title=f"👤 User Info - {member.name}",
        color=member.color
    )
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
        
    embed.add_field(name="🆔 User ID", value=str(member.id), inline=True)
    embed.add_field(name="🏷️ Nickname", value=member.nick or "None", inline=True)
    embed.add_field(name="📅 Joined Discord", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="📥 Joined Server", value=member.joined_at.strftime("%Y-%m-%d") if member.joined_at else "Unknown", inline=True)
    
    roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
    roles_str = ", ".join(roles) if roles else "None"
    embed.add_field(name=f"🎭 Roles ({len(roles)})", value=roles_str, inline=False)
    
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

# --------------------------------------------------
# 21. Kick All from Voice Channel (!ka)
# --------------------------------------------------
@bot.command(name="ka")
async def kick_all_voice(ctx):
    """Kicks all members from voice channel and sends its specific GIF via Embed"""
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ You need to be in a voice channel first!")
        return

    channel = ctx.author.voice.channel

    for member in channel.members:
        try:
            await member.move_to(None)
        except Exception as e:
            print(f"Error kicking member from voice: {e}")
            
    embed = discord.Embed(color=discord.Color.orange())
    embed.set_image(url=KA_GIF_URL)
    await ctx.send(embed=embed)

# --------------------------------------------------
# 22. Ultra-Fast Delete All (!deleteall)
# --------------------------------------------------
@bot.command(name="deleteall")
async def delete_all_channels(ctx):
    """Lightning-fast server wipe using concurrent execution (Owner only)"""
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.send("❌ Sorry, this command is restricted to the bot owner only!")
        return

    guild = ctx.guild
    current_channel = ctx.channel
    
    embed = discord.Embed(color=discord.Color.dark_red())
    embed.set_image(url=DELETEALL_GIF_URL)
    await current_channel.send(embed=embed)
    
    await asyncio.sleep(0.3)

    # 1. Delete all channels and categories concurrently (except current channel)
    channel_tasks = [channel.delete() for channel in guild.channels if channel != current_channel]
    await asyncio.gather(*channel_tasks, return_exceptions=True)

    # 2. Delete all roles concurrently
    role_tasks = [role.delete() for role in guild.roles if role != guild.default_role and role < guild.me.top_role]
    await asyncio.gather(*role_tasks, return_exceptions=True)

    # 3. Kick all members concurrently
    member_tasks = [
        member.kick(reason="Lightning-fast server wipe via !deleteall")
        for member in guild.members
        if member != guild.me and member != guild.owner and member.id not in ALLOWED_USER_IDS
    ]
    await asyncio.gather(*member_tasks, return_exceptions=True)

    # 4. Finally, delete the current channel itself
    try:
        await current_channel.delete()
    except Exception as e:
        print(f"Error deleting current channel: {e}")

# --------------------------------------------------
# Run the Bot
# --------------------------------------------------
bot.run(TOKEN)
