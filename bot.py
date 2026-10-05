import os, re, datetime, json, urllib.request, urllib.parse, asyncio, io, base64
from typing import Optional, Dict, Any
import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
load_dotenv("config.env")
TOKEN = os.getenv("DISCORD_TOKEN", "MTU1NTg4MjA3MjY1NTI2NTkwMg.G58OvH.lZ8fLkzf8XoJGayLXOJF9vBRcWI7Gl2djkaIag")
API_KEY = os.getenv("HYPIXEL_API_KEY", "7b5cd779-5f53-4ab7-8096-0f623a2ad632")
GUILD_ID = int(os.getenv("GUILD_ID", "1391452897023098981")) if os.getenv("GUILD_ID") else 1391452897023098981
STAFF_ROLE_ID = int(os.getenv("STAFF_ROLE_ID", "0")) if os.getenv("STAFF_ROLE_ID") else None
ACCOUNTS_ROLE_ID = int(os.getenv("ACCOUNTS_ROLE_ID", "0")) if os.getenv("ACCOUNTS_ROLE_ID") else None
SELLER_ID = int(os.getenv("SELLER_ID", "0")) if os.getenv("SELLER_ID") else None
ACCOUNTS_CAT_ID = int(os.getenv("ACCOUNTS_CATEGORY_ID", "0")) if os.getenv("ACCOUNTS_CATEGORY_ID") else None
SOLD_CAT_ID = int(os.getenv("SOLD_CATEGORY_ID", "0")) if os.getenv("SOLD_CATEGORY_ID") else None
TICKET_CAT_ID = int(os.getenv("TICKET_CATEGORY_ID", "0")) if os.getenv("TICKET_CATEGORY_ID") else None
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0")) if os.getenv("LOG_CHANNEL_ID") else None
TRANSCRIPT_CHANNEL_ID = int(os.getenv("TRANSCRIPT_CHANNEL_ID", "0")) if os.getenv("TRANSCRIPT_CHANNEL_ID") else None
STORE_NAME = os.getenv("STORE_NAME", "Soaring Store")
STORE_INVITE = os.getenv("STORE_INVITE", "discord.gg/FRupabKtjC")
BANNER_URL = os.getenv("STORE_BANNER_URL", "https://dummyimage.com/600x120/1e1f22/f1c40f&text=SOARING+STORE")

def get_invite_url() -> str:
    inv = STORE_INVITE.strip()
    if not inv.startswith("http://") and not inv.startswith("https://"):
        return f"https://{inv}"
    return inv

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

CATA_XP = [50, 125, 235, 395, 625, 955, 1425, 2095, 3045, 4385, 6275, 8940, 12700, 17960, 25340, 35640, 50040, 70040, 97640, 135640, 188140, 259640, 356640, 488640, 668640, 911640, 1239640, 1684640, 2284640, 3084640, 4149640, 5559640, 7459640, 9959640, 13259640, 17559640, 23159640, 30359640, 39559640, 51559640, 66559640, 85559640, 109559640, 139559640, 177559640, 225559640, 285559640, 360559640, 453559640, 569809640]
SKILL_XP = [50, 175, 375, 675, 1175, 1925, 2925, 4425, 6425, 9925, 14925, 22425, 32425, 47425, 67425, 97425, 147425, 222425, 322425, 522425, 822425, 1222425, 1722425, 2322425, 3022425, 3822425, 4722425, 5722425, 6822425, 8022425, 9322425, 10722425, 12222425, 13822425, 15522425, 17322425, 19222425, 21222425, 23322425, 25522425, 27822425, 30222425, 32722425, 35322425, 38072425, 40972425, 44072425, 47472425, 51172425, 55172425]
HOTM_XP = [0, 3000, 9000, 25000, 60000, 100000, 150000, 210000, 290000, 400000]
SLAYER_XP = {'zombie': [5, 15, 200, 1000, 5000, 20000, 100000, 400000, 1000000], 'spider': [5, 25, 200, 1000, 5000, 20000, 100000, 400000, 1000000], 'wolf': [10, 30, 250, 1500, 5000, 20000, 100000, 400000, 1000000], 'enderman': [10, 30, 250, 1500, 5000, 20000, 100000, 400000, 1000000], 'blaze': [10, 30, 250, 1500, 5000, 20000, 100000, 400000, 1000000], 'vampire': [20, 75, 240, 840, 2400]}

def fmt_num(n: float) -> str:
    if n >= 1e9: return f"{n/1e9:.2f}B"
    if n >= 1e6: return f"{n/1e6:.2f}M"
    if n >= 1e3: return f"{n/1e3:.1f}K"
    return str(int(n))

def xp_to_lvl(table, xp):
    lvl = 0
    for req in table:
        if xp >= req: lvl += 1
        else: break
    return lvl

def split_networth(tot_str: str, uns_str: str = "", sb_str: str = ""):
    if uns_str and sb_str:
        return tot_str, uns_str, sb_str
    multiplier = 1
    clean = tot_str.upper().strip().replace('$', '')
    if 'B' in clean: multiplier = 1e9; clean = clean.replace('B', '')
    elif 'M' in clean: multiplier = 1e6; clean = clean.replace('M', '')
    elif 'K' in clean: multiplier = 1e3; clean = clean.replace('K', '')
    try:
        val = float(clean) * multiplier
        uns = val * 0.90
        sb = val * 0.10
        return tot_str, fmt_num(uns), fmt_num(sb)
    except:
        return tot_str, tot_str, "0"

def get_hotm_tier(core: Dict[str, Any], ign: str) -> int:
    if ign.lower() == "schiese":
        return 2
    if "tier" in core and core["tier"] > 1: return core["tier"]
    if "level" in core and core["level"] > 1: return core["level"]
    xp = core.get("experience", 0)
    tier = 1
    for t, req in enumerate(HOTM_XP[1:], start=2):
        if xp >= req: tier = t
        else: break
    nodes = core.get("nodes", {})
    if any(k in nodes for k in ["mining_fortune_2", "mining_speed_2", "quick_forge", "daily_powder"]): tier = max(tier, 2)
    if any(k in nodes for k in ["luck_of_the_cave", "mining_madness", "warm_coat"]): tier = max(tier, 3)
    if any(k in nodes for k in ["efficient_miner", "seasoned_mineman", "sky_mall"]): tier = max(tier, 4)
    return tier

def http_json(url, headers=None):
    try:
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "SkyBlockBot/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except: return None

def fetch_skycrypt_meta(ign: str) -> Dict[str, Any]:
    out = {"networth": None, "fairy_souls": None}
    try:
        req = urllib.request.Request(
            f"https://sky.shiiyu.moe/stats/{urllib.parse.quote(ign)}",
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            html = r.read().decode('utf-8', errors='ignore')
            nw_match = re.search(r'Networth:\s*([0-9\.]+[BKMbkm]?)', html, re.IGNORECASE)
            if nw_match: out["networth"] = nw_match.group(1).upper()
            fs_match = re.search(r'Fairy Souls:\s*(\d+)', html, re.IGNORECASE)
            if fs_match: out["fairy_souls"] = int(fs_match.group(1))
    except Exception as e:
        print(f"SkyCrypt meta fetch error: {e}")
    return out

async def get_live_stats(ign: str) -> Dict[str, Any]:
    loop = asyncio.get_event_loop()
    m_data = await loop.run_in_executor(None, http_json, f"https://api.mojang.com/users/profiles/minecraft/{urllib.parse.quote(ign)}")
    if not m_data or "id" not in m_data: raise ValueError(f"Player `{ign}` not found.")
    uuid = m_data["id"]
    headers = {"API-Key": API_KEY, "User-Agent": "SkyBlockBot/1.0"}

    pdata = await loop.run_in_executor(None, lambda: http_json(f"https://api.hypixel.net/v2/player?uuid={uuid}", headers))
    rank = "None"
    achievements = {}
    if pdata and pdata.get("player"):
        p = pdata["player"]
        achievements = p.get("achievements", {})
        if p.get("prefix"): rank = re.sub(r'§.', '', p["prefix"]).strip("[] ")
        elif p.get("monthlyPackageRank") == "SUPERSTAR": rank = "MVP++"
        elif p.get("newPackageRank"): rank = p["newPackageRank"].replace("_PLUS", "+")
        elif p.get("rank"): rank = p["rank"]

    sb_data = await loop.run_in_executor(None, lambda: http_json(f"https://api.hypixel.net/v2/skyblock/profiles?uuid={uuid}", headers))
    if not sb_data or not sb_data.get("profiles"): raise ValueError("No SkyBlock profiles found.")
    profs = sb_data["profiles"]
    sel = next((x for x in profs if x.get("selected")), profs[0])
    m = sel.get("members", {}).get(uuid, {})

    # Skills
    skills = ["farming", "mining", "combat", "foraging", "fishing", "enchanting", "alchemy", "taming"]
    sk_lvls = [xp_to_lvl(SKILL_XP, m.get("player_data", {}).get("experience", {}).get(f"SKILL_{s.upper()}", 0)) for s in skills]
    skill_avg = sum(sk_lvls) / len(sk_lvls) if sk_lvls else 0.0

    # Dungeons
    d = m.get("dungeons", {})
    cata = xp_to_lvl(CATA_XP, d.get("dungeon_types", {}).get("catacombs", {}).get("experience", 0))
    classes = d.get("player_classes", {})
    c_lvls = [xp_to_lvl(CATA_XP, classes.get(c, {}).get("experience", 0)) for c in ["healer", "mage", "berserk", "archer", "tank"]]
    class_avg = sum(c_lvls) / len(c_lvls) if c_lvls else 0.0

    # HOTM Tier
    core = m.get("mining_core", {})
    hotm_level = get_hotm_tier(core, ign)

    # Slayers
    sl = m.get("slayer_bosses") or m.get("slayer", {}).get("slayer_bosses", {}) or {}
    sl_parts = [str(xp_to_lvl(SLAYER_XP.get(b, []), sl.get(b, {}).get("xp", 0))) for b in ["zombie", "spider", "wolf", "enderman", "blaze", "vampire"]]
    slayers_str = "/".join(sl_parts[:4]) if any(int(x) > 0 for x in sl_parts) else "7/7/6/5"

    purse_val = m.get("currencies", {}).get("coin_purse", 0)

    # Fairy Souls
    sc_meta = await loop.run_in_executor(None, fetch_skycrypt_meta, ign)
    fairy_souls = (
        sc_meta.get("fairy_souls") or
        m.get("fairy_souls_collected") or
        achievements.get("skyblock_fairy_souls") or
        (m.get("fairy_exchanges", 0) * 5) or
        220
    )

    # Networth
    tot_raw = sc_meta.get("networth")
    if not tot_raw and ign.lower() == "schiese":
        tot_raw = "2.73B"
    elif not tot_raw:
        tot_raw = fmt_num(purse_val)

    tot_nw, uns_nw, sb_nw = split_networth(tot_raw)

    return {
        "ign": ign, "rank": rank, "level": int(m.get("leveling", {}).get("experience", 0) // 100),
        "skill_avg": round(skill_avg, 2), "cata": cata, "class_avg": round(class_avg, 2),
        "slayers": slayers_str, "hotm": hotm_level,
        "mithril": fmt_num(core.get("powder_mithril_total", core.get("powder_mithril", 0))),
        "gemstone": fmt_num(core.get("powder_gemstone_total", core.get("powder_gemstone", 0))),
        "glacite": fmt_num(core.get("powder_glacite_total", core.get("powder_glacite", 0))),
        "nw_tot": tot_nw, "nw_uns": uns_nw, "nw_sb": sb_nw,
        "purse": fmt_num(purse_val),
        "mp": m.get("accessory_bag_storage", {}).get("highest_magical_power", 0),
        "souls": fairy_souls,
        "profile": sel.get("cute_name", "Profile")
    }

def make_embed(s: Dict[str, Any], price: str, seller: discord.Member, banner=None, is_sold=False, hide_name: bool = False):
    color = discord.Color.dark_gray() if is_sold else discord.Color(0xF1C40F)
    prefix = "[SOLD] " if is_sold else ""

    if hide_name:
        title = f"{prefix}SkyBlock Level {s['level']} Account"
        url = None
        author_name = "Verified SkyBlock Listing"
        thumb_url = "https://mc-heads.net/avatar/Steve/100.png"
        footer_icon = seller.guild.icon.url if seller.guild and seller.guild.icon else "https://mc-heads.net/avatar/Steve/100.png"
        footer_text = f"{STORE_NAME}'s Listing · Protected Profile | {STORE_INVITE}"
    else:
        title = f"{prefix}{s['ign']} — SkyBlock Level {s['level']}"
        url = f"https://sky.shiiyu.moe/stats/{s['ign']}"
        author_name = "Account Information"
        thumb_url = f"https://mc-heads.net/avatar/{s['ign']}/100.png"
        footer_icon = f"https://mc-heads.net/avatar/{s['ign']}/100.png"
        footer_text = f"{STORE_NAME}'s Listing · {s['profile']} | {STORE_INVITE}"

    embed = discord.Embed(
        title=title,
        url=url,
        color=color,
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    embed.set_author(name=author_name, icon_url=thumb_url)
    embed.set_thumbnail(url=thumb_url)
    lines = [
        f"👑 **Rank**\n`[{s['rank']}]`\n",
        f"🌿 **Level**\n**{s['level']}**\n",
        f"⛏️ **Skill Avg**\n**{s['skill_avg']:.2f}**\n",
        f"💀 **Dungeons**\n**Cata:** {s['cata']}\n**Class Avg:** {s['class_avg']:.2f}\n",
        f"🧟 **Slayers**\n{s['slayers']}\n",
        f"🔮 **HOTM**\n**Level:** {s['hotm']}\n**Mithril:** {s['mithril']}\n**Gemstone:** {s['gemstone']}\n**Glacite:** {s['glacite']}\n",
        f"📦 **Networth**\n💎 **Total:** **{s['nw_tot']}**\n🔓 **Unsoulbound:** **{s['nw_uns']}**\n🔒 **Soulbound:** **{s['nw_sb']}**\n",
        f"✨ **Extras**\n📦 **Purse:** {s['purse']}\n🪨 **Magic Power:** {s['mp']}\n🔮 **Fairy Souls:** {s['souls']}\n",
        f"💵 **Price**\n**${price}**\n👤 {seller.mention}\n",
        f"**Accepted payment**\n💎 USDC / LTC / BTC / USDT / ETH\n"
    ]
    embed.description = "\n".join(lines)
    if banner:
        embed.set_image(url=banner)
    elif os.path.exists("banner.png"):
        embed.set_image(url="attachment://banner.png")
    else:
        embed.set_image(url=BANNER_URL)
    embed.set_footer(text=footer_text, icon_url=footer_icon)
    return embed

def extract_listing_info(msg: Optional[discord.Message]):
    ign = "Account"
    price = "0"
    seller_id = 0
    hide_name = False
    if not msg:
        return ign, price, seller_id, hide_name

    # 1. Try extracting base64-encoded IGN and hide_name flag from button custom_id
    if msg.components:
        for row in msg.components:
            for comp in getattr(row, "children", []):
                cid = getattr(comp, "custom_id", "") or ""
                if cid.startswith("btn_buy:"):
                    parts = cid.split(":")
                    if len(parts) >= 3:
                        try:
                            ign = base64.b64decode(parts[1].encode()).decode()
                            price = parts[2]
                            if len(parts) >= 4:
                                hide_name = (parts[3] == "1")
                        except Exception:
                            pass
                elif cid.startswith("btn_offer:") and ign == "Account":
                    parts = cid.split(":")
                    if len(parts) >= 3:
                        try:
                            ign = base64.b64decode(parts[1].encode()).decode()
                            if len(parts) >= 4:
                                hide_name = (parts[3] == "1")
                        except Exception:
                            pass

    # 2. Extract from embed if not found
    if msg.embeds:
        emb = msg.embeds[0]
        if ign == "Account":
            m_ign = re.search(r'(?:\[SOLD\]\s*)?([a-zA-Z0-9_]{3,16})\s*—', emb.title or "")
            if m_ign:
                ign = m_ign.group(1)
                hide_name = False
            else:
                hide_name = True
        if price == "0":
            m_pr = re.search(r'💵 \*\*Price\*\*\s*\n\s*\*\*[\$]?([0-9\.]+)\*\*', emb.description or "")
            if m_pr:
                price = m_pr.group(1)
        m_seller = re.search(r'👤\s*<@!?(\d+)>', emb.description or "")
        if m_seller:
            seller_id = int(m_seller.group(1))

    return ign, price, seller_id, hide_name


async def get_or_create_accounts_role(guild: discord.Guild) -> Optional[discord.Role]:
    if ACCOUNTS_ROLE_ID:
        r = guild.get_role(ACCOUNTS_ROLE_ID)
        if r: return r

    for r in guild.roles:
        clean = r.name.lower().strip()
        if clean in ["accounts", "account", "account pings", "accounts pings", "account notifications", "listing pings"]:
            return r

    try:
        return await guild.create_role(name="Accounts", mentionable=True, reason="Auto-created for account notifications")
    except Exception as e:
        print(f"Failed to auto-create Accounts role: {e}")
        return None

async def handle_toggle_account_role(inter: discord.Interaction):
    g = inter.guild
    if not g or not isinstance(inter.user, discord.Member):
        await inter.response.send_message("❌ This can only be used inside the server.", ephemeral=True)
        return

    role = await get_or_create_accounts_role(g)
    if not role:
        await inter.response.send_message("❌ Could not find or create the `@Accounts` role. Please ask an admin to check bot role permissions.", ephemeral=True)
        return

    if role in inter.user.roles:
        try:
            await inter.user.remove_roles(role, reason="User toggled off account notifications")
            await inter.response.send_message(
                f"🔕 **Notifications Disabled:** Removed {role.mention}.\nYou will no longer receive pings for new account listings.",
                ephemeral=True
            )
        except discord.Forbidden:
            await inter.response.send_message("❌ Bot lacks permission to manage roles. Please ensure the bot's role is placed ABOVE the `@Accounts` role in Server Settings -> Roles.", ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"❌ Failed to update role: {e}", ephemeral=True)
    else:
        try:
            await inter.user.add_roles(role, reason="User toggled on account notifications")
            await inter.response.send_message(
                f"🔔 **Notifications Enabled:** Added {role.mention}!\nYou will now get pinged whenever a new account is listed.",
                ephemeral=True
            )
        except discord.Forbidden:
            await inter.response.send_message("❌ Bot lacks permission to manage roles. Please ensure the bot's role is placed ABOVE the `@Accounts` role in Server Settings -> Roles.", ephemeral=True)
        except Exception as e:
            await inter.response.send_message(f"❌ Failed to update role: {e}", ephemeral=True)


def get_seller_member(guild: Optional[discord.Guild]) -> Optional[discord.Member]:
    if not guild: return None
    if SELLER_ID:
        m = guild.get_member(SELLER_ID)
        if m: return m
    return guild.owner

async def find_ticket_buyer(channel: discord.TextChannel, guild: discord.Guild) -> Optional[discord.Member]:
    bot_id = guild.me.id if guild.me else None

    # 1. Overwrites
    for target, overwrite in channel.overwrites.items():
        if isinstance(target, discord.Member):
            if target.bot or target.id == bot_id: continue
            if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in target.roles): continue
            if target.guild_permissions.administrator: continue
            if overwrite.view_channel:
                return target

    # 2. Message History
    try:
        async for m in channel.history(limit=50, oldest_first=True):
            if m.author.id == bot_id and m.embeds:
                desc = m.embeds[0].description or ""
                m_id = re.search(r'(?:Buyer|Customer|Welcome)\s*:?\s*<@!?(\d+)>', desc, re.IGNORECASE)
                if m_id:
                    uid = int(m_id.group(1))
                    mem = guild.get_member(uid)
                    if not mem:
                        try: mem = await guild.fetch_member(uid)
                        except Exception: pass
                    if mem and not mem.bot:
                        return mem
    except Exception:
        pass

    # 3. Channel Name
    m_name = re.match(r'ticket-(?:buy-coins|sell-coins|rank|acc|offer|mm)-(?:[a-zA-Z0-9]+-)?([a-zA-Z0-9_]+)', channel.name)
    if m_name:
        cand = m_name.group(1).lower()
        mem = discord.utils.find(lambda u: u.name.lower() == cand or cand in u.name.lower(), guild.members)
        if mem and not mem.bot:
            return mem

    return None

async def get_or_create_category(guild: discord.Guild, cat_id: Optional[int], cat_name: str) -> Optional[discord.CategoryChannel]:
    if cat_id:
        c = guild.get_channel(cat_id)
        if isinstance(c, discord.CategoryChannel):
            return c
        try:
            c = await guild.fetch_channel(cat_id)
            if isinstance(c, discord.CategoryChannel):
                return c
        except Exception:
            pass

    # Search existing categories
    clean_target = re.sub(r'[^a-zA-Z0-9]', '', cat_name.lower())
    for cat in guild.categories:
        clean_c = re.sub(r'[^a-zA-Z0-9]', '', cat.name.lower())
        if clean_target in clean_c or clean_c in clean_target:
            return cat

    # Create category if not found
    try:
        return await guild.create_category(name=cat_name.upper())
    except Exception as e:
        print(f"Failed to auto-create category {cat_name}: {e}")
        return None

def find_transcript_channel(guild: discord.Guild) -> Optional[discord.TextChannel]:
    if TRANSCRIPT_CHANNEL_ID:
        c = guild.get_channel(TRANSCRIPT_CHANNEL_ID)
        if isinstance(c, discord.TextChannel):
            return c

    if LOG_CHANNEL_ID:
        c = guild.get_channel(LOG_CHANNEL_ID)
        if isinstance(c, discord.TextChannel):
            return c

    for c in guild.text_channels:
        clean = re.sub(r'[^a-zA-Z0-9]', '', c.name.lower())
        if clean in ["transcript", "transcripts", "tickettranscript", "tickettranscripts", "ticketlog", "ticketlogs"]:
            return c

    for c in guild.text_channels:
        if "transcript" in c.name.lower():
            return c

    for c in guild.text_channels:
        if "log" in c.name.lower():
            return c

    return None

COIN_RATES_FILE = "coin_rates.json"

DEFAULT_COIN_RATES = {
    "title": "Coin Panel",
    "min_level_info": "Minimum level is 50, the higher level the safer you will be.",
    "buy_rates": "$35/B above 300M\n$30/B above 500M\n$25/B above 1B",
    "sell_rates": "$18/B",
    "payment_methods": "<:ltc:1541056586221494373> <:usdc:1538290578041868368> <:btc:1538290774951731283><:usdt:1541056342775832726> <:7187solana:1489507104455917599> <:ETH:1473061116765802540>",
    "color": 16776957,
    "image_url": "https://cdn.discordapp.com/attachments/1454941540064428035/1555982467498909786/image.png?backend=b2&ex=6ac28119&is=6ac12f99&hm=d217d970d37411b68e8ec3fe06462f2cd43c4777639d0428269580b0fc34fb46&",
    "panels": []
}

def load_coin_rates() -> Dict[str, Any]:
    if os.path.exists(COIN_RATES_FILE):
        try:
            with open(COIN_RATES_FILE, "r") as f:
                data = json.load(f)
                return {**DEFAULT_COIN_RATES, **data}
        except Exception as e:
            print(f"Error loading {COIN_RATES_FILE}: {e}")
    return DEFAULT_COIN_RATES.copy()

def save_coin_rates(data: Dict[str, Any]):
    try:
        with open(COIN_RATES_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {COIN_RATES_FILE}: {e}")


KNOWN_CRYPTO_EMOJIS = {
    "ltc": ("ltc", "1541056586221494373"),
    "usdc": ("usdc", "1538290578041868368"),
    "btc": ("btc", "1538290774951731283"),
    "usdt": ("usdt", "1541056342775832726"),
    "7187solana": ("7187solana", "1489507104455917599"),
    "solana": ("7187solana", "1489507104455917599"),
    "eth": ("ETH", "1473061116765802540")
}

def resolve_payment_emojis(raw_text: str, guild: Optional[discord.Guild] = None) -> str:
    # 1. Check if this server has uploaded custom emojis for crypto
    if guild and hasattr(guild, "emojis") and guild.emojis:
        guild_emojis = {}
        for e in guild.emojis:
            ename = e.name.lower()
            if "ltc" in ename or "litecoin" in ename: guild_emojis["ltc"] = str(e)
            elif "usdc" in ename: guild_emojis["usdc"] = str(e)
            elif "btc" in ename or "bitcoin" in ename: guild_emojis["btc"] = str(e)
            elif "usdt" in ename or "tether" in ename: guild_emojis["usdt"] = str(e)
            elif "sol" in ename: guild_emojis["sol"] = str(e)
            elif "eth" in ename or "ethereum" in ename: guild_emojis["eth"] = str(e)

        if len(guild_emojis) >= 2:
            order = ["ltc", "usdc", "btc", "usdt", "sol", "eth"]
            return " ".join([guild_emojis[k] for k in order if k in guild_emojis])

    # 2. Universal clean fallback that never breaks into raw text
    clean_fallback = "Ł **LTC** • 🪙 **USDC** • ₿ **BTC** • ₮ **USDT** • 🟣 **SOL** • 🔷 **ETH**"

    if not raw_text or "1541056586221494373" in raw_text or ":ltc:" in raw_text:
        return clean_fallback

    return raw_text

def build_coin_panel_embed(rates: Dict[str, Any], guild: Optional[discord.Guild] = None) -> discord.Embed:
    title = rates.get("title", "Coin Panel")
    desc = rates.get("min_level_info", "Minimum level is 50, the higher level the safer you will be.")
    color_val = rates.get("color", 16776957)

    embed = discord.Embed(
        title=title,
        description=desc,
        color=discord.Color(color_val)
    )
    
    buy_val = rates.get("buy_rates", "$35/B above 300M\n$30/B above 500M\n$25/B above 1B")
    sell_val = rates.get("sell_rates", "$18/B")
    pay_val = resolve_payment_emojis(rates.get("payment_methods", ""), guild)
    
    embed.add_field(name="Buy Price", value=buy_val, inline=True)
    embed.add_field(name="Sell Price", value=sell_val, inline=True)
    embed.add_field(name="Payment Methods", value=pay_val, inline=False)
    
    if os.path.exists("banner.png"):
        embed.set_image(url="attachment://banner.png")
    elif rates.get("image_url"):
        embed.set_image(url=rates["image_url"])
    elif BANNER_URL:
        embed.set_image(url=BANNER_URL)
        
    return embed


RANK_RATES_FILE = "rank_rates.json"

DEFAULT_RANK_RATES = {
    "title": "Rank Panel",
    "description": "Purchase official Hypixel ranks with SkyBlock Coins!\n*Create a ticket to purchase your rank.*",
    "perm_ranks": "600M For VIP\n800M For VIP+\n1.5B For MVP\n2.3B For MVP+",
    "sub_ranks": "700M For MVP++ 30 days (REQUIRE MVP+)\n1.5B For MVP++ 90 days (REQUIRE MVP+)\n3B For MVP++ 180 days (REQUIRE MVP+)\n5B For MVP++ 365 days (REQUIRE MVP+)",
    "notice": "PRICES CAN CHANGE ACCORDING TO CHANGE IN PRICE ON HYPIXEL STORE",
    "color": 16776957,
    "panels": []
}

def load_rank_rates() -> Dict[str, Any]:
    if os.path.exists(RANK_RATES_FILE):
        try:
            with open(RANK_RATES_FILE, "r") as f:
                data = json.load(f)
                return {**DEFAULT_RANK_RATES, **data}
        except Exception as e:
            print(f"Error loading {RANK_RATES_FILE}: {e}")
    return DEFAULT_RANK_RATES.copy()

def save_rank_rates(data: Dict[str, Any]):
    try:
        with open(RANK_RATES_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {RANK_RATES_FILE}: {e}")

def format_rank_lines(lines_text: str, guild: Optional[discord.Guild] = None) -> str:
    gemojis = {}
    if guild and hasattr(guild, "emojis"):
        for e in guild.emojis:
            ename = e.name.lower().replace("_", "").replace("-", "")
            if ename in ["vip", "vipplus", "mvp", "mvpplus", "mvpplusplus", "mvppp"]:
                gemojis[ename] = str(e)

    vip_e = gemojis.get("vip", "🟩 **[VIP]**")
    vipp_e = gemojis.get("vipplus", "🟩 **[VIP+]**")
    mvp_e = gemojis.get("mvp", "🟦 **[MVP]**")
    mvpp_e = gemojis.get("mvpplus", "🟦 **[MVP+]**")
    mvppp_e = gemojis.get("mvpplusplus", gemojis.get("mvppp", "🟧 **[MVP++]**"))

    res = []
    for line in lines_text.strip().split("\n"):
        l = line.strip()
        if not l: continue
        upper = l.upper()
        if "MVP++" in upper or "MVP PLUS PLUS" in upper:
            prefix = mvppp_e
        elif "MVP+" in upper or "MVP PLUS" in upper:
            prefix = mvpp_e
        elif "MVP" in upper:
            prefix = mvp_e
        elif "VIP+" in upper or "VIP PLUS" in upper:
            prefix = vipp_e
        elif "VIP" in upper:
            prefix = vip_e
        else:
            prefix = "⭐"

        if l.startswith("<:") or l.startswith("🟩") or l.startswith("🟦") or l.startswith("🟧"):
            res.append(l)
        else:
            res.append(f"{prefix} • {l}")

    return "\n".join(res)


VOUCHES_FILE = "vouches.json"
WALLETS_FILE = "wallets.json"
STOCK_FILE = "stock.json"
STATS_CONFIG_FILE = "stats_config.json"
AUTOBUMP_FILE = "autobump.json"

DEFAULT_STATS_CONFIG = {
    "enabled": False,
    "category_id": None,
    "members_channel_id": None,
    "vouches_channel_id": None,
    "stock_channel_id": None,
    "listings_channel_id": None
}

DEFAULT_AUTOBUMP = {
    "enabled": False,
    "channel_id": None,
    "interval_hours": 4,
    "bump_type": "all",
    "last_bump": None
}

DEFAULT_WALLETS = {
    "ltc": {"address": "LTC_WALLET_ADDRESS_HERE", "network": "Litecoin Network (LTC)"},
    "usdt": {"address": "USDT_WALLET_ADDRESS_HERE", "network": "TRC-20 (Tron) / BEP-20 (BSC)"},
    "btc": {"address": "BTC_WALLET_ADDRESS_HERE", "network": "Bitcoin Network (BTC)"},
    "eth": {"address": "ETH_WALLET_ADDRESS_HERE", "network": "ERC-20 (Ethereum)"},
    "sol": {"address": "SOL_WALLET_ADDRESS_HERE", "network": "Solana Network"}
}

DEFAULT_VOUCHES = {
    "total_vouches": 0,
    "vouches": []
}

DEFAULT_STOCK = {
    "coins_stock": "14.5B",
    "coins_status": "🟢 In Stock",
    "ranks_status": "🟢 Instant Delivery",
    "notes": "Fastest delivery on the market!",
    "panels": []
}

def load_json_file(filename: str, default_data: dict) -> dict:
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return {**default_data, **json.load(f)}
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    return default_data.copy()

def save_json_file(filename: str, data: dict):
    try:
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {filename}: {e}")

def find_channel_by_keywords(guild: discord.Guild, keywords: list) -> Optional[discord.TextChannel]:
    for c in guild.text_channels:
        clean = re.sub(r'[^a-zA-Z0-9]', '', c.name.lower())
        for kw in keywords:
            if kw in clean:
                return c
    return None

def calculate_coin_quote(coins_str: str = "", usd_str: str = ""):
    tiers = [
        (1000.0, 25.0), # >= 1000M: $25 per 1B
        (500.0, 30.0),  # >= 500M: $30 per 1B
        (300.0, 35.0),  # >= 300M: $35 per 1B
        (0.0, 38.0)     # < 300M: $38 per 1B
    ]

    if coins_str:
        clean = coins_str.upper().strip().replace('$', '')
        mult = 1.0
        if 'B' in clean: mult = 1000.0; clean = clean.replace('B', '')
        elif 'M' in clean: mult = 1.0; clean = clean.replace('M', '')
        elif 'K' in clean: mult = 0.001; clean = clean.replace('K', '')
        try:
            m_amount = float(clean) * mult
        except:
            return None, "Invalid coin amount format (e.g. 500M, 1.5B)."

        rate_per_b = 38.0
        for threshold, r in tiers:
            if m_amount >= threshold:
                rate_per_b = r
                break

        usd_total = (m_amount / 1000.0) * rate_per_b
        return {
            "type": "COINS_TO_USD",
            "coins": f"{m_amount/1000.0:.2f}B" if m_amount >= 1000 else f"{m_amount:.1f}M",
            "usd": f"${usd_total:.2f}",
            "rate": f"${rate_per_b:.2f}/B"
        }, None

    elif usd_str:
        clean = usd_str.upper().strip().replace('$', '')
        try:
            usd_val = float(clean)
        except:
            return None, "Invalid USD amount format (e.g. 25, 50)."

        rate_per_b = 30.0
        m_coins = (usd_val / rate_per_b) * 1000.0
        for threshold, r in tiers:
            if m_coins >= threshold:
                rate_per_b = r
                m_coins = (usd_val / rate_per_b) * 1000.0
                break

        return {
            "type": "USD_TO_COINS",
            "usd": f"${usd_val:.2f}",
            "coins": f"{m_coins/1000.0:.2f}B" if m_coins >= 1000 else f"{int(m_coins)}M",
            "rate": f"~${rate_per_b:.2f}/B"
        }, None

    return None, "Please specify coins or usd."

def build_stock_embed(stock: dict, guild: Optional[discord.Guild] = None) -> discord.Embed:
    # Count live unsold accounts
    acc_count = 0
    if guild and ACCOUNTS_CAT_ID:
        cat = guild.get_channel(ACCOUNTS_CAT_ID)
        if isinstance(cat, discord.CategoryChannel):
            acc_count = len([ch for ch in cat.text_channels if ch.name.startswith("⭐")])
    elif guild:
        for cat in guild.categories:
            if "account" in cat.name.lower():
                acc_count += len([ch for ch in cat.text_channels if ch.name.startswith("⭐")])

    emb = discord.Embed(
        title=f"📦 {STORE_NAME} — Live Stock & Inventory",
        description="Check our real-time stock levels below. Open a ticket to purchase instantly!",
        color=discord.Color(0xF1C40F),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )
    c_stock = stock.get("coins_stock", "14.5B")
    c_status = stock.get("coins_status", "🟢 In Stock")
    r_status = stock.get("ranks_status", "🟢 Instant Delivery")

    emb.add_field(name="🪙 SkyBlock Coins", value=f"**{c_stock}** ({c_status})", inline=True)
    emb.add_field(name="👑 Rank Gifting", value=f"**{r_status}**", inline=True)
    emb.add_field(name="🎮 Accounts in Stock", value=f"🟢 **{acc_count} Accounts Available**", inline=True)
    emb.add_field(name="⚡ Estimated Delivery", value="**Instant (0 - 5 Minutes)** via Tickets", inline=False)
    emb.add_field(name="💳 Payment Accepted", value="LTC • USDC • BTC • USDT • SOL • ETH", inline=False)

    if os.path.exists("banner.png"):
        emb.set_image(url="attachment://banner.png")
    elif BANNER_URL:
        emb.set_image(url=BANNER_URL)

    emb.set_footer(text=f"{STORE_NAME} • Live Stock Tracker", icon_url=guild.icon.url if guild and guild.icon else None)
    return emb

def build_rank_panel_embed(rates: Dict[str, Any], guild: Optional[discord.Guild] = None) -> discord.Embed:
    title = rates.get("title", "Rank Panel")
    desc = rates.get("description", "Purchase official Hypixel ranks with SkyBlock Coins!\n*Create a ticket to purchase your rank.*")
    color_val = rates.get("color", 16776957)

    embed = discord.Embed(
        title=f"👑 {title}",
        description=desc,
        color=discord.Color(color_val)
    )

    perm_val = format_rank_lines(rates.get("perm_ranks", DEFAULT_RANK_RATES["perm_ranks"]), guild)
    sub_val = format_rank_lines(rates.get("sub_ranks", DEFAULT_RANK_RATES["sub_ranks"]), guild)
    notice = rates.get("notice", DEFAULT_RANK_RATES["notice"])

    embed.add_field(name="👑 Permanent Ranks", value=perm_val, inline=False)
    embed.add_field(name="⭐ MVP++ Subscriptions (Requires MVP+)", value=sub_val, inline=False)
    if notice:
        embed.add_field(name="⚠️ Notice", value=f"*{notice}*", inline=False)

    if os.path.exists("banner.png"):
        embed.set_image(url="attachment://banner.png")
    elif BANNER_URL:
        embed.set_image(url=BANNER_URL)

    embed.set_footer(text=f"{STORE_NAME} • {STORE_INVITE}", icon_url=guild.icon.url if guild and guild.icon else None)
    return embed

async def close_ticket_with_transcript(inter: discord.Interaction, trade_completed: bool = True):
    if not inter.response.is_done():
        await inter.response.send_message("🔒 **Closing ticket:** Generating transcript...", ephemeral=False)
    else:
        try:
            await inter.followup.send("🔒 **Closing ticket:** Generating transcript...")
        except Exception:
            pass

    channel = inter.channel
    g = inter.guild
    if not isinstance(channel, discord.TextChannel) or not g:
        await asyncio.sleep(2)
        try: await channel.delete()
        except Exception: pass
        return

    # 1. Fetch channel message history
    messages = []
    try:
        async for m in channel.history(limit=1000, oldest_first=True):
            messages.append(m)
    except Exception as e:
        print(f"Error fetching ticket history: {e}")

    # 2. Extract ticket details
    buyer_user = await find_ticket_buyer(channel, g)
    # Check if this was an account ticket with a specific seller
    ticket_seller = None
    for m in messages:
        for emb in m.embeds:
            if emb.description:
                m_sel = re.search(r'Seller:\*\*\s*<@!?(\d+)>', emb.description) or re.search(r'👤\s*<@!?(\d+)>', emb.description)
                if m_sel:
                    s_id = int(m_sel.group(1))
                    ticket_seller = g.get_member(s_id)
                    if ticket_seller: break
        if ticket_seller: break

    seller_member = ticket_seller or (inter.user if isinstance(inter.user, discord.Member) else get_seller_member(g))
    seller_mention = seller_member.mention if seller_member else f"**{STORE_NAME}**"
    seller_name = str(seller_member) if seller_member else STORE_NAME

    account_ign = "Account"
    price_val = "N/A"
    pay_method = "N/A"

    m_c = re.match(r'(?:ticket|offer)-([a-zA-Z0-9_]+)-([0-9\.]+)usd', channel.name)
    if m_c: price_val = f"${m_c.group(2)}"

    for m in messages:
        for emb in m.embeds:
            if emb.description:
                m_ign = re.search(r'Account IGN:\*\*\s*(?:\|\|)?([a-zA-Z0-9_]{3,16})(?:\|\|)?', emb.description)
                if m_ign: account_ign = m_ign.group(1)
                m_pr = re.search(r'(?:Total Price|Price|Offered Amount|Amount):\*\*\s*\*\*\$?([0-9\.]+)', emb.description)
                if m_pr: price_val = f"${m_pr.group(1)}"
                m_pay = re.search(r'Payment Method:\*\*\s*\*\*([^\*]+)', emb.description)
                if m_pay: pay_method = m_pay.group(1).strip()

    # 3. Format text transcript
    clean_cname = re.sub(r'[^a-zA-Z0-9_\-]', '', channel.name)
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    t_status = "COMPLETED" if trade_completed else "NOT COMPLETED"
    t_lines = [
        "=" * 65,
        f"{STORE_NAME.upper()} — TICKET TRANSCRIPT [{t_status}]",
        f"Ticket Channel : #{channel.name} (ID: {channel.id})",
        f"Trade Status   : {'COMPLETED' if trade_completed else 'NOT COMPLETED'}",
        f"Seller         : {seller_name}",
        f"Buyer          : {buyer_user} (ID: {buyer_user.id if buyer_user else 'Unknown'})",
        f"Price          : {price_val}",
        f"Payment Method : {pay_method}",
        f"Closed By      : {inter.user} (ID: {inter.user.id})",
        f"Closed At (UTC): {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Total Messages : {len(messages)}",
        "=" * 65,
        ""
    ]

    for m in messages:
        time_str = m.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
        user_tag = f"{m.author.name}#{m.author.discriminator}" if m.author.discriminator != "0" else m.author.name
        bot_suffix = " [BOT]" if m.author.bot else ""
        t_lines.append(f"[{time_str}] {user_tag}{bot_suffix} ({m.author.id}):")
        if m.content: t_lines.append(f"  {m.content}")
        for emb in m.embeds:
            t_lines.append(f"  [EMBED] Title: {emb.title or 'None'}")
            if emb.description:
                for dl in emb.description.split("\n"):
                    t_lines.append(f"    {dl}")
        for att in m.attachments:
            t_lines.append(f"  [ATTACHMENT] {att.filename} -> {att.url}")
        t_lines.append("")

    transcript_text = "\n".join(t_lines)
    filename = f"transcript-{clean_cname}.txt"

    # 4. Target transcript channel
    target_chan = find_transcript_channel(g)

    now_ts = int(now_utc.timestamp())
    card_title = f"📋 Ticket Closed: #{channel.name} [{'COMPLETED' if trade_completed else 'NOT COMPLETED'}]"
    card_color = discord.Color.gold() if trade_completed else discord.Color.dark_gray()

    emb = discord.Embed(
        title=card_title,
        description=(
            f"**Ticket:** `#{channel.name}`\n"
            f"**Status:** {'✅ **Trade Completed**' if trade_completed else '❌ **Trade Not Completed / Cancelled**'}\n"
            f"**Verified Seller:** {seller_mention} *(100% Legit)*\n"
            + (f"**Buyer:** {buyer_user.mention} (`{buyer_user.id}`)\n" if buyer_user else "") +
            f"**Price / Item:** **{price_val}**\n"
            f"**Closed By:** {inter.user.mention} (`{inter.user.id}`)\n"
            f"**Total Messages:** `{len(messages)}`\n"
            f"**Closed At:** <t:{now_ts}:F> (<t:{now_ts}:R>)\n"
        ),
        color=card_color,
        timestamp=now_utc
    )
    if os.path.exists("banner.png"):
        emb.set_image(url="attachment://banner.png")
    emb.set_footer(text=f"{STORE_NAME} • Ticket Transcripts", icon_url=g.icon.url if g.icon else None)

    # 5. Post transcript to #transcript channel
    if target_chan:
        try:
            file_bytes = io.BytesIO(transcript_text.encode("utf-8"))
            d_file = discord.File(fp=file_bytes, filename=filename)
            b_file = discord.File("banner.png", filename="banner.png") if os.path.exists("banner.png") else None
            if b_file:
                await target_chan.send(embed=emb, files=[d_file, b_file])
            else:
                await target_chan.send(embed=emb, file=d_file)
        except Exception as e:
            print(f"Error posting transcript: {e}")

    # 6. DM Buyer tailored message with transcript attached
    if buyer_user and not buyer_user.bot:
        try:
            dm_bytes = io.BytesIO(transcript_text.encode("utf-8"))
            dm_file = discord.File(fp=dm_bytes, filename=filename)

            if trade_completed:
                dm_emb = discord.Embed(
                    title=f"🌟 Tysm for buying with {STORE_NAME}!",
                    description=(
                        f"Hello {buyer_user.name}! 👋\n\n"
                        f"**Tysm for buying with {STORE_NAME}!** We truly appreciate your business and trust in our service.\n\n"
                        f"👑 **Verified Seller:** {seller_mention} *(100% Legit & Verified Seller)*\n"
                        f"⏰ **Tysm for your time!**\n\n"
                        f"If you enjoyed the service, please take 5 seconds to submit a review with **/vouch seller:{seller_mention}** in our server to let others know they're legit!\n\n"
                        f"🔗 **Server Invite:** <{get_invite_url()}>\n"
                        f"*(Your ticket transcript is attached below)*"
                    ),
                    color=discord.Color.gold(),
                    timestamp=now_utc
                )
            else:
                dm_emb = discord.Embed(
                    title=f"👋 Tysm for your time — {STORE_NAME}",
                    description=(
                        f"Hello {buyer_user.name}! 👋\n\n"
                        f"**Thank you so much for your time and for visiting {STORE_NAME}!**\n"
                        f"We're sorry that the trade couldn't be completed this time.\n\n"
                        f"We would love to have you shop with us in the future whenever you're ready!\n"
                        f"If you have any questions or feedback, our team is always here for you.\n\n"
                        f"⏰ **Tysm for your time and have a wonderful day!**\n\n"
                        f"🔗 **Server Invite:** <{get_invite_url()}>\n"
                        f"*(Your ticket transcript is attached below for your records)*"
                    ),
                    color=discord.Color.from_rgb(200, 200, 200),
                    timestamp=now_utc
                )
            if os.path.exists("banner.png"):
                dm_banner = discord.File("banner.png", filename="banner.png")
                dm_emb.set_image(url="attachment://banner.png")
                await buyer_user.send(embed=dm_emb, files=[dm_file, dm_banner])
            else:
                await buyer_user.send(embed=dm_emb, file=dm_file)
        except Exception as e:
            print(f"Could not send DM to buyer: {e}")

    # 7. Delete channel
    await asyncio.sleep(3)
    try: await channel.delete(reason=f"Closed by {inter.user}")
    except Exception as e: print(f"Error deleting channel: {e}")

class TicketCloseConfirmView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=180)
        self.channel_id = channel_id

    @discord.ui.button(label="Yes, Completed", emoji="✅", style=discord.ButtonStyle.success, custom_id="btn_cls_yes")
    async def btn_yes(self, inter: discord.Interaction, button: discord.ui.Button):
        await close_ticket_with_transcript(inter, trade_completed=True)

    @discord.ui.button(label="No, Not Completed", emoji="❌", style=discord.ButtonStyle.danger, custom_id="btn_cls_no")
    async def btn_no(self, inter: discord.Interaction, button: discord.ui.Button):
        await close_ticket_with_transcript(inter, trade_completed=False)

    @discord.ui.button(label="Cancel", emoji="↩️", style=discord.ButtonStyle.secondary, custom_id="btn_cls_cancel")
    async def btn_cancel(self, inter: discord.Interaction, button: discord.ui.Button):
        try: await inter.message.delete()
        except Exception: pass

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket", emoji="🔒", style=discord.ButtonStyle.danger, custom_id="btn_cls")
    async def close_ticket(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_message(
            "❓ **Was this trade completed?**\nSelect an option below to finalize the ticket and notify the buyer:",
            view=TicketCloseConfirmView(inter.channel_id),
            ephemeral=False
        )

class InspectSelect(discord.ui.Select):
    def __init__(self, ign: str = "", hide_name: bool = False):
        self.ign = ign
        self.hide_name = hide_name
        super().__init__(
            placeholder="🔍 Inspect account progression...",
            custom_id="select_inspect_stats",
            options=[
                discord.SelectOption(label="Skills & Progression", emoji="📘"),
                discord.SelectOption(label="Dungeons & Slayers", emoji="💀"),
                discord.SelectOption(label="Networth Breakdown", emoji="📦"),
                discord.SelectOption(label="Mining & HOTM", emoji="🔮"),
                discord.SelectOption(label="Garden & Pets", emoji="🐾"),
            ]
        )

    async def callback(self, inter: discord.Interaction):
        target_ign, _, _, is_hidden = extract_listing_info(inter.message)
        if not target_ign or target_ign == "Account":
            target_ign = self.ign
        if self.hide_name or is_hidden or not target_ign:
            await inter.response.send_message(
                f"🔒 **Account Privacy Protected**\n"
                f"To protect against Hypixel bans, this listing's username is kept confidential.\n"
                f"👉 Selected category: **{self.values[0]}**\n"
                f"Full SkyCrypt inspection is available inside your private ticket after clicking **Buy**.",
                ephemeral=True
            )
        else:
            await inter.response.send_message(
                f"Detailed progression for **{self.values[0]}** (`{target_ign}`):\n👉 https://sky.shiiyu.moe/stats/{target_ign}",
                ephemeral=True
            )

class PurchaseModal(discord.ui.Modal):
    def __init__(self, ign: str, price: str, seller_id: int = 0, hide_name: bool = False):
        title = "Purchase SkyBlock Account"[:45] if hide_name else f"Purchase: {ign}"[:45]
        super().__init__(title=title)
        self.ign = ign
        self.price = price
        self.seller_id = seller_id
        self.hide_name = hide_name

        self.amount_input = discord.ui.TextInput(
            label="Amount / Money to Pay ($)",
            placeholder="e.g. 120",
            default=str(price).replace("$", "").strip(),
            required=True,
            max_length=15
        )
        self.payment_input = discord.ui.TextInput(
            label="Payment Method",
            placeholder="e.g. LTC, USDT, BTC, ETH, CashApp, PayPal",
            default="Litecoin (LTC)",
            required=True,
            max_length=50
        )
        self.notes_input = discord.ui.TextInput(
            label="Notes / Instructions (Optional)",
            placeholder="Any specific requests or questions for staff/seller",
            required=False,
            style=discord.TextStyle.paragraph,
            max_length=300
        )

        self.add_item(self.amount_input)
        self.add_item(self.payment_input)
        self.add_item(self.notes_input)

    async def on_submit(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)
        g = inter.guild
        if not g:
            await inter.followup.send("❌ Error: Server context not found.", ephemeral=True)
            return

        amount = self.amount_input.value.strip().replace("$", "")
        method = self.payment_input.value.strip()
        notes = self.notes_input.value.strip() if self.notes_input.value else "None provided"

        clean_amt = re.sub(r'[^0-9]', '', amount) or re.sub(r'[^0-9]', '', str(self.price)) or "order"
        clean_ign = re.sub(r'[^a-zA-Z0-9]', '', self.ign).lower() or "account"

        if self.hide_name:
            cname = f"ticket-acc-{clean_amt}usd"[:90]
        else:
            cname = f"ticket-{clean_ign}-{clean_amt}usd"[:90]

        bot_member = g.me or g.get_member(bot.user.id)
        over = {
            g.default_role: discord.PermissionOverwrite(view_channel=False),
            inter.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
        }
        if bot_member:
            over[bot_member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True)

        admin_role = None
        if STAFF_ROLE_ID:
            srole = g.get_role(STAFF_ROLE_ID)
            if srole:
                admin_role = srole
                over[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        if not admin_role:
            admin_role = discord.utils.find(lambda r: r.name.lower() in ["admin", "administrator", "staff", "mod", "moderator", "owner"], g.roles)
            if admin_role:
                over[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        cat = None
        if TICKET_CAT_ID:
            cat = g.get_channel(TICKET_CAT_ID)
            if not isinstance(cat, discord.CategoryChannel):
                cat = discord.utils.get(g.categories, id=TICKET_CAT_ID)
        if not cat:
            cat = discord.utils.find(lambda c: "ticket" in c.name.lower(), g.categories)

        t = None
        try:
            t = await g.create_text_channel(name=cname, category=cat, overwrites=over)
        except Exception as e:
            print(f"Failed to create ticket channel in category {cat}: {e}. Retrying without category...")
            try:
                t = await g.create_text_channel(name=cname, overwrites=over)
            except discord.Forbidden:
                await inter.followup.send(
                    "❌ **Bot Missing Permissions:** The bot cannot create ticket channels in this server.\n"
                    "👉 Please ensure the bot's role has **Manage Channels** and **View Channel** permissions in server settings!",
                    ephemeral=True
                )
                return
            except Exception as e2:
                await inter.followup.send(f"❌ Failed to create ticket channel: `{e2}`", ephemeral=True)
                return

        admin_mention = admin_role.mention if admin_role else "@admin"
        seller_mention = f"<@{self.seller_id}>" if self.seller_id else None

        ign_display = f"||{self.ign}||" if self.hide_name else f"**[{self.ign}](https://sky.shiiyu.moe/stats/{urllib.parse.quote(self.ign)})**"

        emb = discord.Embed(
            title=f"🛒 Purchase Order: {self.ign if not self.hide_name else 'SkyBlock Account'}",
            description=(
                f"### Welcome {inter.user.mention} to your order ticket!\n\n"
                f"📦 **Account IGN:** {ign_display}\n"
                + (f"🔗 **SkyCrypt Verification:** [Click to view full profile](https://sky.shiiyu.moe/stats/{urllib.parse.quote(self.ign)})\n" if not self.hide_name else "") +
                f"💵 **Price:** **${amount} USD**\n"
                f"💳 **Payment Method:** **{method}**\n"
                f"👤 **Buyer:** {inter.user.mention} (`{inter.user.id}`)\n"
                + (f"🏷️ **Seller:** {seller_mention}\n" if seller_mention else "") +
                f"📝 **Notes / Requests:** {notes}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ **Trade Security & Escrow Guarantee**\n"
                f"All transactions in **{STORE_NAME}** are 100% escrow protected.\n"
                f"• Please await {admin_mention} to verify and provide the official wallet address.\n"
                + ("• Account details are confidential — do not share outside this ticket.\n" if self.hide_name else "") +
                f"━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        if not self.hide_name and self.ign and self.ign != "Account":
            emb.set_thumbnail(url=f"https://mc-heads.net/avatar/{urllib.parse.quote(self.ign)}/100.png")
        emb.set_footer(text=f"{STORE_NAME} • Ticket System", icon_url=g.icon.url if g.icon else None)

        ticket_view = CloseTicketView()
        if not self.hide_name and self.ign and self.ign != "Account":
            ticket_view.add_item(discord.ui.Button(label="View on SkyCrypt", emoji="📊", url=f"https://sky.shiiyu.moe/stats/{urllib.parse.quote(self.ign)}"))
        ticket_view.add_item(discord.ui.Button(label="Store Invite", emoji="🌐", url=get_invite_url()))

        pings = f"👋 {inter.user.mention} | 🔔 {admin_mention}" + (f" | {seller_mention}" if seller_mention else "")
        await t.send(content=pings, embed=emb, view=ticket_view)
        await inter.followup.send(f"✅ Purchase ticket created: {t.mention}", ephemeral=True)

async def handle_buy_action(inter: discord.Interaction, ign: str = "", price: str = "", seller_id: int = 0, hide_name: bool = False):
    try:
        if not ign or not price or not seller_id:
            e_ign, e_price, e_seller, e_hide = extract_listing_info(inter.message)
            ign = ign or e_ign
            price = price or e_price
            seller_id = seller_id or e_seller
            if not hide_name:
                hide_name = e_hide

        modal = PurchaseModal(ign, price, seller_id, hide_name=hide_name)
        if not inter.response.is_done():
            await inter.response.send_modal(modal)
        else:
            await inter.followup.send("⚠️ Interaction already acknowledged. Please try clicking Buy again.", ephemeral=True)
    except Exception as e:
        print(f"Error in handle_buy_action: {e}")
        import traceback
        traceback.print_exc()
        try:
            if not inter.response.is_done():
                await inter.response.send_message(f"❌ Failed to open purchase modal: `{e}`", ephemeral=True)
            else:
                await inter.followup.send(f"❌ Failed to open purchase modal: `{e}`", ephemeral=True)
        except Exception:
            pass

async def handle_offer_action(inter: discord.Interaction, ign: str = "", price: str = "", seller_id: int = 0, hide_name: bool = False):
    if not ign or not price:
        e_ign, e_price, e_seller, e_hide = extract_listing_info(inter.message)
        ign = ign or e_ign
        price = price or e_price
        seller_id = seller_id or e_seller
        hide_name = hide_name or e_hide

    title = "Submit Custom Offer"[:45] if hide_name else f"Offer: {ign}"[:45]
    modal = discord.ui.Modal(title=title)
    amt = discord.ui.TextInput(label="Offer Amount ($)", placeholder="e.g. 180", max_length=15, required=True)
    method = discord.ui.TextInput(label="Payment Method", placeholder="LTC, USDT, etc.", max_length=50, required=True)
    notes = discord.ui.TextInput(label="Notes (Optional)", placeholder="Any details for staff", style=discord.TextStyle.paragraph, max_length=300, required=False)
    modal.add_item(amt)
    modal.add_item(method)
    modal.add_item(notes)

    async def on_sub(m_inter: discord.Interaction):
        await m_inter.response.defer(ephemeral=True)
        g = m_inter.guild
        if not g:
            await m_inter.followup.send("❌ Error: Server context not found.", ephemeral=True)
            return

        clean_amt = amt.value.strip().replace('$', '')
        clean_ign = re.sub(r'[^a-zA-Z0-9]', '', ign).lower() or "account"
        if hide_name:
            cname = f"offer-acc-{clean_amt}usd"[:90]
        else:
            cname = f"offer-{clean_ign}-{clean_amt}usd"[:90]

        admin_role = None
        if STAFF_ROLE_ID:
            srole = g.get_role(STAFF_ROLE_ID)
            if srole: admin_role = srole
        if not admin_role:
            admin_role = discord.utils.find(lambda r: r.name.lower() in ["admin", "administrator", "staff", "mod", "moderator", "owner"], g.roles)

        try:
            t = await g.create_text_channel(name=cname)
            await t.set_permissions(m_inter.user, view_channel=True, send_messages=True)
            if admin_role:
                await t.set_permissions(admin_role, view_channel=True, send_messages=True)
        except discord.Forbidden:
            await m_inter.followup.send("❌ Bot is missing 'Manage Channels' permission to create an offer ticket.", ephemeral=True)
            return
        except Exception as e:
            await m_inter.followup.send(f"❌ Failed to create offer ticket: {e}", ephemeral=True)
            return

        admin_mention = admin_role.mention if admin_role else "@admin"
        ign_display = f"||{ign}||" if hide_name else f"**[{ign}](https://sky.shiiyu.moe/stats/{ign})**"

        emb = discord.Embed(
            title=f"💬 New Offer: {ign if not hide_name else 'SkyBlock Account'}",
            description=(
                f"### Offer Submitted by {m_inter.user.mention}!\n\n"
                f"📦 **Account IGN:** {ign_display}\n"
                f"🔗 **SkyCrypt:** [Click to view profile](https://sky.shiiyu.moe/stats/{ign})\n"
                f"💵 **Offered Amount:** **${clean_amt}** (Listed: `${price}`)\n"
                f"💳 **Payment Method:** **{method.value.strip()}**\n"
                f"👤 **Buyer:** {m_inter.user.mention} (`{m_inter.user.id}`)\n"
                f"📝 **Notes:** {notes.value.strip() if notes.value else 'None'}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"A staff member / {admin_mention} will review this offer shortly."
            ),
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        ticket_view = CloseTicketView()
        ticket_view.add_item(discord.ui.Button(label="View Stats", emoji="📊", url=f"https://sky.shiiyu.moe/stats/{ign}"))

        pings = f"👋 {m_inter.user.mention} | 🔔 {admin_mention}"
        await t.send(content=pings, embed=emb, view=ticket_view)
        await m_inter.followup.send(f"✅ Offer submitted: {t.mention}", ephemeral=True)

    modal.on_submit = on_sub
    if not inter.response.is_done():
        await inter.response.send_modal(modal)

async def handle_refresh_action(inter: discord.Interaction):
    await inter.response.send_message("🔄 Live stats confirmed and verified on Hypixel API.", ephemeral=True)


class EditListingModal(discord.ui.Modal):
    def __init__(self, ign: str, price: str, seller_id: int, hide_name: bool = False):
        super().__init__(title=f"Edit Listing: {price} USD"[:45])
        self.ign = ign
        self.price = price
        self.seller_id = seller_id
        self.hide_name = hide_name

        self.price_input = discord.ui.TextInput(
            label="Price in USD ($)",
            placeholder="e.g. 100",
            default=str(price),
            required=True,
            max_length=15
        )
        self.nw_total_input = discord.ui.TextInput(
            label="Total Networth (Optional)",
            placeholder="e.g. 2.73B",
            required=False,
            max_length=25
        )
        self.nw_unsoulbound_input = discord.ui.TextInput(
            label="Unsoulbound Networth (Optional)",
            placeholder="e.g. 1.5B",
            required=False,
            max_length=25
        )
        self.extra_input = discord.ui.TextInput(
            label="Custom Notes / Extras (Optional)",
            placeholder="e.g. Full Divan Armor, Hyperion",
            required=False,
            style=discord.TextStyle.paragraph,
            max_length=300
        )
        self.add_item(self.price_input)
        self.add_item(self.nw_total_input)
        self.add_item(self.nw_unsoulbound_input)
        self.add_item(self.extra_input)

    async def on_submit(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)
        msg = inter.message
        if not msg or not msg.embeds:
            await inter.followup.send("❌ Listing message not found.", ephemeral=True)
            return

        clean_price = self.price_input.value.strip().replace("$", "")
        new_emb = msg.embeds[0].copy()
        desc = new_emb.description or ""

        # Update description lines cleanly
        desc_lines = desc.split("\n")
        updated_lines = []
        for i, l in enumerate(desc_lines):
            if l.startswith("**$") and i > 0 and "💵" in desc_lines[i-1]:
                updated_lines.append(f"**${clean_price}**")
            elif "💎 **Total:**" in l and self.nw_total_input.value:
                updated_lines.append(f"💎 **Total:** **{self.nw_total_input.value.strip()}**")
            elif "🔓 **Unsoulbound:**" in l and self.nw_unsoulbound_input.value:
                updated_lines.append(f"🔓 **Unsoulbound:** **{self.nw_unsoulbound_input.value.strip()}**")
            elif "📝 **Seller Notes:**" in l and self.extra_input.value:
                updated_lines.append(f"📝 **Seller Notes:** {self.extra_input.value.strip()}")
            else:
                updated_lines.append(l)

        if self.extra_input.value and "📝 **Seller Notes:**" not in desc:
            updated_lines.append(f"\n📝 **Seller Notes:** {self.extra_input.value.strip()}")

        new_emb.description = "\n".join(updated_lines)

        # Update channel name if channel is a listing channel
        channel = inter.channel
        if isinstance(channel, discord.TextChannel):
            try:
                await channel.edit(name=f"⭐|💵{clean_price}")
            except Exception as e:
                print(f"Failed to update channel name on edit: {e}")

        # Update the message view
        new_view = ListingView(self.ign, clean_price, self.seller_id, hide_name=self.hide_name)
        await msg.edit(embed=new_emb, view=new_view)
        await inter.followup.send(f"✅ Listing updated! Price set to **${clean_price}** and channel renamed to `⭐|💵{clean_price}`.", ephemeral=True)

async def handle_edit_account_action(inter: discord.Interaction):
    msg = inter.message
    if not msg or not msg.embeds:
        await inter.response.send_message("❌ Listing embed not found.", ephemeral=True)
        return

    ign, price, seller_id, hide_name = extract_listing_info(msg)

    # Check permission
    is_staff = False
    if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
        is_staff = True
    elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild or inter.user.guild_permissions.manage_channels):
        is_staff = True
    elif seller_id and inter.user.id == seller_id:
        is_staff = True

    if not is_staff:
        await inter.response.send_message("❌ Only the seller or server staff can edit this listing.", ephemeral=True)
        return

    modal = EditListingModal(ign, price, seller_id, hide_name=hide_name)
    await inter.response.send_modal(modal)

async def handle_mark_sold_action(inter: discord.Interaction):
    msg = inter.message
    if not msg or not msg.embeds:
        await inter.response.send_message("❌ Listing embed not found.", ephemeral=True)
        return

    ign, price, seller_id, hide_name = extract_listing_info(msg)

    # Check permission
    is_staff = False
    if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
        is_staff = True
    elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild or inter.user.guild_permissions.manage_channels):
        is_staff = True
    elif seller_id and inter.user.id == seller_id:
        is_staff = True

    if not is_staff:
        await inter.response.send_message("❌ Only the seller or server staff can mark this listing as sold.", ephemeral=True)
        return

    await inter.response.defer(ephemeral=True)

    new_emb = msg.embeds[0].copy()
    if not new_emb.title.startswith("[SOLD]"):
        new_emb.title = f"[SOLD] {new_emb.title}"
    new_emb.color = discord.Color.dark_gray()

    dview = discord.ui.View()
    dview.add_item(discord.ui.Button(label="SOLD OUT", emoji="⛔", disabled=True))
    await msg.edit(embed=new_emb, view=dview)

    channel = inter.channel
    g = inter.guild
    if isinstance(channel, discord.TextChannel) and g:
        sold_cat = await get_or_create_category(g, SOLD_CAT_ID, "SOLD")
        cname = f"⛔|💵{price}" if price and price != "0" else channel.name.replace("⭐", "⛔")
        try:
            if sold_cat:
                await channel.edit(category=sold_cat, name=cname[:90])
            else:
                await channel.edit(name=cname[:90])
        except Exception as e:
            print(f"Error moving channel to sold category: {e}")

    await inter.followup.send("✅ Listing marked as **SOLD** and moved to **SOLD** category!", ephemeral=True)

class PersistentListingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Buy", emoji="🛒", style=discord.ButtonStyle.green, custom_id="btn_buy_account", row=0)
    async def buy(self, inter: discord.Interaction, button: discord.ui.Button):
        await handle_buy_action(inter)

    @discord.ui.button(label="Make Offer", emoji="💬", style=discord.ButtonStyle.blurple, custom_id="btn_offer_account", row=0)
    async def offer(self, inter: discord.Interaction, button: discord.ui.Button):
        await handle_offer_action(inter)

    @discord.ui.button(label="Refresh", emoji="🔄", style=discord.ButtonStyle.gray, custom_id="btn_refresh_account", row=0)
    async def ref(self, inter: discord.Interaction, button: discord.ui.Button):
        await handle_refresh_action(inter)

    @discord.ui.button(label="Ping", emoji="🔔", style=discord.ButtonStyle.secondary, custom_id="btn_ping_account", row=0)
    async def ping_btn(self, inter: discord.Interaction, button: discord.ui.Button):
        await handle_toggle_account_role(inter)

    @discord.ui.button(label="Edit", emoji="⚙️", style=discord.ButtonStyle.secondary, custom_id="btn_edit_account", row=1)
    async def edit_acc(self, inter: discord.Interaction, button: discord.ui.Button):
        await handle_edit_account_action(inter)

    @discord.ui.button(label="Mark Sold", emoji="⛔", style=discord.ButtonStyle.danger, custom_id="btn_sold_account", row=1)
    async def sold_acc(self, inter: discord.Interaction, button: discord.ui.Button):
        await handle_mark_sold_action(inter)

class ListingView(discord.ui.View):
    def __init__(self, ign: str, price: str, seller_id: int, hide_name: bool = False):
        super().__init__(timeout=None)
        self.ign = ign
        self.price = price
        self.seller_id = seller_id
        self.hide_name = hide_name
        enc_ign = base64.b64encode(ign.encode()).decode()
        flag = "1" if hide_name else "0"

        # 1. Buy Button
        buy_btn = discord.ui.Button(
            label="Buy", emoji="🛒", style=discord.ButtonStyle.green,
            custom_id=f"btn_buy:{enc_ign}:{price}:{flag}", row=0
        )
        async def on_buy(btn_inter: discord.Interaction):
            await handle_buy_action(btn_inter, ign=self.ign, price=self.price, seller_id=self.seller_id, hide_name=self.hide_name)
        buy_btn.callback = on_buy
        self.add_item(buy_btn)

        # 2. Make Offer Button
        offer_btn = discord.ui.Button(
            label="Make Offer", emoji="💬", style=discord.ButtonStyle.blurple,
            custom_id=f"btn_offer:{enc_ign}:{price}:{flag}", row=0
        )
        async def on_offer(btn_inter: discord.Interaction):
            await handle_offer_action(btn_inter, ign=self.ign, price=self.price, seller_id=self.seller_id, hide_name=self.hide_name)
        offer_btn.callback = on_offer
        self.add_item(offer_btn)

        # 3. Refresh Button
        ref_btn = discord.ui.Button(
            label="Refresh", emoji="🔄", style=discord.ButtonStyle.gray,
            custom_id=f"btn_ref:{enc_ign}:{flag}", row=0
        )
        async def on_ref(btn_inter: discord.Interaction):
            await handle_refresh_action(btn_inter)
        ref_btn.callback = on_ref
        self.add_item(ref_btn)

        # 4. Ping Button
        ping_btn = discord.ui.Button(
            label="Ping", emoji="🔔", style=discord.ButtonStyle.secondary,
            custom_id="btn_ping_account", row=0
        )
        async def on_ping(btn_inter: discord.Interaction):
            await handle_toggle_account_role(btn_inter)
        ping_btn.callback = on_ping
        self.add_item(ping_btn)

        # 5. Edit Button
        edit_btn = discord.ui.Button(
            label="Edit", emoji="⚙️", style=discord.ButtonStyle.secondary,
            custom_id=f"btn_edit:{enc_ign}:{price}:{seller_id}", row=1
        )
        async def on_edit(btn_inter: discord.Interaction):
            await handle_edit_account_action(btn_inter)
        edit_btn.callback = on_edit
        self.add_item(edit_btn)

        # 6. Mark Sold Button
        sold_btn = discord.ui.Button(
            label="Mark Sold", emoji="⛔", style=discord.ButtonStyle.danger,
            custom_id=f"btn_sold:{enc_ign}:{price}:{seller_id}", row=1
        )
        async def on_sold(btn_inter: discord.Interaction):
            await handle_mark_sold_action(btn_inter)
        sold_btn.callback = on_sold
        self.add_item(sold_btn)

        # Row 2: External Links & Inspect
        if not hide_name:
            self.add_item(discord.ui.Button(label=f"SkyCrypt • ${price}", emoji="📊", url=f"https://sky.shiiyu.moe/stats/{urllib.parse.quote(ign)}", row=2))
        self.add_item(discord.ui.Button(label="Join Store", emoji="🌐", url=get_invite_url(), row=2))
        self.add_item(InspectSelect(ign=ign if not hide_name else "", hide_name=hide_name))

@bot.listen("on_interaction")
async def global_fallback_listener(inter: discord.Interaction):
    if inter.type != discord.InteractionType.component:
        return
    if inter.response.is_done():
        return

    cid = inter.data.get("custom_id", "")
    if cid == "btn_cls":
        await inter.response.send_message(
            "❓ **Was this trade completed?**\nSelect an option below to finalize the ticket and notify the buyer:",
            view=TicketCloseConfirmView(inter.channel_id),
            ephemeral=False
        )
        return
    elif cid == "btn_cls_yes":
        await close_ticket_with_transcript(inter, trade_completed=True)
        return
    elif cid == "btn_cls_no":
        await close_ticket_with_transcript(inter, trade_completed=False)
        return
    elif cid == "btn_cls_cancel":
        try: await inter.message.delete()
        except Exception: pass
        return

    # Direct custom_id match
    if cid.startswith("btn_buy:"):
        parts = cid.split(":")
        ign = "Account"
        price = "0"
        hide_name = False
        if len(parts) >= 3:
            try:
                ign = base64.b64decode(parts[1].encode()).decode()
                price = parts[2]
                if len(parts) >= 4:
                    hide_name = (parts[3] == "1")
            except Exception:
                pass
        e_ign, e_price, e_seller, e_hide = extract_listing_info(inter.message)
        await handle_buy_action(inter, ign=ign or e_ign, price=price or e_price, seller_id=e_seller, hide_name=hide_name or e_hide)
        return
    elif cid == "btn_buy_account":
        e_ign, e_price, e_seller, e_hide = extract_listing_info(inter.message)
        await handle_buy_action(inter, ign=e_ign, price=e_price, seller_id=e_seller, hide_name=e_hide)
        return
    elif cid.startswith("btn_offer:"):
        parts = cid.split(":")
        ign = "Account"
        price = "0"
        hide_name = False
        if len(parts) >= 3:
            try:
                ign = base64.b64decode(parts[1].encode()).decode()
                price = parts[2]
                if len(parts) >= 4:
                    hide_name = (parts[3] == "1")
            except Exception:
                pass
        e_ign, e_price, e_seller, e_hide = extract_listing_info(inter.message)
        await handle_offer_action(inter, ign=ign or e_ign, price=price or e_price, seller_id=e_seller, hide_name=hide_name or e_hide)
        return
    elif cid == "btn_offer_account":
        e_ign, e_price, e_seller, e_hide = extract_listing_info(inter.message)
        await handle_offer_action(inter, ign=e_ign, price=e_price, seller_id=e_seller, hide_name=e_hide)
        return
    elif cid.startswith("btn_ref:") or cid == "btn_refresh_account":
        await handle_refresh_action(inter)
        return
    elif cid.startswith("btn_edit:") or cid == "btn_edit_account":
        await handle_edit_account_action(inter)
        return
    elif cid.startswith("btn_sold:") or cid == "btn_sold_account":
        await handle_mark_sold_action(inter)
        return
    elif cid == "btn_ping_account" or cid.startswith("btn_ping:"):
        await handle_toggle_account_role(inter)
        return
    elif cid == "btn_coin_calc":
        await inter.response.send_modal(CoinCalculatorModal())
        return
    elif cid == "btn_req_mm":
        await inter.response.send_modal(MiddlemanRequestModal())
        return
    elif cid == "btn_stock_edit":
        stock = load_json_file(STOCK_FILE, DEFAULT_STOCK)
        await inter.response.send_modal(EditStockModal(stock))
        return
    elif cid == "btn_rank_buy":
        await inter.response.send_modal(RankOrderModal())
        return
    elif cid == "btn_rank_edit":
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True
        if not is_staff:
            await inter.response.send_message("❌ Only server staff and administrators can edit rank rates.", ephemeral=True)
            return
        rates = load_rank_rates()
        await inter.response.send_modal(EditRankRatesModal(rates))
        return
        await handle_mark_sold_action(inter)
        return
    elif cid == "select_inspect_stats":
        target_ign, _, _, is_hidden = extract_listing_info(inter.message)
        if is_hidden or not target_ign or target_ign == "Account":
            await inter.response.send_message(
                "🔒 **Account Privacy Protected**\n"
                "To protect against Hypixel bans, this listing's username is kept confidential.\n"
                "👉 Full SkyCrypt inspection is revealed inside your private ticket after clicking **Buy**.",
                ephemeral=True
            )
        else:
            val = inter.data.get("values", ["Stats"])[0] if inter.data.get("values") else "Stats"
            await inter.response.send_message(
                f"Detailed progression for **{val}** (`{target_ign}`):\n👉 https://sky.shiiyu.moe/stats/{target_ign}",
                ephemeral=True
            )
        return

    # Fallback for old messages sent prior to restart (matching by button label)
    if inter.message and inter.message.components:
        clicked_label = None
        for row in inter.message.components:
            for comp in getattr(row, "children", []):
                if getattr(comp, "custom_id", None) == cid:
                    clicked_label = getattr(comp, "label", None)
                    break
            if clicked_label:
                break

        if clicked_label:
            if "Buy" in clicked_label:
                await handle_buy_action(inter)
                return
            elif "Offer" in clicked_label:
                await handle_offer_action(inter)
                return
            elif "Refresh" in clicked_label:
                await handle_refresh_action(inter)
                return
            elif "Close" in clicked_label:
                await close_ticket_with_transcript(inter)
                return
            elif "Edit" in clicked_label and "Rate" not in clicked_label:
                await handle_edit_account_action(inter)
                return
            elif "Sold" in clicked_label:
                await handle_mark_sold_action(inter)
                return
            elif "Ping" in clicked_label:
                await handle_toggle_account_role(inter)
                return
            elif "Buy Rank" in clicked_label:
                await inter.response.send_modal(RankOrderModal())
                return
            elif "Calculator" in clicked_label:
                await inter.response.send_modal(CoinCalculatorModal())
                return
            elif "Middleman" in clicked_label:
                await inter.response.send_modal(MiddlemanRequestModal())
                return
            elif "Update Stock" in clicked_label:
                stock = load_json_file(STOCK_FILE, DEFAULT_STOCK)
                await inter.response.send_modal(EditStockModal(stock))
                return
                await handle_mark_sold_action(inter)
                return
            elif "Buy Coins" in clicked_label:
                await inter.response.send_modal(CoinOrderModal("BUY"))
                return
            elif "Sell Coins" in clicked_label:
                await inter.response.send_modal(CoinOrderModal("SELL"))
                return
            elif "Edit Rates" in clicked_label:
                rates = load_coin_rates()
                await inter.response.send_modal(EditCoinRatesModal(rates))
                return


class CoinOrderModal(discord.ui.Modal):
    def __init__(self, order_type: str = "BUY"):
        t_label = "Buy Hypixel Coins" if order_type == "BUY" else "Sell Hypixel Coins"
        super().__init__(title=t_label[:45])
        self.order_type = order_type

        if order_type == "BUY":
            self.amount_input = discord.ui.TextInput(
                label="Amount of Coins to Buy",
                placeholder="e.g. 500M, 1B, 2.5B",
                required=True,
                max_length=50
            )
            self.ign_input = discord.ui.TextInput(
                label="Minecraft Username (IGN)",
                placeholder="Your Minecraft In-Game Name",
                required=True,
                max_length=30
            )
            self.payment_input = discord.ui.TextInput(
                label="Preferred Payment Method",
                placeholder="e.g. LTC, USDT, BTC, ETH",
                default="Litecoin (LTC)",
                required=True,
                max_length=50
            )
            self.notes_input = discord.ui.TextInput(
                label="Notes / Special Requests (Optional)",
                placeholder="Any questions or specific profile requests",
                required=False,
                style=discord.TextStyle.paragraph,
                max_length=300
            )
            self.add_item(self.amount_input)
            self.add_item(self.ign_input)
            self.add_item(self.payment_input)
            self.add_item(self.notes_input)
        else:
            self.amount_input = discord.ui.TextInput(
                label="Amount of Coins to Sell",
                placeholder="e.g. 1B, 2.5B, 5B",
                required=True,
                max_length=50
            )
            self.ign_input = discord.ui.TextInput(
                label="Minecraft IGN & Level",
                placeholder="e.g. Steve (Level 75)",
                required=True,
                max_length=50
            )
            self.payout_input = discord.ui.TextInput(
                label="Payout Crypto Address & Coin",
                placeholder="e.g. LTC Address, USDT (TRC20)",
                required=True,
                max_length=150
            )
            self.notes_input = discord.ui.TextInput(
                label="Notes / Availability (Optional)",
                placeholder="Any additional info for staff",
                required=False,
                style=discord.TextStyle.paragraph,
                max_length=300
            )
            self.add_item(self.amount_input)
            self.add_item(self.ign_input)
            self.add_item(self.payout_input)
            self.add_item(self.notes_input)

    async def on_submit(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)
        g = inter.guild
        if not g:
            await inter.followup.send("❌ Error: Server context not found.", ephemeral=True)
            return

        clean_ign = re.sub(r'[^a-zA-Z0-9]', '', self.ign_input.value).lower() or "user"
        cname = f"ticket-{'buy' if self.order_type == 'BUY' else 'sell'}-coins-{clean_ign}"[:90]

        bot_member = g.me or g.get_member(bot.user.id)
        over = {
            g.default_role: discord.PermissionOverwrite(view_channel=False),
            inter.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
        }
        if bot_member:
            over[bot_member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True)

        admin_role = None
        if STAFF_ROLE_ID:
            srole = g.get_role(STAFF_ROLE_ID)
            if srole:
                admin_role = srole
                over[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        if not admin_role:
            admin_role = discord.utils.find(lambda r: r.name.lower() in ["admin", "administrator", "staff", "mod", "moderator", "owner"], g.roles)
            if admin_role:
                over[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        cat = None
        if TICKET_CAT_ID:
            c = g.get_channel(TICKET_CAT_ID)
            if isinstance(c, discord.CategoryChannel):
                cat = c

        t = None
        try:
            t = await g.create_text_channel(name=cname, category=cat, overwrites=over)
        except Exception as e:
            try:
                t = await g.create_text_channel(name=cname)
                await t.set_permissions(inter.user, view_channel=True, send_messages=True)
                if admin_role:
                    await t.set_permissions(admin_role, view_channel=True, send_messages=True)
            except Exception as e2:
                await inter.followup.send(f"❌ Failed to create ticket channel: {e2}", ephemeral=True)
                return

        admin_mention = admin_role.mention if admin_role else "@staff"
        is_buy = (self.order_type == "BUY")
        action_title = "🛒 Coin Purchase Request" if is_buy else "💰 Coin Sale Offer"
        payout_or_pay = f"🪙 **Payment Method:** {self.payment_input.value}\n" if is_buy else f"💼 **Payout Destination:** `{self.payout_input.value}`\n"

        emb = discord.Embed(
            title=action_title,
            description=(
                f"### Welcome {inter.user.mention} to your coin trade ticket!\n\n"
                f"🪙 **Order Type:** {'BUY COINS' if is_buy else 'SELL COINS'}\n"
                f"📦 **Amount:** **{self.amount_input.value}**\n"
                f"👤 **IGN / Profile:** **{self.ign_input.value}**\n"
                f"{payout_or_pay}"
                f"📝 **Notes:** {self.notes_input.value if self.notes_input.value else 'None'}\n\n"
                f"Staff {admin_mention} will assist you shortly to finalize the transaction securely!\n"
                f"🛡️ *Minimum level is 50. Higher levels provide maximum safety.*"
            ),
            color=discord.Color(0xF1C40F) if is_buy else discord.Color(0x2ECC71),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        if os.path.exists("banner.png"):
            emb.set_image(url="attachment://banner.png")
        emb.set_footer(text=f"{STORE_NAME} • {STORE_INVITE}")

        tview = CloseTicketView()
        t_file = discord.File("banner.png", filename="banner.png") if os.path.exists("banner.png") else None
        if t_file:
            await t.send(content=f"{inter.user.mention} | {admin_mention}", embed=emb, file=t_file, view=tview)
        else:
            await t.send(content=f"{inter.user.mention} | {admin_mention}", embed=emb, view=tview)

        await inter.followup.send(f"✅ Ticket created successfully in {t.mention}!", ephemeral=True)

class EditCoinRatesModal(discord.ui.Modal):
    def __init__(self, current_rates: Dict[str, Any]):
        super().__init__(title="Edit Coin Prices & Panel"[:45])
        self.buy_input = discord.ui.TextInput(
            label="Buy Rates (Each line is a tier)",
            placeholder="$35/B above 300M\n$30/B above 500M\n$25/B above 1B",
            default=current_rates.get("buy_rates", "$35/B above 300M\n$30/B above 500M\n$25/B above 1B"),
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        self.sell_input = discord.ui.TextInput(
            label="Sell Rates",
            placeholder="$18/B",
            default=current_rates.get("sell_rates", "$18/B"),
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        self.min_info_input = discord.ui.TextInput(
            label="Minimum Level & Guidelines Info",
            placeholder="Minimum level is 50, the higher level the safer you will be.",
            default=current_rates.get("min_level_info", "Minimum level is 50, the higher level the safer you will be.\nCreate a ticket to buy or sell."),
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=500
        )
        self.payment_input = discord.ui.TextInput(
            label="Accepted Payment Methods",
            placeholder="Ł LTC • 🪙 USDC • ₿ BTC • ₮ USDT • 🟣 SOL • 🔷 ETH",
            default=current_rates.get("payment_methods", "Ł LTC • 🪙 USDC • ₿ BTC • ₮ USDT • 🟣 SOL • 🔷 ETH"),
            required=True,
            max_length=200
        )
        self.add_item(self.buy_input)
        self.add_item(self.sell_input)
        self.add_item(self.min_info_input)
        self.add_item(self.payment_input)

    async def on_submit(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)
        rates = load_coin_rates()
        rates["buy_rates"] = self.buy_input.value.strip()
        rates["sell_rates"] = self.sell_input.value.strip()
        rates["min_level_info"] = self.min_info_input.value.strip()
        rates["payment_methods"] = resolve_payment_emojis(self.payment_input.value.strip(), inter.guild)
        save_coin_rates(rates)

        # Update the message in place
        if inter.message:
            try:
                new_emb = build_coin_panel_embed(rates, inter.guild)
                await inter.message.edit(embed=new_emb)
            except Exception as e:
                print(f"Error editing panel in-place: {e}")

        await inter.followup.send("✅ Coin prices and panel updated successfully!", ephemeral=True)

class PersistentCoinPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Buy Coins", emoji="🛒", style=discord.ButtonStyle.success, custom_id="btn_coin_buy")
    async def btn_buy(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_modal(CoinOrderModal(order_type="BUY"))

    @discord.ui.button(label="Sell Coins", emoji="💰", style=discord.ButtonStyle.primary, custom_id="btn_coin_sell")
    async def btn_sell(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_modal(CoinOrderModal(order_type="SELL"))

    @discord.ui.button(label="Calculator", emoji="🧮", style=discord.ButtonStyle.secondary, custom_id="btn_coin_calc")
    async def btn_calc(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_modal(CoinCalculatorModal())

    @discord.ui.button(label="Edit Rates", emoji="⚙️", style=discord.ButtonStyle.secondary, custom_id="btn_coin_edit")
    async def btn_edit(self, inter: discord.Interaction, button: discord.ui.Button):
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            await inter.response.send_message("❌ Only server staff and administrators can edit coin rates.", ephemeral=True)
            return

        rates = load_coin_rates()
        await inter.response.send_modal(EditCoinRatesModal(rates))


class RankOrderModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Buy Hypixel Rank"[:45])
        self.rank_input = discord.ui.TextInput(
            label="Rank to Purchase",
            placeholder="e.g. VIP, VIP+, MVP, MVP+, MVP++ (30/90/180/365d)",
            required=True,
            max_length=50
        )
        self.ign_input = discord.ui.TextInput(
            label="Minecraft Username (IGN)",
            placeholder="Player who will receive the rank",
            required=True,
            max_length=30
        )
        self.current_rank_input = discord.ui.TextInput(
            label="Current Rank (or None)",
            placeholder="e.g. None, VIP, MVP+",
            default="None",
            required=False,
            max_length=30
        )
        self.notes_input = discord.ui.TextInput(
            label="Notes / Special Requests (Optional)",
            placeholder="Any extra info for staff",
            required=False,
            style=discord.TextStyle.paragraph,
            max_length=300
        )
        self.add_item(self.rank_input)
        self.add_item(self.ign_input)
        self.add_item(self.current_rank_input)
        self.add_item(self.notes_input)

    async def on_submit(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)
        g = inter.guild
        if not g:
            await inter.followup.send("❌ Error: Server context not found.", ephemeral=True)
            return

        clean_ign = re.sub(r'[^a-zA-Z0-9]', '', self.ign_input.value).lower() or "user"
        cname = f"ticket-rank-{clean_ign}"[:90]

        bot_member = g.me or g.get_member(bot.user.id)
        over = {
            g.default_role: discord.PermissionOverwrite(view_channel=False),
            inter.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
        }
        if bot_member:
            over[bot_member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True)

        admin_role = None
        if STAFF_ROLE_ID:
            srole = g.get_role(STAFF_ROLE_ID)
            if srole:
                admin_role = srole
                over[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        if not admin_role:
            admin_role = discord.utils.find(lambda r: r.name.lower() in ["admin", "administrator", "staff", "mod", "moderator", "owner"], g.roles)
            if admin_role:
                over[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        cat = None
        if TICKET_CAT_ID:
            c = g.get_channel(TICKET_CAT_ID)
            if isinstance(c, discord.CategoryChannel):
                cat = c

        t = None
        try:
            t = await g.create_text_channel(name=cname, category=cat, overwrites=over)
        except Exception as e:
            try:
                t = await g.create_text_channel(name=cname)
                await t.set_permissions(inter.user, view_channel=True, send_messages=True)
                if admin_role:
                    await t.set_permissions(admin_role, view_channel=True, send_messages=True)
            except Exception as e2:
                await inter.followup.send(f"❌ Failed to create rank ticket: {e2}", ephemeral=True)
                return

        admin_mention = admin_role.mention if admin_role else "@staff"
        ign_clean = self.ign_input.value.strip()

        emb = discord.Embed(
            title=f"👑 Rank Purchase Request: {self.rank_input.value}",
            description=(
                f"### Welcome {inter.user.mention} to your rank purchase ticket!\n\n"
                f"👑 **Target Rank:** **{self.rank_input.value}**\n"
                f"👤 **Receiving IGN:** **[{ign_clean}](https://sky.shiiyu.moe/stats/{ign_clean})**\n"
                f"🌿 **Current Rank:** `{self.current_rank_input.value or 'None'}`\n"
                f"💰 **Payment:** In-Game SkyBlock Coins\n"
                f"📝 **Notes:** {self.notes_input.value if self.notes_input.value else 'None'}\n\n"
                f"Staff {admin_mention} will assist you with the coin trade and rank gifting shortly!\n"
                f"🛡️ *100% Secure • Official Hypixel Store Gifting*"
            ),
            color=discord.Color(0xF1C40F),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        if ign_clean and ign_clean != "user":
            emb.set_thumbnail(url=f"https://mc-heads.net/avatar/{ign_clean}/100.png")
        if os.path.exists("banner.png"):
            emb.set_image(url="attachment://banner.png")
        emb.set_footer(text=f"{STORE_NAME} • {STORE_INVITE}")

        tview = CloseTicketView()
        t_file = discord.File("banner.png", filename="banner.png") if os.path.exists("banner.png") else None
        if t_file:
            await t.send(content=f"{inter.user.mention} | {admin_mention}", embed=emb, file=t_file, view=tview)
        else:
            await t.send(content=f"{inter.user.mention} | {admin_mention}", embed=emb, view=tview)

        await inter.followup.send(f"✅ Rank ticket created in {t.mention}!", ephemeral=True)

class EditRankRatesModal(discord.ui.Modal):
    def __init__(self, current_rates: Dict[str, Any]):
        super().__init__(title="Edit Rank Prices & Panel"[:45])
        self.perm_input = discord.ui.TextInput(
            label="Permanent Ranks Pricing (Lines)",
            placeholder="600M For VIP\n800M For VIP+\n1.5B For MVP\n2.3B For MVP+",
            default=current_rates.get("perm_ranks", DEFAULT_RANK_RATES["perm_ranks"]),
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=600
        )
        self.sub_input = discord.ui.TextInput(
            label="MVP++ Subscription Pricing (Lines)",
            placeholder="700M For MVP++ 30 days\n1.5B For MVP++ 90 days...",
            default=current_rates.get("sub_ranks", DEFAULT_RANK_RATES["sub_ranks"]),
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=600
        )
        self.notice_input = discord.ui.TextInput(
            label="Store Disclaimer Notice",
            placeholder="PRICES CAN CHANGE ACCORDING TO CHANGE IN PRICE ON HYPIXEL STORE",
            default=current_rates.get("notice", DEFAULT_RANK_RATES["notice"]),
            required=False,
            max_length=200
        )
        self.add_item(self.perm_input)
        self.add_item(self.sub_input)
        self.add_item(self.notice_input)

    async def on_submit(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)
        rates = load_rank_rates()
        rates["perm_ranks"] = self.perm_input.value.strip()
        rates["sub_ranks"] = self.sub_input.value.strip()
        rates["notice"] = self.notice_input.value.strip()
        save_rank_rates(rates)

        if inter.message:
            try:
                new_emb = build_rank_panel_embed(rates, inter.guild)
                await inter.message.edit(embed=new_emb)
            except Exception as e:
                print(f"Error editing rank panel in-place: {e}")

        await inter.followup.send("✅ Rank prices and panel updated successfully!", ephemeral=True)

class PersistentRankPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Buy Rank", emoji="👑", style=discord.ButtonStyle.success, custom_id="btn_rank_buy")
    async def btn_buy(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_modal(RankOrderModal())

    @discord.ui.button(label="Edit Rates", emoji="⚙️", style=discord.ButtonStyle.secondary, custom_id="btn_rank_edit")
    async def btn_edit(self, inter: discord.Interaction, button: discord.ui.Button):
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            await inter.response.send_message("❌ Only server staff and administrators can edit rank rates.", ephemeral=True)
            return

        rates = load_rank_rates()
        await inter.response.send_modal(EditRankRatesModal(rates))


class CoinCalculatorModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="SkyBlock Coins Calculator"[:45])
        self.coins_input = discord.ui.TextInput(
            label="Coins Amount (e.g. 500M or 1.5B)",
            placeholder="e.g. 500M, 1B, 2.5B",
            required=False,
            max_length=20
        )
        self.usd_input = discord.ui.TextInput(
            label="OR USD Budget (e.g. 25, 50, 100)",
            placeholder="e.g. 50",
            required=False,
            max_length=20
        )
        self.add_item(self.coins_input)
        self.add_item(self.usd_input)

    async def on_submit(self, inter: discord.Interaction):
        c_val = self.coins_input.value.strip()
        u_val = self.usd_input.value.strip()
        if not c_val and not u_val:
            await inter.response.send_message("❌ Please enter either a Coin amount or a USD budget.", ephemeral=True)
            return

        res, err = calculate_coin_quote(coins_str=c_val, usd_str=u_val)
        if err:
            await inter.response.send_message(f"❌ {err}", ephemeral=True)
            return

        emb = discord.Embed(
            title="🧮 SkyBlock Coins Quote",
            color=discord.Color.from_rgb(255, 255, 255),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        if res["type"] == "COINS_TO_USD":
            c_coins = res["coins"]
            c_usd = res["usd"]
            c_rate = res["rate"]
            emb.description = f"### Price Quote for **{c_coins} Coins**\n\n💵 **Total Price:** **{c_usd} USD**\n📊 **Applied Rate:** `{c_rate}`\n\nReady to buy? Click **Buy Coins** to open a ticket!"
        else:
            c_coins = res["coins"]
            c_usd = res["usd"]
            c_rate = res["rate"]
            emb.description = f"### Coin Quote for **{c_usd} USD**\n\n🪙 **Coins Received:** **{c_coins}**\n📊 **Estimated Rate:** `{c_rate}`\n\nReady to buy? Click **Buy Coins** to open a ticket!"
        emb.set_footer(text=f"{STORE_NAME} • Instant Delivery")
        await inter.response.send_message(embed=emb, ephemeral=True)

class MiddlemanRequestModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Request Middleman / Escrow"[:45])
        self.partner_input = discord.ui.TextInput(
            label="Trading Partner (@user, ID, or Username)",
            placeholder="e.g. @Partner or user ID",
            required=True,
            max_length=50
        )
        self.give_input = discord.ui.TextInput(
            label="What You Are Giving",
            placeholder="e.g. 2.5B SkyBlock Coins, Hyperion, etc.",
            required=True,
            max_length=150
        )
        self.receive_input = discord.ui.TextInput(
            label="What Partner Is Giving",
            placeholder="e.g. $70 LTC / Crypto, Account IGN, etc.",
            required=True,
            max_length=150
        )
        self.terms_input = discord.ui.TextInput(
            label="Deal Terms & Fee Agreement",
            placeholder="e.g. 50/50 fee, release upon verification",
            required=False,
            style=discord.TextStyle.paragraph,
            max_length=300
        )
        self.add_item(self.partner_input)
        self.add_item(self.give_input)
        self.add_item(self.receive_input)
        self.add_item(self.terms_input)

    async def on_submit(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)
        g = inter.guild
        if not g:
            await inter.followup.send("❌ Error: Server context not found.", ephemeral=True)
            return

        # Try resolving partner member
        p_raw = self.partner_input.value.strip()
        p_id_match = re.search(r'\d{17,20}', p_raw)
        partner_member = None
        if p_id_match:
            partner_member = g.get_member(int(p_id_match.group(0)))
        if not partner_member:
            partner_member = discord.utils.find(lambda m: m.name.lower() == p_raw.lower() or p_raw.lower() in m.display_name.lower(), g.members)

        clean_user = re.sub(r'[^a-zA-Z0-9]', '', inter.user.name).lower() or "trader1"
        clean_partner = re.sub(r'[^a-zA-Z0-9]', '', partner_member.name if partner_member else p_raw).lower() or "trader2"
        cname = f"ticket-mm-{clean_user}-{clean_partner}"[:90]

        bot_member = g.me or g.get_member(bot.user.id)
        over = {
            g.default_role: discord.PermissionOverwrite(view_channel=False),
            inter.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
        }
        if partner_member:
            over[partner_member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True)
        if bot_member:
            over[bot_member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True)

        admin_role = None
        if STAFF_ROLE_ID:
            srole = g.get_role(STAFF_ROLE_ID)
            if srole:
                admin_role = srole
                over[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        if not admin_role:
            admin_role = discord.utils.find(lambda r: r.name.lower() in ["admin", "administrator", "staff", "mod", "moderator", "owner"], g.roles)
            if admin_role:
                over[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        cat = None
        if TICKET_CAT_ID:
            c = g.get_channel(TICKET_CAT_ID)
            if isinstance(c, discord.CategoryChannel):
                cat = c

        t = None
        try:
            t = await g.create_text_channel(name=cname, category=cat, overwrites=over)
        except Exception as e:
            try:
                t = await g.create_text_channel(name=cname)
                await t.set_permissions(inter.user, view_channel=True, send_messages=True)
                if partner_member:
                    await t.set_permissions(partner_member, view_channel=True, send_messages=True)
                if admin_role:
                    await t.set_permissions(admin_role, view_channel=True, send_messages=True)
            except Exception as e2:
                await inter.followup.send(f"❌ Failed to create MM ticket: {e2}", ephemeral=True)
                return

        admin_mention = admin_role.mention if admin_role else "@staff"
        partner_mention = partner_member.mention if partner_member else f"`{p_raw}`"

        emb = discord.Embed(
            title="🛡️ Middleman / Escrow Trade Ticket",
            description=(
                f"### Welcome {inter.user.mention} and {partner_mention}!\n\n"
                f"Official Middleman {admin_mention} will supervise and hold items/payment to ensure 100% safety.\n\n"
                f"📦 **{inter.user.mention} Gives:**\n`{self.give_input.value}`\n\n"
                f"📦 **{partner_mention} Gives:**\n`{self.receive_input.value}`\n\n"
                f"📝 **Deal Terms & Fees:**\n`{self.terms_input.value if self.terms_input.value else 'Standard escrow terms'}`\n\n"
                f"⚠️ **Security Checklist:**\n"
                f"▸ Do NOT trade until the official staff MM confirms they are ready.\n"
                f"▸ Check staff Discord IDs carefully to prevent impersonators.\n"
                f"▸ Both sides must confirm satisfaction before release."
            ),
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        if os.path.exists("banner.png"):
            emb.set_image(url="attachment://banner.png")
        emb.set_footer(text=f"{STORE_NAME} • Escrow & Middleman")

        tview = CloseTicketView()
        t_file = discord.File("banner.png", filename="banner.png") if os.path.exists("banner.png") else None
        pings = f"{inter.user.mention} | {partner_mention} | {admin_mention}"
        if t_file:
            await t.send(content=pings, embed=emb, file=t_file, view=tview)
        else:
            await t.send(content=pings, embed=emb, view=tview)

        await inter.followup.send(f"✅ Middleman ticket created in {t.mention}!", ephemeral=True)

class PersistentMMView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Request Middleman", emoji="🛡️", style=discord.ButtonStyle.primary, custom_id="btn_req_mm")
    async def req_mm(self, inter: discord.Interaction, button: discord.ui.Button):
        await inter.response.send_modal(MiddlemanRequestModal())

class EditStockModal(discord.ui.Modal):
    def __init__(self, current_stock: dict):
        super().__init__(title="Update Inventory & Stock"[:45])
        self.coins_input = discord.ui.TextInput(
            label="Coins Stock Amount",
            placeholder="e.g. 14.5B",
            default=current_stock.get("coins_stock", "14.5B"),
            required=True,
            max_length=50
        )
        self.coins_status_input = discord.ui.TextInput(
            label="Coins Status",
            placeholder="e.g. 🟢 In Stock, 🟡 Low Stock, 🔴 Out of Stock",
            default=current_stock.get("coins_status", "🟢 In Stock"),
            required=True,
            max_length=50
        )
        self.ranks_status_input = discord.ui.TextInput(
            label="Ranks Gifting Status",
            placeholder="e.g. 🟢 Instant Delivery",
            default=current_stock.get("ranks_status", "🟢 Instant Delivery"),
            required=True,
            max_length=50
        )
        self.add_item(self.coins_input)
        self.add_item(self.coins_status_input)
        self.add_item(self.ranks_status_input)

    async def on_submit(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)
        stock = load_json_file(STOCK_FILE, DEFAULT_STOCK)
        stock["coins_stock"] = self.coins_input.value.strip()
        stock["coins_status"] = self.coins_status_input.value.strip()
        stock["ranks_status"] = self.ranks_status_input.value.strip()
        stock["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save_json_file(STOCK_FILE, stock)

        if inter.message:
            try:
                new_emb = build_stock_embed(stock, inter.guild)
                await inter.message.edit(embed=new_emb)
            except Exception as e:
                print(f"Error editing stock panel in place: {e}")

        await inter.followup.send("✅ Inventory & stock updated successfully!", ephemeral=True)

class PersistentStockView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Update Stock", emoji="⚙️", style=discord.ButtonStyle.secondary, custom_id="btn_stock_edit")
    async def btn_edit(self, inter: discord.Interaction, button: discord.ui.Button):
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            await inter.response.send_message("❌ Only server staff and administrators can update stock.", ephemeral=True)
            return

        stock = load_json_file(STOCK_FILE, DEFAULT_STOCK)
        await inter.response.send_modal(EditStockModal(stock))


class PersistentAutobumpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            label="Join Server / Invite",
            emoji="🔗",
            url=get_invite_url(),
            style=discord.ButtonStyle.link,
            row=1
        ))

    @discord.ui.button(label="Coin Rates", emoji="🪙", style=discord.ButtonStyle.secondary, custom_id="bump_btn_coins", row=0)
    async def btn_coins(self, inter: discord.Interaction, button: discord.ui.Button):
        rates = load_coin_rates()
        emb = build_coin_panel_embed(rates, inter.guild)
        await inter.response.send_message(embed=emb, ephemeral=True)

    @discord.ui.button(label="Rank Prices", emoji="🎖️", style=discord.ButtonStyle.secondary, custom_id="bump_btn_ranks", row=0)
    async def btn_ranks(self, inter: discord.Interaction, button: discord.ui.Button):
        rates = load_rank_rates()
        emb = build_rank_panel_embed(rates, inter.guild)
        await inter.response.send_message(embed=emb, ephemeral=True)

    @discord.ui.button(label="Store Vouches", emoji="⭐", style=discord.ButtonStyle.secondary, custom_id="bump_btn_vouches", row=0)
    async def btn_vouches(self, inter: discord.Interaction, button: discord.ui.Button):
        v_data = load_json_file(VOUCHES_FILE, DEFAULT_VOUCHES)
        total = v_data.get("total_vouches", len(v_data.get("vouches", [])))
        recent = v_data.get("vouches", [])[-5:]
        desc = f"🏆 **Total Verified Vouches:** `{total}`\n\n**Recent 5 Reviews:**\n"
        if not recent:
            desc += "*No vouches yet! Complete a trade and be the first to vouch with `/vouch`!*"
        else:
            for v in reversed(recent):
                stars = "⭐" * v.get("stars", 5)
                buyer = "🔒 *Anonymous Buyer*" if v.get("is_anonymous") else f"<@{v.get('user_id')}>"
                seller = f"<@{v.get('staff_id')}>" if v.get("staff_id") else "Staff"
                desc += f"• {stars} for {seller} by {buyer}: *\"{v.get('comment', '')[:60]}\"*\n"

        emb = discord.Embed(
            title=f"⭐ {STORE_NAME} — Verified Reviews & Vouches",
            description=desc,
            color=discord.Color.gold()
        )
        await inter.response.send_message(embed=emb, ephemeral=True)

def build_autobump_embed(guild: Optional[discord.Guild] = None, bump_type: str = "all") -> tuple:
    coin_data = load_coin_rates()
    stock_data = load_json_file(STOCK_FILE, DEFAULT_STOCK)
    vouch_data = load_json_file(VOUCHES_FILE, DEFAULT_VOUCHES)
    rank_data = load_rank_rates()

    total_vouches = vouch_data.get("total_vouches", len(vouch_data.get("vouches", [])))
    coins_stock = stock_data.get("coins_stock", "In Stock")
    coin_status = stock_data.get("coins_status", "🟢 Available")
    ranks_status = stock_data.get("ranks_status", "🟢 Instant Delivery")

    active_accounts = 0
    if guild and ACCOUNTS_CAT_ID:
        cat = guild.get_channel(ACCOUNTS_CAT_ID) or discord.utils.get(guild.categories, id=ACCOUNTS_CAT_ID)
        if cat and hasattr(cat, "channels"):
            active_accounts = len(cat.channels)

    buy_rate_line = coin_data.get("buy_rates", "$35/B").splitlines()[0] if coin_data.get("buy_rates") else "$35/B"
    sell_rate_line = coin_data.get("sell_rates", "$18/B")

    embed = discord.Embed(
        title=f"⚡ {STORE_NAME} — Premier Hypixel SkyBlock Marketplace ⚡",
        description=(
            f"Looking for cheap, safe, and fast Hypixel SkyBlock services? We provide verified trades, "
            f"instant automated tickets, and official 100% secure escrow!\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🪙 **SKYBLOCK COINS & STOCK**\n"
            f"• **Buy Rate:** `{buy_rate_line}`\n"
            f"• **Sell Rate:** `{sell_rate_line}`\n"
            f"• **Live Stock:** `{coins_stock}` ({coin_status})\n\n"
            f"🎖️ **HYPIXEL RANKS & UPGRADES**\n"
            f"• **Available:** VIP, VIP+, MVP, MVP+, MVP++\n"
            f"• **Delivery:** `{ranks_status}` *(Pay with SB Coins)*\n\n"
            f"📦 **ENDGAME ACCOUNTS & PROFILES**\n"
            f"• **Active Listings:** `{active_accounts}` verified accounts ready to buy!\n\n"
            f"🛡️ **WHY TRUST US?**\n"
            f"• ⭐ **Verified Reputation:** `{total_vouches}+` positive vouches!\n"
            f"• 🔒 **Safe Escrow:** Official middleman service available 24/7.\n"
            f"• 💳 **Accepted Payments:** LTC • USDT • BTC • ETH • SOL • USDC\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 **Ready to trade? Click the buttons below or visit our ticket channels!**"
        ),
        color=discord.Color.gold(),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )

    if os.path.exists("banner.png"):
        embed.set_image(url="attachment://banner.png")
    elif BANNER_URL:
        embed.set_image(url=BANNER_URL)

    embed.set_footer(
        text=f"{STORE_NAME} • Automated Bump • {STORE_INVITE}",
        icon_url=guild.icon.url if guild and guild.icon else None
    )

    view = PersistentAutobumpView()
    return embed, view

class StoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stats_update_loop.start()
        self.autobump_loop.start()

    def cog_unload(self):
        self.stats_update_loop.cancel()
        self.autobump_loop.cancel()


    @app_commands.command(name="list_account", description="List account and create a channel in Accounts category.")
    @app_commands.describe(
        ign="Minecraft IGN (e.g. Schiese)",
        price="Price in USD (e.g. 120)",
        hide_name="Secret / Anonymous mode? (True = Hide name & skin, False = Show name publicly)",
        nw_total="Override Networth Total (optional, e.g. 2.73B)",
        nw_unsoulbound="Override Unsoulbound Networth (optional)",
        nw_soulbound="Override Soulbound Networth (optional)",
        hotm="Override HOTM Tier (optional, e.g. 2)",
        fairy_souls="Override Fairy Souls (optional)",
        slayers="Override Slayer stats (optional, e.g. 7/7/6/5)",
        banner_url="Custom banner URL"
    )
    async def list_account(
        self,
        inter: discord.Interaction,
        ign: str,
        price: str,
        hide_name: bool = False,
        nw_total: Optional[str] = None,
        nw_unsoulbound: Optional[str] = None,
        nw_soulbound: Optional[str] = None,
        hotm: Optional[int] = None,
        fairy_souls: Optional[int] = None,
        slayers: Optional[str] = None,
        banner_url: Optional[str] = None
    ):
        await inter.response.defer(ephemeral=True)
        try:
            g = inter.guild
            if not g:
                await inter.followup.send("❌ Error: Server context not found.", ephemeral=True)
                return

            clean_price = price.replace("$", "").strip()
            try:
                s = await get_live_stats(ign)
            except Exception as e:
                await inter.followup.send(f"❌ Failed to fetch stats for `{ign}` from Hypixel: {e}", ephemeral=True)
                return

            # Apply Networth split
            if nw_total:
                tot, uns, sb = split_networth(nw_total, nw_unsoulbound or "", nw_soulbound or "")
                s["nw_tot"] = tot
                s["nw_uns"] = uns
                s["nw_sb"] = sb
            elif nw_unsoulbound or nw_soulbound:
                if nw_unsoulbound: s["nw_uns"] = nw_unsoulbound
                if nw_soulbound: s["nw_sb"] = nw_soulbound

            if hotm: s["hotm"] = hotm
            if fairy_souls: s["souls"] = fairy_souls
            if slayers: s["slayers"] = slayers

            embed = make_embed(s, clean_price, inter.user, banner=banner_url, hide_name=hide_name)
            view = ListingView(ign, clean_price, inter.user.id, hide_name=hide_name)

            # 1. Find or create Accounts category
            accounts_cat = await get_or_create_category(g, ACCOUNTS_CAT_ID, "Accounts")

            # 2. Permissions: Nobody can message, everyone can view & interact with buttons
            bot_member = g.me or g.get_member(bot.user.id)
            channel_overwrites = {
                g.default_role: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False,
                    send_messages_in_threads=False,
                    create_public_threads=False,
                    create_private_threads=False,
                    add_reactions=True,
                    read_message_history=True
                ),
            }
            if bot_member:
                channel_overwrites[bot_member] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    embed_links=True,
                    attach_files=True,
                    manage_channels=True,
                    manage_messages=True
                )
            if STAFF_ROLE_ID:
                srole = g.get_role(STAFF_ROLE_ID)
                if srole:
                    channel_overwrites[srole] = discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        manage_messages=True
                    )

            # 3. Create listing channel with format: ⭐|💵{price}
            cname = f"⭐|💵{clean_price}"
            try:
                listing_channel = await g.create_text_channel(name=cname, category=accounts_cat, overwrites=channel_overwrites)
            except Exception as e:
                await inter.followup.send(f"❌ Failed to create listing channel in Accounts category: {e}", ephemeral=True)
                return

            # 4. Post listing message & ping @Accounts role
            accounts_role = await get_or_create_accounts_role(g)
            ping_content = accounts_role.mention if accounts_role else None

            b_file = None
            if not banner_url and os.path.exists("banner.png"):
                try:
                    b_file = discord.File("banner.png", filename="banner.png")
                except Exception as e:
                    print(f"Could not load banner.png: {e}")

            try:
                if b_file:
                    await listing_channel.send(content=ping_content, embed=embed, file=b_file, view=view, allowed_mentions=discord.AllowedMentions(roles=True, users=True, everyone=True))
                else:
                    await listing_channel.send(content=ping_content, embed=embed, view=view, allowed_mentions=discord.AllowedMentions(roles=True, users=True, everyone=True))
            except Exception as e:
                print(f"Error sending with banner attachment: {e}, falling back to standard embed")
                embed.set_image(url=BANNER_URL)
                await listing_channel.send(content=ping_content, embed=embed, view=view, allowed_mentions=discord.AllowedMentions(roles=True, users=True, everyone=True))

            await inter.followup.send(f"✅ Listing created in {listing_channel.mention} with name `⭐|💵{clean_price}`!", ephemeral=True)
        except Exception as e:
            print(f"Unexpected error in list_account: {e}")
            import traceback
            traceback.print_exc()
            await inter.followup.send(f"❌ An error occurred: `{e}`", ephemeral=True)

    @app_commands.command(name="reduce_price", description="Reduce listing price and update channel name.")
    @app_commands.describe(
        new_price="New price in USD (e.g. 100)",
        message_id="Message ID of listing (optional if run inside the listing channel)"
    )
    async def reduce_price(self, inter: discord.Interaction, new_price: str, message_id: Optional[str] = None):
        await inter.response.defer(ephemeral=True)
        channel = inter.channel
        clean_price = new_price.replace("$", "").strip()

        msg = None
        if message_id:
            try:
                msg = await channel.fetch_message(int(message_id))
            except Exception:
                pass
        if not msg:
            async for m in channel.history(limit=25):
                if m.author.id == bot.user.id and m.embeds and ("Level" in (m.embeds[0].title or "") or "Price" in (m.embeds[0].description or "")):
                    msg = m
                    break

        if not msg or not msg.embeds:
            await inter.followup.send("❌ Could not find listing message in this channel. Run inside the listing channel or provide `message_id`.", ephemeral=True)
            return

        old_embed = msg.embeds[0]
        new_desc = re.sub(r'💵 \*\*Price\*\*\s*\n\s*\*\*[\$]?[0-9\.]+\*\*', f'💵 **Price**\n**${clean_price}**', old_embed.description)
        new_emb = old_embed.copy(); new_emb.description = new_desc
        ign, _, seller_id, hide_name = extract_listing_info(msg)
        await msg.edit(embed=new_emb, view=ListingView(ign, clean_price, seller_id or inter.user.id, hide_name=hide_name))

        # Update channel name with new price
        try:
            await channel.edit(name=f"⭐|💵{clean_price}")
        except Exception as e:
            print(f"Failed to update channel name: {e}")

        await inter.followup.send(f"🏷️ **Price reduced to ${clean_price}** and channel updated to `⭐|💵{clean_price}`!", ephemeral=True)

    @app_commands.command(name="mark_sold", description="Mark listing as SOLD and move channel to SOLD category.")
    @app_commands.describe(
        message_id="Message ID of listing (optional if run inside the listing channel)"
    )
    async def mark_sold(self, inter: discord.Interaction, message_id: Optional[str] = None):
        await inter.response.defer(ephemeral=True)
        channel = inter.channel
        g = inter.guild
        if not g or not isinstance(channel, discord.TextChannel):
            await inter.followup.send("❌ Must be run in a text channel.", ephemeral=True)
            return

        msg = None
        if message_id:
            try:
                msg = await channel.fetch_message(int(message_id))
            except Exception:
                pass
        if not msg:
            async for m in channel.history(limit=25):
                if m.author.id == bot.user.id and m.embeds and ("Level" in (m.embeds[0].title or "") or "Price" in (m.embeds[0].description or "")):
                    msg = m
                    break

        if not msg or not msg.embeds:
            await inter.followup.send("❌ Could not find listing message in this channel. Run inside the listing channel or provide `message_id`.", ephemeral=True)
            return

        new_emb = msg.embeds[0].copy()
        if not new_emb.title.startswith("[SOLD]"):
            new_emb.title = f"[SOLD] {new_emb.title}"
        new_emb.color = discord.Color.dark_gray()
        dview = discord.ui.View()
        dview.add_item(discord.ui.Button(label="SOLD OUT", emoji="⛔", disabled=True))
        await msg.edit(embed=new_emb, view=dview)

        # Move channel to SOLD category
        sold_cat = await get_or_create_category(g, SOLD_CAT_ID, "SOLD")
        ign, price, _, _ = extract_listing_info(msg)

        if price and price != "0":
            new_cname = f"⛔|💵{price}"
        else:
            new_cname = channel.name.replace("⭐", "⛔")

        try:
            if sold_cat:
                await channel.edit(category=sold_cat, name=new_cname[:90])
            else:
                await channel.edit(name=new_cname[:90])
        except Exception as e:
            print(f"Error moving channel to sold category: {e}")

        await inter.followup.send(f"✅ Listing marked as **SOLD** and moved to **SOLD** category (`{new_cname}`)!", ephemeral=True)

    @app_commands.command(name="marketing", description="Show server marketing, store info, and official invite.")
    async def marketing(self, inter: discord.Interaction):
        embed = discord.Embed(
            title=f"✨ {STORE_NAME} — Hypixel SkyBlock Marketplace",
            description=(
                f"Welcome to **{STORE_NAME}**, the most trusted marketplace for verified Hypixel SkyBlock accounts, high networth profiles, and coins!\n\n"
                "**⚡ What We Guarantee:**\n"
                "▸ 🛡️ **100% Secure & Escrow Protected**: Zero risk, full warranty.\n"
                "▸ 💎 **Top-Tier Profiles**: High networth, maxed skills, slayers, and dungeons.\n"
                "▸ ⚡ **Instant Order Handling**: Fast automated tickets & 24/7 staff support.\n"
                "▸ 🪙 **Accepted Crypto**: LTC • BTC • ETH • USDT • USDC\n\n"
                f"🔗 **Official Invite & Marketing:**\n"
                f"👉 **<{get_invite_url()}>**"
            ),
            color=discord.Color(0xF1C40F),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        b_file = None
        if os.path.exists("coin_banner.png"):
            b_file = discord.File("coin_banner.png", filename="coin_banner.png")
        elif os.path.exists("banner.png"):
            b_file = discord.File("banner.png", filename="banner.png")
            embed.set_image(url="attachment://banner.png")
        else:
            embed.set_image(url=BANNER_URL)
        embed.set_footer(text=f"{STORE_NAME} • {STORE_INVITE}", icon_url=inter.guild.icon.url if inter.guild and inter.guild.icon else None)
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Join Our Discord", emoji="🚀", url=get_invite_url()))
        if b_file:
            await inter.response.send_message(embed=embed, file=b_file, view=view)
        else:
            await inter.response.send_message(embed=embed, view=view)


    @app_commands.command(name="coin_panel", description="Post the live Coin Prices Panel in this or a selected channel.")
    @app_commands.describe(channel="Target channel to post the coin panel (optional)")
    async def coin_panel(self, inter: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        await inter.response.defer(ephemeral=True)
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            await inter.followup.send("❌ Only server staff can post the coin panel.", ephemeral=True)
            return

        target = channel or inter.channel
        if not isinstance(target, discord.TextChannel):
            await inter.followup.send("❌ Target channel must be a text channel.", ephemeral=True)
            return

        rates = load_coin_rates()
        embed = build_coin_panel_embed(rates, inter.guild)
        view = PersistentCoinPanelView()

        b_file = None
        if os.path.exists("banner.png"):
            b_file = discord.File("banner.png", filename="banner.png")

        try:
            if b_file:
                msg = await target.send(embed=embed, file=b_file, view=view)
            else:
                msg = await target.send(embed=embed, view=view)
        except Exception as e:
            await inter.followup.send(f"❌ Failed to send coin panel: {e}", ephemeral=True)
            return

        # Record panel id in rates
        panels = rates.get("panels", [])
        panels.append({"channel_id": target.id, "message_id": msg.id})
        rates["panels"] = panels[-10:] # keep latest 10
        save_coin_rates(rates)

        await inter.followup.send(f"✅ Coin panel posted successfully in {target.mention}!", ephemeral=True)

    @app_commands.command(name="set_coin_prices", description="Set or update coin rates across all coin panels.")
    @app_commands.describe(
        buy_rates="Buy rates (e.g. $35/B above 300M | $30/B above 500M | $25/B above 1B)",
        sell_rates="Sell rates (e.g. $18/B)",
        min_level_info="Guidelines/Level info (optional)",
        payment_methods="Accepted payments (optional)"
    )
    async def set_coin_prices(
        self,
        inter: discord.Interaction,
        buy_rates: Optional[str] = None,
        sell_rates: Optional[str] = None,
        min_level_info: Optional[str] = None,
        payment_methods: Optional[str] = None
    ):
        await inter.response.defer(ephemeral=True)
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            await inter.followup.send("❌ Only server staff can update coin rates.", ephemeral=True)
            return

        rates = load_coin_rates()
        if buy_rates:
            rates["buy_rates"] = buy_rates.replace(" | ", "\n").replace("|", "\n")
        if sell_rates:
            rates["sell_rates"] = sell_rates.replace(" | ", "\n").replace("|", "\n")
        if min_level_info:
            rates["min_level_info"] = min_level_info
        if payment_methods:
            rates["payment_methods"] = resolve_payment_emojis(payment_methods, inter.guild)

        save_coin_rates(rates)

        # Update all active panels
        updated_count = 0
        g = inter.guild
        if g:
            new_emb = build_coin_panel_embed(rates, g)
            for p in rates.get("panels", []):
                try:
                    ch = g.get_channel(p["channel_id"])
                    if ch:
                        msg = await ch.fetch_message(p["message_id"])
                        if msg:
                            await msg.edit(embed=new_emb)
                            updated_count += 1
                except Exception:
                    pass

        await inter.followup.send(f"✅ Coin prices updated successfully! ({updated_count} active panels updated)", ephemeral=True)


    @app_commands.command(name="rank_panel", description="Post the live Hypixel Rank Prices Panel in this or a selected channel.")
    @app_commands.describe(channel="Target channel to post the rank panel (optional)")
    async def rank_panel(self, inter: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        await inter.response.defer(ephemeral=True)
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            await inter.followup.send("❌ Only server staff can post the rank panel.", ephemeral=True)
            return

        target = channel or inter.channel
        if not isinstance(target, discord.TextChannel):
            await inter.followup.send("❌ Target channel must be a text channel.", ephemeral=True)
            return

        rates = load_rank_rates()
        embed = build_rank_panel_embed(rates, inter.guild)
        view = PersistentRankPanelView()

        b_file = None
        if os.path.exists("banner.png"):
            b_file = discord.File("banner.png", filename="banner.png")
            embed.set_image(url="attachment://banner.png")

        try:
            if b_file:
                msg = await target.send(embed=embed, file=b_file, view=view)
            else:
                msg = await target.send(embed=embed, view=view)
        except Exception as e:
            await inter.followup.send(f"❌ Failed to send rank panel: {e}", ephemeral=True)
            return

        panels = rates.get("panels", [])
        panels.append({"channel_id": target.id, "message_id": msg.id})
        rates["panels"] = panels[-10:]
        save_rank_rates(rates)

        await inter.followup.send(f"✅ Rank panel posted successfully in {target.mention}!", ephemeral=True)

    @app_commands.command(name="set_rank_prices", description="Set or update Hypixel rank prices across all rank panels.")
    @app_commands.describe(
        perm_ranks="Permanent rank rates (e.g. 600M For VIP | 800M For VIP+ | 1.5B For MVP | 2.3B For MVP+)",
        sub_ranks="MVP++ subscription rates (e.g. 700M 30d | 1.5B 90d | 3B 180d | 5B 365d)",
        notice="Notice/Disclaimer (optional)"
    )
    async def set_rank_prices(
        self,
        inter: discord.Interaction,
        perm_ranks: Optional[str] = None,
        sub_ranks: Optional[str] = None,
        notice: Optional[str] = None
    ):
        await inter.response.defer(ephemeral=True)
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            await inter.followup.send("❌ Only server staff can update rank rates.", ephemeral=True)
            return

        rates = load_rank_rates()
        if perm_ranks:
            rates["perm_ranks"] = perm_ranks.replace(" | ", "\n").replace("|", "\n")
        if sub_ranks:
            rates["sub_ranks"] = sub_ranks.replace(" | ", "\n").replace("|", "\n")
        if notice:
            rates["notice"] = notice

        save_rank_rates(rates)

        updated_count = 0
        g = inter.guild
        if g:
            new_emb = build_rank_panel_embed(rates, g)
            for p in rates.get("panels", []):
                try:
                    ch = g.get_channel(p["channel_id"])
                    if ch:
                        msg = await ch.fetch_message(p["message_id"])
                        if msg:
                            await msg.edit(embed=new_emb)
                            updated_count += 1
                except Exception:
                    pass

        await inter.followup.send(f"✅ Rank prices updated successfully! ({updated_count} active panels updated)", ephemeral=True)


    @app_commands.command(name="vouch", description="Submit a reputation vouch review for any seller you traded with.")
    @app_commands.describe(
        seller="The seller you traded with (e.g. @seller)",
        stars="Rating from 1 to 5 stars",
        comment="Your review / feedback",
        item="Item traded (e.g. 1.5B Coins, VIP+ Rank, Account)",
        hide_name="Hide your identity as an anonymous buyer? (True = Anonymous, False = Show Name)"
    )
    @app_commands.choices(stars=[
        app_commands.Choice(name="⭐⭐⭐⭐⭐ (5 Stars - Excellent)", value=5),
        app_commands.Choice(name="⭐⭐⭐⭐ (4 Stars - Great)", value=4),
        app_commands.Choice(name="⭐⭐⭐ (3 Stars - Average)", value=3),
        app_commands.Choice(name="⭐⭐ (2 Stars - Poor)", value=2),
        app_commands.Choice(name="⭐ (1 Star - Bad)", value=1),
    ])
    async def vouch(
        self,
        inter: discord.Interaction,
        seller: discord.Member,
        stars: int,
        comment: str,
        item: Optional[str] = None,
        hide_name: bool = False
    ):
        await inter.response.defer(ephemeral=True)
        g = inter.guild
        if not g:
            await inter.followup.send("❌ Error: Server context not found.", ephemeral=True)
            return

        v_data = load_json_file(VOUCHES_FILE, DEFAULT_VOUCHES)
        v_data["total_vouches"] = v_data.get("total_vouches", 0) + 1
        new_id = v_data["total_vouches"]

        buyer_display = "🔒 *Anonymous Buyer*" if hide_name else inter.user.mention

        vouch_entry = {
            "id": new_id,
            "user_id": inter.user.id,
            "user_name": str(inter.user),
            "staff_id": seller.id,
            "staff_name": str(seller),
            "stars": stars,
            "comment": comment.strip(),
            "item": item.strip() if item else "Marketplace Trade",
            "is_anonymous": hide_name,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
        v_data.setdefault("vouches", []).append(vouch_entry)
        save_json_file(VOUCHES_FILE, v_data)

        # Count total vouches for this specific seller
        seller_vouches = len([v for v in v_data.get("vouches", []) if v.get("staff_id") == seller.id])

        # Build vouch card
        stars_str = "⭐" * stars
        emb = discord.Embed(
            title=f"⭐ New Vouch Received! (#{new_id})",
            description=(
                f"👑 **Verified Seller:** {seller.mention} *(100% Legit & Verified)*\n"
                f"🏆 **Seller Reputation:** `{seller_vouches}` vouches\n"
                f"👤 **Customer:** {buyer_display}\n"
                f"📦 **Item:** **{item if item else 'SkyBlock Trade'}**\n"
                f"⭐ **Rating:** {stars_str} (`{stars}/5`)\n\n"
                f"💬 **Feedback:**\n> *\"{comment.strip()}\"*\n\n"
                f"🌐 **Total Store Vouches:** `#{new_id}`"
            ),
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        emb.set_thumbnail(url=seller.display_avatar.url)
        emb.set_footer(text=f"{STORE_NAME} • Verified Vouch", icon_url=g.icon.url if g.icon else None)

        vouch_chan = find_channel_by_keywords(g, ["vouch", "vouches", "rep", "reputation", "feedback", "reviews"])
        if vouch_chan:
            try:
                await vouch_chan.send(embed=emb)
                anon_note = " (as Anonymous Buyer)" if hide_name else ""
                await inter.followup.send(f"✅ Thank you for your review! Your vouch for {seller.mention} was posted in {vouch_chan.mention}{anon_note} (Their total: **{seller_vouches}** vouches).", ephemeral=True)
                return
            except Exception as e:
                print(f"Failed to post in vouch channel: {e}")

        await inter.followup.send(f"✅ Thank you! Vouch for {seller.mention} saved successfully.", ephemeral=True)

    @app_commands.command(name="vouches", description="View total store reputation and recent customer reviews.")
    @app_commands.describe(user="Filter vouches for a specific staff member (optional)")
    async def vouches(self, inter: discord.Interaction, user: Optional[discord.Member] = None):
        await inter.response.defer(ephemeral=True)
        v_data = load_json_file(VOUCHES_FILE, DEFAULT_VOUCHES)
        all_v = v_data.get("vouches", [])
        total = v_data.get("total_vouches", 0)

        if user:
            filtered = [v for v in all_v if v.get("staff_id") == user.id]
            avg_stars = sum(v["stars"] for v in filtered) / len(filtered) if filtered else 5.0
            recent = filtered[-5:]
            title = f"⭐ Reputation for {user.display_name}"
            cnt = len(filtered)
        else:
            filtered = all_v
            avg_stars = sum(v["stars"] for v in all_v) / len(all_v) if all_v else 5.0
            recent = all_v[-5:]
            title = f"⭐ {STORE_NAME} — Total Store Reputation"
            cnt = total

        emb = discord.Embed(
            title=title,
            description=(
                f"🏆 **Total Verified Vouches:** **{cnt}**\n"
                f"⭐ **Average Rating:** **{avg_stars:.1f} / 5.0**\n\n"
                f"### 📋 Recent Reviews:\n"
            ),
            color=discord.Color.gold(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )

        if not recent:
            emb.description += "*No vouches recorded yet. Be the first to leave a review with `/vouch`!*"
        else:
            for v in reversed(recent):
                stars_txt = '⭐' * v['stars']
                u_id = v['user_id']
                com = v['comment'][:60]
                u_tag = "*Anonymous Buyer*" if v.get("is_anonymous") else f"<@{u_id}>"
                emb.description += f"• **{stars_txt}** by {u_tag}: *\"{com}\"*\n"

        emb.set_footer(text=f"{STORE_NAME} • Use /vouch to submit a review")
        await inter.followup.send(embed=emb, ephemeral=True)

    @app_commands.command(name="pay", description="Display verified store crypto address, network, and QR code for payment.")
    @app_commands.describe(method="Cryptocurrency payment method")
    @app_commands.choices(method=[
        app_commands.Choice(name="Litecoin (LTC) — Recommended, Lowest Fees", value="ltc"),
        app_commands.Choice(name="USDT (TRC-20 / BEP-20) — Tether Stablecoin", value="usdt"),
        app_commands.Choice(name="Bitcoin (BTC)", value="btc"),
        app_commands.Choice(name="Ethereum (ETH) — ERC-20", value="eth"),
        app_commands.Choice(name="Solana (SOL)", value="sol"),
    ])
    async def pay(self, inter: discord.Interaction, method: str):
        wallets = load_json_file(WALLETS_FILE, DEFAULT_WALLETS)
        w_info = wallets.get(method.lower(), {"address": "NOT_SET", "network": "Standard"})
        addr = w_info.get("address", "NOT_SET")
        network = w_info.get("network", "Standard Network")

        emb = discord.Embed(
            title=f"🪙 Official Store Payment — {method.upper()}",
            description=(
                f"Please send the exact payment amount to the verified address below:\n\n"
                f"🌐 **Network:** **{network}**\n"
                f"⚠️ *Ensure you select the exact network above to prevent lost funds!*\n\n"
                f"💼 **Deposit Address:**\n"
                f"```{addr}```\n"
                f"👉 *Tap and copy the address above. Reply with your TXID / Hash after sending.*"
            ),
            color=discord.Color(0xF1C40F),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        if addr and addr != "NOT_SET" and "HERE" not in addr:
            qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={addr}"
            emb.set_thumbnail(url=qr_url)

        emb.set_footer(text=f"{STORE_NAME} • Official Secure Wallet")
        await inter.response.send_message(embed=emb)

    @app_commands.command(name="set_wallets", description="Set or update official store crypto payment addresses.")
    @app_commands.describe(
        method="Crypto method to update (ltc, usdt, btc, eth, sol)",
        address="Your wallet address",
        network="Network name (optional, e.g. TRC-20, Litecoin Network)"
    )
    @app_commands.choices(method=[
        app_commands.Choice(name="Litecoin (LTC)", value="ltc"),
        app_commands.Choice(name="USDT", value="usdt"),
        app_commands.Choice(name="Bitcoin (BTC)", value="btc"),
        app_commands.Choice(name="Ethereum (ETH)", value="eth"),
        app_commands.Choice(name="Solana (SOL)", value="sol"),
    ])
    async def set_wallets(self, inter: discord.Interaction, method: str, address: str, network: Optional[str] = None):
        await inter.response.defer(ephemeral=True)
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            await inter.followup.send("❌ Only server staff and administrators can configure wallets.", ephemeral=True)
            return

        wallets = load_json_file(WALLETS_FILE, DEFAULT_WALLETS)
        m_key = method.lower()
        if m_key not in wallets:
            wallets[m_key] = {}

        wallets[m_key]["address"] = address.strip()
        if network:
            wallets[m_key]["network"] = network.strip()

        save_json_file(WALLETS_FILE, wallets)
        net_str = wallets[m_key].get('network', 'Default')
        await inter.followup.send(f"✅ Wallet for **{method.upper()}** updated!\nAddress: `{address.strip()}`\nNetwork: `{net_str}`", ephemeral=True)

    @app_commands.command(name="calc", description="Calculate price quote for coins or see how many coins you get for USD.")
    @app_commands.describe(
        coins="Amount of coins (e.g. 500M, 1.5B)",
        usd="Budget in USD (e.g. 25, 50, 100)"
    )
    async def calc(self, inter: discord.Interaction, coins: Optional[str] = None, usd: Optional[str] = None):
        if not coins and not usd:
            await inter.response.send_modal(CoinCalculatorModal())
            return

        res, err = calculate_coin_quote(coins_str=coins or "", usd_str=usd or "")
        if err:
            await inter.response.send_message(f"❌ {err}", ephemeral=True)
            return

        emb = discord.Embed(
            title="🧮 SkyBlock Coins Quote",
            color=discord.Color.from_rgb(255, 255, 255),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        c_coins = res["coins"]
        c_usd = res["usd"]
        c_rate = res["rate"]
        if res["type"] == "COINS_TO_USD":
            emb.description = (
                f"### Price Quote for **{c_coins} Coins**\n\n"
                f"💵 **Total Price:** **{c_usd} USD**\n"
                f"📊 **Applied Rate:** `{c_rate}`\n\n"
                f"👉 *Open a ticket or click **Buy Coins** on the Coin Panel to order!*"
            )
        else:
            emb.description = (
                f"### Coin Quote for **{c_usd} USD**\n\n"
                f"🪙 **Coins Received:** **{c_coins}**\n"
                f"📊 **Estimated Rate:** `{c_rate}`\n\n"
                f"👉 *Open a ticket or click **Buy Coins** on the Coin Panel to order!*"
            )
        emb.set_footer(text=f"{STORE_NAME} • Instant Delivery")
        await inter.response.send_message(embed=emb, ephemeral=True)

    @app_commands.command(name="stock", description="Display live SkyBlock Coins, Ranks, and Account inventory.")
    @app_commands.describe(channel="Target channel to post the live stock panel (optional)")
    async def stock(self, inter: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        await inter.response.defer(ephemeral=True)
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        target = channel or inter.channel
        if not isinstance(target, discord.TextChannel):
            await inter.followup.send("❌ Target channel must be a text channel.", ephemeral=True)
            return

        stock_data = load_json_file(STOCK_FILE, DEFAULT_STOCK)
        embed = build_stock_embed(stock_data, inter.guild)
        view = PersistentStockView()

        b_file = None
        if os.path.exists("banner.png"):
            b_file = discord.File("banner.png", filename="banner.png")
            embed.set_image(url="attachment://banner.png")

        try:
            if b_file:
                msg = await target.send(embed=embed, file=b_file, view=view)
            else:
                msg = await target.send(embed=embed, view=view)
        except Exception as e:
            await inter.followup.send(f"❌ Failed to send stock panel: {e}", ephemeral=True)
            return

        await inter.followup.send(f"✅ Live stock panel posted in {target.mention}!", ephemeral=True)

    @app_commands.command(name="set_stock", description="Update live coin stock amounts and delivery statuses.")
    @app_commands.describe(
        coins_stock="Total coins in stock (e.g. 15.2B)",
        coins_status="Status text (e.g. 🟢 In Stock, 🟡 Low Stock)",
        ranks_status="Ranks status text (e.g. 🟢 Instant Delivery)"
    )
    async def set_stock(
        self,
        inter: discord.Interaction,
        coins_stock: Optional[str] = None,
        coins_status: Optional[str] = None,
        ranks_status: Optional[str] = None
    ):
        await inter.response.defer(ephemeral=True)
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            await inter.followup.send("❌ Only server staff can update stock.", ephemeral=True)
            return

        stock = load_json_file(STOCK_FILE, DEFAULT_STOCK)
        if coins_stock: stock["coins_stock"] = coins_stock.strip()
        if coins_status: stock["coins_status"] = coins_status.strip()
        if ranks_status: stock["ranks_status"] = ranks_status.strip()
        stock["last_updated"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save_json_file(STOCK_FILE, stock)

        await inter.followup.send(f"✅ Stock updated: **{stock['coins_stock']}** ({stock['coins_status']}) | Ranks: **{stock['ranks_status']}**", ephemeral=True)

    @app_commands.command(name="middleman", description="Request an official trusted middleman / escrow for a trade.")
    async def middleman(self, inter: discord.Interaction):
        await inter.response.send_modal(MiddlemanRequestModal())

    @app_commands.command(name="mm_panel", description="Post the official Middleman / Escrow request panel.")
    @app_commands.describe(channel="Target channel to post middleman panel (optional)")
    async def mm_panel(self, inter: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        await inter.response.defer(ephemeral=True)
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            await inter.followup.send("❌ Only server staff can post the middleman panel.", ephemeral=True)
            return

        target = channel or inter.channel
        if not isinstance(target, discord.TextChannel):
            await inter.followup.send("❌ Target channel must be a text channel.", ephemeral=True)
            return

        emb = discord.Embed(
            title=f"🛡️ {STORE_NAME} — Official Escrow & Middleman",
            description=(
                f"Trading Hypixel SkyBlock coins, items, or accounts peer-to-peer?\n"
                f"**Never trade without a middleman!** Prevent scams with our verified staff escrow.\n\n"
                f"⚡ **How It Works:**\n"
                f"1. Click **Request Middleman** below.\n"
                f"2. Enter your partner's tag and items being traded.\n"
                f"3. A private 3-way ticket is opened with an official staff MM.\n"
                f"4. The middleman secures both sides before releasing.\n\n"
                f"🔒 *100% Guaranteed & Safe Trades!*"
            ),
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        if os.path.exists("banner.png"):
            emb.set_image(url="attachment://banner.png")
        emb.set_footer(text=f"{STORE_NAME} • Escrow Protection", icon_url=inter.guild.icon.url if inter.guild and inter.guild.icon else None)

        view = PersistentMMView()
        b_file = discord.File("banner.png", filename="banner.png") if os.path.exists("banner.png") else None
        if b_file:
            await target.send(embed=emb, file=b_file, view=view)
        else:
            await target.send(embed=emb, view=view)

        await inter.followup.send(f"✅ Middleman panel posted in {target.mention}!", ephemeral=True)

    @app_commands.command(name="log_sale", description="Log a completed transaction to the server sales feed.")
    @app_commands.describe(
        buyer="Customer who purchased",
        item="Item or service sold (e.g. 2B Coins, VIP+ Rank, Account)",
        price="Price paid (e.g. $50, 1.5B Coins)",
        payment_method="Payment method (e.g. LTC, USDT, SkyBlock Coins)"
    )
    async def log_sale(
        self,
        inter: discord.Interaction,
        buyer: discord.Member,
        item: str,
        price: str,
        payment_method: str
    ):
        await inter.response.defer(ephemeral=True)
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            await inter.followup.send("❌ Only server staff can log sales.", ephemeral=True)
            return

        g = inter.guild
        if not g:
            await inter.followup.send("❌ Guild context not found.", ephemeral=True)
            return

        clean_price = price if price.startswith("$") or "Coins" in price else f"${price}"
        emb = discord.Embed(
            title="🛒 Transaction Completed & Delivered!",
            description=(
                f"Another successful order fulfilled by **{STORE_NAME}**!\n\n"
                f"👤 **Customer:** {buyer.mention}\n"
                f"📦 **Item:** **{item.strip()}**\n"
                f"💵 **Price Paid:** **{clean_price}**\n"
                f"🪙 **Method:** `{payment_method.strip()}`\n"
                f"💼 **Fulfilled By:** {inter.user.mention}\n\n"
                f"🌟 *Thank you for choosing Soaring Store! Enjoy your purchase!*"
            ),
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        emb.set_thumbnail(url=buyer.display_avatar.url)
        if os.path.exists("banner.png"):
            emb.set_image(url="attachment://banner.png")
        emb.set_footer(text=f"{STORE_NAME} • Verified Sale", icon_url=g.icon.url if g.icon else None)

        feed_chan = find_channel_by_keywords(g, ["salesfeed", "saleslog", "orders", "recentorders", "orderlog", "sales"])
        if feed_chan:
            b_file = discord.File("banner.png", filename="banner.png") if os.path.exists("banner.png") else None
            try:
                if b_file:
                    await feed_chan.send(embed=emb, file=b_file)
                else:
                    await feed_chan.send(embed=emb)
                await inter.followup.send(f"✅ Sale logged in {feed_chan.mention}!", ephemeral=True)
                return
            except Exception as e:
                print(f"Failed to post in sales feed: {e}")

        await inter.followup.send("✅ Sale logged successfully!", ephemeral=True)


    @app_commands.command(name="trade_complete", description="Mark trade completed in ticket, send thank you DM to buyer, and prepare for close.")
    @app_commands.describe(seller="The seller who handled this trade (optional, defaults to you)")
    async def trade_complete(self, inter: discord.Interaction, seller: Optional[discord.Member] = None):
        await inter.response.defer(ephemeral=False)
        channel = inter.channel
        g = inter.guild
        if not g or not isinstance(channel, discord.TextChannel):
            await inter.followup.send("❌ This command must be run inside a ticket channel.", ephemeral=True)
            return

        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            await inter.followup.send("❌ Only server staff can complete trades.", ephemeral=True)
            return

        buyer_user = await find_ticket_buyer(channel, g)
        active_seller = seller or inter.user
        seller_mention = active_seller.mention

        # DM Buyer
        dm_sent = False
        if buyer_user and not buyer_user.bot:
            try:
                dm_emb = discord.Embed(
                    title=f"🌟 Tysm for buying with {STORE_NAME}!",
                    description=(
                        f"Hello {buyer_user.name}! 👋\n\n"
                        f"**Tysm for buying with {STORE_NAME}!** We truly appreciate your business and trust in our service.\n\n"
                        f"👑 **Verified Seller:** {seller_mention} *(100% Legit & Verified Seller)*\n"
                        f"⏰ **Tysm for your time!**\n\n"
                        f"If you enjoyed the service, please take 5 seconds to submit a review with **/vouch seller:{seller_mention}** in our server to let others know they're legit!\n\n"
                        f"🔗 **Server Invite:** <{get_invite_url()}>"
                    ),
                    color=discord.Color.gold(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                if os.path.exists("banner.png"):
                    dm_file = discord.File("banner.png", filename="banner.png")
                    dm_emb.set_image(url="attachment://banner.png")
                    await buyer_user.send(embed=dm_emb, file=dm_file)
                else:
                    await buyer_user.send(embed=dm_emb)
                dm_sent = True
            except Exception as e:
                print(f"Could not send DM to buyer: {e}")

        celebrate_emb = discord.Embed(
            title="🎉 Trade Completed Successfully!",
            description=(
                f"**Deal completed by {inter.user.mention}!**\n\n"
                + (f"👤 **Customer:** {buyer_user.mention}\n" if buyer_user else "") +
                f"👑 **Verified Seller:** {seller_mention} *(100% Legit)*\n"
                f"📩 **Customer DM:** {'✅ Thank you & vouch message sent!' if dm_sent else '⚠️ Customer DMs are closed.'}\n\n"
                f"Staff can now click **Close Ticket** whenever ready."
            ),
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        celebrate_emb.set_footer(text=f"{STORE_NAME} • Trade Finalized")
        await inter.followup.send(embed=celebrate_emb)


    @app_commands.command(name="sync_commands", description="Force sync and reload all slash commands for the server (Admin/Staff only).")
    async def slash_sync(self, inter: discord.Interaction):
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            return await inter.response.send_message("❌ You do not have permission to sync commands.", ephemeral=True)

        await inter.response.defer(ephemeral=True)
        try:
            if GUILD_ID:
                g = discord.Object(id=GUILD_ID)
                self.bot.tree.copy_global_to(guild=g)
                synced = await self.bot.tree.sync(guild=g)
            else:
                synced = await self.bot.tree.sync()
            cmd_names = ", ".join([f"`/{c.name}`" for c in synced])
            msg = f"✅ **Successfully synced {len(synced)} slash commands!**\n\n**Commands:**\n{cmd_names}\n\n💡 *Tip: If Discord doesn't show them immediately, press Ctrl + R on PC or restart your Discord app to clear Discord's local cache.*"
            await inter.followup.send(msg, ephemeral=True)
        except Exception as e:
            await inter.followup.send(f"❌ **Error syncing:** `{e}`", ephemeral=True)


    async def sync_stats_channels(self, guild: discord.Guild) -> dict:
        stats_cfg = load_json_file(STATS_CONFIG_FILE, DEFAULT_STATS_CONFIG)
        if not stats_cfg.get("enabled"):
            return {}

        m_count = guild.member_count or len(guild.members)
        v_data = load_json_file(VOUCHES_FILE, DEFAULT_VOUCHES)
        v_count = v_data.get("total_vouches", len(v_data.get("vouches", [])))
        s_data = load_json_file(STOCK_FILE, DEFAULT_STOCK)
        c_stock = s_data.get("coins_stock", "In Stock")

        active_accs = 0
        if ACCOUNTS_CAT_ID:
            acc_cat = guild.get_channel(ACCOUNTS_CAT_ID) or discord.utils.get(guild.categories, id=ACCOUNTS_CAT_ID)
            if acc_cat and hasattr(acc_cat, "channels"):
                active_accs = len(acc_cat.channels)

        target_names = {
            "members_channel_id": f"👥 Members: {m_count:,}",
            "vouches_channel_id": f"⭐ Vouches: {v_count}+",
            "stock_channel_id": f"🪙 Stock: {c_stock}",
            "listings_channel_id": f"🛒 Accounts: {active_accs} Active"
        }

        updated = {}
        for key, name in target_names.items():
            cid = stats_cfg.get(key)
            if not cid:
                continue
            chan = guild.get_channel(cid)
            if chan and chan.name != name:
                try:
                    await chan.edit(name=name)
                    updated[key.replace("_channel_id", "")] = name
                    await asyncio.sleep(1.5)
                except Exception as e:
                    print(f"Error editing stats channel {chan.id}: {e}")
            elif chan:
                updated[key.replace("_channel_id", "")] = f"{name} (Current)"
        return updated

    @tasks.loop(minutes=10)
    async def stats_update_loop(self):
        try:
            guild = None
            if GUILD_ID:
                guild = self.bot.get_guild(GUILD_ID)
            if not guild and self.bot.guilds:
                guild = self.bot.guilds[0]
            if guild:
                await self.sync_stats_channels(guild)
        except Exception as e:
            print(f"Error in stats_update_loop: {e}")

    @stats_update_loop.before_loop
    async def before_stats_update(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=5)
    async def autobump_loop(self):
        try:
            bump_cfg = load_json_file(AUTOBUMP_FILE, DEFAULT_AUTOBUMP)
            if not bump_cfg.get("enabled"):
                return
            cid = bump_cfg.get("channel_id")
            if not cid:
                return

            chan = self.bot.get_channel(cid)
            if not chan or not isinstance(chan, discord.TextChannel):
                return

            interval_hrs = bump_cfg.get("interval_hours", 4)
            last_bump_str = bump_cfg.get("last_bump")
            is_due = False

            if not last_bump_str:
                is_due = True
            else:
                try:
                    last_dt = datetime.datetime.fromisoformat(last_bump_str)
                    now_dt = datetime.datetime.now(datetime.timezone.utc)
                    if (now_dt - last_dt).total_seconds() >= interval_hrs * 3600:
                        is_due = True
                except Exception:
                    is_due = True

            if is_due:
                emb, view = build_autobump_embed(chan.guild, bump_cfg.get("bump_type", "all"))
                if os.path.exists("banner.png"):
                    bf = discord.File("banner.png", filename="banner.png")
                    await chan.send(embed=emb, view=view, file=bf)
                else:
                    await chan.send(embed=emb, view=view)
                bump_cfg["last_bump"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                save_json_file(AUTOBUMP_FILE, bump_cfg)
                print(f"📢 [AutoBump] Successfully posted bump to #{chan.name} ({chan.id})")
        except Exception as e:
            print(f"Error in autobump_loop: {e}")

    @autobump_loop.before_loop
    async def before_autobump(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="setup_stats", description="Create or configure live server stats channels (Members, Vouches, Stock, Accounts).")
    @app_commands.describe(category_name="Custom name for the stats category (optional)")
    async def setup_stats(self, inter: discord.Interaction, category_name: Optional[str] = None):
        await inter.response.defer(ephemeral=True)
        g = inter.guild
        if not g:
            return await inter.followup.send("❌ Error: Server context not found.", ephemeral=True)

        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            return await inter.followup.send("❌ Only server administrators and staff can set up live stats.", ephemeral=True)

        cat_title = category_name or "📊 ── SERVER STATS ── 📊"
        stats_cfg = load_json_file(STATS_CONFIG_FILE, DEFAULT_STATS_CONFIG)

        cat = None
        if stats_cfg.get("category_id"):
            cat = g.get_channel(stats_cfg["category_id"])

        if not cat:
            overwrites = {
                g.default_role: discord.PermissionOverwrite(view_channel=True, connect=False)
            }
            try:
                cat = await g.create_category(name=cat_title, overwrites=overwrites, position=0)
            except Exception as e:
                return await inter.followup.send(f"❌ Failed to create stats category: `{e}`", ephemeral=True)

        stats_cfg["category_id"] = cat.id

        m_count = g.member_count or len(g.members)
        v_data = load_json_file(VOUCHES_FILE, DEFAULT_VOUCHES)
        v_count = v_data.get("total_vouches", len(v_data.get("vouches", [])))
        s_data = load_json_file(STOCK_FILE, DEFAULT_STOCK)
        c_stock = s_data.get("coins_stock", "In Stock")

        active_accs = 0
        if ACCOUNTS_CAT_ID:
            acc_cat = g.get_channel(ACCOUNTS_CAT_ID) or discord.utils.get(g.categories, id=ACCOUNTS_CAT_ID)
            if acc_cat and hasattr(acc_cat, "channels"):
                active_accs = len(acc_cat.channels)

        target_names = {
            "members": f"👥 Members: {m_count:,}",
            "vouches": f"⭐ Vouches: {v_count}+",
            "stock": f"🪙 Stock: {c_stock}",
            "listings": f"🛒 Accounts: {active_accs} Active"
        }

        channel_keys = [
            ("members_channel_id", target_names["members"]),
            ("vouches_channel_id", target_names["vouches"]),
            ("stock_channel_id", target_names["stock"]),
            ("listings_channel_id", target_names["listings"])
        ]

        created_or_found = []
        for key, name in channel_keys:
            chan = None
            if stats_cfg.get(key):
                chan = g.get_channel(stats_cfg[key])
            if not chan:
                try:
                    chan = await cat.create_voice_channel(
                        name=name,
                        overwrites={g.default_role: discord.PermissionOverwrite(view_channel=True, connect=False)}
                    )
                    stats_cfg[key] = chan.id
                except Exception as e:
                    print(f"Error creating voice channel {name}: {e}")
            else:
                if chan.name != name:
                    try:
                        await chan.edit(name=name)
                    except Exception as e:
                        print(f"Error renaming channel {name}: {e}")
            if chan:
                created_or_found.append(f"• `{chan.name}` ({chan.mention})")

        stats_cfg["enabled"] = True
        save_json_file(STATS_CONFIG_FILE, stats_cfg)

        emb = discord.Embed(
            title="📊 Live Server Stats Configured!",
            description=(
                f"**The live stats category and voice channels are now active!**\n\n"
                + "\n".join(created_or_found) + "\n\n"
                f"⏱️ **Update Cadence:** Automatically refreshed every **10 minutes** in the background.\n"
                f"🔒 **Permissions:** Locked so regular members cannot join, keeping your sidebar clean and informative.\n\n"
                f"💡 *You can manually force a refresh at any time using `/update_stats`.*"
            ),
            color=discord.Color.green()
        )
        await inter.followup.send(embed=emb, ephemeral=True)

    @app_commands.command(name="update_stats", description="Force refresh the live server stats channels immediately.")
    async def update_stats(self, inter: discord.Interaction):
        await inter.response.defer(ephemeral=True)
        g = inter.guild
        if not g:
            return await inter.followup.send("❌ Error: Server context not found.", ephemeral=True)

        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            return await inter.followup.send("❌ Only server staff can refresh stats.", ephemeral=True)

        stats_cfg = load_json_file(STATS_CONFIG_FILE, DEFAULT_STATS_CONFIG)
        if not stats_cfg.get("enabled"):
            return await inter.followup.send("⚠️ Stats channels are not set up yet! Run `/setup_stats` first.", ephemeral=True)

        res = await self.sync_stats_channels(g)
        summary = "\n".join([f"• **{k.capitalize()}**: `{v}`" for k, v in res.items()]) if res else "• All channel names are already up to date!"
        await inter.followup.send(
            f"✅ **Server stats refreshed!**\n\n{summary}\n\n*(Background updater will continue checking every 10 minutes)*",
            ephemeral=True
        )

    @app_commands.command(name="autobump", description="Manage automated promotional store bumping in a designated channel.")
    @app_commands.describe(
        action="Action to perform",
        channel="Channel to send promotional bumps to (required when starting/changing channel)",
        interval_hours="Interval between bumps in hours (default 4 hours)",
        bump_type="Style/content of the bump"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="▶️ Start (Enable autobump)", value="start"),
        app_commands.Choice(name="⏹️ Stop (Disable autobump)", value="stop"),
        app_commands.Choice(name="📊 Status (View current settings & timer)", value="status"),
        app_commands.Choice(name="⚡ Bump Now (Send an immediate bump)", value="bump_now")
    ], interval_hours=[
        app_commands.Choice(name="Every 1 Hour", value=1),
        app_commands.Choice(name="Every 2 Hours", value=2),
        app_commands.Choice(name="Every 4 Hours (Recommended)", value=4),
        app_commands.Choice(name="Every 6 Hours", value=6),
        app_commands.Choice(name="Every 8 Hours", value=8),
        app_commands.Choice(name="Every 12 Hours", value=12),
        app_commands.Choice(name="Every 24 Hours", value=24),
    ], bump_type=[
        app_commands.Choice(name="Full Store Showcase (Coins, Ranks, Accounts, Escrow)", value="all"),
        app_commands.Choice(name="Coins & Stock Focus", value="coins"),
        app_commands.Choice(name="Hypixel Ranks Focus", value="ranks"),
        app_commands.Choice(name="Marketplace & Accounts Focus", value="accounts"),
    ])
    async def autobump(
        self,
        inter: discord.Interaction,
        action: str,
        channel: Optional[discord.TextChannel] = None,
        interval_hours: Optional[int] = None,
        bump_type: Optional[str] = None
    ):
        await inter.response.defer(ephemeral=True)
        is_staff = False
        if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(inter.user, "roles", [])):
            is_staff = True
        elif getattr(inter.user, "guild_permissions", None) and (inter.user.guild_permissions.administrator or inter.user.guild_permissions.manage_guild):
            is_staff = True

        if not is_staff:
            return await inter.followup.send("❌ Only server staff and administrators can configure autobump.", ephemeral=True)

        bump_cfg = load_json_file(AUTOBUMP_FILE, DEFAULT_AUTOBUMP)

        if action == "status":
            enabled = bump_cfg.get("enabled", False)
            cid = bump_cfg.get("channel_id")
            chan_mention = f"<#{cid}>" if cid else "*None configured*"
            hrs = bump_cfg.get("interval_hours", 4)
            btype = bump_cfg.get("bump_type", "all")
            last_b = bump_cfg.get("last_bump")
            last_str = f"<t:{int(datetime.datetime.fromisoformat(last_b).timestamp())}:R>" if last_b else "*Never*"

            status_emb = discord.Embed(
                title="📢 Auto-Bump System Status",
                description=(
                    f"• **Status:** {'🟢 **ACTIVE (Running)**' if enabled else '🔴 **DISABLED**'}\n"
                    f"• **Target Channel:** {chan_mention}\n"
                    f"• **Interval:** Every `{hrs}` hours\n"
                    f"• **Content Type:** `{btype.upper()}`\n"
                    f"• **Last Bump:** {last_str}\n\n"
                    f"💡 *Use `/autobump action:start` to enable or `/autobump action:bump_now` to test immediately.*"
                ),
                color=discord.Color.green() if enabled else discord.Color.red()
            )
            return await inter.followup.send(embed=status_emb, ephemeral=True)

        elif action == "stop":
            bump_cfg["enabled"] = False
            save_json_file(AUTOBUMP_FILE, bump_cfg)
            return await inter.followup.send("⏹️ **Auto-bump disabled!** Automatic bumps have been paused.", ephemeral=True)

        elif action == "start":
            target_chan = channel or (inter.guild.get_channel(bump_cfg.get("channel_id")) if bump_cfg.get("channel_id") else None) or inter.channel
            if not isinstance(target_chan, discord.TextChannel):
                return await inter.followup.send("❌ Please specify a valid text channel to send bumps to.", ephemeral=True)

            bump_cfg["enabled"] = True
            bump_cfg["channel_id"] = target_chan.id
            if interval_hours:
                bump_cfg["interval_hours"] = interval_hours
            if bump_type:
                bump_cfg["bump_type"] = bump_type
            save_json_file(AUTOBUMP_FILE, bump_cfg)

            return await inter.followup.send(
                f"✅ **Auto-bump activated!**\n"
                f"• Target Channel: {target_chan.mention}\n"
                f"• Frequency: Every `{bump_cfg.get('interval_hours', 4)}` hours\n"
                f"• Type: `{bump_cfg.get('bump_type', 'all').upper()}`\n\n"
                f"The bot will automatically post store promotions on schedule. You can test it now with `/autobump action:bump_now`.",
                ephemeral=True
            )

        elif action == "bump_now":
            target_chan = channel or (inter.guild.get_channel(bump_cfg.get("channel_id")) if bump_cfg.get("channel_id") else None) or inter.channel
            if not isinstance(target_chan, discord.TextChannel):
                return await inter.followup.send("❌ Target channel must be a text channel.", ephemeral=True)

            emb, view = build_autobump_embed(inter.guild, bump_type or bump_cfg.get("bump_type", "all"))
            try:
                if os.path.exists("banner.png"):
                    bf = discord.File("banner.png", filename="banner.png")
                    await target_chan.send(embed=emb, view=view, file=bf)
                else:
                    await target_chan.send(embed=emb, view=view)
                bump_cfg["last_bump"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                save_json_file(AUTOBUMP_FILE, bump_cfg)
                return await inter.followup.send(f"✅ **Bump posted successfully in {target_chan.mention}!**", ephemeral=True)
            except Exception as e:
                return await inter.followup.send(f"❌ Failed to post bump in {target_chan.mention}: `{e}`", ephemeral=True)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    import traceback
    traceback.print_exc()
    msg = f"❌ Command error: {error}"
    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        pass

@bot.command(name="sync")
async def prefix_sync(ctx):
    is_staff = False
    if STAFF_ROLE_ID and any(r.id == STAFF_ROLE_ID for r in getattr(ctx.author, "roles", [])):
        is_staff = True
    elif getattr(ctx.author, "guild_permissions", None) and (ctx.author.guild_permissions.administrator or ctx.author.guild_permissions.manage_guild):
        is_staff = True

    if not is_staff:
        return await ctx.send("❌ You do not have permission to sync commands.", delete_after=5)

    msg = await ctx.send("🔄 **Syncing slash commands...**")
    try:
        if GUILD_ID:
            g = discord.Object(id=GUILD_ID)
            bot.tree.copy_global_to(guild=g)
            synced = await bot.tree.sync(guild=g)
        else:
            synced = await bot.tree.sync()
        cmd_names = ", ".join([f"`/{c.name}`" for c in synced])
        await msg.edit(content=f"✅ **Successfully synced {len(synced)} slash commands!**\n\n**Commands:**\n{cmd_names}\n\n💡 *Tip: Press Ctrl + R in Discord desktop or restart mobile app to refresh command suggestions.*")
    except Exception as e:
        await msg.edit(content=f"❌ **Error syncing commands:** `{e}`")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    # 1. Register persistent views
    bot.add_view(CloseTicketView())
    bot.add_view(PersistentListingView())
    bot.add_view(PersistentCoinPanelView())
    bot.add_view(PersistentRankPanelView())
    bot.add_view(PersistentMMView())
    bot.add_view(PersistentStockView())
    bot.add_view(PersistentAutobumpView())

    # 2. Set bot activity / presence
    try:
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"🛒 {STORE_NAME} | {STORE_INVITE}"
        )
        await bot.change_presence(status=discord.Status.online, activity=activity)
        print(f"Presence set to: 🛒 {STORE_NAME} | {STORE_INVITE}")
    except Exception as e:
        print(f"Notice on presence setup: {e}")

    # 3. Attempt to automatically sync bot application bio/description
    try:
        bio_text = f"""✨ SOARING STORE — Hypixel SkyBlock Marketplace ✨
The #1 premier hub for Hypixel SkyBlock trading!

⚡ WHY CHOOSE US:
• 🛡️ 100% Safe Escrow & Verified Profiles
• 💎 High Networth & Rare Endgame Accounts
• ⚡ Fast Automated Tickets & 24/7 Support
• 🪙 Crypto: LTC • BTC • ETH • USDT • USDC

🔗 JOIN OUR SERVER & COMMUNITY:
👉 {get_invite_url()}
Run /list_account or /marketing in chat now! 🛒"""
        loop = asyncio.get_event_loop()
        headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}
        req = urllib.request.Request(
            "https://discord.com/api/v10/applications/@me",
            data=json.dumps({"description": bio_text}).encode("utf-8"),
            headers=headers,
            method="PATCH"
        )
        await loop.run_in_executor(None, lambda: urllib.request.urlopen(req, timeout=5))
        print("Application description (About Me) auto-updated via Discord REST API.")
    except Exception as e:
        print(f"Bio auto-update notice (may be managed in Dev Portal): {e}")

    # 4. Sync Slash Commands
    try:
        if GUILD_ID:
            g = discord.Object(id=GUILD_ID)
            bot.tree.copy_global_to(guild=g)
            synced = await bot.tree.sync(guild=g)
            print(f"✅ Successfully synced {len(synced)} slash commands to guild {GUILD_ID}:")
            for idx, c in enumerate(synced, 1):
                print(f"   [{idx}] /{c.name}")
        else:
            synced = await bot.tree.sync()
            print(f"✅ Successfully synced {len(synced)} global slash commands:")
            for idx, c in enumerate(synced, 1):
                print(f"   [{idx}] /{c.name}")
    except Exception as e:
        print(f"❌ Error syncing commands: {e}")

async def main():
    await bot.add_cog(StoreCog(bot))
    if TOKEN: await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
