#!/usr/bin/env python3
"""Validate the generated V3 output thoroughly."""
import json, csv, yaml, os, sys
from pathlib import Path

d = r'C:\xampp\htdocs\Antigravity-Pro\nearby-hiring-project\Base-India-Career-Project\career_graph_output_v3'
errors = []
warnings = []

print("=== VALIDATION REPORT ===")

# 1. Read generation stats
with open(os.path.join(d, 'generation_stats.json')) as f:
    stats = json.load(f)
print(f"Stats: {stats['total_paths']} paths, {stats['total_nodes']} nodes, {stats['total_edges']} edges")

# 2. Validate JSONL files
for fname in ['nodes.jsonl', 'edges.jsonl']:
    path = os.path.join(d, fname)
    ids = set()
    line_count = 0
    dupes = 0
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line_count += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"{fname} line {line_count}: JSON decode error: {e}")
                continue
            # Check ID field
            id_field = 'node_id' if 'node_id' in obj else 'edge_id' if 'edge_id' in obj else None
            if id_field is None:
                # try source_id for edges
                id_field = 'source_id'
            if id_field == 'node_id' and obj.get('node_id') in ids:
                dupes += 1
                if dupes <= 3:
                    errors.append(f"{fname}: Duplicate {id_field} '{obj['node_id']}' at line {line_count}")
            elif id_field == 'node_id':
                ids.add(obj['node_id'])
            # Check required fields for first 5 entries
            if line_count <= 5:
                if fname == 'nodes.jsonl':
                    required = ['node_id', 'node_type', 'title']
                    missing = [r for r in required if r not in obj]
                    if missing:
                        errors.append(f"{fname} line {line_count}: missing fields {missing}")
                if fname == 'edges.jsonl':
                    required = ['source_id', 'destination_id', 'relationship_type']
                    missing = [r for r in required if r not in obj]
                    if missing:
                        errors.append(f"{fname} line {line_count}: missing fields {missing}")
    print(f"  {fname}: {line_count} entries, {len(ids)} unique IDs, {dupes} duplicates")
    if dupes > 3:
        print(f"    (showing first 3 of {dupes} duplicates above)")

# 3. Validate JSON files
for fname in ['nodes.json', 'edges.json']:
    path = os.path.join(d, fname)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"  {fname}: valid JSON, {len(data)} entries")
    except json.JSONDecodeError as e:
        errors.append(f"{fname}: Invalid JSON: {e}")

# 4. Validate CSV files
for fname in ['nodes.csv', 'edges.csv']:
    path = os.path.join(d, fname)
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        print(f"  {fname}: {len(rows)} rows, headers: {reader.fieldnames[:5]}...")

# 5. Validate YAML files
for fname in ['nodes.yaml', 'edges.yaml']:
    path = os.path.join(d, fname)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        print(f"  {fname}: valid YAML, documents loaded")
    except yaml.YAMLError as e:
        errors.append(f"{fname}: YAML error: {e}")

# 6. Validate career_paths.txt format
path = os.path.join(d, 'career_paths.txt')
line_count = 0
path_count = 0
with open(path, 'r', encoding='utf-8') as f:
    for line in f:
        line_count += 1
        if line.strip().startswith('Path #'):
            path_count += 1
print(f"  career_paths.txt: {line_count} lines, {path_count} paths")

# 7. Edge referential integrity
print("\n  Checking edge referential integrity...")
node_ids = set()
with open(os.path.join(d, 'nodes.jsonl'), 'r', encoding='utf-8') as f:
    for line in f:
        node = json.loads(line)
        node_ids.add(node['node_id'])

bad_edges = 0
with open(os.path.join(d, 'edges.jsonl'), 'r', encoding='utf-8') as f:
    for line in f:
        edge = json.loads(line)
        if edge['source_id'] not in node_ids:
            bad_edges += 1
            if bad_edges <= 3:
                errors.append(f"Edge source '{edge['source_id']}' not found in nodes")
        if edge['destination_id'] not in node_ids:
            bad_edges += 1
            if bad_edges <= 3:
                errors.append(f"Edge dest '{edge['destination_id']}' not found in nodes")
print(f"  Referential integrity: {bad_edges} bad edges out of {stats['total_edges']}")

# 8. Sample nodes
print("\n  Sample nodes:")
with open(os.path.join(d, 'nodes.jsonl'), 'r', encoding='utf-8') as f:
    lines = f.readlines()
import random
random.seed(42)
samples = random.sample(lines, min(10, len(lines)))
for s in samples:
    n = json.loads(s)
    print(f"    {n['node_id'][:12]}... | {n.get('node_type','?'):15s} | {n.get('title','?'):40s}")

# Summary
print(f"\n=== SUMMARY ===")
if errors:
    print(f"ERRORS ({len(errors)}):")
    for e in errors[:10]:
        print(f"  - {e}")
else:
    print("  No errors found!")
if warnings:
    print(f"Warnings: {len(warnings)}")

print(f"\nAll checks passed: {len(errors) == 0}")
