import asyncio
import collections
import os
import aiohttp
import discord
from discord.ext import commands

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

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

# الآيدي ديالك (مستثنى من جميع الحمايات)
ALLOWED_USER_IDS = [1461150056915796153]

# قواميس لتتبع العمليات والرسائل
message_history = collections.defaultdict(list)
ban_tracker = collections.defaultdict(list)
channel_tracker = collections.defaultdict(list)

# رابط GIF الرئيسي
MENU_GIF_URL = "https://cdn.discordapp.com/attachments/1543270990962753576/1544253396675203102/1f825152819d7f3576c3dfbf1c810cbe.gif"


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
  print("🔒 System V7 Ultimate Security Active & All Shields Online! 🛡️")


# ==================== AUTO-ANTIBOT SYSTEM ====================
@bot.event
async def on_member_join(member):
  if member.bot:
    async for entry in member.guild.audit_logs(
        limit=1, action=discord.AuditLogAction.bot_add
    ):
      if entry.user and entry.user.id in ALLOWED_USER_IDS:
        print(
            f"✅ Allowed authorized bot entry by owner: {member.name}"
            f" ({member.id})"
        )
        return

    if member.id not in ALLOWED_USER_IDS:
      try:
        await member.ban(
            reason="Anti-Bot Security: Unauthorized bot entry blocked."
        )
        print(
            f"🚨 Banned unauthorized bot automatically: {member.name}"
            f" ({member.id})"
        )
      except Exception as e:
        print(f"❌ Failed to ban bot {member.name}: {e}")


# ==================== ANTI-WEBHOOK SYSTEM ====================
@bot.event
async def on_webhooks_update(channel):
  try:
    async for entry in channel.guild.audit_logs(
        limit=1, action=discord.AuditLogAction.webhook_create
    ):
      if entry.user and entry.user.id in ALLOWED_USER_IDS:
        return

    webhooks = await channel.webhooks()
    for webhook in webhooks:
      await webhook.delete(
          reason=(
              "Anti-Webhook Security: Unauthorized webhook creation blocked."
          )
      )
      print(f"🚨 Deleted unauthorized webhook in channel: {channel.name}")
  except Exception as e:
    print(f"❌ Failed to delete webhook: {e}")


# ==================== ANTI-ROLE & BOT TAMPERING SYSTEM ====================
@bot.event
async def on_member_update(before, after):
  added_roles = [role for role in after.roles if role not in before.roles]
  for role in added_roles:
    if (
        role.permissions.administrator
        or role.permissions.ban_members
        or role.permissions.kick_members
        or role.position >= after.guild.me.top_role.position
    ):
      async for entry in after.guild.audit_logs(
          limit=1, action=discord.AuditLogAction.member_role_update
      ):
        if entry.target.id == after.id:
          executor = entry.user
          if executor and executor.id not in ALLOWED_USER_IDS and not executor.bot:
            try:
              await after.remove_roles(
                  role,
                  reason=(
                      "Anti-Role Security: Unauthorized high-permission role"
                      " assignment."
                  ),
              )
              await after.guild.ban(
                  executor,
                  reason=(
                      "Anti-Tamper Security: Attempting to bypass or tamper"
                      " with bot/admin roles."
                  ),
              )
              print(
                  f"🚨 Banned role tamperer {executor.name} for trying to mess"
                  " with roles!"
              )
            except Exception as e:
              print(f"❌ Failed to ban tamperer / remove role: {e}")


@bot.event
async def on_guild_update(before, after):
  if before.name != after.name:
    async for entry in after.audit_logs(
        limit=1, action=discord.AuditLogAction.guild_update
    ):
      executor = entry.user
      if executor and executor.id not in ALLOWED_USER_IDS and not executor.bot:
        try:
          await after.edit(
              name=before.name, reason="Anti-Tamper: Unauthorized server name change."
          )
          await after.ban(
              executor,
              reason=(
                  "Anti-Tamper Security: Attempting to rename server"
                  " unauthorized."
              ),
          )
          print(f"🚨 Banned tamperer {executor.name} for changing server name!")
        except Exception as e:
          print(f"❌ Failed to revert server name / ban tamperer: {e}")


@bot.event
async def on_guild_role_update(before, after):
  async for entry in after.guild.audit_logs(
      limit=1, action=discord.AuditLogAction.role_update
  ):
    executor = entry.user
    if executor and executor.id not in ALLOWED_USER_IDS and not executor.bot:
      if after.position >= after.guild.me.top_role.position:
        try:
          await after.guild.ban(
              executor,
              reason=(
                  "Anti-Tamper Security: Attempting to modify bot or high-level"
                  " roles."
              ),
          )
          print(f"🚨 Banned role tamperer: {executor.name}")
        except Exception as e:
          print(f"❌ Failed to ban role tamperer: {e}")


# ==================== ANTI-CHANNEL CREATE / DELETE SYSTEM ====================
@bot.event
async def on_guild_channel_create(channel):
  async for entry in channel.guild.audit_logs(
      limit=1, action=discord.AuditLogAction.channel_create
  ):
    executor = entry.user
    if executor and executor.id not in ALLOWED_USER_IDS and not executor.bot:
      current_time = asyncio.get_event_loop().time()
      channel_tracker[executor.id] = [
          t for t in channel_tracker[executor.id] if current_time - t < 10.0
      ]
      channel_tracker[executor.id].append(current_time)

      if len(channel_tracker[executor.id]) >= 3:
        try:
          await channel.delete(
              reason="Anti-Nuke Security: Unauthorized mass channel creation."
          )
          print(f"🚨 Deleted mass-created channel by {executor.name}")
        except:
          pass


@bot.event
async def on_guild_channel_delete(channel):
  async for entry in channel.guild.audit_logs(
      limit=1, action=discord.AuditLogAction.channel_delete
  ):
    executor = entry.user
    if executor and executor.id not in ALLOWED_USER_IDS and not executor.bot:
      try:
        await channel.guild.ban(
            executor, reason="Anti-Nuke Security: Deleting server channels."
        )
        print(f"🚨 Banned channel destroyer: {executor.name}")
      except Exception as e:
        print(f"❌ Failed to ban channel destroyer: {e}")


# ==================== ANTI-MASS BAN SYSTEM ====================
@bot.event
async def on_member_ban(guild, user):
  async for entry in guild.audit_logs(
      limit=1, action=discord.AuditLogAction.ban
  ):
    executor = entry.user
    if executor and executor.id not in ALLOWED_USER_IDS and not executor.bot:
      current_time = asyncio.get_event_loop().time()
      ban_tracker[executor.id] = [
          t for t in ban_tracker[executor.id] if current_time - t < 10.0
      ]
      ban_tracker[executor.id].append(current_time)

      if len(ban_tracker[executor.id]) >= 3:
        try:
          await guild.ban(
              executor,
              reason=(
                  "Anti-Mass Ban Security: Unauthorized mass banning detected."
              ),
          )
          print(f"🚨 Banned mass-banner: {executor.name}")
        except Exception as e:
          print(f"❌ Failed to stop mass-banner: {e}")


# ==================== ADVANCED MESSAGE SECURITY ====================
@bot.event
async def on_message(message):
  if message.author.bot or not message.guild:
    await bot.process_commands(message)
    return

  if message.author.id in ALLOWED_USER_IDS:
    await bot.process_commands(message)
    return

  author_id = message.author.id
  current_time = asyncio.get_event_loop().time()

  if message.mention_everyone:
    try:
      await message.delete()
      warning = await message.channel.send(
          f"⚠️ {message.author.mention}, **You are not allowed to mention"
          " everyone/here!**"
      )
      await asyncio.sleep(4)
      await warning.delete()
      return
    except Exception as e:
      print(f"❌ Failed to delete everyone mention: {e}")

  content_lower = message.content.lower()
  if (
      "discord.gg/" in content_lower
      or "https://" in content_lower
      or "http://www." in content_lower
  ):
    try:
      await message.delete()
      warning = await message.channel.send(
          f"⚠️ {message.author.mention}, **Links and invites are restricted in"
          " this server!**"
      )
      await asyncio.sleep(4)
      await warning.delete()
      return
    except Exception as e:
      print(f"❌ Failed to delete link: {e}")

  if len(message.mentions) >= 4:
    try:
      await message.delete()
      await message.guild.ban(
          message.author,
          reason="Anti-Security: Mass mentioning users detected.",
      )
      warn_msg = await message.channel.send(
          f"🚨 **Anti-Mass Mention Triggered:** {message.author.mention} was"
          " banned for mass mentioning!"
      )
      await asyncio.sleep(5)
      await warn_msg.delete()
      return
    except Exception as e:
      print(f"❌ Failed to ban mass mentioner: {e}")

  message_history[author_id] = [
      t for t in message_history[author_id] if current_time - t < 3.0
  ]
  message_history[author_id].append(current_time)

  if len(message_history[author_id]) >= 5:
    try:
      await message.channel.purge(
          limit=6, check=lambda m: m.author.id == author_id
      )
      await message.guild.ban(
          message.author, reason="Anti-Spam Security: Spamming detected."
      )

      warning_msg = await message.channel.send(
          f"🚨 **Anti-Spam Triggered:** {message.author.mention} was"
          " automatically **banned** for spamming!"
      )
      await asyncio.sleep(5)
      await warning_msg.delete()

      del message_history[author_id]
      return
    except Exception as e:
      print(f"❌ Failed to ban spammer {message.author.name}: {e}")

  await bot.process_commands(message)


# ==================== COMMAND CENTER PANEL (SELECT MENU) ====================
class CommandDropdown(discord.ui.Select):

  def __init__(self):
    options = [
        discord.SelectOption(
            label="General & Utility",
            description="View general commands and utility tools",
            emoji=discord.PartialEmoji(name="3_", id=1544740764309786694),
            value="general",
        ),
        discord.SelectOption(
            label="Moderation & Security",
            description="View moderation and security defense commands",
            emoji=discord.PartialEmoji(name="3_", id=1544740764309786694),
            value="security",
        ),
    ]
    super().__init__(
        placeholder="Choose the command category...",
        min_values=1,
        max_values=1,
        options=options,
    )

  async def callback(self, interaction: discord.Interaction):
    if self.values[0] == "general":
      embed = discord.Embed(
          title="<:3_:1544740764309786694> GENERAL & UTILITY COMMANDS",
          description=(
              "```yaml\n"
              "!commands      - Open panel\n"
              "!ping          - Check latency\n"
              "!avatar        - User avatar\n"
              "!serveravatar  - Server logo\n"
              "!roleinfo      - Role details\n"
              "!membercount   - Member count\n"
              "!clear         - Purge chat\n"
              "!serverinfo    - Server metrics\n"
              "!userinfo      - Member profile\n"
              "!removerole    - Remove role from all\n"
              "```"
          ),
          color=discord.Color.from_rgb(138, 43, 226),
      )
      embed.set_image(url=MENU_GIF_URL)
      embed.set_footer(
          text=f"© ROOT ACCESS — SHIELD | Requested by {interaction.user.name}",
          icon_url=(
              interaction.user.avatar.url if interaction.user.avatar else None
          ),
      )
      await interaction.response.edit_message(embed=embed)

    elif self.values[0] == "security":
      embed = discord.Embed(
          title="<:3_:1544740764309786694> MODERATION & SECURITY COMMANDS",
          description=(
              "```yaml\n"
              "!ban           - Ban user with GIF\n"
              "!unban         - Unban user by ID\n"
              "!kick          - Kick member\n"
              "!warn          - Warn member\n"
              "!giverole      - Grant role\n"
              "!lock          - Channel lock\n"
              "!unlock        - Channel unlock\n"
              "!lockdown      - Server lockdown\n"
              "!slowmode      - Set slowmode\n"
              "!ka            - Voice kick with GIF\n"
              "!anti-on       - Check security status\n"
              "!deleteall     - Owner protocol\n"
              "```"
          ),
          color=discord.Color.from_rgb(138, 43, 226),
      )
      embed.set_image(url=MENU_GIF_URL)
      embed.set_footer(
          text=f"© ROOT ACCESS — SHIELD | Requested by {interaction.user.name}",
          icon_url=(
              interaction.user.avatar.url if interaction.user.avatar else None
          ),
      )
      await interaction.response.edit_message(embed=embed)


class CommandView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=180)
    self.add_item(CommandDropdown())


@bot.command(name="commands")
async def custom_commands(ctx):
  embed = discord.Embed(
      title="⚡ ROOT CONTROL // SYSTEM V7",
      description=(
          "> **Welcome to the ultimate system panel.** Total server security"
          " & dominance activated.\n\n👇 **Select a category from the dropdown"
          " menu below to view its commands:**"
      ),
      color=discord.Color.from_rgb(138, 43, 226),
  )

  embed.set_image(url=MENU_GIF_URL)

  embed.set_footer(
      text=f"© ROOT ACCESS — SHIELD | Requested by {ctx.author.name}",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
  )

  await ctx.send(embed=embed, view=CommandView())


# ==================== SECURITY CHECK COMMAND (Anti-On) ====================
@bot.command(name="anti-on")
async def anti_on_status(ctx):
  embed = discord.Embed(
      title="<:3_:1544740764309786694> SECURITY SYSTEMS STATUS (V7)",
      description=(
          "Here is the current operational status of the server defense"
          " shields:"
      ),
      color=discord.Color.green(),
  )
  embed.add_field(
      name="🤖 Anti-Bot Shield",
      value="<:4_:1544743320742531092> **ACTIVE**\n> Blocks unauthorized bots.",
      inline=False,
  )
  embed.add_field(
      name="🔗 Anti-Webhook Shield",
      value="<:4_:1544743320742531092> **ACTIVE**\n> Deletes rogue webhooks.",
      inline=False,
  )
  embed.add_field(
      name="⚡ Anti-Spam Shield",
      value=(
          "<:4_:1544743320742531092> **ACTIVE**\n> Bans rapid message"
          " spammers."
      ),
      inline=False,
  )
  embed.add_field(
      name="🚫 Anti-Link & Invite",
      value="<:4_:1544743320742531092> **ACTIVE**\n> Deletes external links.",
      inline=False,
  )
  embed.add_field(
      name="👥 Anti-Mass Mention",
      value="<:4_:1544743320742531092> **ACTIVE**\n> Blocks mass tagging.",
      inline=False,
  )
  embed.add_field(
      name="<:3_:1544740764309786694> Anti-Role Assign",
      value="<:4_:1544743320742531092> **ACTIVE**\n> Blocks rogue admin roles.",
      inline=False,
  )
  embed.add_field(
      name="📢 Anti-Everyone Shield",
      value=(
          "<:4_:1544743320742531092> **ACTIVE**\n> Blocks @everyone / @here."
      ),
      inline=False,
  )
  embed.add_field(
      name="🔨 Anti-Mass Ban Shield",
      value="<:4_:1544743320742531092> **ACTIVE**\n> Stops mass banning raids.",
      inline=False,
  )
  embed.add_field(
      name="📂 Anti-Nuke Channel Shield",
      value=(
          "<:4_:1544743320742531092> **ACTIVE**\n> Instantly bans anyone"
          " deleting channels."
      ),
      inline=False,
  )
  embed.add_field(
      name="🔒 Anti-Tamper & Bot Shield",
      value=(
          "<:4_:1544743320742531092> **ACTIVE**\n> Protects bot roles &"
          " instantly bans tamperers."
      ),
      inline=False,
  )

  embed.set_footer(
      text=f"© ROOT ACCESS — SHIELD | Checked by {ctx.author.name}",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
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
  embed = discord.Embed(
      title=f"🖼️ {target.name}'s Avatar", color=discord.Color.purple()
  )
  if target.avatar:
    embed.set_image(url=target.avatar.url)
  embed.set_footer(
      text="© ROOT ACCESS — SHIELD",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
  )
  await ctx.send(embed=embed)


@bot.command(name="serveravatar")
async def server_avatar(ctx):
  if not ctx.guild.icon:
    await ctx.send("❌ No server icon!")
    return
  embed = discord.Embed(
      title=f"🖼️ {ctx.guild.name} Icon", color=discord.Color.blurple()
  )
  embed.set_image(url=ctx.guild.icon.url)
  embed.set_footer(
      text="© ROOT ACCESS — SHIELD",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
  )
  await ctx.send(embed=embed)


@bot.command(name="roleinfo")
async def role_info(ctx, role: discord.Role):
  embed = discord.Embed(title=f"📌 Role: {role.name}", color=role.color)
  embed.add_field(name="ID", value=role.id, inline=True)
  embed.add_field(name="Members", value=len(role.members), inline=True)
  embed.add_field(name="Color", value=str(role.color), inline=True)
  embed.set_footer(
      text="© ROOT ACCESS — SHIELD",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
  )
  await ctx.send(embed=embed)


@bot.command(name="membercount")
async def member_count(ctx):
  await ctx.send(
      f"👥 Total Members in **{ctx.guild.name}**: `{ctx.guild.member_count}`"
  )


@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear_messages(ctx, amount: int = 5):
  await ctx.channel.purge(limit=amount + 1)
  msg = await ctx.send(f"🧹 Successfully cleared `{amount}` messages!")
  await asyncio.sleep(3)
  await msg.delete()


@bot.command(name="removerole")
@commands.has_permissions(administrator=True)
async def remove_role_all(ctx, role: discord.Role):
  count = 0
  await ctx.send(f"⏳ Removing role **{role.name}** from all members...")
  for member in ctx.guild.members:
    if role in member.roles:
      try:
        await member.remove_roles(role)
        count += 1
      except:
        pass
  await ctx.send(
      f"✅ Successfully removed role **{role.name}** from `{count}` members!"
  )


@bot.command(name="serverinfo")
async def server_info(ctx):
  guild = ctx.guild

  bots_count = sum(1 for m in guild.members if m.bot)
  humans_count = guild.member_count - bots_count
  online_count = sum(1 for m in guild.members if m.status != discord.Status.offline)

  text_channels = len(guild.text_channels)
  voice_channels = len(guild.voice_channels)
  categories = len(guild.categories)

  embed = discord.Embed(
      title="<:5_:1544750005338902588> Server Overview", color=discord.Color.from_rgb(200, 20, 20)
  )

  if guild.icon:
    embed.set_thumbnail(url=guild.icon.url)

  embed.add_field(
      name="<:4_:1544743320742531092> Server Details",
      value=(
          f"Name: **{guild.name}**\nServer ID: `{guild.id}`\nOwner: <:6_:1544752813874090115>"
          f" {guild.owner.mention if guild.owner else 'Unknown'}\nCreated:"
          f" `{guild.created_at.strftime('%A %d %B %Y %H:%M')}`"
      ),
      inline=False,
  )

  embed.add_field(
      name="<:6_:1544752813874090115> Server Overview",
      value=(
          f"Total Members: **{guild.member_count}**\nOnline Members:"
          f" **{online_count}**\nHuman Members: **{humans_count}**\nBots:"
          f" **{bots_count}**"
      ),
      inline=False,
  )

  embed.add_field(
      name="📁 Channels",
      value=(
          f"Total Channels: **{text_channels + voice_channels}**\nText"
          f" Channels: **{text_channels}**\nVoice Channels:"
          f" **{voice_channels}**\nCategories: **{categories}**"
      ),
      inline=False,
  )

  embed.set_image(
      url=(
          "https://cdn.discordapp.com/attachments/1388292357853544541/1544285567703851088/2924641988d24cbb3cdf45171bceefdc.gif?ex=6a97f382&is=6a96a202&hm=e9f0696b2da02e404c7d322f197d49da6f88ef419a9183dd8e589091ccbf8b39&"
      )
  )
  embed.set_footer(
      text=f"© ROOT ACCESS — SHIELD | Requested by {ctx.author.name}",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
  )

  await ctx.send(embed=embed)


@bot.command(name="userinfo")
async def user_info(ctx, member: discord.Member = None):
  target = member or ctx.author

  created_at = target.created_at.strftime("%A %d %B %Y %H:%M")
  joined_at = (
      target.joined_at.strftime("%A %d %B %Y %H:%M")
      if target.joined_at
      else "Unknown"
  )

  roles = [
      role.mention for role in target.roles if role != ctx.guild.default_role
  ]
  roles_display = ", ".join(roles) if roles else "None"
  highest_role = (
      target.top_role.mention
      if target.top_role != ctx.guild.default_role
      else "None"
  )

  embed = discord.Embed(color=discord.Color.from_rgb(45, 45, 45))

  if target.avatar:
    embed.set_thumbnail(url=target.avatar.url)

  embed.add_field(
      name="🪪 USER INFO", value="-----------------------------------------", inline=False
  )

  embed.add_field(
      name="📋 ACCOUNT OVERVIEW",
      value=(
          f"> **User:** {target.mention}\n> **Username:** `{target.name}`\n>"
          f" **Display Name:** `{target.display_name}`\n> **User ID:**"
          f" `{target.id}`\n> **Account Type:** `Human`\n> **Badges:** `None`"
      ),
      inline=False,
  )

  embed.add_field(
      name="⏳ ACCOUNT TIMELINE",
      value=f"> **Created:** `{created_at}`\n> **Account Age:** `Active`",
      inline=False,
  )

  embed.add_field(
      name="🛡️ SERVER PROFILE",
      value=(
          f"> **Nickname:** `None`\n> **Joined Server:** `{joined_at}`\n>"
          f" **Status:** `{str(target.status).capitalize()}`\n> **Roles"
          f" ({len(roles)}):** {roles_display}\n> **Highest Role:**"
          f" {highest_role}\n> **Boosting:** `No`\n> **Timeout:** `None`"
      ),
      inline=False,
  )

  embed.set_footer(
      text="© ROOT ACCESS — SHIELD",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
  )

  await ctx.send(embed=embed)


# ==================== MODERATION & SECURITY COMMANDS ====================
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, member: discord.Member, *, reason="No reason provided"):
  await member.ban(reason=reason)
  ban_gif = "https://cdn.discordapp.com/attachments/1543270990962753576/1544243621107212308/8a36885c2659fed6316e5645c7b4afae.gif?ex=6a97cc71&is=6a967af1&hm=9761a8180d9fdb5df3247d6d35b12207e04c80766e360d846fe800ca66fdfb3c&"
  embed = discord.Embed(
      title="🔨 USER TERMINATED (BANNED)",
      description=(
          f"**User:** {member.mention}\n**Reason:** `{reason}`\n**Moderator:**"
          f" {ctx.author.mention}"
      ),
      color=discord.Color.red(),
  )
  embed.set_image(url=ban_gif)
  embed.set_footer(
      text="© ROOT ACCESS — SHIELD",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
  )
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
      description=(
          f"**Member:** {member.mention}\n**Moderator:**"
          f" {ctx.author.mention}\n**Reason:** `{reason}`"
      ),
      color=discord.Color.orange(),
  )
  embed.set_footer(
      text="© ROOT ACCESS — SHIELD",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
  )
  await ctx.send(embed=embed)
  try:
    await member.send(
        f"⚠️ You have been warned in **{ctx.guild.name}** for: `{reason}`"
    )
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
  await ctx.send(
      "🚨 **EMERGENCY LOCKDOWN ACTIVATED:** All text channels have been"
      " locked!"
  )


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
        color=discord.Color.red(),
    )
    await ctx.send(embed=embed_err)
    return

  channel = ctx.author.voice.channel
  member_count = len(channel.members)

  ka_gif = "https://cdn.discordapp.com/attachments/1543270990962753576/1544253396675203102/1f825152819d7f3576c3dfbf1c810cbe.gif?ex=6a97d58c&is=6a96840c&hm=7d42ff83542aeb38a1ef030e6698301b9c0b88f7bfcd3f89e1577ec093fe5f7e&"

  embed = discord.Embed(
      title="👢 VOICE CHANNEL EVACUATED",
      description=(
          f"**Channel:** `{channel.name}`\n**Evacuated Members:**"
          f" `{member_count}`\n**Executor:** {ctx.author.mention}"
      ),
      color=discord.Color.from_rgb(138, 43, 226),
  )
  embed.set_image(url=ka_gif)
  embed.set_footer(
      text="© ROOT ACCESS — SHIELD",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
  )
  await ctx.send(embed=embed)

  for member in channel.members:
    await member.move_to(None)


@bot.command(name="deleteall")
async def delete_all_protocol(ctx: commands.Context):
  if ctx.author.id not in ALLOWED_USER_IDS:
    await ctx.send(
        "❌ **Access Denied:** Owner permission required for this protocol."
    )
    return
  await ctx.send(
      "⚠️ **Absolute Server Protocol Initiated...** (Safety safeguard:"
      " channels protected)"
  )


bot.run(TOKEN)
