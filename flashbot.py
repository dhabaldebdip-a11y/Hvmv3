import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import requests

# ================= CONFIG =================
TOKEN = "DISCORD_BIT_TOKEN"

PANEL_URL = "PANEL_URL"
API_KEY = "API_KEY"

GUILD_ID = 1426420145735209061
ADMIN_ROLE_ID = 1449611528713142446

LOCATION_ID = 1
PAPER_EGG_ID = 2
# =========================================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "Application/vnd.pterodactyl.v1+json",
    "Content-Type": "application/json"
}

# ================= READY ==================
@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="FlashNodes Panel"
        )
    )
    print(f"✅ Logged in as {bot.user}")

# ================= HELPERS =================
def is_admin(member):
    return any(role.id == ADMIN_ROLE_ID for role in member.roles)

def get_user_id_by_email(email):
    r = requests.get(f"{PANEL_URL}/api/application/users", headers=headers)
    if r.status_code != 200:
        return None
    for u in r.json()["data"]:
        if u["attributes"]["email"].lower() == email.lower():
            return u["attributes"]["id"]
    return None

def get_server_by_user(user_id):
    r = requests.get(f"{PANEL_URL}/api/application/servers", headers=headers)
    if r.status_code != 200:
        return None
    for s in r.json()["data"]:
        if s["attributes"]["user"] == user_id:
            return s["attributes"]
    return None

def power(server_id, signal):
    requests.post(
        f"{PANEL_URL}/api/application/servers/{server_id}/power",
        headers=headers,
        json={"signal": signal}
    )

# ================= BUTTON VIEW =================
class ServerControl(View):
    def __init__(self, server_id, owner_id):
        super().__init__(timeout=None)
        self.server_id = server_id
        self.owner_id = owner_id

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "❌ Ye server tumhara nahi hai",
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Start", style=discord.ButtonStyle.success, emoji="🟢")
    async def start(self, interaction: discord.Interaction, button: Button):
        power(self.server_id, "start")
        await interaction.response.send_message("🟢 Server starting...", ephemeral=True)

    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="🔴")
    async def stop(self, interaction: discord.Interaction, button: Button):
        power(self.server_id, "stop")
        await interaction.response.send_message("🔴 Server stopping...", ephemeral=True)

    @discord.ui.button(label="Restart", style=discord.ButtonStyle.secondary, emoji="🟡")
    async def restart(self, interaction: discord.Interaction, button: Button):
        power(self.server_id, "restart")
        await interaction.response.send_message("🟡 Server restarting...", ephemeral=True)

# ================= SLASH COMMANDS =================

@bot.tree.command(name="ping", description="Bot status", guild=discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong! Bot online hai", ephemeral=True)

# ---------- CREATE USER ----------
@bot.tree.command(name="create_user", description="Create panel user", guild=discord.Object(id=GUILD_ID))
async def create_user(interaction: discord.Interaction, email: str, password: str):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    data = {
        "email": email,
        "username": email.split("@")[0],
        "first_name": "Panel",
        "last_name": "User",
        "password": password
    }

    r = requests.post(
        f"{PANEL_URL}/api/application/users",
        headers=headers,
        json=data
    )

    if r.status_code == 201:
        await interaction.response.send_message("✅ User created successfully", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Error:\n```{r.text}```", ephemeral=True)

# ---------- CREATE SERVER ----------
@bot.tree.command(name="create_server", description="Create minecraft server", guild=discord.Object(id=GUILD_ID))
async def create_server(
    interaction: discord.Interaction,
    ram_gb: int,
    cpu: int,
    disk_gb: int,
    mc_version: str,
    owner_email: str
):
    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ Admin only", ephemeral=True)
        return

    user_id = get_user_id_by_email(owner_email)
    if not user_id:
        await interaction.response.send_message("❌ User email not found", ephemeral=True)
        return

    data = {
        "name": f"Minecraft {mc_version}",
        "user": user_id,
        "egg": PAPER_EGG_ID,
        "docker_image": "ghcr.io/pterodactyl/yolks:java_21",
        "startup": "java -Xms128M -Xmx{{SERVER_MEMORY}}M -jar server.jar",
        "environment": {
            "SERVER_JARFILE": "server.jar",
            "BUILD_NUMBER": "latest",
            "SERVER_VERSION": mc_version
        },
        "limits": {
            "memory": ram_gb * 1024,
            "swap": 0,
            "disk": disk_gb * 1024,
            "io": 500,
            "cpu": cpu
        },
        "feature_limits": {
            "databases": 1,
            "allocations": 1,
            "backups": 1
        },
        "deploy": {
            "locations": [LOCATION_ID],
            "dedicated_ip": False,
            "port_range": []
        }
    }

    r = requests.post(
        f"{PANEL_URL}/api/application/servers",
        headers=headers,
        json=data
    )

    if r.status_code == 201:
        await interaction.response.send_message("🚀 Server created successfully", ephemeral=True)
    else:
        await interaction.response.send_message(f"❌ Error:\n```{r.text}```", ephemeral=True)

# ---------- USER PANEL ----------
@bot.tree.command(name="my_server", description="Control your server", guild=discord.Object(id=GUILD_ID))
async def my_server(interaction: discord.Interaction, email: str):
    await interaction.response.defer(ephemeral=True)

    user_id = get_user_id_by_email(email)
    server = get_server_by_user(user_id)

    if not server:
        await interaction.followup.send("❌ Server not found", ephemeral=True)
        return

    limits = server["limits"]

    embed = discord.Embed(
        title="🖥️ Your Server",
        color=discord.Color.green()
    )
    embed.add_field(name="RAM", value=f"{limits['memory']//1024} GB")
    embed.add_field(name="CPU", value=f"{limits['cpu']}%")
    embed.add_field(name="Disk", value=f"{limits['disk']//1024} GB")

    view = ServerControl(server["id"], interaction.user.id)

    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

# ================= RUN =====================
bot.run(TOKEN)