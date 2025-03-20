import os
import subprocess
from typing import Dict, List, Optional
import re

def get_available_configurations(repo_path: str) -> List[str]:
    """Get list of available Gradle configurations."""
    try:
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        # Run Gradle to list configurations
        cmd = ["./gradlew", "configurations"]
        print(f"\nListing configurations in {repo_path}:")
        print(" ".join(cmd))
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse configurations from output
        configurations = []
        for line in result.stdout.split('\n'):
            if line.strip() and not line.startswith('>') and not line.startswith('\\'):
                config = line.strip()
                if config and not config.startswith('---'):
                    configurations.append(config)
        
        os.chdir(original_dir)
        return configurations
        
    except subprocess.CalledProcessError as e:
        print(f"\nError listing configurations in {repo_path}:")
        print(f"Command failed with exit code: {e.returncode}")
        print("\nCommand output:")
        print(e.stdout)
        print("\nError output:")
        print(e.stderr)
        return []
    finally:
        os.chdir(original_dir)

def is_plugin(repo_name: str) -> bool:
    """Check if the repository is a plugin."""
    # List of known plugins
    plugins = {
        "alerting", "anomaly-detection", "asynchronous-search", "cross-cluster-replication",
        "geospatial", "index-management", "job-scheduler", "knn", "ml-commons",
        "notifications", "observability", "performance-analyzer", "reports-scheduler",
        "security", "sql", "system-indices"
    }
    return repo_name in plugins

def fix_settings_gradle(repo_dir: str) -> None:
    """Fix settings.gradle by moving pluginManagement block to the top."""
    settings_file = os.path.join(repo_dir, "settings.gradle")
    if not os.path.exists(settings_file):
        return
        
    with open(settings_file, 'r') as f:
        content = f.read()
    
    # Extract pluginManagement block if it exists
    plugin_management = re.search(r'pluginManagement\s*{[^}]*}', content, re.DOTALL)
    if plugin_management:
        # Remove the pluginManagement block from its current position
        content = content.replace(plugin_management.group(0), '')
        # Add it to the top of the file
        content = plugin_management.group(0) + '\n\n' + content
        
        with open(settings_file, 'w') as f:
            f.write(content)

def clone_plugin(repo_name: str, version: str = "2.18.0.0") -> str:
    """Clone an OpenSearch plugin repository."""
    repo_url = f"https://github.com/opensearch-project/{repo_name}.git"
    repo_dir = repo_name
    
    if os.path.exists(repo_dir):
        print(f"Repository {repo_dir} already exists, skipping clone")
        return repo_dir
        
    print(f"Cloning {repo_name} plugin version {version}...")
    subprocess.run(["git", "clone", repo_url, repo_dir], check=True)
    
    # Checkout specific version
    os.chdir(repo_dir)
    subprocess.run(["git", "checkout", version], check=True)
    os.chdir("..")
    return repo_dir

def get_runtime_dependencies(repo_path: str, repo_name: str) -> str:
    """Get compile-time dependencies for the project."""
    try:
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        all_output = []
        
        # Project-specific configurations
        project_configs = {
            "alerting": {
                "use_project_prefix": True,  # Use :alerting:dependencies
                "project_name": "alerting"
            },
            "observability": {
                "use_project_prefix": False,  # Use just dependencies
                "project_name": "opensearch-observability"
            },
            "reporting": {
                "use_project_prefix": False,  # Use just dependencies
                "project_name": "opensearch-reports-scheduler"
            }
        }
        
        # Get project config
        config = project_configs.get(repo_name, {
            "use_project_prefix": False,
            "project_name": repo_name
        })
        
        # Build the command based on project config
        if config["use_project_prefix"]:
            cmd = ["./gradlew", f":{config['project_name']}:dependencies"]
        else:
            cmd = ["./gradlew", "dependencies"]
            
        print(f"\nExecuting command in {repo_path}:")
        print(" ".join(cmd))
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            all_output.append(f"\nCommand: {' '.join(cmd)}")
            all_output.append("=" * 80)
            all_output.append(result.stdout)
            
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code: {e.returncode}")
            print("Error output:")
            print(e.stderr)
        
        os.chdir(original_dir)
        return "\n".join(all_output)
        
    except Exception as e:
        print(f"\nUnexpected error in {repo_path}:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return ""
    finally:
        os.chdir(original_dir)

def run_gradle_dependencies(repo_path: str) -> str:
    """Run Gradle dependencies task and return the output."""
    try:
        # Change to the repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        all_output = []
        
        # Run just one focused command for dependencies
        cmd = ["./gradlew", "--refresh-dependencies", ":alerting:dependencies"]
        print(f"\nExecuting command in {repo_path}:")
        print(" ".join(cmd))
        
        try:
            # Run Gradle dependencies task
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            all_output.append(f"\nCommand: {' '.join(cmd)}")
            all_output.append("=" * 80)
            all_output.append(result.stdout)
            
        except subprocess.CalledProcessError as e:
            print(f"Command failed with exit code: {e.returncode}")
            print("Error output:")
            print(e.stderr)
        
        # Change back to original directory
        os.chdir(original_dir)
        return "\n".join(all_output)
        
    except Exception as e:
        print(f"\nUnexpected error in {repo_path}:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        return ""
    finally:
        os.chdir(original_dir)

def analyze_repository(repo_path: str, repo_name: str) -> str:
    """Analyze dependencies for a single repository."""
    print(f"\nAnalyzing dependencies for {repo_name}...")
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
            results[repo_name] = analyze_repository(repo_path, repo_name)
    
    return results

def save_results(output: str, repo_name: str, output_dir: str = "dependencies") -> None:
    """Save the compile-time dependency results to a text file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"{repo_name}_dependencies.txt")
    with open(output_file, 'w') as f:
        f.write(f"{repo_name.title()} Plugin Compile-Time Dependencies (version 2.18.0.0)\n")
        f.write(f"{'='*80}\n\n")
        f.write(output)
    print(f"Saved compile-time dependencies to {output_file}")

def main():
    # List of plugins to analyze
    plugins = ["alerting", "observability", "reporting"]
    version = "2.18.0.0"
    
    for plugin in plugins:
        print(f"\nAnalyzing {plugin} plugin...")
        
        # Clone the plugin
        repo_dir = clone_plugin(plugin, version)
        
        # Run dependency analysis
        output = get_runtime_dependencies(repo_dir, plugin)
        
        # Save results
        save_results(output, plugin)

if __name__ == "__main__":
    main()
