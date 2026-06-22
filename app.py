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
    {'name': 'Assassin', 'combo': 'Iron + Ghost OR Iron + Dark', 'recipes': [['Iron', 'Ghost'], ['Iron', 'Dark']]},
    {'name': 'Berserk', 'combo': 'Charm + Bleed OR Charm + Burn', 'recipes': [['Charm', 'Bleed'], ['Charm', 'Burn']]},
    {'name': 'Black Hole', 'combo': 'Dark + Sun', 'recipes': [['Dark', 'Sun']]},
    {'name': 'Blizzard', 'combo': 'Freeze + Wind OR Freeze + Lightning', 'recipes': [['Freeze', 'Wind'], ['Freeze', 'Lightning']]},
    {'name': 'Bomb', 'combo': 'Burn + Iron', 'recipes': [['Burn', 'Iron']]},
    {'name': 'Flash', 'combo': 'Lightning + Light', 'recipes': [['Lightning', 'Light']]},
    {'name': 'Flicker', 'combo': 'Light + Dark', 'recipes': [['Light', 'Dark']]},
    {'name': 'Freeze Ray', 'combo': 'Freeze + Laser (H or V)', 'recipes': [['Freeze', 'Laser (Horizontal)'], ['Freeze', 'Laser (Vertical)']]},
    {'name': 'Frozen Flame', 'combo': 'Burn + Freeze', 'recipes': [['Burn', 'Freeze']]},
    {'name': 'Glacier', 'combo': 'Freeze + Earthquake', 'recipes': [['Freeze', 'Earthquake']]},
    {'name': 'Hemorrhage', 'combo': 'Bleed + Iron', 'recipes': [['Bleed', 'Iron']]},
    {'name': 'Holy Laser', 'combo': 'Laser (H) + Laser (V)', 'recipes': [['Laser (Horizontal)', 'Laser (Vertical)']]},
    {'name': 'Incubus', 'combo': 'Charm + Dark', 'recipes': [['Charm', 'Dark']]},
    {'name': 'Inferno', 'combo': 'Burn + Wind', 'recipes': [['Burn', 'Wind']]},
    {'name': 'Laser Beam', 'combo': 'Light + Laser (H or V)', 'recipes': [['Light', 'Laser (Horizontal)'], ['Light', 'Laser (Vertical)']]},
    {'name': 'Leech', 'combo': 'Brood Mother + Bleed', 'recipes': [['Brood Mother', 'Bleed']]},
    {'name': 'Lightning Rod', 'combo': 'Lightning + Iron', 'recipes': [['Lightning', 'Iron']]},
    {'name': 'Lovestruck', 'combo': 'Charm + Light OR Charm + Lightning', 'recipes': [['Charm', 'Light'], ['Charm', 'Lightning']]},
    {'name': 'Maggot', 'combo': 'Brood Mother + Cell', 'recipes': [['Brood Mother', 'Cell']]},
    {'name': 'Magma', 'combo': 'Burn + Earthquake', 'recipes': [['Burn', 'Earthquake']]},
    {'name': 'Mosquito King', 'combo': 'Vampire + Brood Mother', 'recipes': [['Vampire', 'Brood Mother']]},
    {'name': 'Mosquito Swarm', 'combo': 'Vampire + Egg Sac', 'recipes': [['Vampire', 'Egg Sac']]},
    {'name': 'Noxious', 'combo': 'Poison + Wind OR Dark + Wind', 'recipes': [['Poison', 'Wind'], ['Dark', 'Wind']]},
    {'name': 'Nuclear Bomb', 'combo': 'Bomb + Poison', 'recipes': [['Bomb', 'Poison']]},
    {'name': 'Overgrowth', 'combo': 'Earthquake + Cell', 'recipes': [['Earthquake', 'Cell']]},
    {'name': 'Phantom', 'combo': 'Dark + Ghost', 'recipes': [['Dark', 'Ghost']]},
    {'name': 'Radiation Beam', 'combo': 'Laser (H or V) + Poison OR Cell', 'recipes': [['Laser (Horizontal)', 'Poison'], ['Laser (Vertical)', 'Poison'], ['Laser (Horizontal)', 'Cell'], ['Laser (Vertical)', 'Cell']]},
    {'name': 'Sacrifice', 'combo': 'Bleed + Dark', 'recipes': [['Bleed', 'Dark']]},
    {'name': 'Sandstorm', 'combo': 'Earthquake + Wind', 'recipes': [['Earthquake', 'Wind']]},
    {'name': 'Satan', 'combo': 'Incubus + Succubus', 'recipes': [['Incubus', 'Succubus']]},
    {'name': 'Shotgun', 'combo': 'Iron + Egg Sac', 'recipes': [['Iron', 'Egg Sac']]},
    {'name': 'Soul Sucker', 'combo': 'Vampire + Ghost', 'recipes': [['Vampire', 'Ghost']]},
    {'name': 'Spider Queen', 'combo': 'Brood Mother + Egg Sac', 'recipes': [['Brood Mother', 'Egg Sac']]},
    {'name': 'Storm', 'combo': 'Lightning + Wind', 'recipes': [['Lightning', 'Wind']]},
    {'name': 'Succubus', 'combo': 'Charm + Vampire', 'recipes': [['Charm', 'Vampire']]},
    {'name': 'Sun', 'combo': 'Burn + Light', 'recipes': [['Burn', 'Light']]},
    {'name': 'Swamp', 'combo': 'Poison + Earthquake', 'recipes': [['Poison', 'Earthquake']]},
    {'name': 'Vampire Lord', 'combo': 'Vampire + Bleed OR Vampire + Dark', 'recipes': [['Vampire', 'Bleed'], ['Vampire', 'Dark']]},
    {'name': 'Virus', 'combo': 'Poison + Ghost OR Poison + Cell', 'recipes': [['Poison', 'Ghost'], ['Poison', 'Cell']]},
    {'name': 'Voluptuous Egg Sac', 'combo': 'Egg Sac + Cell', 'recipes': [['Egg Sac', 'Cell']]},
    {'name': 'Wraith', 'combo': 'Freeze + Ghost', 'recipes': [['Freeze', 'Ghost']]},
    {'name': 'Nosferatu', 'combo': 'Vampire Lord + Spider Queen + Mosquito King', 'recipes': [['Vampire Lord', 'Spider Queen', 'Mosquito King']]},
    {'name': 'Banished Flame', 'combo': 'Dark + Burn', 'recipes': [['Dark', 'Burn']]},
    {'name': 'Banshee', 'combo': 'Phantom + Wraith', 'recipes': [['Phantom', 'Wraith']]},
    {'name': 'Brimstone', 'combo': 'Burn + Stone OR Poison', 'recipes': [['Burn', 'Stone'], ['Burn', 'Poison']]},
    {'name': 'Catapult', 'combo': 'Stone + Egg Sac', 'recipes': [['Stone', 'Egg Sac']]},
    {'name': 'Erosion', 'combo': 'Time + Wind', 'recipes': [['Time', 'Wind']]},
    {'name': 'Fireworks', 'combo': 'Burn + Egg Sac', 'recipes': [['Burn', 'Egg Sac']]},
    {'name': 'Heart Swallower', 'combo': 'Bleed + Ghost', 'recipes': [['Bleed', 'Ghost']]},
    {'name': 'Landslide', 'combo': 'Stone + Earthquake', 'recipes': [['Stone', 'Earthquake']]},
    {'name': 'Laser Cutter', 'combo': 'Steel + Laser (H or V)', 'recipes': [['Steel', 'Laser (Horizontal)'], ['Steel', 'Laser (Vertical)']]},
    {'name': 'Reaper', 'combo': 'Soul Sucker + Heart Swallower', 'recipes': [['Soul Sucker', 'Heart Swallower']]},
    {'name': 'Sniper', 'combo': 'Shotgun + Assassin', 'recipes': [['Shotgun', 'Assassin']]},
    {'name': 'Steel', 'combo': 'Iron + Stone', 'recipes': [['Iron', 'Stone']]},
    {'name': 'Time Bomb', 'combo': 'Time + Bomb', 'recipes': [['Time', 'Bomb']]},
    {'name': 'Timestop', 'combo': 'Time + Freeze', 'recipes': [['Time', 'Freeze']]},
    {'name': 'Venom', 'combo': 'Poison + Freeze', 'recipes': [['Poison', 'Freeze']]},
    {'name': 'Warp', 'combo': 'Time + Light', 'recipes': [['Time', 'Light']]},
]

TOP_EVOLUTIONS = [
    "Frozen Flame", "Nuclear Bomb", "Hemorrhage", "Vampire Lord", "Holy Laser",
    "Satan", "Nosferatu", "Black Hole", "Radiation Beam", "Sun", "Timestop", "Laser Cutter", "Banished Flame", "Reaper",
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



from collections import Counter

def get_recipes(ball_name):
    for eb in EVOLVED_BALLS:
        if eb['name'].lower() == ball_name.lower():
            return eb.get('recipes', [])
    return []

def min_distance(target, current_counts):
    # current_counts is a Counter
    if current_counts.get(target, 0) > 0:
        return 0, Counter({target: 1})
    
    recipes = get_recipes(target)
    if not recipes:
        return 1, Counter()
        
    best_dist = float('inf')
    best_used = Counter()
    
    for recipe in recipes:
        dist = 0
        used = Counter()
        local_counts = current_counts.copy()
        
        for comp in recipe:
            comp_dist, comp_used = min_distance(comp, local_counts)
            dist += comp_dist
            used += comp_used
            local_counts -= comp_used
            
        if dist < best_dist:
            best_dist = dist
            best_used = used
            
    return best_dist, best_used

def fusion_distance(fusion_recipe, current_counts):
    dist = 0
    local_counts = current_counts.copy()
    for comp in fusion_recipe:
        c_dist, c_used = min_distance(comp, local_counts)
        dist += c_dist
        local_counts -= c_used
    return dist

def evaluate_options(current_balls, level_up_options):
    current_counts = Counter(current_balls)
    
    base_evo_dists = {evo: min_distance(evo, current_counts)[0] for evo in TOP_EVOLUTIONS}
    base_fusion_dists = {idx: fusion_distance(fusion["balls"], current_counts) for idx, fusion in enumerate(TOP_FUSIONS)}
    
    best_score = -1
    best_option = None
    results = {}
    
    for option in level_up_options:
        new_counts = current_counts.copy()
        new_counts[option] += 1
        
        score = 0
        synergies = []
        improvements = []
        
        for evo in TOP_EVOLUTIONS:
            new_dist = min_distance(evo, new_counts)[0]
            old_dist = base_evo_dists[evo]
            if new_dist < old_dist:
                if new_dist == 0:
                    synergies.append(f"Evolution: {evo}")
                    score += 1000
                else:
                    improvements.append((new_dist, f"Closer to {evo} ({new_dist} away)"))
                    score += 10 / new_dist
                    
        for idx, fusion in enumerate(TOP_FUSIONS):
            new_dist = fusion_distance(fusion["balls"], new_counts)
            old_dist = base_fusion_dists[idx]
            if new_dist < old_dist:
                fusion_name = f"{fusion['balls'][0]} × {fusion['balls'][1]}"
                if new_dist == 0:
                    synergies.append(f"Fusion: {fusion_name}")
                    score += 2000
                else:
                    improvements.append((new_dist, f"Closer to {fusion_name} ({new_dist} away)"))
                    score += 20 / new_dist
                    
        # Sort improvements by distance
        improvements.sort(key=lambda x: x[0])
        imp_strings = [x[1] for x in improvements]
        
        results[option] = {
            "score": score,
            "synergies": synergies,
            "improvements": imp_strings
        }
        
        if score > best_score:
            best_score = score
            best_option = option
            
    if best_score <= 0:
        return {"best_pick": "None", "text_advice": "No significant synergies found. Pick based on base stats.", "raw_results": results}
        
    res = results[best_option]
    advice = f"🎯 Best Pick: **{best_option}**\n\n"
    
    if res["synergies"]:
        advice += "🔥 **IMMEDIATE SYNERGIES (Win Fast)**\n"
        for syn in res["synergies"]:
            advice += f"• Completes {syn}!\n"
        advice += "\n"
        
    if res["improvements"]:
        advice += "📈 **EVOLUTION PATH FINDER**\nThis ball brings you closer to:\n"
        for imp in res["improvements"][:5]:
            advice += f"• {imp}\n"
            
    runners_up = [(opt, data) for opt, data in results.items() if opt != best_option and data["score"] > 0]
    runners_up.sort(key=lambda x: x[1]["score"], reverse=True)
    if runners_up:
        advice += f"\n🥈 **Runner up:** {runners_up[0][0]}"
        
    return {
        "best_pick": best_option,
        "text_advice": advice,
        "raw_results": results
    }

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

    try:
        res = evaluate_options(current_balls, level_up_options)
        return jsonify({
            "advice": res["text_advice"],
            "structured": res
        })
    except Exception as e:
        return jsonify({"error": f"Failed to calculate advice: {str(e)}"}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
