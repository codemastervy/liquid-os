#!/usr/bin/env python3
"""Rewrite the screenshots section of README.md between the
LIQUID_OS_SCREENSHOTS markers with whatever PNGs currently exist in
docs/screenshots/. Called by the CI screenshot job after it captures frames.
"""
import re
from pathlib import Path

README = Path("README.md")
SHOT_DIR = Path("docs/screenshots")
START = "<!-- LIQUID_OS_SCREENSHOTS_START -->"
END = "<!-- LIQUID_OS_SCREENSHOTS_END -->"


def build_block():
    shots = sorted(SHOT_DIR.glob("*.png"))
    lines = [START]
    if shots:
        for shot in shots:
            lines.append(f"![{shot.name}](docs/screenshots/{shot.name})")
            lines.append("")
    else:
        lines.append(
            "_No screenshots captured this run -- see the screenshot job logs._"
        )
    lines.append(END)
    return "\n".join(lines)


def main():
    readme = README.read_text()
    block = build_block()
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    readme = pattern.sub(block, readme)
    README.write_text(readme)


if __name__ == "__main__":
    main()
