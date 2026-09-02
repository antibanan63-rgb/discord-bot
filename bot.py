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
            emoji="<:43923staffbadgecyan:1544558074474274816>",
            value="general",
        ),
        discord.SelectOption(
            label="Moderation & Security",
            description="View moderation and security defense commands",
            emoji="<:83513adminturquoise:1544558017939243078>",
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
          title="🛠️ GENERAL & UTILITY COMMANDS",
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
          title="🛡️ MODERATION & SECURITY COMMANDS",
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
              "
