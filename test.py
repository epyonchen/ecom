import json
with open('config.txt', 'r') as f:
    data = f.read()
print(data)
a = json.loads(data)
print(a)