#!/usr/bin/python3

import argparse
import os
import time
import subprocess
import sys
import threading
import colorama
from colorama import Fore, Style

colorama.init()

def banner():
    print("""

        _                                                _
  /\/\ (_)_ __ _ __ ___  _ __ /\/\   __ _ _ ____   _____| |
 /    \| | '__| '__/ _ \| '__/    \ / _` | '__\ \ / / _ \ |
/ /\/\ \ | |  | | | (_) | | / /\/\ \ (_| | |   \ V /  __/ |
\/    \/_|_|  |_|  \___/|_| \/    \/\__,_|_|    \_/ \___|_|
\n""")

def print_developer_details():
    print(
        f"{Fore.YELLOW}{Style.BRIGHT}{'='*50}\n"
        f"{'Website Cloner Script':^50}\n"
        f"{'Developer: Dooms D4y':^50}\n"
        f"{'Contact:kakashimodieshi@gmail.com':^50}\n"
        f"{'Version: 1.0':^50}\n"
        f"{'='*50}{Style.RESET_ALL}\n"
    )
banner()
print_developer_details()

DEFAULT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
DEFAULT_RETRIES = 3
DEFAULT_TIMEOUT = 30

def validate_directory(directory):
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except OSError as e:
        print(f"{Fore.RED}[x] Error creating directory: {e}{Style.RESET_ALL}")
        return False

def clone_website(url, user_agent, directory, retries, timeout, log_file, custom_headers, host_locally):
    if not validate_directory(directory):
        return

    print(f"{Fore.YELLOW}[+] Directory exists or created successfully.\n{Style.RESET_ALL}")
    time.sleep(1)

    log_fd = open(log_file, 'a') if log_file else sys.stdout

    print(f"{Fore.YELLOW}[*] Cloning in progress...{Style.RESET_ALL}")

    headers = f'--header="User-Agent: {user_agent}"'
    if custom_headers:
        headers += f' --header="{custom_headers}"'

    # Cloning the website using wget with additional options
    command = (
        f'wget --mirror --convert-links --adjust-extension {headers} '
        f'--tries={retries} --timeout={timeout} --waitretry=1 --random-wait --no-check-certificate '
        f'--recursive --level=inf  --page-requisites --no-parent --progress=bar:force --no-verbose {url} -P {directory}'
    )

    try:
        subprocess.run(command, shell=True, check=True, stdout=log_fd, stderr=log_fd)
        print(f"{Fore.GREEN}[√] Website cloned successfully!{Style.RESET_ALL}")

        if host_locally:
            local_url = start_local_server(directory)
            print(f"{Fore.YELLOW}[+] Website hosted locally. Visit: {local_url}{Style.RESET_ALL}\n")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}[x] Cloning was unsuccessful. Error: {e}{Style.RESET_ALL}")
    finally:
        if log_file:
            log_fd.close()

def start_local_server(directory):
    import http.server
    import socketserver

    port = 8000

    os.chdir(directory)
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        return f"http://localhost:{port}"

def main():
    parser = argparse.ArgumentParser(description='Website Cloner')
    parser.add_argument('-u', '--url', type=str, required=True, help='URL of the website to clone')
    parser.add_argument('-a', '--user_agent', type=str, default=DEFAULT_USER_AGENT, help='Custom user-agent')
    parser.add_argument('-d', '--directory', type=str, default=os.getcwd(), help='Directory to save the cloned website')
    parser.add_argument('-r', '--retries', type=int, default=DEFAULT_RETRIES, help='Number of retries')
    parser.add_argument('-t', '--timeout', type=int, default=DEFAULT_TIMEOUT, help='Timeout')
    parser.add_argument('-l', '--log_file', type=str, help='Log file to store the cloning process (optional)')
    parser.add_argument('-c', '--custom_headers', type=str, help='Custom headers for the request (optional)')
    parser.add_argument('--host_locally', action='store_true', help='Host the cloned website locally using Python HTTP server(optional)')
    args = parser.parse_args()

    # Ask for user confirmation
    choice = input(f"{Fore.YELLOW}[?] Do you want to start cloning? (y/n): {Style.RESET_ALL}\n")
    if choice.lower() != 'y':
        print(f"{Fore.CYAN}[-] Cloning canceled by user.{Style.RESET_ALL}")
        sys.exit()

    # Cloning the website using multiple threads
    clone_thread = threading.Thread(target=clone_website, args=(args.url, args.user_agent, args.directory, args.retries, args.timeout, args.log_file, args.custom_headers, args.host_locally))
    clone_thread.start()

if __name__ == '__main__':
    main()
