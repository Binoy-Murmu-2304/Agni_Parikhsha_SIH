import os
for root, dirs, files in os.walk('.'):
    if '.git' in root or 'node_modules' in root or '__pycache__' in root: continue
    for file in files:
        if file.endswith('.md') or file.endswith('.js') or file.endswith('.py'):
            try:
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '0%' in content or 'AGNI-SIM' in content or 'dead' in content:
                        print(f"Found something in {os.path.join(root, file)}")
            except: pass
