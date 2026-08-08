"""
Patch for faust-streaming bug: tracing.py crashes with AttributeError
when parent.tracer is None during partition rebalance.
Detects the correct indentation dynamically.
"""

import pathlib

p = pathlib.Path("/usr/local/lib/python3.11/site-packages/faust/utils/tracing.py")
src = p.read_text()
lines = src.splitlines(keepends=True)
new_lines = []
patched = 0

for line in lines:
    stripped = line.lstrip()
    if stripped.startswith("child = parent.tracer.start_span("):
        indent = line[: len(line) - len(stripped)]
        new_lines.append(f"{indent}if parent.tracer is None:\n")
        new_lines.append(f"{indent}    return\n")
        patched += 1
    new_lines.append(line)

p.write_text("".join(new_lines))
print(f"Patch applied: {patched} occurrence(s) fixed.")
