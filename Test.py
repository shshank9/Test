import os
import subprocess
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

    def run_gradle_dependencies(self, repo_path: str) -> str:
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

    def analyze_all_repositories(self) -> Dict[str, str]:
        """Analyze dependencies for all repositories."""
        self.clone_repositories()
        
        results = {}
        for repo_name in self.repos:
            repo_path = os.path.join(self.base_dir, repo_name)
            print(f"\nAnalyzing dependencies for {repo_name}...")
            results[repo_name] = self.run_gradle_dependencies(repo_path)
            
        return results

    def save_results(self, results: Dict[str, str], output_file: str = "dependencies.txt") -> None:
        """Save the dependency results to a text file in an indented format."""
        with open(output_file, 'w') as f:
            for repo_name, dependencies in results.items():
                f.write(f"\n{'='*80}\n")
                f.write(f"Repository: {repo_name}\n")
                f.write(f"{'='*80}\n\n")
                f.write(dependencies)
                f.write("\n")

def main():
    analyzer = OpenSearchDependencyAnalyzer()
    results = analyzer.analyze_all_repositories()
    analyzer.save_results(results)

if __name__ == "__main__":
    main()
