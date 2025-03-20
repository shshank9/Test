import re

def parse_dependency_tree(lines):
    """Parses the dependency tree into a nested dictionary and a flat dictionary."""
    nested_map = {}
    flat_map = {}

    stack = []  # Track indentation levels
    parent = nested_map

    for line in lines:
        match = re.match(r"(\| +)?(\+---|\---) (.+)", line)
        if match:
            indent = len(match.group(1) or '')  # Count leading "|  " indentation
            dependency = match.group(3).strip()

            # Maintain proper hierarchy based on indentation
            while stack and stack[-1][0] >= indent:
                stack.pop()

            if stack:
                parent = stack[-1][1]  # Parent dictionary

            parent[dependency] = {}  # Add dependency
            flat_map[dependency] = None  # Store in flat dictionary
            stack.append((indent, parent[dependency]))  # Push current dependency

    return nested_map, flat_map

def write_dependency_tree(nested_map, indent=0):
    """Writes back the dependency tree in the exact input format."""
    output_lines = []
    prefix = "|   " * indent + "+--- " if indent > 0 else "+--- "

    for key, sub_map in nested_map.items():
        output_lines.append(prefix + key)
        output_lines.extend(write_dependency_tree(sub_map, indent + 1))

    return output_lines

def main():
    input_filename = "input.txt"
    output_filename = "output.txt"

    # Read input from file
    with open(input_filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Process input
    nested_map, flat_map = parse_dependency_tree(lines)

    # Write output back to file
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write("\n".join(write_dependency_tree(nested_map)))

    print("Processed successfully! Output written to", output_filename)

if __name__ == "__main__":
    main()
