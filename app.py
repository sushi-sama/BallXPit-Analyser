"""
BALL x PIT Build Advisor — Python/Flask Web Application
Converted from ballxpit-advisor.jsx
"""

import os
import json
from flask import Flask, render_template, request, jsonify
import requests as http_requests

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Ball Data
# ---------------------------------------------------------------------------

BASE_BALLS = [
    {"name": "Bleed", "desc": "Inflicts 2 stacks of bleed. Bleeding enemies receive 1 damage per stack when hit (max 8 stacks)."},
    {"name": "Brood Mother", "desc": "25% chance of birthing a baby ball each time it hits an enemy."},
    {"name": "Burn", "desc": "Adds 1 stack of burn on hit for 3 seconds (max 3 stacks). 4-8 damage per stack per second."},
    {"name": "Cell", "desc": "Splits into a clone on hit 2 times."},
    {"name": "Charm", "desc": "4% chance to charm enemy for 5 seconds. Charmed units attack enemies."},
    {"name": "Dark", "desc": "Deals 3x damage but destroys itself after hitting an enemy. 3 second cooldown."},
    {"name": "Earthquake", "desc": "Deals 5-13 damage to nearby units in a 3x3 tile square."},
    {"name": "Egg Sac", "desc": "Explodes into 2-4 baby balls on hitting an enemy. 3 second cooldown."},
    {"name": "Freeze", "desc": "4% chance to freeze enemies for 5 seconds. Frozen enemies take 25% more damage."},
    {"name": "Ghost", "desc": "Passes through enemies."},
    {"name": "Iron", "desc": "Deals double damage but moves 40% slower."},
    {"name": "Laser (Horizontal)", "desc": "Deals 9-18 damage to all enemies in the same row."},
    {"name": "Laser (Vertical)", "desc": "Deals 9-18 damage to all enemies in the same column."},
    {"name": "Light", "desc": "Blinds enemies on hit for 3 seconds. Blinded units have 50% chance of missing attacks."},
    {"name": "Lightning", "desc": "Deals 1-20 damage to up to 3 nearby enemies."},
    {"name": "Poison", "desc": "Applies 1 stack of poison on hit (max 5 stacks). 1-4 damage per stack per second."},
    {"name": "Vampire", "desc": "4.5% chance of healing 1 health per hit."},
    {"name": "Wind", "desc": "Passes through enemies, slows by 30% for 5 seconds. Deals 25% less damage."},
    {"name": "Stone", "desc": "Initially deals 300% damage. Damage erodes by 40% each hit (min 50%). [Post-Launch]"},
    {"name": "Time", "desc": "Explodes into a time snare on hit. Stays 20 seconds, freezing enemies inside. [Post-Launch]"},
]

EVOLVED_BALLS = [
    {"name": "Assassin", "combo": "Iron + Ghost OR Iron + Dark", "desc": "Backstabs deal 30% bonus damage, passes through front of enemies."},
    {"name": "Berserk", "combo": "Charm + Bleed OR Charm + Burn", "desc": "30% chance to cause berserk for 6 seconds. Berserk enemies damage adjacent foes."},
    {"name": "Black Hole", "combo": "Dark + Sun", "desc": "Instantly kills first non-boss enemy hit. 7 second cooldown."},
    {"name": "Blizzard", "combo": "Freeze + Wind OR Freeze + Lightning", "desc": "Freezes all enemies in 2 tile radius for 0.8s, dealing 1-50 damage."},
    {"name": "Bomb", "combo": "Burn + Iron", "desc": "Explodes on hit, 150-300 damage to nearby enemies. 3 second cooldown."},
    {"name": "Flash", "combo": "Lightning + Light", "desc": "Damages all enemies on screen for 1-3 and blinds for 2 seconds."},
    {"name": "Flicker", "combo": "Light + Dark", "desc": "Deals 1-7 damage to every enemy on screen every 1.4 seconds."},
    {"name": "Freeze Ray", "combo": "Freeze + Laser (H or V)", "desc": "Emits freeze ray on hit, 20-50 damage to all in path, 10% freeze chance."},
    {"name": "Frozen Flame", "combo": "Burn + Freeze", "desc": "Applies frostburn stacks (max 4). 8-12 damage/stack/sec, enemies take 25% more damage."},
    {"name": "Glacier", "combo": "Freeze + Earthquake", "desc": "Releases glacial spikes, freezing and dealing 15-30 damage."},
    {"name": "Hemorrhage", "combo": "Bleed + Iron", "desc": "Applies 3 bleed stacks. At 12+ stacks, consumes all to deal 20% of current health."},
    {"name": "Holy Laser", "combo": "Laser (H) + Laser (V)", "desc": "Deals 24-36 damage to all enemies in same row AND column."},
    {"name": "Incubus", "combo": "Charm + Dark", "desc": "4% charm chance for 9 seconds. Charmed enemies curse nearby foes (100-200 damage on 5 hits)."},
    {"name": "Inferno", "combo": "Burn + Wind", "desc": "Applies 1 burn stack/second to all enemies in 2 tile radius."},
    {"name": "Laser Beam", "combo": "Light + Laser (H or V)", "desc": "Emits laser on hit, 30-42 damage, blinds for 8 seconds."},
    {"name": "Leech", "combo": "Brood Mother + Bleed", "desc": "Attaches leeches that add 2 bleed stacks/second (max 24 stacks)."},
    {"name": "Lightning Rod", "combo": "Lightning + Iron", "desc": "Plants rod; struck by lightning every 3 seconds, 1-30 damage to up to 8 nearby enemies."},
    {"name": "Lovestruck", "combo": "Charm + Light OR Charm + Lightning", "desc": "Lovestruck enemies have 50% chance to heal you for 5 when they attack."},
    {"name": "Maggot", "combo": "Brood Mother + Cell", "desc": "Infests enemies; when they die, explode into 1-2 baby balls."},
    {"name": "Magma", "combo": "Burn + Earthquake", "desc": "Emits lava blobs. Enemies hit take 15-30 damage and gain burn stacks."},
    {"name": "Mosquito King", "combo": "Vampire + Brood Mother", "desc": "Spawns mosquito per hit, dealing 80-120 damage each. Kill = steal 1 health."},
    {"name": "Mosquito Swarm", "combo": "Vampire + Egg Sac", "desc": "Explodes into 3-6 mosquitos, each dealing 80-120 damage. Kill = steal 1 health."},
    {"name": "Noxious", "combo": "Poison + Wind OR Dark + Wind", "desc": "Passes through enemies, applies 3 poison stacks in 2 tile radius."},
    {"name": "Nuclear Bomb", "combo": "Bomb + Poison", "desc": "300-500 damage explosion + 1 radiation stack to all (max 5). Each stack = 10% more damage taken."},
    {"name": "Overgrowth", "combo": "Earthquake + Cell", "desc": "At 3 overgrowth stacks, deals 150-200 damage in 3x3 area."},
    {"name": "Phantom", "combo": "Dark + Ghost", "desc": "Curses enemies on hit. Cursed = 100-200 damage after 5 hits."},
    {"name": "Radiation Beam", "combo": "Laser (H or V) + Poison OR Cell", "desc": "24-48 damage beam + radiation stack per hit. Each stack = 10% more damage taken."},
    {"name": "Sacrifice", "combo": "Bleed + Dark", "desc": "Inflicts 4 bleed stacks (max 15) and curses hit enemies."},
    {"name": "Sandstorm", "combo": "Earthquake + Wind", "desc": "Passes through enemies, dealing 10-20 damage/second and blinding nearby."},
    {"name": "Satan", "combo": "Incubus + Succubus", "desc": "Adds 1 burn/second to ALL active enemies (max 5 stacks) AND makes them go berserk."},
    {"name": "Shotgun", "combo": "Iron + Egg Sac", "desc": "Shoots 3-7 iron baby balls after hitting a wall at 200% speed."},
    {"name": "Soul Sucker", "combo": "Vampire + Ghost", "desc": "30% chance to steal 1 health and reduce enemy attack by 20%."},
    {"name": "Spider Queen", "combo": "Brood Mother + Egg Sac", "desc": "25% chance to birth an Egg Sac per hit."},
    {"name": "Storm", "combo": "Lightning + Wind", "desc": "Emits lightning to strike nearby enemies every second, 1-40 damage."},
    {"name": "Succubus", "combo": "Charm + Vampire", "desc": "4% charm chance for 9 seconds. Heals 1 when hitting charmed enemy."},
    {"name": "Sun", "combo": "Burn + Light", "desc": "Blinds all enemies in view + 1 burn/second (max 5 stacks). 6-12 damage/stack/sec."},
    {"name": "Swamp", "combo": "Poison + Earthquake", "desc": "Leaves tar blobs: 15-30 damage, 50% slow, poison stacks (max 8)."},
    {"name": "Vampire Lord", "combo": "Vampire + Bleed OR Vampire + Dark", "desc": "3 bleed stacks per hit. Heals 1 and consumes all stacks at 10+."},
    {"name": "Virus", "combo": "Poison + Ghost OR Poison + Cell", "desc": "Disease stacks (max 8), 3-6 damage/stack/sec, 15% spread chance."},
    {"name": "Voluptuous Egg Sac", "combo": "Egg Sac + Cell", "desc": "Explodes into 2-3 egg sacs on hit. 3 second cooldown."},
    {"name": "Wraith", "combo": "Freeze + Ghost", "desc": "Freezes any enemy it passes through for 0.8 seconds."},
    {"name": "Nosferatu", "combo": "Vampire Lord + Spider Queen + Mosquito King", "desc": "Spawns vampire bat per bounce, dealing 132-176 damage. Bat turns into Vampire Lord."},
    {"name": "Banished Flame", "combo": "Dark + Burn", "desc": "Darkflame stacks (max 6), 1-30 damage/stack/sec. On expiry: 1-100 bonus damage."},
    {"name": "Banshee", "combo": "Phantom + Wraith", "desc": "Curses all enemies on field when launched. 150-300 damage after 6 hits."},
    {"name": "Brimstone", "combo": "Burn + Stone OR Poison", "desc": "1 burn + poison stack/second in 2 tile radius (max 4 stacks each)."},
    {"name": "Catapult", "combo": "Stone + Egg Sac", "desc": "Launches 3-5 stone baby balls every 1.5 seconds."},
    {"name": "Erosion", "combo": "Time + Wind", "desc": "Passes through enemies. Deals 3% of enemy current health as bonus damage."},
    {"name": "Fireworks", "combo": "Burn + Egg Sac", "desc": "Explodes into 3-6 fireworks targeting random enemies, 20-30 damage + burn."},
    {"name": "Heart Swallower", "combo": "Bleed + Ghost", "desc": "40% chance to steal 1 health and reduce enemy attack by 20%."},
    {"name": "Landslide", "combo": "Stone + Earthquake", "desc": "Creates landslide on hit (destroys self). 20-30 damage/sec in 2 tile radius for 5 seconds."},
    {"name": "Laser Cutter", "combo": "Steel + Laser (H or V)", "desc": "Constantly emits laser forward, 100-150 damage per second."},
    {"name": "Reaper", "combo": "Soul Sucker + Heart Swallower", "desc": "10% chance to instantly kill enemies on impact, healing 5 health."},
    {"name": "Sniper", "combo": "Shotgun + Assassin", "desc": "Pierces enemies, shoots 3-7 sniper baby balls after hitting a wall."},
    {"name": "Steel", "combo": "Iron + Stone", "desc": "Double damage, 50% slower. Damage grows +10% per hit (max 300%)."},
    {"name": "Time Bomb", "combo": "Time + Bomb", "desc": "Throws a time bomb every few seconds, exploding for 80-120 damage."},
    {"name": "Timestop", "combo": "Time + Freeze", "desc": "Freezes everything on field for 5 seconds. Destroys self. 30 second cooldown."},
    {"name": "Venom", "combo": "Poison + Freeze", "desc": "Venom stacks (max 8), 3-6 damage/stack/sec + slows enemies."},
    {"name": "Warp", "combo": "Time + Light", "desc": "Warps to random spot after each hit, speeds up by 5% each warp."},
]

TOP_EVOLUTIONS = [
    "Frozen Flame", "Nuclear Bomb", "Hemorrhage", "Vampire Lord", "Holy Laser",
    "Satan", "Nosferatu", "Black Hole", "Radiation Beam", "Sun",
    "Steel", "Timestop", "Laser Cutter", "Banished Flame", "Reaper",
]

TOP_FUSIONS = [
    {"balls": ["Flicker", "Frozen Flame"], "tip": "Screen-wide damage + frostburn stacks for devastating AoE."},
    {"balls": ["Phantom", "Voluptuous Egg Sac"], "tip": "Curse spread via mass egg sac explosions."},
    {"balls": ["Flash", "Hemorrhage"], "tip": "Screen-wide blind + bleed-stack burst damage."},
    {"balls": ["Flicker", "Hemorrhage"], "tip": "Constant screen damage feeds bleed-stack execution."},
    {"balls": ["Maggot", "Holy Laser"], "tip": "Infested enemies explode into babies while laser clears rows & columns."},
    {"balls": ["Maggot", "Nuclear Bomb"], "tip": "Infestation + radiation stacks for exponential damage scaling."},
    {"balls": ["Maggot", "Freeze Ray"], "tip": "Freeze-locked enemies die and birth more baby balls."},
    {"balls": ["Overgrowth", "Flash"], "tip": "Overgrowth AoE burst + screen-wide blind & damage."},
    {"balls": ["Mosquito Swarm", "Bomb"], "tip": "Swarm mosquitos + explosion for massive burst & health steal."},
    {"balls": ["Mosquito Swarm", "Nuclear Bomb"], "tip": "Mosquito swarm with radiation stacking for insane scaling."},
    {"balls": ["Mosquito Swarm", "Phantom"], "tip": "Swarm + curse for guaranteed 100-200 bonus damage per enemy."},
]

ALL_BALLS = BASE_BALLS + EVOLVED_BALLS

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_ball(name: str):
    """Case-insensitive ball lookup."""
    for b in ALL_BALLS:
        if b["name"].lower() == name.lower():
            return b
    return None


def ball_data_text(names: list[str]) -> str:
    """Format a list of ball names into descriptive text."""
    lines = []
    for n in names:
        b = find_ball(n)
        lines.append(f"{n}: {b['desc']}" if b else n)
    return "\n".join(lines)


def build_prompt(current_balls: list[str], level_up_options: list[str]) -> str:
    evolved_context = "\n".join(
        f"{e['name']} ({e['combo']}): {e['desc']}" for e in EVOLVED_BALLS
    )
    fusion_context = "\n".join(
        f"{f['balls'][0]} × {f['balls'][1]}: {f['tip']}" for f in TOP_FUSIONS
    )
    return f"""You are an expert BALL x PIT roguelite advisor. Analyze this player's situation and give strategic advice.

CURRENT BALLS:
{ball_data_text(current_balls) if current_balls else "None yet"}

LEVEL-UP OPTIONS BEING OFFERED:
{ball_data_text(level_up_options) if level_up_options else "Not specified"}

ALL POSSIBLE EVOLUTIONS (for reference):
{evolved_context}

TOP-TIER EVOLUTIONS TO AIM FOR: {", ".join(TOP_EVOLUTIONS)}

TOP-TIER FUSIONS (combining 2 balls together — can be base+base, base+evolved, or evolved+evolved):
{fusion_context}

Give clear, specific advice:
1. Which level-up option to pick (and why, based on synergies with current balls)
2. What evolutions are NOW possible or 1 ball away
3. What fusions (2-ball combos) are possible or close with current balls
4. The ideal build path to aim for given the current state
5. Any balls to prioritize getting next

Be concise, tactical, and specific. Format with clear sections. Mention specific ball names and combos."""

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/balls")
def api_balls():
    return jsonify({
        "base": BASE_BALLS,
        "evolved": EVOLVED_BALLS,
        "top_evolutions": TOP_EVOLUTIONS,
        "top_fusions": TOP_FUSIONS,
    })


@app.route("/api/advice", methods=["POST"])
def api_advice():
    data = request.get_json(force=True)
    current_balls = data.get("current_balls", [])
    level_up_options = data.get("level_up_options", [])

    if not current_balls and not level_up_options:
        return jsonify({"error": "Add at least your current balls or level-up options."}), 400

    api_key = data.get("api_key", "").strip()
    if not api_key:
        api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return jsonify({"error": "No API key provided. Enter your Gemini API key in the settings panel."}), 400

    prompt = build_prompt(current_balls, level_up_options)

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent?key={api_key}"
        resp = http_requests.post(
            url,
            headers={
                "Content-Type": "application/json",
            },
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 1000},
            },
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()
        
        try:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            text = "No advice returned."
            
        return jsonify({"advice": text})
    except http_requests.exceptions.HTTPError as e:
        error_body = ""
        try:
            error_body = e.response.json().get("error", {}).get("message", str(e))
        except Exception:
            error_body = str(e)
        return jsonify({"error": f"API error: {error_body}"}), 502
    except Exception as e:
        return jsonify({"error": f"Failed to get advice: {str(e)}"}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
