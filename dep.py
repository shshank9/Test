def parse_dependency_line(line: str) -> tuple[str, str, int]:
    """Parse a dependency line to extract artifact, version, and nesting level.
    Example: '+--- org.opensearch:opensearch:2.18.0.0' -> ('org.opensearch:opensearch', '2.18.0.0', 0)
             '|   +--- org.jetbrains:annotations:13.0' -> ('org.jetbrains:annotations', '13.0', 1)"""
    line = line.strip()
    nesting_level = 0
    
    if line.startswith('|   +---'):
        nesting_level = 1
        line = line.replace('|   +---', '').strip()
    elif line.startswith('+---'):
        line = line.replace('+---', '').strip()
    else:
        return None, None, None
    
    # Split into artifact and version
    parts = line.split(':')
    if len(parts) < 3:
        return None, None, None
        
    artifact = ':'.join(parts[:-1])
    version = parts[-1]
    
    return artifact, version, nesting_level

def read_dependencies(file_path: str) -> list[tuple[str, str, int]]:
    """Read dependencies from a file and return list of (artifact, version, nesting_level) tuples."""
    dependencies = []
    with open(file_path, 'r') as f:
        for line in f:
            artifact, version, nesting_level = parse_dependency_line(line)
            if artifact and version is not None:
                dependencies.append((artifact, version, nesting_level))
    return dependencies

def create_flat_map(dependencies: list[tuple[str, str]]) -> dict[str, str]:
    """Create a flat map of artifact -> version."""
    return dict(dependencies)

def create_nested_map(dependencies: list[tuple[str, str]]) -> dict:
    """Create a nested map of group -> artifact -> version."""
    nested = {}
    for artifact, version in dependencies:
        group, name = artifact.split(':', 1)
        if group not in nested:
            nested[group] = {}
        nested[group][name] = version
    return nested

def write_dependencies(dependencies: list[tuple[str, str, int]], output_file: str) -> None:
    """Write dependencies back to a file in the original format."""
    with open(output_file, 'w') as f:
        for i, (artifact, version, level) in enumerate(dependencies):
            # Remove any (n) markers from version
            version = version.replace(' (n)', '')
            
            # First dependency starts with +---, others with |   +---
            prefix = "+--- " if i == 0 else "|   +--- "
            
            # Add proper indentation based on nesting level
            indent = "    " * (level - 1) if level > 1 else ""
            
            # Add vertical lines for nested dependencies
            if level > 1:
                prefix = "|   " * (level - 2) + "|   +--- "
            
            f.write(f"{indent}{prefix}{artifact}:{version}\n")

def extract_compile_classpath(content: str) -> str:
    """Extract compileClasspath section from dependencies output."""
    lines = content.split('\n')
    compile_classpath_lines = []
    in_compile_classpath = False
    
    for line in lines:
        if 'compileClasspath' in line:
            in_compile_classpath = True
            continue
        elif in_compile_classpath and line.strip() and not line.startswith('\\'):
            if 'runtimeClasspath' in line or 'testCompileClasspath' in line:
                break
            compile_classpath_lines.append(line)
    
    return '\n'.join(compile_classpath_lines)

def process_dependencies_file(file_path: str) -> tuple[list[tuple[str, str, int]], dict[str, str], dict]:
    """Process a dependencies file and return dependencies in different formats."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract compileClasspath section
    compile_classpath = extract_compile_classpath(content)
    
    # Parse dependencies
    dependencies = []
    for line in compile_classpath.split('\n'):
        artifact, version, nesting_level = parse_dependency_line(line)
        if artifact and version is not None:
            dependencies.append((artifact, version, nesting_level))
    
    # Create maps (using only the first occurrence of each dependency)
    flat_map = {}
    nested_map = {}
    
    for artifact, version, _ in dependencies:
        if artifact not in flat_map:
            flat_map[artifact] = version
            group, name = artifact.split(':', 1)
            if group not in nested_map:
                nested_map[group] = {}
            nested_map[group][name] = version
    
    return dependencies, flat_map, nested_map

def test_dependency_processing():
    """Test the dependency processing functions."""
    test_file = "dependencies/alerting_dependencies.txt"
    output_file = "dependencies/test_output.txt"
    
    print("\nTesting dependency processing...")
    print(f"Processing file: {test_file}")
    
    # Process dependencies
    deps, flat_map, nested_map = process_dependencies_file(test_file)
    
    # Write dependencies in Gradle format
    write_dependencies(deps, output_file)
    print(f"\nWrote dependencies to: {output_file}")
    
    # Print results
    print("\nDependencies list:")
    for artifact, version, nesting_level in deps:
        print(f"{'  ' * nesting_level}{artifact}:{version}")
    
    print("\nFlat map:")
    for artifact, version in flat_map.items():
        print(f"{artifact}:{version}")
    
    print("\nNested map:")
    for group, artifacts in nested_map.items():
        print(f"\n{group}:")
        for name, version in artifacts.items():
            print(f"  {name}:{version}")

if __name__ == "__main__":
    test_dependency_processing() 
