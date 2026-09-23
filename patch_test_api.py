import os

with open('tests/test_api.py', 'r') as f:
    c = f.read()

c = c.replace('"value_24h": 10.1', '"value_24h": 10.0')

with open('tests/test_api.py', 'w') as f:
    f.write(c)
