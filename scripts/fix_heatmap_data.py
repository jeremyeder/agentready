#!/usr/bin/env python3
"""Fix heatmap by removing duplicate attributes from successful batch assessment."""

import json
from pathlib import Path


def fix_duplicate_attributes():
    """Remove duplicate attribute findings from all-assessments.json."""
    input_file = Path(".agentready/batch/reports-20251124-160049/all-assessments.json")
    output_file = Path(
        ".agentready/batch/reports-20251124-160049/all-assessments-fixed.json"
    )

    print(f"Loading {input_file}...")
    with input_file.open() as f:
        data = json.load(f)

    total_removed = 0
    for result in data["results"]:
        assessment = result.get("assessment")
        if not assessment:
            continue

        # Track seen attributes and filter duplicates (keep first occurrence)
        seen_attrs = set()
        fixed_findings = []

        for finding in assessment["findings"]:
            attr_id = finding["attribute"]["id"]
            if attr_id in seen_attrs:
                total_removed += 1
                print(
                    f"  Removing duplicate: {attr_id} from "
                    f"{assessment['repository']['name']}"
                )
                continue
            seen_attrs.add(attr_id)
            fixed_findings.append(finding)

        # Update findings list
        assessment["findings"] = fixed_findings

        # Update counts
        assessment["attributes_assessed"] = len(fixed_findings)

    print(f"\n✓ Removed {total_removed} duplicate attribute findings")
    print(f"✓ Writing fixed data to {output_file}...")

    with output_file.open("w") as f:
        json.dump(data, f, indent=2)

    print(f"✓ Done! File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    fix_duplicate_attributes()
