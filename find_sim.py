import os
for root, dirs, files in os.walk('.'):
    if '.git' in root or 'node_modules' in root or '__pycache__' in root or 'venv' in root: continue
    for file in files:
        if file.endswith('.md') or file.endswith('.js'):
            try:
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'AGNI-SIM' in content:
                        print(f"FOUND AGNI-SIM in {os.path.join(root, file)}")
            except: pass
