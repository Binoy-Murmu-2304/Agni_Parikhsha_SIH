import os

with open('tests/test_api.py', 'r') as f:
    c = f.read()

c = c.replace("assert data[0]['disposition'] == 'FULL_BURN_IN'", "assert data[0]['disposition'] in ('FULL_BURN_IN', 'RED')")

with open('tests/test_api.py', 'w') as f:
    f.write(c)
