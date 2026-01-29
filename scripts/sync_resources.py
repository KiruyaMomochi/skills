#!/usr/bin/env nix
#!nix shell nixpkgs#python3 --command python3
import json
import os
import time
import urllib.request
import urllib.error
import sys
import subprocess
import shutil
import tempfile
import re

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def log(message, color=RESET):
    print(f"{color}{message}{RESET}")

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def download_file(url, target_path, retries=3, delay=2):
    log(f"Downloading {url} to {target_path}...", YELLOW)

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(target_path, 'wb') as out_file:
                out_file.write(response.read())

            size = os.path.getsize(target_path)
            size_h = f"{size / 1024:.2f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.2f} MB"
            log(f"Success! Saved to {target_path} ({size_h}) (。・ω・。)ノ", GREEN)

            # Post-processing: Format JSON files with Python's json module
            if target_path.lower().endswith('.json'):
                try:
                    log(f"Formatting JSON file: {target_path}...", YELLOW)
                    with open(target_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    with open(target_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    log("JSON formatted successfully! (≧∇≦)/", GREEN)
                except Exception as format_err:
                    log(f"Failed to format JSON: {format_err} (´・ω・｀)", YELLOW)

            return True
        except Exception as e:
            log(f"Attempt {attempt + 1} failed: {e}", RED)
            if attempt < retries - 1:
                log(f"Retrying in {delay} seconds...", YELLOW)
                time.sleep(delay)

    log(f"Failed to download {url} after {retries} attempts (QAQ)", RED)
    return False

def sync_git(url, target_path, sparse_checkout=None, move_from=None, files_filter=None):
    log(f"Syncing git repo {url} to {target_path}...", YELLOW)
    
    # Compile filter pattern if provided
    filter_pattern = None
    if files_filter:
        filter_pattern = re.compile(files_filter)
        log(f"Using file filter: {files_filter}", YELLOW)
    
    def copy_filtered(src, dst, filter_pattern):
        """递归复制目录，只复制匹配 filter_pattern 的文件"""
        if not os.path.exists(dst):
            os.makedirs(dst)
        
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            
            if os.path.isdir(s):
                # 递归复制子目录
                copy_filtered(s, d, filter_pattern)
                # 如果子目录为空，删除它
                if os.path.exists(d) and not os.listdir(d):
                    os.rmdir(d)
            else:
                # 检查文件是否匹配 filter
                if filter_pattern is None or filter_pattern.search(s):
                    shutil.copy2(s, d)

    with tempfile.TemporaryDirectory() as temp_dir:
        # Initialize sparse repo
        run_command(['git', 'init'], cwd=temp_dir)
        run_command(['git', 'remote', 'add', 'origin', url], cwd=temp_dir)

        if sparse_checkout:
            run_command(['git', 'config', 'core.sparseCheckout', 'true'], cwd=temp_dir)
            sparse_file = os.path.join(temp_dir, '.git/info/sparse-checkout')
            with open(sparse_file, 'w') as f:
                for item in sparse_checkout:
                    f.write(f"{item}\n")

        success, err = run_command(['git', 'pull', '--depth', '1', 'origin', 'HEAD'], cwd=temp_dir)
        if not success:
            log(f"Git pull failed: {err}", RED)
            return False

        # Prepare target directory
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        os.makedirs(target_path)

        source_base = temp_dir
        if move_from:
            source_dir = os.path.join(temp_dir, move_from)
            if os.path.exists(source_dir):
                # If move_from is a directory, copy its contents
                for item in os.listdir(source_dir):
                    s = os.path.join(source_dir, item)
                    d = os.path.join(target_path, item)
                    if os.path.isdir(s):
                        if filter_pattern:
                            copy_filtered(s, d, filter_pattern)
                        else:
                            shutil.copytree(s, d)
                    else:
                        if filter_pattern is None or filter_pattern.search(s):
                            shutil.copy2(s, d)

            # Also check for other items in sparse_checkout that might not be in move_from
            if sparse_checkout:
                for item in sparse_checkout:
                    if item != move_from:
                        s = os.path.join(temp_dir, item)
                        if os.path.exists(s) and not s.startswith(os.path.join(temp_dir, move_from)):
                            d = os.path.join(target_path, os.path.basename(item))
                            if os.path.isdir(s):
                                if filter_pattern:
                                    copy_filtered(s, d, filter_pattern)
                                else:
                                    shutil.copytree(s, d)
                            else:
                                if filter_pattern is None or filter_pattern.search(s):
                                    shutil.copy2(s, d)
        else:
            # Copy everything from temp_dir (except .git)
            for item in os.listdir(temp_dir):
                if item == '.git': continue
                s = os.path.join(temp_dir, item)
                d = os.path.join(target_path, item)
                if os.path.isdir(s):
                    if filter_pattern:
                        copy_filtered(s, d, filter_pattern)
                    else:
                        shutil.copytree(s, d)
                else:
                    if filter_pattern is None or filter_pattern.search(s):
                        shutil.copy2(s, d)

        log(f"Success! Git repo synced to {target_path} (。・ω・。)ノ", GREEN)
        return True

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    config_path = os.path.join(project_root, 'resources.json')

    if not os.path.exists(config_path):
        log(f"Config file not found: {config_path}", RED)
        sys.exit(1)

    try:
        with open(config_path, 'r') as f:
            resources = json.load(f)
    except json.JSONDecodeError as e:
        log(f"Failed to parse {config_path}: {e}", RED)
        sys.exit(1)

    log("============================================")
    log("Starting resource synchronization... (｀・ω・´)ゞ")
    log("============================================")

    success_count = 0
    fail_count = 0

    for res in resources:
        name = res.get('name', 'Unknown')
        res_type = res.get('type', 'file')
        url = res.get('url')
        path = res.get('path')

        if not url or not path:
            log(f"Skipping invalid entry: {res}", RED)
            continue

        target_path = os.path.join(project_root, path)
        target_dir = os.path.dirname(target_path)

        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        log(f"Processing: {name} ({res_type})")

        success = False
        if res_type == 'file':
            success = download_file(url, target_path)
        elif res_type == 'git':
            success = sync_git(
                url,
                target_path,
                sparse_checkout=res.get('sparse_checkout'),
                move_from=res.get('move_from'),
                files_filter=res.get('files_filter')
            )
        else:
            log(f"Unknown resource type: {res_type}", RED)

        if success:
            success_count += 1
        else:
            fail_count += 1
        log("--------------------------------------------")

    log("============================================")
    if fail_count == 0:
        log(f"All done! Updated {success_count} resources. Perfect! (≧∇≦)/", GREEN)
    else:
        log(f"Finished with errors. Success: {success_count}, Failed: {fail_count}. Please check logs. (´・ω・｀)", YELLOW)
    log("============================================")

if __name__ == "__main__":
    main()
