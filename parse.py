import json
import re

def parse_dependency_tree(lines):
    """Parses the indented dependency tree into a nested dictionary."""
    stack = []
    root = {}
    current = root
    indent_map = {}

    for line in lines:
        match = re.match(r'([| ]*)([+\\\-]+) (.+)', line)
        if not match:
            continue

        indent, _, dep = match.groups()
        level = indent.count("|")
        package, version = dep.rsplit(":", 1) if ":" in dep else (dep, "")
        
        node = {"version": version, "dependencies": {}, "original": line}

        if level == 0:
            root[package] = node
            stack = [(package, node)]
        else:
            while len(stack) > level:
                stack.pop()

            parent_name, parent_node = stack[-1]
            parent_node["dependencies"][package] = node
            stack.append((package, node))

    return root

def flatten_dependencies(nested_map, parent=""):
    """Flattens a nested dictionary into a key-value dictionary."""
    flat_map = {}

    def flatten_helper(subtree, path):
        for key, value in subtree.items():
            current_path = f"{path}/{key}" if path else key
            flat_map[current_path] = value["version"]
            flatten_helper(value["dependencies"], current_path)

    flatten_helper(nested_map, parent)
    return flat_map

def write_dependency_tree(nested_map):
    """Writes the nested dependency map back exactly as the input format."""
    output = []

    def write_helper(subtree):
        for key, value in subtree.items():
            output.append(value["original"])
            write_helper(value["dependencies"])

    write_helper(nested_map)
    return "\n".join(output)

# Sample input (replace this with reading from a file if needed)
input_text = """
+--- org.opensearch:opensearch:2.18.0
|    +--- org.opensearch:opensearch-common:2.18.0
|    +--- org.opensearch:opensearch-core:2.18.0
|    |    +--- org.opensearch:opensearch-common:2.18.0
|    |    +--- com.fasterxml.jackson.core:jackson-core:2.17.2
"""

# Convert input text to lines
lines = input_text.strip().split("\n")

# Parse into nested dictionary
nested_map = parse_dependency_tree(lines)

# Convert to flat map
flat_map = flatten_dependencies(nested_map)

# Convert back to original format
output_text = write_dependency_tree(nested_map)

# Print results
print("Nested Map (JSON format):")
print(json.dumps(nested_map, indent=2))

print("\nFlat Map:")
print(json.dumps(flat_map, indent=2))

print("\nReconstructed Output:")
print(output_text)
