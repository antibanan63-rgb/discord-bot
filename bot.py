import discord
from discord.ext import commands
import asyncio
import json
import os

# Load configuration from config.json
if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        config = json.load(f)
        TOKEN = config.get("TOKEN")
else:
    print("❌ Error: config.json file not found! Please create it.")
    exit()

# Bot Configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Remove the default help command to avoid conflicts
bot.remove_command('help')

# Your User ID allowed to use the !deleteall command
ALLOWED_USER_IDS = [
    1461150056915796153,
]

# --------------------------------------------------
# GIFs Configuration (Each command has its own GIF)
# --------------------------------------------------
BAN_GIF_URL = "https://cdn.discordapp.com/attachments/1543690530582691850/1543693424815771748/33875edb0f5c2901e1f7a34a0de2ff05.gif?ex=6a95cc08&is=6a947a88&hm=424e9dd7a9a08ec6cf6842b1ec841bfd851e275eaa53135df1dc3ac8916bdebf&"
KA_GIF_URL = "https://cdn.discordapp.com/attachments/1543690530582691850/1543694170491719752/1f825152819d7f3576c3dfbf1c810cbe.gif?ex=6a95ccba&is=6a947b3a&hm=3758448e150114fa094d2b019ddf5dde5a7be517c597554cbb91440637e98658&"
DELETEALL_GIF_URL = "https://cdn.discordapp.com/attachments/1543690503348813934/1543707506751180873/8a36885c2659fed6316e5645c7b4afae.gif?ex=6a95d926&is=6a9487a6&hm=c99e5d2712d54feae9a2f724cd2ff432d490d389ead1a1cb0908edc12a8f3d07&"

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")

# --------------------------------------------------
# 1. Commands Menu (!commands)
# --------------------------------------------------
@bot.command(name="commands")
async def custom_commands(ctx):
    """Displays the list of all available bot commands cleanly"""
    embed = discord.Embed(
        title="🤖 Bot Control Panel",
        description="Here is the complete list of available commands and how to use them:",
        color=discord.Color.from_rgb(0, 162, 255)
    )
    
    embed.add_field(
        name="🛠️ General & Utility",
        value=(
            "`!commands` - Displays this menu.\n"
            "`!hello` - Tests if the bot is responsive.\n"
            "`!clear <amount>` - Deletes a specific number of messages."
        ),
        inline=False
    )
    
    embed.add_field(
        name="🛡️ Moderation & Server",
        value=(
            "`!ban <@user> [reason]` - Bans a member with its specific GIF.\n"
            "`!unban <@user_or_id>` - Unbans a member using mention or ID.\n"
            "`!giverole <@user> <role_id>` - Assigns a role using its ID.\n"
            "`!ka` - Kicks everyone from VC with its specific GIF.\n"
            "`!deleteall` - Ultra-fast server wipe (Owner only)."
        ),
        inline=False
    )
    
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
    
    await ctx.send(embed=embed)

# --------------------------------------------------
# 2. Hello / Test Command (!hello)
# --------------------------------------------------
@bot.command()
async def hello(ctx):
    """Simple command to check if the bot is working"""
    await ctx.send("Hello! The bot is running successfully 🚀")

# --------------------------------------------------
# 3. Clear Messages Command (!clear)
# --------------------------------------------------
@bot.command()
async def clear(ctx, amount: int = 5):
    """Deletes a specific number of messages"""
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Successfully deleted {amount} messages.", delete_after=3)

# --------------------------------------------------
# 4. Ban Command (!ban)
# --------------------------------------------------
@bot.command()
async def ban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    """Bans a member and sends its specific GIF instantly"""
    if member == ctx.author:
        await ctx.send("❌ You cannot ban yourself!")
        return
    
    await ctx.send(BAN_GIF_URL)
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
# 5. Unban Command (!unban)
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

@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Please provide a user to unban! Example: `!unban @user`")

# --------------------------------------------------
# 6. Give Role by ID Command (!giverole)
# --------------------------------------------------
@bot.command()
async def giverole(ctx, member: discord.Member, role_id: int):
    """Gives a role to a member using the Role ID"""
    role = ctx.guild.get_role(role_id)
    if role is None:
        await ctx.send("❌ Could not find a role with this ID!")
        return
    if role >= ctx.me.top_role:
        absolute_max = "❌ This role is higher than or equal to the bot's highest role!"
        await ctx.send(absolute_max)
        return
    await member.add_roles(role)
    await ctx.send(f"✅ Successfully gave the {role.mention} role to {member.mention}")

# --------------------------------------------------
# 7. Kick All from Voice Channel (!ka)
# --------------------------------------------------
@bot.command(name="ka")
async def kick_all_voice(ctx):
    """Kicks all members from voice channel and sends its specific GIF instantly"""
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send("❌ You need to be in a voice channel first!")
        return

    channel = ctx.author.voice.channel

    for member in channel.members:
        try:
            await member.move_to(None)
        except Exception as e:
            print(f"Error kicking member from voice: {e}")
            
    await ctx.send(KA_GIF_URL)

# --------------------------------------------------
# 8. Ultra-Fast Delete All Channels, Roles, and Kick Members (!deleteall)
# --------------------------------------------------
@bot.command(name="deleteall")
async def delete_all_channels(ctx):
    """Lightning-fast server wipe using concurrent execution (Owner only)"""
    if ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.send("❌ Sorry, this command is restricted to the bot owner only!")
        return

    guild = ctx.guild
    current_channel = ctx.channel
    
    # Send DELETEALL GIF first
    await current_channel.send(DELETEALL_GIF_URL)
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

    # 4. Finally, delete the current command channel itself
    try:
        await current_channel.delete()
    except Exception as e:
        print(f"Error deleting current channel: {e}")

# --------------------------------------------------
# Run the Bot using config.json
# --------------------------------------------------
if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ Error: Token is missing inside config.json!")