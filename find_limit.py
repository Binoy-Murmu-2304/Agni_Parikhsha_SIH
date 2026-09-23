import os
for root, dirs, files in os.walk('.'):
    if '.git' in root or 'node_modules' in root or '__pycache__' in root or 'venv' in root: continue
    for file in files:
        if file.endswith('.md') or file.endswith('.js') or file.endswith('.py') or file.endswith('.json'):
            try:
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    content = f.read()
                    if '0 detections' in content or '0%' in content or 'dead' in content:
                        print(f"File {file} matched")
            except: pass
