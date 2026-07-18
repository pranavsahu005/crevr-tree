#!/usr/bin/env python3
"""Validation script for the Career Knowledge Graph output."""
import json
import csv
import os
import random
import yaml

OUTPUT_DIR = "./career_graph_output"

def main():
    random.seed(42)
    errors = []
    warnings = []

    expected_files = [
        "nodes.jsonl", "edges.jsonl",
        "nodes.json", "edges.json",
        "nodes.csv", "edges.csv",
        "nodes.yaml", "edges.yaml",
        "career_paths.txt"
    ]
    print("=" * 60)
    print("STEP 1: File existence and size check")
    print("=" * 60)
    for fname in expected_files:
        fpath = os.path.join(OUTPUT_DIR, fname)
        if os.path.exists(fpath):
            size = os.path.getsize(fpath)
            status = "OK" if size > 0 else "EMPTY!"
            if size == 0:
                errors.append(f"{fname} is empty")
            print(f"  {fname}: {size:>10} bytes  [{status}]")
        else:
            errors.append(f"{fname} does not exist")
            print(f"  {fname}: MISSING!")

    print("\n" + "=" * 60)
    print("STEP 2: JSON/JSONL validation")
    print("=" * 60)
    with open(os.path.join(OUTPUT_DIR, "nodes.jsonl"), "r", encoding="utf-8") as f:
        all_nodes = [json.loads(line) for line in f if line.strip()]
    with open(os.path.join(OUTPUT_DIR, "edges.jsonl"), "r", encoding="utf-8") as f:
        all_edges = [json.loads(line) for line in f if line.strip()]
    print(f"  nodes.jsonl: {len(all_nodes)} valid records")
    print(f"  edges.jsonl: {len(all_edges)} valid records")
    for entity, records in [("nodes", all_nodes), ("edges", all_edges)]:
        json_path = os.path.join(OUTPUT_DIR, f"{entity}.json")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                json_records = json.load(f)
            print(f"  {entity}.json: {len(json_records)} records (JSON array)")
            if len(json_records) != len(records):
                warnings.append(f"{entity}.json has {len(json_records)} vs {len(records)} in JSONL")
        except json.JSONDecodeError as e:
            errors.append(f"{entity}.json: invalid JSON: {e}")

    print("\n" + "=" * 60)
    print("STEP 3: CSV validation")
    print("=" * 60)
    for entity in ["nodes", "edges"]:
        csv_path = os.path.join(OUTPUT_DIR, f"{entity}.csv")
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            row_count = sum(1 for _ in reader)
        print(f"  {entity}.csv: {row_count} rows, {len(headers)} columns")

    print("\n" + "=" * 60)
    print("STEP 4: YAML validation")
    print("=" * 60)
    for entity in ["nodes", "edges"]:
        yaml_path = os.path.join(OUTPUT_DIR, f"{entity}.yaml")
        with open(yaml_path, "r", encoding="utf-8") as f:
            docs = list(yaml.safe_load_all(f))
        print(f"  {entity}.yaml: loaded {len(docs)} YAML document(s)")

    print("\n" + "=" * 60)
    print("STEP 5: career_paths.txt validation")
    print("=" * 60)
    with open(os.path.join(OUTPUT_DIR, "career_paths.txt"), "r", encoding="utf-8") as f:
        content = f.read()
    paths = [p.strip() for p in content.split("---") if p.strip()]
    print(f"  career_paths.txt: {len(paths)} career paths")
    if paths:
        sample_path = paths[0][:120].encode("ascii", "replace").decode("ascii")
        print(f"  Sample: {sample_path}...")

    print("\n" + "=" * 60)
    print("STEP 6: Sample 10 random nodes - field validation")
    print("=" * 60)
    required_node_fields = ["node_id", "node_type", "title"]
    sample_nodes = random.sample(all_nodes, min(10, len(all_nodes)))
    for i, node in enumerate(sample_nodes):
        has_all = all(f in node for f in required_node_fields)
        title = node.get("title", "N/A")
        ntype = node.get("node_type", "N/A")
        safe_title = str(title).encode("ascii", "replace").decode("ascii")
        safe_ntype = str(ntype).encode("ascii", "replace").decode("ascii")
        print(f"  Node {i+1}: [{safe_ntype}] {safe_title} - fields OK: {has_all}")
        if not has_all:
            missing = [f for f in required_node_fields if f not in node]
            errors.append(f"Node missing fields: {missing}")

    print("\n" + "=" * 60)
    print("STEP 7: Sample 10 random edges - field validation")
    print("=" * 60)
    required_edge_fields = ["source_id", "destination_id", "relationship_type"]
    sample_edges = random.sample(all_edges, min(10, len(all_edges)))
    for i, edge in enumerate(sample_edges):
        has_all = all(f in edge for f in required_edge_fields)
        print(f"  Edge {i+1}: {edge.get('relationship_type', 'N/A')} - fields OK: {has_all}")
        if not has_all:
            missing = [f for f in required_edge_fields if f not in edge]
            errors.append(f"Edge missing fields: {missing}")

    print("\n" + "=" * 60)
    print("STEP 8: Duplicate ID check")
    print("=" * 60)
    node_ids = [n["node_id"] for n in all_nodes]
    unique_node_ids = set(node_ids)
    node_dups = len(node_ids) - len(unique_node_ids)
    print(f"  Nodes: {len(node_ids)} total, {len(unique_node_ids)} unique, {node_dups} duplicates")
    if node_dups > 0:
        errors.append(f"{node_dups} duplicate node IDs found")

    edge_sigs = [f'{e["source_id"]}|{e["destination_id"]}|{e["relationship_type"]}' for e in all_edges]
    unique_edge_sigs = set(edge_sigs)
    edge_dups = len(edge_sigs) - len(unique_edge_sigs)
    print(f"  Edges: {len(edge_sigs)} total, {len(unique_edge_sigs)} unique, {edge_dups} duplicates")
    if edge_dups > 0:
        errors.append(f"{edge_dups} duplicate edge signatures found")

    print("\n" + "=" * 60)
    print("STEP 9: Relationship integrity")
    print("=" * 60)
    node_id_set = set(node_ids)
    broken_sources = []
    broken_dests = []
    for edge in all_edges:
        if edge["source_id"] not in node_id_set:
            broken_sources.append(edge["source_id"])
        if edge["destination_id"] not in node_id_set:
            broken_dests.append(edge["destination_id"])
    broken_total = len(broken_sources) + len(broken_dests)
    print(f"  Broken source refs: {len(broken_sources)}")
    print(f"  Broken dest refs:   {len(broken_dests)}")
    if broken_total > 0:
        warnings.append(f"{broken_total} broken edge references (edges may reference dynamically-created nodes not in output)")
        # Show some examples
        for sid in broken_sources[:3]:
            print(f"    Missing source: {sid}")
        for did in broken_dests[:3]:
            print(f"    Missing dest:   {did}")

    print("\n" + "=" * 60)
    print("STEP 10: Checkpoint file validation")
    print("=" * 60)
    cp_path = "./career_checkpoint.json"
    if os.path.exists(cp_path):
        with open(cp_path, "r") as f:
            cp = json.load(f)
        print(f"  Checkpoint exists: nodes={cp.get('generated_nodes_count')}, edges={cp.get('generated_edges_count')}, paths={cp.get('path_counter')}")
    else:
        warnings.append("Checkpoint file not found")

    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"  Nodes generated:   {len(all_nodes)}")
    print(f"  Edges generated:   {len(all_edges)}")
    print(f"  Career paths:      {len(paths)}")
    total_size = sum(os.path.getsize(os.path.join(OUTPUT_DIR, f)) for f in os.listdir(OUTPUT_DIR))
    print(f"  Output dir size:   {total_size:,} bytes ({total_size/1024:.1f} KB)")
    print(f"  Errors:            {len(errors)}")
    print(f"  Warnings:          {len(warnings)}")
    if errors:
        print("\n  ERRORS:")
        for e in errors:
            print(f"    - {e}")
    if warnings:
        print("\n  WARNINGS:")
        for w in warnings:
            print(f"    - {w}")
    if not errors:
        print("\n  ALL CHECKS PASSED!")
    else:
        print("\n  SOME CHECKS FAILED - see errors above.")

if __name__ == "__main__":
    main()
