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
    {"name": "Bleed", "desc": "Inflicts 2 stacks of bleed. Bleeding enemies receive 1 damage per stack when hit by a ball (max 8 stacks)."},
    {"name": "Brood Mother", "desc": "Has a 25% chance of birthing a baby ball each time it hits an enemy."},
    {"name": "Burn", "desc": "Add 1 stack of burn on hit for 3 seconds (max 3 stacks). Burnt units are dealt 4-8 damage per stack per second."},
    {"name": "Cell", "desc": "Splits into a clone on hit 2 times."},
    {"name": "Charm", "desc": "Each hit has a 4% chance of charming the enemy for 5 seconds. Charmed units walk up the board and attack enemies."},
    {"name": "Dark", "desc": "Deals 3.0x damage but destroys itself after hitting an enemy. Has a 3 second cooldown before it can be shot again."},
    {"name": "Earthquake", "desc": "Deals 5-13 damage to nearby units in a 3x3 tile square."},
    {"name": "Egg Sac", "desc": "Explodes into 2-4 baby balls on hitting an enemy. Has a 3 second cooldown before it can be shot again."},
    {"name": "Freeze", "desc": "Has a 4% chance to freeze enemies for 5.0 seconds. Frozen enemies receive 25% more damage."},
    {"name": "Ghost", "desc": "Passes through enemies."},
    {"name": "Iron", "desc": "Deals double damage but moves 40% slower."},
    {"name": "Laser (Horizontal)", "desc": "Deals 9-18 damage to all enemies in the same row."},
    {"name": "Laser (Vertical)", "desc": "Deals 9-18 damage to all enemies in the same column."},
    {"name": "Light", "desc": "Blinds enemies on hit for 3 seconds. Blinded units have a hard time detecting you and have a 50% chance of missing when they attack."},
    {"name": "Lightning", "desc": "Deals 1-20 damage to up to 3 nearby enemies."},
    {"name": "Stone", "desc": "Initially deals 300% damage. Damage erodes by 40% each time hitting an enemy (minimum 50%)."},
    {"name": "Poison", "desc": "Applies 1 stack of poison on hit (max 5 stacks). Poison lasts for 6 seconds and each stack deals 1-4 damage per second."},
    {"name": "Time", "desc": "Explodes into a time snare upon hitting an enemy, which stays on the field for 20 seconds and freezes enemies inside it."},
    {"name": "Vampire", "desc": "Each hit has a 4.5% chance of healing 1 health."},
    {"name": "Wind", "desc": "Passes through enemies and slows them down by 30% for 5 seconds, but deals 25% less damage."},
]

EVOLVED_BALLS = [
    {"name": "Assassin", "combo": "Base", "desc": "Passes through the front of enemies, but not the back. Backstabs deal 30% bonus damage.", "recipes": [["Iron", "Ghost"], ["Iron", "Dark"]]},
    {"name": "Banished Flame", "combo": "Base", "desc": "Add 1 stack of darkflame on hit for 2 seconds (max 6 stacks). Darkflame deals 1-30 damage per stack per second. When the darkflame goes out, it deals 1-100 to the enemy.", "recipes": [["Dark", "Burn"]]},
    {"name": "Banshee", "combo": "Base", "desc": "Curses all enemies while on the field when launched. Cursed enemies are dealt 150-300 after being hit 6 times.", "recipes": [["Phantom", "Storm"]]},
    {"name": "Berserk", "combo": "Base", "desc": "Each hit has a 30% chance of causing enemies to go berserk for 6 seconds. Berserk enemies deal 15-24 damage to adjacent enemies every second", "recipes": [["Charm", "Burn"], ["Charm", "Bleed"]]},
    {"name": "Black Hole", "combo": "Base", "desc": "Instantly kills the first non-boss enemy that it hits, but destroys itself afterwards. Has a 7 second cooldown before it can be shot again", "recipes": [["Dark", "Sun"]]},
    {"name": "Blizzard", "combo": "Base, AOE", "desc": "Freezes all enemies within a 2 tile radius for 0.8 seconds, dealing 1-50 damage", "recipes": [["Freeze", "Lightning"], ["Freeze", "Wind"]]},
    {"name": "Bomb", "combo": "AOE", "desc": "Explodes when hitting an enemy, dealing 150-300 damage to nearby enemies. Has a 3 second cooldown before it can be shot again", "recipes": [["Burn", "Iron"]]},
    {"name": "Brimstone", "combo": "Base", "desc": "Applies 1 stack of burn and poison every second to all enemies within a 2 tile radius (max 4 stacks). Burn deals 1-4 damage per stack per second and poison deals 2-3 damage per stack per second.", "recipes": [["Burn", "Poison"], ["Burn", "Stone"]]},
    {"name": "Catapult", "combo": "Base", "desc": "Launches 3-5 stone baby balls every 1.5 seconds, which are destroyed after hitting anything.", "recipes": [["Egg Sac", "Stone"]]},
    {"name": "Erosion", "combo": "Base", "desc": "Passes through enemies. Deals 3% of enemy's current health as bonus damage on hit.", "recipes": [["Time", "Wind"]]},
    {"name": "Fireworks", "combo": "Base", "desc": "Explodes into 3-6 fireworks. Fireworks target random enemies, dealing 20-30 damage and applying 1 stack of burn. Burnt units are dealt 7-11 damage per stack per second.", "recipes": [["Burn", "Egg Sac"]]},
    {"name": "Flash", "combo": "Base, AOE", "desc": "Damage all enemies on screen for 1-3 damage after hitting an enemy and blind them for 2 seconds", "recipes": [["Light", "Lightning"]]},
    {"name": "Flicker", "combo": "Base, AOE", "desc": "Deals 1-7 damage to every enemy on screen every 1.4 seconds", "recipes": [["Light", "Dark"]]},
    {"name": "Freeze Ray", "combo": "Base, AOE", "desc": "Emits a freeze ray when hitting an enemy, dealing 20-50 to all enemies in its path, with a 10% chance of freezing them for 10.0 seconds", "recipes": [["Freeze", "Laser (Horizontal)"], ["Freeze", "Laser (Vertical)"]]},
    {"name": "Frozen Flame", "combo": "Base", "desc": "Add 1 stack of frostburn on hit for 20 seconds (max 4 stacks). Frostburnt units are dealt 8-12 damage per stack per second and receive 25% more damage from other sources", "recipes": [["Burn", "Freeze"]]},
    {"name": "Glacier", "combo": "Base", "desc": "Releases glacial spikes over time that deal 15-30 to enemies that touch them and freeze them for 2.0 seconds. This ball and its glacial spikes also deal 6-12 damage to nearby units", "recipes": [["Freeze", "Earthquake"]]},
    {"name": "Heart Swallower", "combo": "Base", "desc": "Saps enemies on hit, with a 40% chance of stealing 1 health and reducing their attack damage by 20%. Lifesteal chance only applies once per enemy.", "recipes": [["Bleed", "Ghost"]]},
    {"name": "Hemorrhage", "combo": "Base", "desc": "Inflicts 3 stacks of bleed. When hitting an enemy with 12 stacks of bleed or more, consumes all stacks of bleed to deal 20% of their current health", "recipes": [["Bleed", "Iron"]]},
    {"name": "Holy Laser", "combo": "AOE", "desc": "Deals 24-36 damage to all enemies in the same row and column", "recipes": [["Laser (Horizontal)", "Laser (Vertical)"]]},
    {"name": "Incubus", "combo": "Base", "desc": "Each hit has a 4% chance of charming the enemy for 9 seconds. Charmed enemies curse nearby enemies. Cursed enemies are dealt 100-200 after being hit 5 times", "recipes": [["Charm", "Dark"]]},
    {"name": "Inferno", "combo": "AOE", "desc": "Applies 1 stack of burn every second to all enemies within a 2 tile radius. Burn lasts for 6 seconds, dealing 3-7 damage per stack per seconds", "recipes": [["Burn", "Wind"]]},
    {"name": "Landslide", "combo": "Base, AOE", "desc": "Creates a landslide and destroys self upon hitting an enemy. The landslide lasts for 5 seconds and deals 20-30 damage per second to enemies within a 2 tile radius", "recipes": [["Earthquake", "Stone"]]},
    {"name": "Laser Beam", "combo": "Base, AOE", "desc": "Emit a laser beam on hit that deals 30-42 damage and blinds enemies for 8 seconds", "recipes": [["Laser (Horizontal)", "Light"], ["Laser (Vertical)", "Light"]]},
    {"name": "Laser Cutter", "combo": "Base, AOE", "desc": "Constantly emits a laser in front of it, which deals 100-150 damage per second.", "recipes": [["Steel", "Laser (Horizontal)"], ["Steel", "Laser (Vertical)"]]},
    {"name": "Leech", "combo": "Base", "desc": "Attaches up to 1 leech onto enemies it hits, which add 2 stacks of bleed per seconds (max 24 stacks)", "recipes": [["Bleed", "Brood Mother"]]},
    {"name": "Lightning Rod", "combo": "Base, AOE", "desc": "Plants a lightning rod into enemies it hits. These enemies are struck by lightning every 3.0 seconds, dealing 1-30 damage to up to 8 nearby enemies", "recipes": [["Lightning", "Iron"]]},
    {"name": "Lovestruck", "combo": "Base", "desc": "Inflicts lovestruck on hit enemies for 20 seconds. Lovestruck units have a 50% chance of healing you for 5 health when they attack", "recipes": [["Charm", "Light"], ["Charm", "Lightning"]]},
    {"name": "Maggot", "combo": "Base", "desc": "Infest enemies on hit with maggots. When they dies, they explode into 1-2 baby balls", "recipes": [["Brood Mother", "Cell"]]},
    {"name": "Magma", "combo": "Base, AOE", "desc": "Emits lava blobs over time. Enemies who walk into lava blobs are dealt 15-30 damage and gain 1 stack of burn (max 3 stacks). Burn lasts for 3 seconds, dealing 3-8 damage per stack per second. This ball and its lava blobs also deal 6-12 damage to nearby units", "recipes": [["Burn", "Earthquake"]]},
    {"name": "Mosquito King", "combo": "Base", "desc": "Spawns a mosquito each time it hits an enemy. Mosquitos attack a random enemy, dealing 80-120 damage each. If a mosquito kills an enemy, they steal 1 health", "recipes": [["Vampire", "Brood Mother"]]},
    {"name": "Mosquito Swarm", "combo": "Base", "desc": "Explodes into 3-6 mosquitos. Mosquitos attack random enemies, dealing 80-120 damage each. If a mosquito kills an enemy, they steal 1 health", "recipes": [["Vampire", "Egg Sac"]]},
    {"name": "Nosferatu", "combo": "Base", "desc": "Spawns a vampire bat each bounce. Vampire bats fly towards a random enemy, dealing 132-176 damage on hit, turning into a Vampire Lord", "recipes": [["Vampire Lord", "Spider Queen", "Mosquito King"]]},
    {"name": "Noxious", "combo": "Base", "desc": "Passes through enemies and applies 3 stacks of poison to nearby enemies within a 2 tile radius. Poison lasts for 4 seconds and each stack deals 1-3 damage per second", "recipes": [["Poison", "Wind"], ["Dark", "Wind"]]},
    {"name": "Nuclear Bomb", "combo": "AOE", "desc": "Explodes when hitting an enemy, dealing 300-500 damage to nearby enemies and applying 1 stack of radiation to everyone present indefinitely (max 5 stacks). Each stack of radiation increases damage received by 10%. Has a 3 second cooldown", "recipes": [["Bomb", "Poison"]]},
    {"name": "Overgrowth", "combo": "Base, AOE", "desc": "Applies 1 stack of overgrowth. Upon reaching 3, consume all stacks and deal 150-200 damage to all enemies in a 3x3 tile square", "recipes": [["Cell", "Earthquake"]]},
    {"name": "Phantom", "combo": "Base", "desc": "Curse enemies on hit. Cursed enemies are dealt 100-200 damage after being hit 5 times", "recipes": [["Dark", "Ghost"]]},
    {"name": "Radiation Beam", "combo": "Base, AOE", "desc": "Emit a radiation beam on hit that deals 24-48 damage and applies 1 stack of radiation (max 5 stacks). Radiation lasts for 15 seconds and cause enemies to receive 10% more damage from all sources per stack", "recipes": [["Cell", "Laser (Horizontal)"], ["Cell", "Laser (Vertical)"], ["Poison", "Laser (Horizontal)"], ["Poison", "Laser (Vertical)"]]},
    {"name": "Reaper", "combo": "Base", "desc": "Has a 10% chance to kill enemies on impact, healing you for 5 health.", "recipes": [["Soul Sucker", "Heart Swallower"]]},
    {"name": "Sacrifice", "combo": "Base", "desc": "Inflicts 4 stacks of bleed (max 15 stacks) and applies curse to hit enemies. Cursed enemies are dealt 50-100 after being hit 5 times", "recipes": [["Bleed", "Dark"]]},
    {"name": "Sandstorm", "combo": "Base, AOE", "desc": "Goes through enemies and is surrounded by a raging storm dealing 10-20 damage per second and blinding nearby enemies for 3 seconds", "recipes": [["Earthquake", "Wind"]]},
    {"name": "Satan", "combo": "Base", "desc": "While active, add 1 stack of burn to all active enemies per second (max 5 stacks), dealing 10-20 damage per stack per second and make them go berserk, dealing 15-24 damage to adjacent enemies every second", "recipes": [["Incubus", "Succubus"]]},
    {"name": "Shotgun", "combo": "Base", "desc": "Shoots 3-7 iron baby balls after hitting a wall. Iron baby balls move at 200% speed but are destroyed upon hitting anything", "recipes": [["Iron", "Egg Sac"]]},
    {"name": "Sniper", "combo": "Base", "desc": "Pierces enemies and shoots 3-7 sniper baby balls after hitting a wall. Sniper baby balls pierce enemies but are destroyed upon hitting a wall.", "recipes": [["Shotgun", "Assassin"]]},
    {"name": "Soul Sucker", "combo": "Base", "desc": "Passes through enemies and saps them, with a 30% chance of stealing 1 health and reducing their attack damage by 20%. Lifesteal chance only applies once per enemy", "recipes": [["Vampire", "Ghost"]]},
    {"name": "Spider Queen", "combo": "Base", "desc": "Has a 25% chance of birthing an Egg Sac each time it hits an enemy", "recipes": [["Brood Mother", "Egg Sac"]]},
    {"name": "Steel", "combo": "Base", "desc": "Initially deals double damage but moves 50% slower. Damage increases by 10% each time it hits an enemy (max 300%).", "recipes": [["Stone", "Iron"]]},
    {"name": "Storm", "combo": "AOE", "desc": "Emits lightning to strike nearby enemies every second, dealing 1-40 damage", "recipes": [["Lightning", "Wind"]]},
    {"name": "Succubus", "combo": "Base", "desc": "Each hit has a 4% chance of charming the enemy for 9 seconds. Heals 1 when hitting a charmed enemy", "recipes": [["Charm", "Vampire"]]},
    {"name": "Sun", "combo": "Base", "desc": "Blind all enemies in view and add 1 stack of burn every second (max 5 stacks). Burn lasts for 6 seconds and deals 6-12 damage per stack per second", "recipes": [["Burn", "Light"]]},
    {"name": "Swamp", "combo": "Base, AOE", "desc": "Leaves behind tar blobs over time. Enemies who walk into tar blobs are dealt 15-30, are slowed by 50% for 7 seconds and gain 1 stack of poison (max 8 stacks). Each stack of poison deals 1-3 damage per second. This ball and its tar blobs also deal 6-12 damage to nearby units", "recipes": [["Poison", "Earthquake"]]},
    {"name": "Time Bomb", "combo": "Base, AOE", "desc": "Throws a time bomb every few seconds, which explodes after a delay, dealing 80-120 damage to nearby enemies.", "recipes": [["Time", "Bomb"]]},
    {"name": "Timestop", "combo": "Base", "desc": "Freezes everything on the field for 5.0 seconds but destroys itself after hitting an enemy. Has a 30 second cooldown before it can be shot again.", "recipes": [["Time", "Freeze"]]},
    {"name": "Vampire Lord", "combo": "Base", "desc": "Each hit inflicts 3 stacks of bleed. Heals 1 health and consumes all stacks when hitting an enemy with at least 10 stacks of bleed", "recipes": [["Vampire", "Bleed"], ["Vampire", "Dark"]]},
    {"name": "Venom", "combo": "Base", "desc": "Applies 1 stack of venom on hit (max 8 stacks). Each stack deal 3-6 damage per second and slows down enemies.", "recipes": [["Poison", "Freeze"]]},
    {"name": "Virus", "combo": "Base", "desc": "Applies 1 stack of disease to units it hits (max 8 stacks). Disease lasts for 6 seconds. Each stack of disease deals 3-6 damage per second and diseased units have a 15% chance of passing a stack to undiseased nearby enemies each second", "recipes": [["Poison", "Ghost"], ["Poison", "Cell"]]},
    {"name": "Voluptuous Egg Sac", "combo": "Base", "desc": "Explodes into 2-3 egg sacs on hitting an enemy. Has a 3 second cooldown before it can be shot again", "recipes": [["Egg Sac", "Cell"]]},
    {"name": "Warp", "combo": "Base", "desc": "After each hit, warps to a random spot on the field and speeds up by 5%.", "recipes": [["Time", "Light"]]},
    {"name": "Wraith", "combo": "Base", "desc": "Freezes any enemy it passes through for 0.8 seconds", "recipes": [["Freeze", "Ghost"]]},
    {"name": "X Ray", "combo": "Base", "desc": "Emits an X-shaped laser on hit, which deals 50-75 damage to enemies and applies 1 stack of radiation (max 5 stacks). Radiation causes enemies to receive 10% more damage from all sources per stack.", "recipes": [["Holy Laser", "Laser Beam"]]},
]

TOP_EVOLUTIONS = [
    "Frozen Flame", "Nuclear Bomb", "Hemorrhage", "Vampire Lord", "Holy Laser",
    "Satan", "Nosferatu", "Black Hole", "Radiation Beam", "Sun", "Laser Cutter", "Banished Flame", "Reaper",
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

def get_base_combo_string(ball_name):
    ball = find_ball(ball_name)
    if not ball:
        return ball_name.lower()
        
    if ball in BASE_BALLS:
        return ball_name.lower()
        
    recipes = get_recipes(ball_name)
    if not recipes:
        return ball_name.lower()
        
    recipe = recipes[0]
    
    all_base = True
    for c in recipe:
        c_ball = find_ball(c)
        if c_ball not in BASE_BALLS:
            all_base = False
            break
            
    if all_base:
        return "+".join(c.lower() for c in recipe)
    else:
        parts = [get_base_combo_string(c) for c in recipe]
        return ",".join(parts)

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
    
    # Pre-calculate distances for ALL evolutions, not just TOP_EVOLUTIONS
    base_evo_dists = {evo['name']: min_distance(evo['name'], current_counts)[0] for evo in EVOLVED_BALLS}
    base_fusion_dists = {idx: fusion_distance(fusion["balls"], current_counts) for idx, fusion in enumerate(TOP_FUSIONS)}
    
    if not level_up_options:
        # Give advice based ONLY on current balls
        close_evos = [(evo_name, dist) for evo_name, dist in base_evo_dists.items() if dist == 1]
        close_evos.sort(key=lambda x: (0 if x[0] in TOP_EVOLUTIONS else 1, x[0]))
        
        almost_evos = [{"name": name, "is_top": name in TOP_EVOLUTIONS} for name, dist in close_evos[:8]]
        
        close_fusions = [(idx, dist) for idx, dist in base_fusion_dists.items() if dist == 1]
        almost_fusions = [{"name": f"{TOP_FUSIONS[idx]['balls'][0]} × {TOP_FUSIONS[idx]['balls'][1]}"} for idx, dist in close_fusions[:4]]
        
        advice = "No specific targets are 1 piece away right now. Pick strong base balls to start new combos."
        
        return {
            "best_pick": "Analysis Only",
            "text_advice": advice,
            "analysis": {
                "almost_evos": almost_evos,
                "almost_fusions": almost_fusions
            },
            "raw_results": {}
        }
    
    best_score = -1
    best_option = None
    results = {}
    
    for option in level_up_options:
        new_counts = current_counts.copy()
        new_counts[option] += 1
        
        score = 0
        synergies = []
        improvements = []
        
        # Check against ALL evolved balls
        for evo in EVOLVED_BALLS:
            evo_name = evo['name']
            new_dist = min_distance(evo_name, new_counts)[0]
            old_dist = base_evo_dists[evo_name]
            
            if new_dist < old_dist:
                is_top = evo_name in TOP_EVOLUTIONS
                if new_dist == 0:
                    prefix = "⭐ Top Evolution" if is_top else "Evolution"
                    synergies.append(f"{prefix}: {evo_name}")
                    score += 1000 if is_top else 400
                else:
                    improvements.append((new_dist, f"Closer to {evo_name} ({new_dist} away)", is_top))
                    score += (20 if is_top else 5) / new_dist
                    
        for idx, fusion in enumerate(TOP_FUSIONS):
            new_dist = fusion_distance(fusion["balls"], new_counts)
            old_dist = base_fusion_dists[idx]
            if new_dist < old_dist:
                fusion_name = f"{fusion['balls'][0]} × {fusion['balls'][1]}"
                if new_dist == 0:
                    synergies.append(f"⭐ Fusion: {fusion_name}")
                    score += 2000
                else:
                    improvements.append((new_dist, f"Closer to {fusion_name} ({new_dist} away)", True))
                    score += 40 / new_dist
                    
        # Sort improvements by distance, then whether they are top
        improvements.sort(key=lambda x: (x[0], not x[2]))
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
    fuses_into_map = {}
    for eb in EVOLVED_BALLS:
        for recipe in eb.get("recipes", []):
            for comp in recipe:
                comp_lower = comp.lower()
                if comp_lower not in fuses_into_map:
                    fuses_into_map[comp_lower] = set()
                fuses_into_map[comp_lower].add(eb["name"])

    base_with_info = []
    for b in BASE_BALLS:
        b_copy = dict(b)
        b_copy['fuses_into'] = sorted(list(fuses_into_map.get(b['name'].lower(), set())))
        base_with_info.append(b_copy)

    evolved_with_combo = []
    for b in EVOLVED_BALLS:
        b_copy = dict(b)
        b_copy['base_combo'] = get_base_combo_string(b['name'])
        b_copy['fuses_into'] = sorted(list(fuses_into_map.get(b['name'].lower(), set())))
        evolved_with_combo.append(b_copy)
        
    fusions_with_combo = []
    for f in TOP_FUSIONS:
        f_copy = dict(f)
        parts = [get_base_combo_string(c) for c in f['balls']]
        f_copy['base_combo'] = ",".join(parts)
        fusions_with_combo.append(f_copy)

    return jsonify({
        "base": base_with_info,
        "evolved": evolved_with_combo,
        "top_evolutions": TOP_EVOLUTIONS,
        "top_fusions": fusions_with_combo,
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
