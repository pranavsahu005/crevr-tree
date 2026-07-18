#!/usr/bin/env python3
"""Final assembly of career_generator_v3.py from all part files."""
import os
import sys

d = r'C:\xampp\htdocs\Antigravity-Pro\nearby-hiring-project\Base-India-Career-Project'
out = os.path.join(d, 'career_generator_v3.py')

# Read base/assemble file to extract prefix
base_path = os.path.join(d, '_assemble.py')
with open(base_path, 'r', encoding='utf-8') as f:
    base = f.read()

# Find the prefix string - starts after "prefix = r'''" or "prefix = '''"
marker = "prefix = r'''" if "prefix = r'''" in base else "prefix = '''"
idx = base.find(marker)
if idx < 0:
    print("ERROR: prefix marker not found")
    sys.exit(1)

start = idx + len(marker)
# Find closing ''', look for ''' followed by newline and then (optional whitespace) parts =
end_marker = "'''"
end_idx = base.find(end_marker, start)
if end_idx < 0:
    print("ERROR: closing triple quotes not found")
    sys.exit(1)

prefix = base[start:end_idx]
print(f"Extracted prefix: {len(prefix)} bytes")

# Verify prefix ends with a newline
if not prefix.endswith('\n'):
    prefix += '\n'

# Part files to concatenate
part_files = [
    "taxonomies_part.py",
    "jobroles_part.py",
    "rest_taxonomies.py",
    "generator_logic.py",
]

# Assembly
total = 0
with open(out, 'w', encoding='utf-8') as o:
    o.write(prefix)
    total += len(prefix)
    for pf in part_files:
        p = os.path.join(d, pf)
        if os.path.exists(p):
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
            o.write('\n' + content)
            total += len(content) + 1
            print(f"  Added {pf}: {len(content)} bytes")
        else:
            print(f"  MISSING: {pf}")

print(f"\nTotal: {total} bytes written to {out}")

# Syntax check
try:
    compile(open(out, 'rb').read(), out, 'exec')
    print("Syntax: OK!")
except SyntaxError as e:
    print(f"\nSyntax ERROR at line {e.lineno}: {e.msg}")
    with open(out, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for i in range(max(0, e.lineno-3), min(len(lines), e.lineno+2)):
        print(f"  {i+1}: {lines[i].rstrip()}")
