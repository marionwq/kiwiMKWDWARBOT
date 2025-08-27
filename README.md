# 🥝 Kiwi – Mario Kart World War Bot

Kiwi is a **Discord bot** designed to manage **Mario Kart World wars**.  
It tracks races, calculates scores automatically, applies penalties, and suggests tracks based on the team’s performance.

---

## ✨ Features

- Start and manage wars with customizable team tags  
- Record races by simply typing track tags and placements  
- Automatic score calculation (team vs opponent)  
- Edit past races (`!editrace`) or go back to the previous one (`!back`)  
- Apply or remove penalties (`!addpenalty`, `!removepenalty`)  
- End a war and generate a **final summary embed** with stats and graphs  
- Track suggestions based on last race results  
- Multi-server support (each server keeps its own war state)  
- Persistent war data saved in `state.json`  

---

## 📜 Commands

| Command | Description |
|---------|-------------|
| `!warstart <your_tag> <opponent_tag>` | Start a new war |
| `!setchannel` | Set the current channel as war log channel |
| `!addpenalty <team/opponent> <points>` | Add penalty points |
| `!removepenalty <team/opponent> <points>` | Remove penalty points |
| `!back` | Cancel the last recorded race |
| `!editrace <race_number> [track_tag] [placements]` | Edit an existing race |
| `!endwar` | Finish the war and generate the final summary |

Additionally:  
- You can type a **track tag** (e.g. `DBB`) to set the next race track.  
- You can input **placements** (e.g. `1 3 6 7 9 12`) directly, and Kiwi will record the race.  

---

## 🚀 Installation

1. Click [here](https://discord.com/oauth2/authorize?client_id=1388648962193494287&permissions=125952&scope=bot) to invite the bot to your own server. The permissions needed are listed in the page right before inviting the bot.
