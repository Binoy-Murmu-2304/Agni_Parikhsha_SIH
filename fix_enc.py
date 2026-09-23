import os
with open('agnipariksha/config.py', 'rb') as f:
    c = f.read().decode('cp1252', errors='ignore')

c = c.replace('"unit": "??A"', '"unit": "?A"')
c = c.replace('"unit": "??V"', '"unit": "?V"')

with open('agnipariksha/config.py', 'w', encoding='utf-8') as f:
    f.write(c)
