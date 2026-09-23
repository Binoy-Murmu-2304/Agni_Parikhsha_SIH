import os
with open('agnipariksha/api/main.py', 'r') as f:
    c = f.read()

c = c.replace('qa_gen.generate_markdown', 'qa_gen.generate_card')
with open('agnipariksha/api/main.py', 'w') as f:
    f.write(c)

