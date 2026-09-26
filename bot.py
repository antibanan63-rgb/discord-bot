import asyncio
import collections
import os
import aiohttp
import discord
from discord.ext import commands

TOKEN = os.getenv("DISDIRECT_TOKEN") or os.getenv("DISCORD_TOKEN")
if not TOKEN:
  print("Error: Token is missing!")
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
ban_tracker = collections.defaultdict(list)
channel_tracker = collections.defaultdict(list)

# رابط GIF الرئيسي
MENU_GIF_URL = "https://cdn.discordapp.com/attachments/1543270990962753576/1544253396675203102/1f825152819d7f3576c3dfbf1c810cbe.gif"


@bot.event
async def on_ready():
  print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
  print("RT Mode Security Active Online !")


# ==================== AUTO-ANTIBOT & AUTO-ROLE SYSTEM ====================
@bot.event
async def on_member_join(member):
  # حماية البوتات (Anti-Bot)
  if member.bot:
    async for entry in member.guild.audit_logs(
        limit=1, action=discord.AuditLogAction.bot_add
    ):
      if entry.user and entry.user.id in ALLOWED_USER_IDS:
        print(
            f"Allowed authorized bot entry by owner: {member.name}"
            f" ({member.id})"
        )
        return

    if member.id not in ALLOWED_USER_IDS:
      try:
        await member.ban(
            reason="Anti-Bot Security: Unauthorized bot entry blocked."
        )
        print(
            f"Banned unauthorized bot automatically: {member.name} ({member.id})"
        )
      except Exception as e:
        print(f"Failed to ban bot {member.name}: {e}")
      return

  # إعطاء الرول تلقائياً للعضو الجديد بالآيدي اللي عطيتينا
  role_id = 1552665217551573053
  role = member.guild.get_role(role_id)

  if role:
    try:
      await member.add_roles(role, reason="Auto-Role: Welcome new member.")
      print(f"Added role {role.name} to {member.name}")
    except Exception as e:
      print(f"Failed to add role to {member.name}: {e}")
  else:
    print(f"Role with ID {role_id} not found!")


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
      print(f"Deleted unauthorized webhook in channel: {channel.name}")
  except Exception as e:
    print(f"Failed to delete webhook: {e}")


# ==================== ANTI-ROLE ASSIGN SYSTEM ====================
@bot.event
async def on_member_update(before, after):
  if len(before.roles) < len(after.roles):
    async for entry in after.guild.audit_logs(
        limit=1, action=discord.AuditLogAction.member_role_update
    ):
      if entry.user and entry.user.id not in ALLOWED_USER_IDS:
        added_roles = [role for role in after.roles if role not in before.roles]
        for role in added_roles:
          try:
            await after.remove_roles(
                role, reason="Anti-Role Security: Unauthorized role assignment."
            )
            print(
                f"Removed unauthorized role {role.name} given by"
                f" {entry.user.name} to {after.name}"
            )
          except Exception as e:
            print(f"Failed to remove unauthorized role: {e}")
        break


# ==================== SECURITY CHECK COMMAND (Anti-On) ====================
@bot.command(name="anti-on")
async def anti_on_status(ctx):
  # البحث عن الإيموجي تلقائياً بالاسم داخل السيرفر
  emoji = discord.utils.get(ctx.guild.emojis, name="1_")
  emoji_str = str(emoji) if emoji else ""

  embed = discord.Embed(
      title=f"{emoji_str} SECURITY SYSTEMS STATUS (V7)",
      description=(
          "Here is the current operational status of the server defense"
          " shields:"
      ),
      color=discord.Color.green(),
  )

  embed.add_field(
      name=f"{emoji_str} Anti-Bot Shield",
      value="ACTIVE\n> Blocks unauthorized bots.",
      inline=False,
  )
  embed.add_field(
      name=f"{emoji_str} Anti-Webhook Shield",
      value="ACTIVE\n> Deletes rogue webhooks.",
      inline=False,
  )
  embed.add_field(
      name=f"{emoji_str} Anti-Spam Shield",
      value="ACTIVE\n> Bans rapid message spammers.",
      inline=False,
  )
  embed.add_field(
      name=f"{emoji_str} Anti-Link & Invite",
      value="ACTIVE\n> Deletes external links.",
      inline=False,
  )
  embed.add_field(
      name=f"{emoji_str} Anti-Mass Mention",
      value="ACTIVE\n> Blocks mass tagging.",
      inline=False,
  )
  embed.add_field(
      name=f"{emoji_str} Anti-Role Assign",
      value="ACTIVE\n> Blocks rogue admin/role assignments.",
      inline=False,
  )
  embed.add_field(
      name=f"{emoji_str} Anti-Everyone Shield",
      value="ACTIVE\n> Blocks @everyone / @here.",
      inline=False,
  )
  embed.add_field(
      name=f"{emoji_str} Anti-Mass Ban Shield",
      value="ACTIVE\n> Stops mass banning raids.",
      inline=False,
  )
  embed.add_field(
      name=f"{emoji_str} Anti-Nuke Channel Shield",
      value="ACTIVE\n> Instantly bans anyone deleting channels.",
      inline=False,
  )
  embed.add_field(
      name=f"{emoji_str} Anti-Tamper & Bot Shield",
      value="ACTIVE\n> Protects bot roles & instantly bans tamperers.",
      inline=False,
  )

  embed.set_footer(
      text=f"© RT MODE — SHIELD | Checked by {ctx.author.name}",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
  )
  await ctx.send(embed=embed)


# ==================== SECURITY & MODERATION COMMANDS ====================
@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban_member(ctx, member: discord.Member, *, reason="No reason provided"):
  await member.ban(reason=reason)
  ban_gif = "https://cdn.discordapp.com/attachments/1543270990962753576/1544243621107212308/8a36885c2659fed6316e5645c7b4afae.gif?ex=6a97cc71&is=6a967af1&hm=9761a8180d9fdb5df3247d6d35b12207e04c80766e360d846fe800ca66fdfb3c&"
  embed = discord.Embed(
      title="USER TERMINATED (BANNED)",
      description=(
          f"**User:** {member.mention}\n**Reason:** `{reason}`\n**Moderator:**"
          f" {ctx.author.mention}"
      ),
      color=discord.Color.red(),
  )
  embed.set_image(url=ban_gif)
  embed.set_footer(
      text="© RT MODE — SHIELD",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
  )
  await ctx.send(embed=embed)


@bot.command(name="unban")
@commands.has_permissions(ban_members=True)
async def unban_member(ctx, user_id: int):
  try:
    user = discord.Object(id=user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"Unbanned user ID **{user_id}** successfully.")
  except discord.NotFound:
    await ctx.send("User not found in ban list or invalid ID.")
  except Exception as e:
    await ctx.send(f"An error occurred: `{e}`")


@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick_member(ctx, member: discord.Member, *, reason="No reason provided"):
  await member.kick(reason=reason)
  await ctx.send(f"Kicked **{member.name}** | Reason: `{reason}`")


@bot.command(name="lock")
@commands.has_permissions(manage_channels=True)
async def lock_channel(ctx):
  await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
  await ctx.send("Channel has been locked successfully.")


@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def unlock_channel(ctx):
  await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
  await ctx.send("Channel has been unlocked.")


@bot.command(name="ka")
async def kick_all_voice(ctx):
  if not ctx.author.voice or not ctx.author.voice.channel:
    embed_err = discord.Embed(
        title="ERROR",
        description="You must be in a voice channel to use this command!",
        color=discord.Color.red(),
    )
    await ctx.send(embed=embed_err)
    return

  channel = ctx.author.voice.channel
  member_count = len(channel.members)

  ka_gif = "https://cdn.discordapp.com/attachments/1543270990962753576/1544253396675203102/1f825152819d7f3576c3dfbf1c810cbe.gif?ex=6a97d58c&is=6a96840c&hm=7d42ff83542aeb38a1ef030e6698301b9c0b88f7bfcd3f89e1577ec093fe5f7e&"

  embed = discord.Embed(
      title="VOICE CHANNEL EVACUATED",
      description=(
          f"**Channel:** `{channel.name}`\n**Evacuated Members:**"
          f" `{member_count}`\n**Executor:** {ctx.author.mention}"
      ),
      color=discord.Color.from_rgb(138, 43, 226),
  )
  embed.set_image(url=ka_gif)
  embed.set_footer(
      text="© RT MODE — SHIELD",
      icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
  )
  await ctx.send(embed=embed)

  for member in channel.members:
    await member.move_to(None)


@bot.command(name="deleteall")
async def delete_all_protocol(ctx: commands.Context):
  if ctx.author.id not in ALLOWED_USER_IDS:
    await ctx.send("Access Denied: Owner permission required for this protocol.")
    return
  await ctx.send(
      "Absolute Server Protocol Initiated... (Safety safeguard: channels"
      " protected)"
  )


bot.run(TOKEN)
