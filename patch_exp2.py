import os
with open('gen_cards.py', 'r') as f:
    c = f.read()
c = c.replace("'base_value': 0.0}", "'base_value': 0.0, 'top_features': []}")
with open('gen_cards.py', 'w') as f:
    f.write(c)

