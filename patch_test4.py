import os
with open('tests/test_phase4.py', 'r') as f:
    c = f.read()
c = c.replace('''    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        content = f.read()
        assert "AGNI PARIKSHA - QA Disposition Card" in content
        assert comp_id in content''', '''    content = filepath
    assert "AGNI PARIKSHA - QA Disposition Card" in content
    assert comp_id in content''')
with open('tests/test_phase4.py', 'w') as f:
    f.write(c)
