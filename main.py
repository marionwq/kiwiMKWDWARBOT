import discord
from discord import state
from discord.ext import commands
from flask import Flask, ctx, send_file, request, make_response
import os
from threading import Thread
from dotenv import load_dotenv
import re
import json
import random
import io
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import sqlite3


from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import threading
import base64
import asyncio
import sys 
import traceback

app = Flask(__name__)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
ERROR_CHANNEL_ID = 1412586731026251826  
overlay_cache = {}
matplotlib.rcParams["text.usetex"] = False
matplotlib.rcParams["mathtext.default"] = "regular"
matplotlib.rcParams["axes.unicode_minus"] = False
war_states = {}
summary_messages = {}
public_url = "https://marionwq.github.io/kiwi-overlay"
EMBED_COLOR = discord.Color.from_rgb(46, 79, 47)

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://kiwi-overlay-default-rtdb.europe-west1.firebasedatabase.app/'
})

track_names = {
    "RPB": "Peach Beach (GCN) - rPB",
    "PB": "Peach Beach (GCN) - rPB",
    "SSS": "Salty Salty Speedway - SSS",
    "RR": "Rainbow Road - RR",
    "RMC": "Mario Circuit (SNES) - rMC",
    "MC": "Mario Circuit (SNES) - rMC",
    "AH": "Acorn Heights - AH",
    "BC": "Bowser's Castle - BC",
    "RTF": "Toad's Factory (Wii) - rTF",
    "TF": "Toad's Factory (Wii) - rTF",
    "RCM": "Choco Mountain (N64) - rCM",
    "CM": "Choco Mountain (N64) - rCM",
    "RMMM": "Moo Moo Meadows (Wii) - rMMM",
    "MMM": "Moo Moo Meadows (Wii) - rMMM",
    "DBB": "Dry Bones Burnout - DBB",
    "BCI": "Boo Cinema - BCi",
    "DD": "Dandelion Depths - DD",
    "CCF": "Cheep Cheep Falls - CCF",
    "GBR": "Great ? Block Ruins - GBR",
    "RDDJ": "Dino Dino Jungle (GCN) - rDDJ",
    "DDJ": "Dino Dino Jungle (GCN) - rDDJ",
    "PS": "Peach Stadium - PS",
    "FO": "Faraway Oasis - FO",
    "RKTB": "Koopa Troopa Beach (SNES) - rKTB",
    "KTB": "Koopa Troopa Beach (SNES) - rKTB",
    "RKB": "Koopa Troopa Beach (SNES) - rKTB",
    "KB": "Koopa Troopa Beach (SNES) - rKTB",
    "RWSH": "Wario Shipyard (3DS) - rWSh",
    "WSH": "Wario Shipyard (3DS) - rWSh",
    "RSHS": "Sky-High Sundae (Tour) - rSHS",
    "SHS": "Sky-High Sundae (Tour) - rSHS",
    "SP": "Starview Peak - SP",
    "RDKP": "DK Pass (DS) - rDKP",
    "DKP": "DK Pass (DS) - rDKP",
    "RAF": "Airship Fortress (DS) - rAF",
    "AF": "Airship Fortress (DS) - rAF",
    "RWS": "Wario Stadium (N64) - rWS",
    "RSGB": "Shy Guy Bazaar (3DS) - rSGB",
    "SGB": "Shy Guy Bazaar (3DS) - rSGB",
    "WS": "Whistletop Summit - WS",
    "RDH": "Desert Hills (DS) - rDH",
    "DH": "Desert Hills (DS) - rDH",
    "DKS": "DK Spaceport - DKS",
    "CC": "Crown City - CC",
    "MBC": "Mario Bros. Circuit - MBC"
}

emojis = {
    "RPB": "<:rPB:1389656673500528680>",
    "PB": "<:rPB:1389656673500528680>",
    "SSS": "<:SSS:1389656659877695598>",
    "RR": "<:RR:1389656648490025113>",
    "RMC": "<:rMC:1389656639350771814>",
    "MC": "<:rMC:1389656639350771814>",
    "AH": "<:AH:1389656629951205527>",
    "BC": "<:BC:1389656620987977760>",
    "RTF": "<:rTF:1389656605817049178>",
    "TF": "<:rTF:1389656605817049178>",
    "RCM": "<:rCM:1389656590990311507>",
    "CM": "<:rCM:1389656590990311507>",
    "RMMM": "<:rMMM:1389656573122711614>",
    "MMM": "<:rMMM:1389656573122711614>",
    "DBB": "<:DBB:1389656564347961374>",
    "BCI": "<:BCi:1389656556009947256>",
    "DD": "<:DD:1389656537831571516>",
    "CCF": "<:CCF:1389656526876180510>",
    "GBR": "<:GBR:1389656508022788218>",
    "RDDJ": "<:rDDJ:1389656479971147890>",
    "DDJ": "<:rDDJ:1389656479971147890>",
    "PS": "<:PS:1389656462602539038>",
    "FO": "<:FO:1389656450527137933>",
    "RKTB": "<:rKTB:1389656437948678235>",
    "RKB": "<:rKTB:1389656437948678235>",
    "KTB": "<:rKTB:1389656437948678235>",
    "KB": "<:rKTB:1389656437948678235>",
    "RWSH": "<:rWSh:1389656406956707960>",
    "WSH": "<:rWSh:1389656406956707960>",
    "RSHS": "<:rSHS:1389656391228199104>",
    "SHS": "<:rSHS:1389656391228199104>",
    "SP": "<:SP:1389656377550700625>",
    "RDKP": "<:rDKP:1389656363764023297>",
    "DKP": "<:rDKP:1389656363764023297>",
    "RAF": "<:rAF:1389656348333178940>",
    "AF": "<:rAF:1389656348333178940>",
    "RWS": "<:rWS:1389656338946199776>",
    "RSGB": "<:rSGB:1389656322424963122>",
    "SGB": "<:rSGB:1389656322424963122>",
    "RDH": "<:rDH:1389656310945026169>",
    "DH": "<:rDH:1389656310945026169>",
    "DKS": "<:DKS:1389656299402170492>",
    "WS": "<:WS:1389656280767139930>",
    "CC": "<:CC:1389656259443163300>",
    "MBC": "<:MBC:1389656225691734108>"
}

DB_PATH = "stats.db"
MAX_TRACK_PERFORMANCES = 50


def init_stats_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            track_tag TEXT NOT NULL,
            diff INTEGER NOT NULL,
            placements TEXT NOT NULL,
            timestamp REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_track_history
        ON performances(guild_id, track_tag, timestamp DESC)
    """)

    conn.commit()
    conn.close()


def normalize_track_tag(track_tag):
    aliases = {
        "RPB": "PB",
        "RMC": "MC",
        "RTF": "TF",
        "RCM": "CM",
        "RMMM": "MMM",
        "RDDJ": "DDJ",

        "RKTB": "KTB",
        "RKB": "KTB",
        "KB": "KTB",

        "RWSH": "WSH",
        "RSHS": "SHS",
        "RDKP": "DKP",
        "RAF": "AF",
        "RWS": "WS",
        "RSGB": "SGB",
        "RDH": "DH",
}

    return aliases.get(track_tag.upper(), track_tag.upper())


def save_track_performance(guild_id, track_tag, diff, placements):
    track_tag = normalize_track_tag(track_tag)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO performances
        (guild_id, track_tag, diff, placements, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (
        guild_id,
        track_tag,
        diff,
        json.dumps(placements),
        time.time()
    ))

    performance_id = cursor.lastrowid

    cursor.execute("""
        DELETE FROM performances
        WHERE guild_id = ?
          AND track_tag = ?
          AND id NOT IN (
              SELECT id
              FROM performances
              WHERE guild_id = ?
                AND track_tag = ?
              ORDER BY timestamp DESC
              LIMIT ?
          )
    """, (
        guild_id,
        track_tag,
        guild_id,
        track_tag,
        MAX_TRACK_PERFORMANCES
    ))

    conn.commit()
    conn.close()

    return performance_id


def get_track_performances(guild_id, track_tag):
    track_tag = normalize_track_tag(track_tag)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, diff, placements, timestamp
        FROM performances
        WHERE guild_id = ?
          AND track_tag = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """, (
        guild_id,
        track_tag,
        MAX_TRACK_PERFORMANCES
    ))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "diff": row[1],
            "placements": json.loads(row[2]),
            "timestamp": row[3]
        }
        for row in rows
    ]

def delete_track_performance(performance_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM performances
        WHERE id = ?
    """, (performance_id,))

    conn.commit()
    conn.close()

def update_track_performance(performance_id, track_tag, diff, placements):
    track_tag = normalize_track_tag(track_tag)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE performances
        SET track_tag = ?,
            diff = ?,
            placements = ?,
            timestamp = ?
        WHERE id = ?
    """, (
        track_tag,
        diff,
        json.dumps(placements),
        time.time(),
        performance_id
    ))

    conn.commit()
    conn.close()

init_stats_db()

async def send_error_to_channel(error_text: str):
    await bot.wait_until_ready()
    channel = bot.get_channel(ERROR_CHANNEL_ID)
    if channel:
        if len(error_text) > 1900:
            chunks = [error_text[i:i+1900] for i in range(0, len(error_text), 1900)]
            for chunk in chunks:
                await channel.send(f"```py\n{chunk}\n```")
        else:
            await channel.send(f"```py\n{error_text}\n```")

@bot.event
async def on_command_error(ctx, error):
    error_text = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    await send_error_to_channel(error_text)

@bot.event
async def on_error(event, *args, **kwargs):
    error_text = traceback.format_exc()
    await send_error_to_channel(f"Ignoring exception in {event}:\n{error_text}")

def push_war_state_to_firebase(guild_id):
    state = get_war_state(guild_id)
    server_key = str(guild_id)

    data = {
        "teams": [state.get('team_tag', 'Team A'), state.get('opponent_tag', 'Team B')],
        "scores": [sum(state.get('team_scores', [])), sum(state.get('opponent_scores', []))],
        "dif": f"+{sum(state.get('team_scores', [])) - sum(state.get('opponent_scores', []))}",
        "win": sum(state.get('team_scores', [])) > sum(state.get('opponent_scores', [])),
        "left": state.get('total_races', 12) - state.get('current_race', 1) + 1
    }

    ref = db.reference(f'/server/{server_key}')
    ref.set(data)
    
def handle_exception(loop, context):
    error = context.get("exception")
    if error:
        error_text = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    else:
        error_text = context.get("message", "Unknown error")
    asyncio.create_task(send_error_to_channel(error_text))

try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

loop.set_exception_handler(handle_exception)

@bot.command()
async def crash(ctx):
    1 / 0 


def get_war_state(guild_id):
    if guild_id not in war_states:
        war_states[guild_id] = {
            'current_race': 1,
            'total_races': 12,
            'team_scores': [],
            'opponent_scores': [],
            'results': [],
            'war_active': False,
            'current_track': None,
            'tracks': [],
            'team_tag': None,
            'opponent_tag': None,
            'channel_id': None,
            'penalties': {'team': 0, 'opponent': 0}
        }
    return war_states[guild_id]

def save_war_state():
    with open("state.json", "w") as f:
        json.dump(war_states, f)

    for gid, state in war_states.items():
        if isinstance(gid, int) or (isinstance(gid, str) and gid.isdigit()):
            push_war_state_to_firebase(gid)
        

def load_war_states():
    global war_states
    if os.path.exists("state.json"):
        try:
            with open("state.json", "r") as f:
                war_states = json.load(f)
        except Exception:
            war_states = {}

load_war_states()

def calculate_points(positions):
    points_table = [15, 12, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    return sum(points_table[pos - 1] for pos in positions if 1 <= pos <= 12)

def parse_positions(s: str):
    result = []

    tokens = re.split(r"[\s,]+", s.strip())

    for token in tokens:
        if '-' in token:
            start_str, end_str = token.split('-')
            
            start_list = []
            i = 0
            while i < len(start_str):
                if start_str[i:i+2] == "12":
                    start_list.extend([1, 2])
                    i += 2
                elif start_str[i:i+2] in ["10", "11"]:
                    start_list.append(int(start_str[i:i+2]))
                    i += 2
                else:
                    start_list.append(int(start_str[i]))
                    i += 1
            
            end_list = []
            i = 0
            while i < len(end_str):
                if end_str[i:i+2] in ["10","11","12"]:
                    end_list.append(int(end_str[i:i+2]))
                    i += 2
                else:
                    end_list.append(int(end_str[i]))
                    i += 1

            if not start_list or not end_list:
                continue

            range_start = start_list[-1] + 1
            range_end = end_list[0] - 1
            
            if range_start <= range_end:
                mid_range = list(range(range_start, range_end + 1))
            else:
                mid_range = []

            result.extend(start_list + mid_range + end_list)
            continue

        i = 0
        while i < len(token):
            if token[i:i+2] == "12":
                result.extend([1, 2])
                i += 2
            elif token[i:i+2] in ["10", "11"]:
                result.append(int(token[i:i+2]))
                i += 2
            else:
                result.append(int(token[i]))
                i += 1

    return sorted(set(result))

def load_track_bg(track_tag=None):
    base_path = "tracks_bg"

    if track_tag:
        candidates = [f"BG{track_tag}.png", f"BG{track_tag}.jpg"]
    else:
        candidates = ["BG.png", "BG.jpg"]

    for filename in candidates:
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            return Image.open(filepath).convert("RGBA")
        
    default_file = os.path.join(base_path, "BG.png")
    if os.path.exists(default_file):
        return Image.open(default_file).convert("RGBA")

    return Image.new("RGBA", (800, 600), (0, 0, 0, 0))
        
def get_embed_color(diff):
    max_diff = 70  
    diff = max(-max_diff, min(diff, max_diff))

    if diff > 0:
        green = 255
        red = int(255 * (max_diff - diff) / max_diff)
    elif diff < 0:
        red = 255
        green = int(255 * (max_diff + diff) / max_diff)
    else:
        red = 255
        green = 255

    blue = 0

    return discord.Color.from_rgb(red, green, blue)

@bot.command()
async def warstart(ctx, our_team_tag: str = None, opponent_team_tag: str = None):
    if not our_team_tag or not opponent_team_tag:
        await ctx.send("Use: !warstart <your_tag> <opponent_tag>")
        return
    state = get_war_state(ctx.guild.id)
    state.update({
        'current_race': 1,
        'team_scores': [],
        'opponent_scores': [],
        'results': [],
        'war_active': True,
        'current_track': None,
        'team_tag': our_team_tag,
        'opponent_tag': opponent_team_tag,
        'channel_id': ctx.channel.id,
        'penalties': {'team': 0, 'opponent': 0},
        'tracks': []
    })
    summary_messages[ctx.guild.id] = None
    db.reference(f'/server/{ctx.guild.id}').delete()
    save_war_state()
    await ctx.send(f"War started: `{our_team_tag}` vs `{opponent_team_tag}` in {ctx.channel.mention}!")

@bot.command()
async def addpenalty(ctx, team_tag: str, amount: int):
    state = get_war_state(ctx.guild.id)
    if team_tag.lower() not in ['team', 'opponent'] or amount <= 0:
        await ctx.send("Use: !addpenalty <team/opponent> <penalty value>")
        return
    state['penalties'][team_tag.lower()] += amount
    save_war_state()
    await ctx.send(f"{amount} points penalty added to {team_tag}.")

@bot.command()
async def removepenalty(ctx, team_tag: str, amount: int):
    state = get_war_state(ctx.guild.id)
    if team_tag.lower() not in ['team', 'opponent'] or amount <= 0:
        await ctx.send("Use: !removepenalty <team/opponent> <penalty value>")
        return
    team = team_tag.lower()
    state['penalties'][team] = max(0, state['penalties'][team] - amount)
    save_war_state()
    await ctx.send(f"Penalty removed. Current penalty: {state['penalties'][team]} points.")

@bot.command()
async def setchannel(ctx, channel: discord.TextChannel = None):
    state = get_war_state(ctx.guild.id)

    if channel is None:
        channel = ctx.channel

    state['channel_id'] = channel.id
    save_war_state()
    await ctx.send(f"Set channel: {channel.mention}.")

@bot.command()
async def obs(ctx):
    guild_id = ctx.guild.id
    url = f"{public_url}/index.html?server={guild_id}"
    await ctx.send(f"Overlay URL: {url}")



@bot.command()
async def endwar(ctx):
    state = get_war_state(ctx.guild.id)
    guild_id = ctx.guild.id

    # Ultima pista giocata
    track_tag = state['results'][-1]['track_tag']
    bg_img = load_track_bg(track_tag)
    
    team_tag = state.get('team_tag', "Team A")
    opp_tag  = state.get('opponent_tag', "Team B")

    team_scores = state['team_scores']
    opp_scores  = state['opponent_scores']

    raw_team_total = sum(team_scores)
    raw_opp_total  = sum(opp_scores)

    team_penalty = state['penalties'].get('team', 0)
    opp_penalty  = state['penalties'].get('opponent', 0)

    total_team = raw_team_total - team_penalty
    total_opp  = raw_opp_total - opp_penalty

    state['war_active'] = False
    save_war_state()
    embed = format_summary_embed(ctx.guild.id)

    team_cum = [sum(team_scores[:i+1]) for i in range(len(team_scores))]
    opp_cum  = [sum(opp_scores[:i+1]) for i in range(len(opp_scores))]
    diff = [t - o for t, o in zip(team_cum, opp_cum)]
    races = list(range(1, len(team_scores)+1))

    fig, ax = plt.subplots(figsize=(6,3))
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor("none")
    fig.patch.set_alpha(0)

    min_diff = int(min(diff))
    max_diff = int(max(diff))
    mid_low  = int((min_diff + 0) / 2) if min_diff < -20 else 0
    mid_high = int((max_diff + 0) / 2) if max_diff > 20 else 0
    yticks = sorted(set([min_diff, mid_low, 0, mid_high, max_diff]))
    ax.set_yticks(yticks)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

    ax.text(0.41, 1.05, team_tag, color="#424242", fontsize="32", fontweight="bold",
            ha='right', transform=ax.transAxes)
    ax.text(0.51, 1.05, opp_tag, color="#424242", fontsize="32", fontweight="bold",
            ha='left', transform=ax.transAxes)
    ax.text(0.46, 1.05, "vs", color="#424242", fontsize="18", fontweight="bold",
            ha='center', transform=ax.transAxes)

    ax.axhline(0, color='black', linewidth=1)
    
    if max_diff < 20 or min_diff > -20:
        yticks = [y for y in yticks if y != 0]
        ax.set_yticks(yticks)

    ax.plot(races, diff, linewidth=2, color="red")
    ax.tick_params(axis='both', which='both', length=0)
    ax.grid(axis='y')

    buf = io.BytesIO()
    plt.savefig(buf, format="PNG", bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)

    graph_img = Image.open(buf).convert("RGBA")
    bg_resized = bg_img.resize(graph_img.size)
    final_img = Image.alpha_composite(bg_resized, graph_img)

    final_buf = io.BytesIO()
    final_img.save(final_buf, format="PNG")
    final_buf.seek(0)

    if summary_messages.get(guild_id):
        try:
            await summary_messages[guild_id].delete()
        except discord.NotFound:
            pass
    summary_messages[guild_id] = None
    
    embed.set_image(url="attachment://war_summary.png")
    await ctx.send(embed=embed, file=discord.File(final_buf, filename="war_summary.png"))

@bot.command()
async def back(ctx):
    state = get_war_state(ctx.guild.id)
    if state['current_race'] <= 1:
        await ctx.send("Can't go back if at first race.")
        return
    state['current_race'] -= 1

    if state['results']:
        last_result = state['results'][-1]
        stats_id = last_result.get('stats_id')

        if stats_id:
            delete_track_performance(stats_id)

    for key in ['team_scores', 'opponent_scores', 'results']:
        if state[key]:
            state[key].pop()
    if state.get('tracks'):
        state['tracks'].pop()
    state['current_track'] = None
    save_war_state()
    await ctx.send(f"Race {state['current_race']} cancelled.")
    
@bot.command()
async def serverlist(ctx):
    guilds = bot.guilds
    names = [f"{g.name} ({g.id})" for g in guilds]
    await ctx.send("\n" + "\n".join(names))
    
@bot.command()
async def editrace(ctx, race_number: int, *args):
    state = get_war_state(ctx.guild.id)
    if not state['results']:
        await ctx.send("No races to edit yet.")
        return

    if not (1 <= race_number <= state['total_races']):
        await ctx.send("Invalid race number.")
        return

    current_result = state['results'][race_number - 1]
    
    track_tag = None
    placements_raw = args

    if args and args[0].strip().upper() in track_names:
        track_tag = args[0].strip().upper()
        placements_raw = args[1:]

    if track_tag:
        track = track_tag
    else:
        track = current_result.get('track_tag')
        if not track:
            await ctx.send("Unknown error.")
            return

    if placements_raw:
        content = " ".join(placements_raw)
        placements = parse_positions(content)
        placements = sorted(set(p for p in placements if 1 <= p <= 12))

        if 1 <= len(placements) < 6:
            all_positions = list(range(12, 0, -1))
            missing = [p for p in all_positions if p not in placements]
            completions = missing[:6 - len(placements)]
            placements += completions
            placements = sorted(placements)

        if len(placements) != 6 or len(set(placements)) != 6:
            await ctx.send("Placements needs to be 6 different numbers between 1 and 12.")
            return
    else:
        placements = current_result.get('placements')
        if not placements:
            await ctx.send("Unknown error.")
            return

    team_set = set(placements)
    opponent_set = set(range(1, 13)) - team_set

    old_result = state['results'][race_number - 1]
    stats_id = old_result.get('stats_id')

    team_points = calculate_points(placements)
    opponent_points = calculate_points(opponent_set)

    if stats_id:
        update_track_performance(
            stats_id,
            track,
            team_points - opponent_points,
            placements
        )
    else:
        stats_id = save_track_performance(
            ctx.guild.id,
            track,
            team_points - opponent_points,
            placements
        )

    state['results'][race_number - 1] = {
        'race': race_number,
        'track_tag': track,
        'track_name': track_names[track],
        'team_points': team_points,
        'opponent_points': opponent_points,
        'placements': placements,
        'stats_id': stats_id
    }

    state['team_scores'][race_number - 1] = team_points
    state['opponent_scores'][race_number - 1] = opponent_points

    if 'tracks' not in state:
        state['tracks'] = []

    if len(state['tracks']) >= race_number:
        state['tracks'][race_number - 1] = track
    else:
        while len(state['tracks']) < race_number - 1:
            state['tracks'].append(None)
        state['tracks'].append(track)

    save_war_state()

    guild_id = ctx.guild.id
    if summary_messages.get(guild_id):
        try:
            await summary_messages[guild_id].delete()
        except discord.NotFound:
            pass

    if not state['war_active']:
        await endwar(ctx)
        return

    embed = format_summary_embed(guild_id)
    summary_messages[guild_id] = await ctx.send(embed=embed)
    await ctx.send(f"Race number {race_number} updated.")

@bot.command()
async def trackstats(ctx, track_tag: str = None):
    if not track_tag:
        await show_track_ranking(ctx)
        return

    track_tag = track_tag.upper()

    if track_tag not in track_names:
        await ctx.send("Unknown track tag.")
        return

    normalized = normalize_track_tag(track_tag)
    performances = get_track_performances(ctx.guild.id, normalized)

    if not performances:
        await ctx.send(f"No stats available for **{track_names[track_tag]}**.")
        return

    diffs = [p["diff"] for p in performances]

    wins = sum(1 for d in diffs if d > 0)
    losses = sum(1 for d in diffs if d < 0)
    draws = sum(1 for d in diffs if d == 0)

    total = len(performances)
    winrate = wins / total * 100
    avg_diff = sum(diffs) / total

    best = max(performances, key=lambda p: p["diff"])
    worst = min(performances, key=lambda p: p["diff"])

    def format_placements(placements):
        return "`" + ", ".join(map(str, placements)) + "`"

    last_5 = performances[:5]

    last_5_str = "`" + "  ".join(
        f"{p['diff']:+}"
        for p in reversed(last_5)
    ) + "`"

    emoji = emojis.get(track_tag, '')

    embed = discord.Embed(
        title=f"{emoji} {track_names[track_tag]} | Last {total}",
        color=EMBED_COLOR
    )

    summary = (
        f"**W/L/T:** {wins} / {losses} / {draws}\n"
        f"**Win rate:** {winrate:.1f}%\n\n"
        f"**Avg diff:** {avg_diff:+.2f}\n"
        f"**Best:** {best['diff']:+} | {format_placements(best['placements'])}\n"
        f"**Worst:** {worst['diff']:+} | {format_placements(worst['placements'])}\n\n"
        f"**Last 5:**\n{last_5_str}"
    )

    embed.description = summary

    await ctx.send(embed=embed)


async def show_track_ranking(ctx):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT track_tag, diff
        FROM performances
        WHERE guild_id = ?
        ORDER BY timestamp DESC
    """, (ctx.guild.id,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await ctx.send("No track statistics available yet.")
        return

    track_data = {}

    for track_tag, diff in rows:
        track_data.setdefault(track_tag, [])

        if len(track_data[track_tag]) < MAX_TRACK_PERFORMANCES:
            track_data[track_tag].append(diff)

    rankings = []

    for track_tag, diffs in track_data.items():
        if not diffs:
            continue

        avg_diff = sum(diffs) / len(diffs)
        rankings.append((track_tag, avg_diff, len(diffs)))

    rankings.sort(key=lambda x: x[1], reverse=True)

    lines = [
        f"**{i}. {emojis.get(tag, '')} {track_names.get(tag, tag)}** Avg: {avg:+.2f} ({count} race{'s' if count != 1 else ''})"
        for i, (tag, avg, count) in enumerate(rankings, start=1)
    ]

    embed = discord.Embed(
        title="Track Rankings",
        description="\n".join(lines),
        color=EMBED_COLOR
    )

    await ctx.send(embed=embed)

def suggest_tracks(placements):
    top = sum(1 for p in placements if p <= 3)
    bottom = sum(1 for p in placements if p >= 8)

    if top >= 2 and bottom <= 2:  # tanti davanti
        return ["RR <:RR:1389656648490025113>", "BC <:BC:1389656620987977760>", "BCi <:BCi:1389656556009947256>", "rSHS <:rSHS:1389656391228199104>", "rAF <:rAF:1389656348333178940>", "rWS <:rWS:1389656338946199776>", "rSGB <:rSGB:1389656322424963122>", "rWSh <:rWSh:1389656406956707960>", "SP <:SP:1389656377550700625>"]
    elif bottom >= 3 and top <= 2:  # tanti dietro
        return ["rDH <:rDH:1389656310945026169>", "DKS <:DKS:1389656299402170492>", "rPB <:rPB:1389656673500528680>", "rTF <:rTF:1389656605817049178>", "WS <:WS:1389656280767139930>", "rMC <:rMC:1389656639350771814>", "SSS <:SSS:1389656659877695598>", "rCM <:rCM:1389656590990311507>", "rMMM <:rMMM:1389656573122711614>", "rDDJ <:rDDJ:1389656479971147890>", "rKTB <:rKTB:1389656437948678235>", "rDKP <:rDKP:1389656363764023297>", "MBC <:MBC:1389656225691734108>", "DBB <:DBB:1389656564347961374>", "CC <:CC:1389656259443163300>"]
    else:  # situazione mista
        return ["AH <:AH:1389656629951205527>", "DBB <:DBB:1389656564347961374>", "GBR <:GBR:1389656508022788218>", "PS <:PS:1389656462602539038>", "FO <:FO:1389656450527137933>", "SP <:SP:1389656377550700625>", "rSGB <:rSGB:1389656322424963122>", "CC <:CC:1389656259443163300>", "MBC <:MBC:1389656225691734108>"]

def format_summary_embed(guild_id):
    state = get_war_state(guild_id)

    raw_team_total = sum(state['team_scores'])
    raw_opp_total = sum(state['opponent_scores'])

    team_penalty = state['penalties'].get('team', 0)
    opp_penalty = state['penalties'].get('opponent', 0)

    total_team = raw_team_total - team_penalty
    total_opp = raw_opp_total - opp_penalty
    diff_total = total_team - total_opp

    color = get_embed_color(diff_total)

    team_tag = state.get('team_tag', 'nostro')
    opp_tag = state.get('opponent_tag', 'avversario')

    embed = discord.Embed(
        title=f"{team_tag} vs {opp_tag}",
        description=f"{total_team} - {total_opp} ({diff_total:+})",
        color=color
    )

    wins = losses = draws = 0

    for result in state['results']:
        race = result['race']
        emoji = emojis.get(result['track_tag'], '❓')
        name = f"{race} - {emoji} {result['track_name']}"
        
        placements_str = "`" + ", ".join(map(str, result['placements'])) + "`"
        diff_race = result['team_points'] - result['opponent_points']
        value = f"{result['team_points']} : {result['opponent_points']} ({diff_race:+}) | {placements_str}"
        embed.add_field(name=name, value=value, inline=False)

        if diff_race > 0:
            wins += 1
        elif diff_race < 0:
            losses += 1
        else:
            draws += 1

    if team_penalty > 0 or opp_penalty > 0:
        pen_msg = ""
        if team_penalty > 0:
            pen_msg += f"**{team_tag}**: -{team_penalty} punti\n"
        if opp_penalty > 0:
            pen_msg += f"**{opp_tag}**: -{opp_penalty} punti"
        embed.add_field(name="Penalties", value=pen_msg, inline=False)

    summary = f"W: **{wins}**  L: **{losses}**"
    if draws > 0:
        summary += f"  T: **{draws}**"
    embed.add_field(name="Stats", value=summary, inline=False)

    if state['results'] and state['war_active']: 
        last_race = state['results'][-1]
        rec = suggest_tracks(last_race['placements'])
        random.shuffle(rec)
        embed.add_field(
            name="Suggested tracks",
            value=" | ".join(rec),
            inline=False
        )
        embed.set_footer(
            text="Kiwi by marionee - 1.3.1",
        )
    return embed



@bot.event
async def on_message(message):
    
    if message.author.id == 1388648962193494287 or not message.guild:
        return
    
    guild_id = message.guild.id
    state = get_war_state(guild_id)
    
    if message.content.lower() == "pardopippa":
        await message.channel.send("pardopippa")
        
    if state.get('channel_id') and message.channel.id != state['channel_id']:
        return

    content = message.content.strip()
    if content.startswith('!'):
        await bot.process_commands(message)
        return

    tag = message.content.strip().upper()
    if tag in track_names and state['war_active']:
        state['current_track'] = tag

        embed = discord.Embed(
            title=f"{track_names[tag]}",
            color=EMBED_COLOR
        )

        embed.set_author(name="Next track:")

        embed.set_image(
            url=f"https://raw.githubusercontent.com/marionwq/kiwiMKWDWARBOT/main/tracks_thumbnail/{tag.lower()}thumbnail.jpg?raw=true"
         )

        embed.set_footer(text="Map: © Super Mario Wiki")

        await message.channel.send(embed=embed)

        return

    if state['war_active']:
        placements = parse_positions(content)
        if 1 <= len(placements) < 6:
            all_pos = list(range(12, 0, -1))
            missing = [p for p in all_pos if p not in placements]
            placements += missing[:6 - len(placements)]
        placements = sorted(set(placements))

        if len(placements) == 6:            
            track_tag = state['current_track'] or 'N/A'
            track_name = track_names.get(track_tag, 'Unknown')
            team_set = set(placements)
            opponent_set = set(range(1, 13)) - team_set
            team_pts = calculate_points(placements)
            opp_pts = calculate_points(opponent_set)
            race = state['current_race']

            stats_id = save_track_performance(
                guild_id,
                track_tag,
                team_pts - opp_pts,
                placements
            )

            state['team_scores'].append(team_pts)
            state['opponent_scores'].append(opp_pts)
            state['results'].append({
                'race': race,
                'track_tag': track_tag,
                'track_name': track_name,
                'team_points': team_pts,
                'opponent_points': opp_pts,
                'placements': placements,
                'stats_id': stats_id
            })

            
            
            state['tracks'].append(track_tag)

            

            if summary_messages.get(guild_id):
                try:
                    await summary_messages[guild_id].delete()
                except:
                    pass
            
            if race < state['total_races']:
                state['current_race'] += 1
                state['current_track'] = None
                save_war_state()
            else:
                save_war_state()
                await endwar(message.channel)
                return

            embed = format_summary_embed(guild_id)
            summary_messages[guild_id] = await message.channel.send(embed=embed)
            return
            

    await bot.process_commands(message)

def run_flask():
    app.run(host="0.0.0.0", port=13047)  

threading.Thread(target=run_flask, daemon=True).start()

if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv("TOKEN"))
