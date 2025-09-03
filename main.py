import discord
from discord.ext import commands
from pyngrok import ngrok
from flask import Flask, send_file, request, make_response
import os
from threading import Thread
from dotenv import load_dotenv
from discord.ext import commands
import re
import json
import random
import io
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
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

war_states = {}
summary_messages = {}

track_names = {
    "RPB": "Peach Beach",
    "SSS": "Salty Salty Speedway",
    "RR": "Rainbow Road",
    "RMC": "Mario Circuit (SNES)",
    "AH": "Acorn Heights",
    "BC": "Bowser's Castle",
    "RTF": "Toad's Factory",
    "RCM": "Choco Mountain",
    "RMMM": "Moo Moo Meadows",
    "DBB": "Dry Bones Burnout",
    "BCI": "Boo Cinema",
    "DD": "Dandelion Depths",
    "CCF": "Cheep Cheep Falls",
    "GBR": "Great ? Block Ruins",
    "RDDJ": "Dino Dino Jungle",
    "PS": "Peach Stadium",
    "FO": "Faraway Oasis",
    "RKTB": "Koopa Troopa Beach",
    "RWSH": "Wario Shipyard",
    "RSHS": "Sky-High Sundae",
    "SP": "Starview Peak",
    "RDKP": "DK Pass",
    "RAF": "Airship Fortress",
    "RWS": "Wario Stadium",
    "RSGB": "Shy Guy Bazaar",
    "WS": "Whistletop Summit",
    "RDH": "Desert Hills (DS)",
    "DKS": "DK Spaceport",
    "CC": "Crown City",
    "MBC": "Mario Bros. Circuit"
}

emojis = {
    "RPB": "<:rPB:1389656673500528680>",
    "SSS": "<:SSS:1389656659877695598>",
    "RR": "<:RR:1389656648490025113>",
    "RMC": "<:rMC:1389656639350771814>",
    "AH": "<:AH:1389656629951205527>",
    "BC": "<:BC:1389656620987977760>",
    "RTF": "<:rTF:1389656605817049178>",
    "RCM": "<:rCM:1389656590990311507>",
    "RMMM": "<:rMMM:1389656573122711614>",
    "DBB": "<:DBB:1389656564347961374>",
    "BCI": "<:BCi:1389656556009947256>",
    "DD": "<:DD:1389656537831571516>",
    "CCF": "<:CCF:1389656526876180510>",
    "GBR": "<:GBR:1389656508022788218>",
    "RDDJ": "<:rDDJ:1389656479971147890>",
    "PS": "<:PS:1389656462602539038>",
    "FO": "<:FO:1389656450527137933>",
    "RKTB": "<:rKTB:1389656437948678235>",
    "RWSH": "<:rWSh:1389656406956707960>",
    "RSHS": "<:rSHS:1389656391228199104>",
    "SP": "<:SP:1389656377550700625>",
    "RDKP": "<:rDKP:1389656363764023297>",
    "RAF": "<:rAF:1389656348333178940>",
    "RWS": "<:rWS:1389656338946199776>",
    "RSGB": "<:rSGB:1389656322424963122>",
    "RDH": "<:rDH:1389656310945026169>",
    "DKS": "<:DKS:1389656299402170492>",
    "WS": "<:WS:1389656280767139930>",
    "CC": "<:CC:1389656259443163300>",
    "MBC": "<:MBC:1389656225691734108>"
}

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

def handle_exception(loop, context):
    error = context.get("exception")
    if error:
        error_text = "".join(traceback.format_exception(type(error), error, error.__traceback__))
    else:
        error_text = context.get("message", "Unknown error")
    asyncio.create_task(send_error_to_channel(error_text))

loop = asyncio.get_event_loop()
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
            if int(start_str) > 12:
                for i, ch in enumerate(start_str):
                    if start_str[i:i+2] in ["10","11","12"]:
                        start_list.append(int(start_str[i:i+2]))
                        break
                    else:
                        start_list.append(int(ch))
            elif start_str == "12":
                start_list.extend([1,2])
            else:
                start_list.append(int(start_str))
            
            end_list = []
            i = 0
            while i < len(end_str):
                if end_str[i:i+2] in ["10","11","12"]:
                    end_list.append(int(end_str[i:i+2]))
                    i += 2
                else:
                    end_list.append(int(end_str[i]))
                    i += 1

            range_start = start_list[-1]+1
            range_end = end_list[0]-1
            if range_start <= range_end:
                mid_range = list(range(range_start, range_end+1))
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

def load_track_bg(track_tag):
    base_path = "tracks_bg"
    candidates = [f"BG{track_tag}.png", f"BG{track_tag}.jpg"]

    for filename in candidates:
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            return Image.open(filepath).convert("RGBA")
        
def get_embed_color(diff):
    max_diff = 70  
    diff = max(-max_diff, min(diff, max_diff))

    if diff > 0:
        # più positivo = più verde, meno giallo
        green = 255
        red = int(255 * (max_diff - diff) / max_diff)
    elif diff < 0:
        # più negativo = più rosso, meno giallo
        red = 255
        green = int(255 * (max_diff + diff) / max_diff)
    else:
        # zero = giallo pieno
        red = 255
        green = 255

    blue = 0

    return discord.Color.from_rgb(red, green, blue)

def generate_overlay_image(state, guild_id):
    width, height = 800, 250
    img = Image.new("RGBA", (width, height), (0,0,0,0))
    draw = ImageDraw.Draw(img)

    rect_x0, rect_y0 = 10, 10
    rect_x1, rect_y1 = width - 10, height - 10
    radius = 25

    shadow = Image.new("RGBA", img.size, (0,0,0,0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_color = (0, 0, 0, 120)
    shadow_offset = 3
    shadow_draw.rounded_rectangle(
        [rect_x0 + shadow_offset, rect_y0 + shadow_offset, rect_x1 + shadow_offset, rect_y1 + shadow_offset],
        radius=radius, fill=shadow_color
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, shadow)
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([rect_x0, rect_y0, rect_x1, rect_y1], radius=radius, fill=(30,30,30,200))

    team_total = sum(state['team_scores'])
    opp_total  = sum(state['opponent_scores'])
    team_tag = state.get('team_tag', "Team A")
    opp_tag  = state.get('opponent_tag', "Team B")
    race_number = state.get('current_race', 1)
    total_races = state.get('total_races', 12)

    font = ImageFont.truetype("Splatoon2.otf", 64)
    text = f"{team_tag} vs {opp_tag}"
    bbox = draw.textbbox((0,0), text, font=font) 
    text_width = bbox[2] - bbox[0]
    draw.text(((800 - text_width)//2, 30), text, fill="white", font=font)

    font = ImageFont.truetype("Splatoon2.otf", 34)
    text = f"(± {abs(team_total - opp_total)})"
    bbox = draw.textbbox((0,0), text, font=font) 
    text_width = bbox[2] - bbox[0]
    draw.text(((800 - text_width)//2, 4), text, fill="white", font=font)

    font = ImageFont.truetype("Splatoon2.otf", 52)
    draw.text((30, 100), f"{team_total}", fill="#BDBDBD", font=font)
    draw.text((685, 100), f"{opp_total}", fill="#BDBDBD", font=font)

    text = f"{race_number}/{total_races}"
    bbox = draw.textbbox((0,0), text, font=font) 
    text_width = bbox[2] - bbox[0]
    draw.text(((800 - text_width)//2, 120), text, fill="yellow", font=font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    img.close()
    shadow.close()

    overlay_cache[guild_id] = buf

    return buf


from flask import Flask, make_response
import base64

app = Flask(__name__)

@app.route("/overlay/<int:guild_id>")
def overlay(guild_id):
    state = war_states.get(guild_id)
    if not state:
        return "No war state for this guild.", 404

    try:
        if guild_id in overlay_cache:
            img_buf = overlay_cache[guild_id]
        else:
            img_buf = generate_overlay_image(state, guild_id) 

        img_b64 = base64.b64encode(img_buf.getvalue()).decode()

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Overlay</title>
            <style>
                body {{ margin:0; padding:0; background:transparent; }}
                img {{ width:100%; height:auto; display:block; }}
            </style>
        </head>
        <body>
            <img src="data:image/png;base64,{img_b64}">
        </body>
        </html>
        """

        response = make_response(html)
        response.headers["ngrok-skip-browser-warning"] = "true"
        return response

    except Exception as e:
        return f"Error generating overlay: {e}", 500

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
        'penalties': {'team': 0, 'opponent': 0}
    })
    summary_messages[ctx.guild.id] = None
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
async def setchannel(ctx):
    state = get_war_state(ctx.guild.id)
    state['channel_id'] = ctx.channel.id
    save_war_state()
    await ctx.send(f"Set channel: {ctx.channel.mention}.")

@bot.command()
async def obs(ctx):
    guild_id = ctx.guild.id
    state = war_states.get(guild_id)
    if not state:
        await ctx.send("No war active for this server.")
        return
    await ctx.send(f"Overlay URL: {public_url}/overlay/{guild_id}")

@bot.command()
async def endwar(ctx):
    state = get_war_state(ctx.guild.id)
    guild_id = ctx.guild.id

    # Ultima pista giocata
    track_tag = state['results'][-1]['track_tag']
    bg_img = load_track_bg(track_tag)
    bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=3))
    
    # Aumento luminosità dello sfondo
    enhancer = ImageEnhance.Brightness(bg_img)
    bg_img = enhancer.enhance(1.08)
    
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

    # === Calcola cumulativi e differenza ===
    team_cum = [sum(team_scores[:i+1]) for i in range(len(team_scores))]
    opp_cum  = [sum(opp_scores[:i+1]) for i in range(len(opp_scores))]
    diff = [t - o for t, o in zip(team_cum, opp_cum)]
    races = list(range(1, len(team_scores)+1))

    # === Crea grafico trasparente ===
    fig, ax = plt.subplots(figsize=(6,3))
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor("none")
    fig.patch.set_alpha(0)

    # Y-ticks
    min_diff = int(min(diff))
    max_diff = int(max(diff))
    mid_low  = int((min_diff + 0) / 2) if min_diff < -20 else 0
    mid_high = int((max_diff + 0) / 2) if max_diff > 20 else 0
    yticks = sorted(set([min_diff, mid_low, 0, mid_high, max_diff]))
    ax.set_yticks(yticks)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

    # Titolo (Team vs Team)
    ax.text(0.41, 1.05, team_tag, color="#424242", fontsize="32", fontweight="bold",
            ha='right', transform=ax.transAxes)
    ax.text(0.51, 1.05, opp_tag, color="#424242", fontsize="32", fontweight="bold",
            ha='left', transform=ax.transAxes)
    ax.text(0.46, 1.05, "vs", color="#424242", fontsize="18", fontweight="bold",
            ha='center', transform=ax.transAxes)

    # Linea zero
    ax.axhline(0, color='black', linewidth=1)
    
    if max_diff < 20 or min_diff > -20:
        yticks = [y for y in yticks if y != 0]
        ax.set_yticks(yticks)

    # Linea differenza
    ax.plot(races, diff, linewidth=2, color="red")
    ax.tick_params(axis='both', which='both', length=0)
    ax.grid(axis='y')

    # Salva grafico trasparente in buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="PNG", bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)

    # Combina grafico trasparente con sfondo
    graph_img = Image.open(buf).convert("RGBA")
    bg_resized = bg_img.resize(graph_img.size)
    final_img = Image.alpha_composite(bg_resized, graph_img)

    # Salva immagine finale in buffer
    final_buf = io.BytesIO()
    final_img.save(final_buf, format="PNG")
    final_buf.seek(0)

    # Cancella vecchio riepilogo
    if summary_messages.get(guild_id):
        try:
            await summary_messages[guild_id].delete()
        except discord.NotFound:
            pass
    summary_messages[guild_id] = None
    
    # Manda immagine finale con embed
    embed.set_image(url="attachment://war_summary.png")
    await ctx.send(embed=embed, file=discord.File(final_buf, filename="war_summary.png"))

@bot.command()
async def back(ctx):
    state = get_war_state(ctx.guild.id)
    if state['current_race'] <= 1:
        await ctx.send("Can't go back if at first race.")
        return
    state['current_race'] -= 1
    for key in ['team_scores', 'opponent_scores', 'results']:
        if state[key]:
            state[key].pop()
    state['current_track'] = None
    save_war_state()
    await ctx.send(f"Race {state['current_race'] + 1} cancelled.")
    
@bot.command()
async def serverlist(ctx):
    guilds = bot.guilds
    names = [f"{g.name} ({g.id})" for g in guilds]
    await ctx.send("\n" + "\n".join(names))
    
@bot.command()
async def editrace(ctx, race_number: int, track_tag: str = None, *placements_raw):
    state = get_war_state(ctx.guild.id)
    if not state['war_active']:
        await ctx.send("War hasn't started yet.")
        return

    if not (1 <= race_number <= state['total_races']):
        await ctx.send("Invalid race number.")
        return

    # Recupera dati attuali
    current_result = state['results'][race_number - 1]

    # --- Gestione pista ---
    if track_tag:  # se è stata passata una pista
        tag = track_tag.strip().upper()
        if tag not in track_names:
            await ctx.send("Unknown track tag.")
            return
        track = tag
    else:  # se non è stata passata, mantieni quella vecchia
        track = current_result.get('track_tag')
        if not track:
            await ctx.send("Unknown error.")
            return

    # --- Gestione piazzamenti ---
    if placements_raw:  # se ci sono piazzamenti nuovi
        content = " ".join(placements_raw)
        digits_only = re.sub(r"[^\d]", "", content)
        placements = parse_positions(digits_only)
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
    else:  # nessun piazzamento nuovo → mantieni quelli vecchi
        placements = current_result.get('placements')
        if not placements:
            await ctx.send("Unknown error.")
            return

    # --- Calcolo punti ---
    team_set = set(placements)
    opponent_set = set(range(1, 13)) - team_set

    team_points = calculate_points(placements)
    opponent_points = calculate_points(opponent_set)

    # --- Aggiorna stato ---
    state['results'][race_number - 1] = {
        'race': race_number,
        'track_tag': track,
        'track_name': track_names[track],
        'team_points': team_points,
        'opponent_points': opponent_points,
        'placements': placements
    }

    state['team_scores'][race_number - 1] = team_points
    state['opponent_scores'][race_number - 1] = opponent_points

    # --- Mantieni sincronizzata la lista tracks ---
    if 'tracks' not in state:
        state['tracks'] = []

    if len(state['tracks']) >= race_number:
        state['tracks'][race_number - 1] = track
    else:
        # Se per qualche motivo manca, riempi fino alla gara attuale
        while len(state['tracks']) < race_number - 1:
            state['tracks'].append(None)
        state['tracks'].append(track)

    save_war_state()

    # --- Aggiorna embed ---
    guild_id = ctx.guild.id
    if summary_messages.get(guild_id):
        try:
            await summary_messages[guild_id].delete()
        except discord.NotFound:
            pass
        embed = format_summary_embed(guild_id)
        summary_messages[guild_id] = await ctx.send(embed=embed)

    await ctx.send(f"Race number {race_number} updated.")

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

    # Conteggio gare vinte, perse, pareggiate
    wins = losses = draws = 0

    for result in state['results']:
        race = result['race']
        emoji = emojis.get(result['track_tag'], '❓')
        name = f"{race} - {emoji} {result['track_name']}"
        
        placements_str = "`" + ", ".join(map(str, result['placements'])) + "`"
        diff_race = result['team_points'] - result['opponent_points']
        value = f"{result['team_points']} : {result['opponent_points']} ({diff_race:+}) | {placements_str}"
        embed.add_field(name=name, value=value, inline=False)

        # Conteggio win/lose/draw
        if diff_race > 0:
            wins += 1
        elif diff_race < 0:
            losses += 1
        else:
            draws += 1

    # Penalità se presenti
    if team_penalty > 0 or opp_penalty > 0:
        pen_msg = ""
        if team_penalty > 0:
            pen_msg += f"**{team_tag}**: -{team_penalty} punti\n"
        if opp_penalty > 0:
            pen_msg += f"**{opp_tag}**: -{opp_penalty} punti"
        embed.add_field(name="Penalties", value=pen_msg, inline=False)

    # Sezione riassuntiva win/loss
    summary = f"W: **{wins}**  L: **{losses}**"
    if draws > 0:
        summary += f"  T: **{draws}**"
    embed.add_field(name="Stats", value=summary, inline=False)

    if state['results'] and state['war_active']:  # se almeno una gara è stata giocata
        last_race = state['results'][-1]
        rec = suggest_tracks(last_race['placements'])
        random.shuffle(rec)
        embed.add_field(
            name="Suggested tracks",
            value=" | ".join(rec),
            inline=False
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
        await message.channel.send(f"Next track: {emojis.get(tag, '')} {track_names[tag]}")
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

            state['team_scores'].append(team_pts)
            state['opponent_scores'].append(opp_pts)
            state['results'].append({
                'race': race,
                'track_tag': track_tag,
                'track_name': track_name,
                'team_points': team_pts,
                'opponent_points': opp_pts,
                'placements': placements
            })
            state['tracks'].append(track_tag)
            save_war_state()

            if summary_messages.get(guild_id):
                try:
                    await summary_messages[guild_id].delete()
                except:
                    pass

            embed = format_summary_embed(guild_id)
            summary_messages[guild_id] = await message.channel.send(embed=embed)

            if race < state['total_races']:
                state['current_race'] += 1
                state['current_track'] = None
                return
            else:
                await endwar(message.channel)
                return

    await bot.process_commands(message)

def run_flask():
    app.run(host="0.0.0.0", port=13047)  # porta di WispByte

threading.Thread(target=run_flask, daemon=True).start()


ngrok.set_auth_token("324Zf8lyqLgA4Q2fRJVvG56HJJ0_4bDfKxk1VogEJi73Pd9Wp")
tunnel = ngrok.connect(13047, bind_tls=True)
public_url = tunnel.public_url
print(f"Overlay URL: {public_url}/overlay/<guild_id>")

@app.after_request
def skip_ngrok_warning(response):
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

if __name__ == "__main__":
    load_dotenv()
    bot.run(os.getenv("TOKEN"))