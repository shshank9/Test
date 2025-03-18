import os
import subprocess
import json
from typing import Dict, List, Optional

class OpenSearchDependencyAnalyzer:
    def __init__(self, base_dir: str = "opensearch-repos"):
        self.base_dir = base_dir
        self.repos = {
            "OpenSearch": "https://github.com/opensearch-project/OpenSearch.git",
            "alerting": "https://github.com/opensearch-project/alerting.git"
        }
        
    def clone_repositories(self) -> None:
        """Clone all required repositories if they don't exist."""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
            
        for repo_name, repo_url in self.repos.items():
            repo_path = os.path.join(self.base_dir, repo_name)
            if not os.path.exists(repo_path):
                print(f"Cloning {repo_name}...")
                subprocess.run(["git", "clone", repo_url, repo_path], check=True)
            else:
                print(f"Repository {repo_name} already exists, skipping clone.")

    def run_gradle_dependencies(self, repo_path: str) -> Dict:
        """Run Gradle dependencies task and parse the output."""
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
            
            # Parse the output
            dependencies = self._parse_gradle_output(result.stdout)
            
            # Change back to original directory
            os.chdir(original_dir)
            return dependencies
            
        except subprocess.CalledProcessError as e:
            print(f"Error running Gradle in {repo_path}: {e}")
            return {}
        finally:
            os.chdir(original_dir)

    def _parse_gradle_output(self, output: str) -> Dict:
        """Parse the Gradle dependencies output into a structured format."""
        dependencies = {
            "runtime": [],
            "compile": []
        }
        
        current_config = None
        for line in output.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if "runtimeClasspath" in line:
                current_config = "runtime"
            elif "compileClasspath" in line:
                current_config = "compile"
            elif current_config and line.startswith("---"):
                # Skip separator lines
                continue
            elif current_config and line and not line.startswith("\\"):
                # Add dependency line
                dependencies[current_config].append(line)
                
        return dependencies

    def analyze_all_repositories(self) -> Dict:
        """Analyze dependencies for all repositories."""
        self.clone_repositories()
        
        results = {}
        for repo_name in self.repos:
            repo_path = os.path.join(self.base_dir, repo_name)
            print(f"\nAnalyzing dependencies for {repo_name}...")
            results[repo_name] = self.run_gradle_dependencies(repo_path)
            
        return results

    def save_results(self, results: Dict, output_file: str = "dependencies.json") -> None:
        """Save the dependency results to a JSON file."""
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {output_file}")

def main():
    analyzer = OpenSearchDependencyAnalyzer()
    results = analyzer.analyze_all_repositories()
    analyzer.save_results(results)

if __name__ == "__main__":
    main()
