import os

with open('task.md', 'r') as f:
    c = f.read()

c = c.replace('[ ] Next.js Dashboard (dashboard/)', '[x] Next.js Dashboard (dashboard/)')
c = c.replace('[ ] PDF Engine (gnipariksha/api/)', '[x] PDF Engine (gnipariksha/qa_cards/)')
c = c.replace('[ ] Behavioral API Test', '[x] Behavioral API Test')

with open('task.md', 'w') as f:
    f.write(c)
