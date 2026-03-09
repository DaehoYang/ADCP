import os
import subprocess
import sys
from pathlib import Path

def setup_ssh():
    ssh_dir = Path.home() / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)
    
    key_path = ssh_dir / "class_key"
    pub_key_path = ssh_dir / "class_key.pub"
    
    print(f"[*] Setting up SSH keys in {ssh_dir}...")
    
    # 1. Generate SSH key if it doesn't exist
    if not key_path.exists():
        print("[-] Key not found. Generating new ed25519 SSH key...")
        try:
            subprocess.run([
                "ssh-keygen", "-t", "ed25519", "-f", str(key_path), "-N", "", "-q"
            ], check=True)
            print("[+] SSH key generated successfully.")
        except subprocess.CalledProcessError:
            print("[!] Failed to generate SSH key. Do you have ssh-keygen installed?")
            sys.exit(1)
    else:
        print("[+] SSH key already exists.")

    # 2. Add config to ~/.ssh/config
    config_path = ssh_dir / "config"
    
    # Use forward slashes or escaped backslashes for IdentityFile to avoid issues
    key_path_str = str(key_path.resolve()).replace('\\', '/')
    
    config_entry = f"""
Host class
    HostName 127.0.0.1
    User student
    Port 22222
    IdentityFile {key_path_str}
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    TCPKeepAlive yes
    ServerAliveInterval 60
"""
    
    print(f"[*] Updating SSH config at {config_path}...")
    
    config_content = ""
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config_content = f.read()
            
    if "Host class\n" in config_content or "Host class\r\n" in config_content or config_content.endswith("Host class"):
        print("[!] 'Host class' already exists in your ~/.ssh/config. Skipping config injection.")
        print("[!] If connection fails, please ensure your config looks like this:")
        print(config_entry)
        print("[!] Also ensure you have deleted any old IdentityFile from previous setups.")
    else:
        with open(config_path, "a", encoding="utf-8") as f:
            # Ensure we start on a new line
            if config_content and not config_content.endswith("\n"):
                f.write("\n")
            f.write(config_entry)
        print("[+] SSH config updated successfully.")

    print("\n[+] Setup complete! You can now start the environment and connect using:")
    print("    docker compose -f environment/docker-compose.yml up -d --build")
    print("    ssh class")

if __name__ == "__main__":
    setup_ssh()
