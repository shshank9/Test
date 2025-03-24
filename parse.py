import re
import json

def parse_dependency_tree(lines):
    """Parses the dependency tree into a nested dictionary and a flat dictionary."""
    nested_map = {}
    flat_map = {}
    stack = [(0, nested_map)]  # (Indent Level, Parent Dict)
    dependency_references = {}

    for line in lines:
        match = re.match(r"(\| +)?(\+---|\---) (.+)", line)
        if match:
            indent = len(match.group(1) or '')  # Count leading "|  " indentation
            dependency = match.group(3).strip()

            # Handle dependencies marked with (*)
            if dependency.endswith("(*)"):
                dependency = dependency[:-4].strip()
                if dependency in dependency_references:
                    parent = stack[-1][1]
                    parent[dependency] = dependency_references[dependency]
                    continue  # Avoid duplicating existing dependencies

            # Find the correct parent based on indentation level
            while stack and stack[-1][0] >= indent:
                stack.pop()

            parent = stack[-1][1]  # Get the correct parent
            parent[dependency] = {}  # Add dependency as nested dict

            # Store in flat dictionary
            flat_map[dependency] = None

            # Store reference for (*) dependencies
            dependency_references[dependency] = parent[dependency]

            # Push to stack for tracking nested levels
            stack.append((indent, parent[dependency]))

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
    flatmap_filename = "flat_map.json"
    nested_filename = "nested_map.json"

    # Read input from file
    with open(input_filename, "r", encoding="utf-8") as file:
        lines = file.readlines()

    # Process input
    nested_map, flat_map = parse_dependency_tree(lines)

    # Write output back to file (preserving structure)
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write("\n".join(write_dependency_tree(nested_map)))

    # Write flat map as JSON
    with open(flatmap_filename, "w", encoding="utf-8") as file:
        json.dump(flat_map, file, indent=4)

    # Write nested map as JSON
    with open(nested_filename, "w", encoding="utf-8") as file:
        json.dump(nested_map, file, indent=4)

    print(f"Processed successfully! Output written to {output_filename}, {flatmap_filename}, and {nested_filename}")

if __name__ == "__main__":
    main()
