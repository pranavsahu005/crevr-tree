#!/usr/bin/env python3
"""Run career_generator_v3.py with scaled parameters"""
import sys
import os
import json
import random
from pathlib import Path
from dataclasses import asdict
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import career_generator_v3 as cgv3

# Fix checkpoint random_state serialization issue
original_load = cgv3.CheckpointManager.load
def patched_load(self, tracker):
    if self.path.exists():
        with open(self.path) as f:
            self.state = json.load(f)
        rs_raw = self.state["random_state"]
        rs_list = list(rs_raw)
        if len(rs_list) >= 2 and isinstance(rs_list[1], list):
            rs_list[1] = tuple(rs_list[1])
        random.setstate(tuple(rs_list))
        if not tracker._is_bloom:
            for s in self.state.get("dedup_signatures", []):
                tracker.add(s)
        print(f"Resumed: {self.state['generated_nodes_count']}N {self.state['generated_edges_count']}E path#{self.state['path_counter']}")
        return (self.state["generated_nodes_count"], self.state["generated_edges_count"], self.state["path_counter"])
    return 0, 0, 0
cgv3.CheckpointManager.load = patched_load

# Also fix save to random_state tuple issue
original_save = cgv3.CheckpointManager.save
def patched_save(self, tracker, nc, ec, pc):
    self.state.update({"generated_nodes_count": nc, "generated_edges_count": ec, "path_counter": pc, "random_state": list(random.getstate())})
    if not tracker._is_bloom:
        self.state["dedup_signatures"] = list(getattr(tracker, "_set", set()))
    self.path.parent.mkdir(parents=True, exist_ok=True)
    with open(self.path, "w") as f:
        json.dump(self.state, f, default=str, indent=2)
cgv3.CheckpointManager.save = patched_save

config = cgv3.GeneratorConfig(
    output_dir="./career_graph_output_v3",
    checkpoint_file="./career_checkpoint_v3.json",
    random_seed=42,
    max_total_paths=5000,
    max_nodes=500000,
    max_edges=1000000,
    branch_probability=0.7,
    max_path_length=16,
)
random.seed(config.random_seed)
taxonomies = cgv3.Taxonomies()
validator = cgv3.TransitionValidator()
generator = cgv3.CareerGraphGenerator(config, taxonomies, validator)
generator.generate()

stats = {
    "total_nodes": generator.generated_nodes,
    "total_edges": generator.generated_edges,
    "total_paths": generator.path_counter,
    "generated_at": str(datetime.now()),
}
stats_path = Path(config.output_dir) / "generation_stats.json"
with open(stats_path, "w") as f:
    json.dump(stats, f, indent=2, default=str)
print(f"\n=== RESULTS (5k test) ===")
print(f"Paths: {generator.path_counter}")
print(f"Nodes: {generator.generated_nodes}")
print(f"Edges: {generator.generated_edges}")
