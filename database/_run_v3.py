#!/usr/bin/env python3
"""Run V3 generator with specified path count"""
import sys, os, json, random
from pathlib import Path
from dataclasses import asdict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import career_generator_v3 as cg

# Parse args
max_paths = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
output_dir = sys.argv[2] if len(sys.argv) > 2 else "./career_graph_output_v3"

config = cg.GeneratorConfig(
    output_dir=output_dir,
    checkpoint_file="./career_checkpoint_v3.json",
    random_seed=42,
    max_total_paths=max_paths,
    max_nodes=2000000,
    max_edges=4000000,
    branch_probability=0.7,
    max_path_length=16,
)
random.seed(config.random_seed)
taxonomies = cg.Taxonomies()
validator = cg.TransitionValidator()
generator = cg.CareerGraphGenerator(config, taxonomies, validator)
generator.generate()

stats = {
    "total_nodes": generator.generated_nodes,
    "total_edges": generator.generated_edges,
    "total_paths": generator.path_counter,
    "max_requested": max_paths,
    "generated_at": str(datetime.now()),
}
stats_path = Path(output_dir) / "generation_stats.json"
with open(stats_path, "w") as f:
    json.dump(stats, f, indent=2, default=str)

print(f"\n=== RESULTS ===")
print(f"Requested paths: {max_paths}")
print(f"Generated paths: {generator.path_counter}")
print(f"Nodes: {generator.generated_nodes}")
print(f"Edges: {generator.generated_edges}")
print(f"Output: {output_dir}")
print(f"Stats: {stats_path}")
