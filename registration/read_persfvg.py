import json

with open('res/persfvg_dump_persone.json', 'r') as f:
  persone = json.load(f)

print(persone)

print()

with open('res/persfvg_dump_matricole.json', 'r') as f:
  matricole = json.load(f)

print(matricole)


