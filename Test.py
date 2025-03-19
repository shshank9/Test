import os
import subprocess
from typing import Dict, List, Optional

def run_gradle_dependencies(repo_path: str) -> str:
    """Run Gradle dependencies task and return the output."""
    try:
        # Change to the repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        # Run Gradle dependencies task
        result = subprocess.run(
            ["./gradlew", "dependencies", "--configuration", "runtimeClasspath", "--configuration", "compileClasspath"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Change back to original directory
        os.chdir(original_dir)
        return result.stdout
        
    except subprocess.CalledProcessError as e:
        print(f"Error running Gradle in {repo_path}: {e}")
        return ""
    finally:
        os.chdir(original_dir)

def analyze_repository(repo_path: str) -> str:
    """Analyze dependencies for a single repository."""
    print(f"\nAnalyzing dependencies for {os.path.basename(repo_path)}...")
    return run_gradle_dependencies(repo_path)

def analyze_all_repositories(parent_dir: str, version: str) -> Dict[str, str]:
    """Analyze dependencies for all repositories in the specified directory structure."""
    java_repos_path = os.path.join(parent_dir, version, "java_repos")
    
    if not os.path.exists(java_repos_path):
        print(f"Error: Directory not found: {java_repos_path}")
        return {}
    
    results = {}
    for repo_name in os.listdir(java_repos_path):
        repo_path = os.path.join(java_repos_path, repo_name)
        if os.path.isdir(repo_path):
            results[repo_name] = analyze_repository(repo_path)
    
    return results

def save_results(results: Dict[str, str], output_dir: str = "dependencies") -> None:
    """Save the dependency results to separate text files for each repository."""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for repo_name, dependencies in results.items():
        output_file = os.path.join(output_dir, f"{repo_name}_dependencies.txt")
        with open(output_file, 'w') as f:
            f.write(f"Repository: {repo_name}\n")
            f.write(f"{'='*80}\n\n")
            f.write(dependencies)
        print(f"Saved dependencies for {repo_name} to {output_file}")

def main():
    # Example usage
    parent_dir = "path/to/parent/dir"  # Replace with actual path
    version = "2.11.0"  # Replace with actual version
    
    results = analyze_all_repositories(parent_dir, version)
    save_results(results)

if __name__ == "__main__":
    main()
