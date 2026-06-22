# BallXPit Analyser 🎱

A **build advisor tool** for the roguelite game [BALL x PIT](https://store.steampowered.com/app/BALL_x_PIT/), helping you make smarter level-up decisions on the fly.

## What It Does

During a run, when you're offered new balls at level-up, it's hard to know which pick best synergises with what you've already got. This tool solves that — instantly.

Enter the balls you currently have, and the balls you're being offered, and the analyser will tell you:

- 🎯 **Best pick** — which offered ball gives you the highest overall value
- 🔥 **Immediate synergies** — which pick completes a top-tier evolution or fusion *right now*
- 📈 **Evolution paths** — which pick brings you closest to future top-tier goals

## How It Works

No AI. No API keys. No internet required.

The advisor uses two pure algorithms:

1. **Synergy Scoring** — Awards points for every top-tier evolution or fusion an offered ball immediately completes. Fusions are weighted higher than evolutions since they require more balls but hit harder.

2. **Evolution Path Finder** — Models balls and evolutions as a graph. Calculates how many missing components separate your current collection from each top-tier goal, then scores each offered ball by how much it reduces that distance. Closer goals are exponentially weighted.

## Running Locally

Requires Python 3.x and Flask.

```bash
pip install flask
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

## To-Do
1. Handle **Banish** and **Reroll** mechanics.
2. Handle **ball limit** (a player can have a maximum of 4 balls at any given time). The only way to bring this down is to evolve (if there's a valid option) or fuse (if there are at least 2 balls that haven't been fused before).
3. Add **triple evolutions** (combinations where you can evolve a ball, and then evolve it again with another).
