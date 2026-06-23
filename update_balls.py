import json
import re

with open('balls_db.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# generate python code
base_balls_str = 'BASE_BALLS = [\n'
for b in db['base']:
    desc = b['desc'].replace('"', '\\"').replace('\n', ' ')
    base_balls_str += f'    {{"name": "{b["name"]}", "desc": "{desc}"}},\n'
base_balls_str += ']\n\n'

evolved_balls_str = 'EVOLVED_BALLS = [\n'
for b in db['evolved']:
    desc = b['desc'].replace('"', '\\"').replace('\n', ' ')
    combo = b["combo"].replace('"', '\\"')
    recipes = str(b["recipes"])
    evolved_balls_str += f'    {{"name": "{b["name"]}", "combo": "{combo}", "desc": "{desc}", "recipes": {recipes}}},\n'
evolved_balls_str += ']\n'

with open('app.py', 'r', encoding='utf-8') as f:
    app_code = f.read()

app_code = re.sub(r'BASE_BALLS = \[.*?\]\n\n', base_balls_str, app_code, flags=re.DOTALL)
app_code = re.sub(r'EVOLVED_BALLS = \[.*?\]\n\n', evolved_balls_str + '\n', app_code, flags=re.DOTALL)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)
print('Updated app.py with new balls data.')
