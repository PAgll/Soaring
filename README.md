# Soaring Store — Premier Hypixel SkyBlock Marketplace Discord Bot

An all-in-one Discord marketplace, ticketing, escrow, reputation, live statistics, and auto-bumping bot built specifically for Hypixel SkyBlock stores.

---

## ⚡ Complete Slash Commands (23 Total)

### 🛒 Listings & Accounts
- `/list_account` — List a new account with custom stats, auto-created dedicated channel, and buy/offer buttons.
- `/reduce_price` — Reduce listing price, update channel name, and post discount notification.
- `/mark_sold` — Mark listing as SOLD, disable buy buttons, and move channel to SOLD category.

### 🪙 Panels & Economy
- `/coin_panel` — Post the live Coin Prices Panel in this or a selected channel.
- `/set_coin_prices` — Set or update coin rates across all coin panels.
- `/rank_panel` — Post the live Hypixel Rank Prices Panel (VIP, VIP+, MVP, MVP+, MVP++).
- `/set_rank_prices` — Set or update Hypixel rank prices across all rank panels.
- `/stock` — Display live SkyBlock Coins, Ranks, and Account inventory.
- `/set_stock` — Update live coin stock amounts and delivery statuses.
- `/calc` — Calculate price quote for coins or see how many coins you get for USD.

### 📊 Live Server Stats
- `/setup_stats` — Create and configure locked voice channels under a clean category displaying live member count, total vouches, coin stock, and active account listings (auto-refreshes every 10 minutes).
- `/update_stats` — Force an immediate refresh of all live stats channels.

### 📢 Automated Promotion & Bumping
- `/autobump` — Manage automated store promotion and bumping in a designated channel. Supports:
  - `action:start` — Enable scheduled bumping with custom interval (every 1h, 2h, 4h, 6h, 12h, 24h).
  - `action:stop` — Pause automated bumping.
  - `action:status` — View current channel, interval, and next scheduled bump.
  - `action:bump_now` — Instantly send an interactive promotional bump with live rates and button shortcuts.

### ⭐ Reputation & Vouches
- `/vouch` — Submit a reputation review for any seller you traded with (`@seller`, star rating, comment, item traded, and optional anonymous toggle `hide_name`).
- `/vouches` — View total store reputation and recent customer reviews (or filter by specific seller).

### 💳 Payments & Wallets
- `/pay` — Display verified store crypto address, network, and QR code for payment.
- `/set_wallets` — Set or update official store crypto payment addresses (LTC, USDT, BTC, ETH, SOL).

### 🛡️ Middleman / Escrow & Trades
- `/middleman` — Request an official trusted middleman / escrow for a trade via interactive modal.
- `/mm_panel` — Post the official Middleman / Escrow request panel with a persistent "Request Middleman" button.
- `/trade_complete` — Mark trade completed in ticket, send personalized thank you DM to buyer, and prepare for ticket closure.
- `/log_sale` — Log a completed transaction to the server sales feed.

### ⚙️ Server & Administration
- `/marketing` — Show server marketing, store info, and official invite.
- `/sync_commands` — Force sync and reload all slash commands for the server (Admin/Staff only).
- `!sync` — Prefix command to force instant slash command sync from chat.

---

## 🚀 Wispbyte Deployment in 3 Easy Steps

1. **Upload ZIP**: On your Wispbyte server panel, go to **Files**, upload `SoaringStore-Bot-Wispbyte.zip`, and click **Unarchive / Extract**.
2. **Restart Console**: Go to **Console** and click **Restart**.
3. **Instant Discord Sync**:
   - In Discord, press `Ctrl + R` (PC) or restart your mobile app to refresh Discord's local slash command cache.
   - You can also type `!sync` in any channel to force-register commands instantly.
