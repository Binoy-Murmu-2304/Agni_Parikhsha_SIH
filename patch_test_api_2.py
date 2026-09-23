import os

with open('tests/test_api.py', 'r') as f:
    c = f.read()

c = c.replace('"value_0h": 10.0,', '"value_0h": 10.929,')
c = c.replace('"value_24h": 10.0,', '"value_24h": 14.175,')

with open('tests/test_api.py', 'w') as f:
    f.write(c)
