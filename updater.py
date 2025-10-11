import subprocess
import os
import sys


def update_and_restart(repo_url, project_dir, service_name):
    """
    Downloads code from a GitHub repository, replaces the existing code, and restarts a service.

    Args:
        repo_url (str): The URL of the GitHub repository.
        project_dir (str): The local directory where the project is located.
        service_name (str): The name of the service to restart.
    """
    try:
        # 1. Navigate to the project directory
        os.chdir(project_dir)

        # 2. Fetch and reset to the latest changes from the remote repository
        print(f"Updating code from {repo_url}...")
        subprocess.run(["git", "fetch", "origin"], check=True)
        subprocess.run(
            ["git", "reset", "--hard", "origin/main"], check=True
        )  # Assuming 'main' is the main branch
        print("Code updated successfully.")

        # 3. Restart the service
        print(f"Restarting service: {service_name}...")
        subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)
        print(f"Service {service_name} restarted successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error during update or restart: {e}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"Error: Command not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


# Example usage (replace with your actual values):
# update_and_restart("https://github.com/yourusername/yourrepo.git", "/path/to/your/project", "your_service_name")
