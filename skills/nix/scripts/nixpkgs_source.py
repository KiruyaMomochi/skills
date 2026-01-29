#!/usr/bin/env python3
"""
Fetch nixpkgs source files from GitHub.

Usage:
  # List directory contents
  ./nixpkgs_source.py pkgs/applications/networking/browsers/chromium

  # Get a specific file
  ./nixpkgs_source.py pkgs/applications/networking/browsers/chromium/default.nix

  # Use a specific branch/channel
  ./nixpkgs_source.py --ref nixos-24.11 pkgs/by-name/he/hello/package.nix
"""
import sys
import json
import argparse
import urllib.request
import urllib.error

DEFAULT_REF = "nixos-unstable"
GITHUB_API = "https://api.github.com/repos/NixOS/nixpkgs/contents"
GITHUB_RAW = "https://raw.githubusercontent.com/NixOS/nixpkgs"


def fetch_json(url):
    """Fetch JSON from URL."""
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def fetch_text(url):
    """Fetch plain text from URL."""
    try:
        with urllib.request.urlopen(url) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def list_directory(path, ref):
    """List contents of a directory."""
    url = f"{GITHUB_API}/{path}?ref={ref}"
    data = fetch_json(url)
    
    if data is None:
        print(f"Not found: {path}", file=sys.stderr)
        return False
    
    if isinstance(data, dict) and data.get("type") == "file":
        # It's a file, not a directory
        print(f"{path} is a file, not a directory. Use without --list to view contents.", file=sys.stderr)
        return False
    
    # Print directory listing
    dirs = []
    files = []
    
    for item in data:
        name = item["name"]
        item_type = item["type"]
        size = item.get("size", 0)
        
        if item_type == "dir":
            dirs.append(f"  {name}/")
        else:
            size_str = f"{size:,} bytes" if size > 0 else ""
            files.append(f"  {name:<40} {size_str}")
    
    print(f"Contents of {path} (ref: {ref}):\n")
    
    if dirs:
        print("Directories:")
        for d in sorted(dirs):
            print(d)
        print()
    
    if files:
        print("Files:")
        for f in sorted(files):
            print(f)
    
    return True


def get_file(path, ref):
    """Get contents of a file."""
    url = f"{GITHUB_RAW}/{ref}/{path}"
    content = fetch_text(url)
    
    if content is None:
        print(f"Not found: {path}", file=sys.stderr)
        return False
    
    print(content)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Fetch nixpkgs source files from GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s pkgs/applications/networking/browsers/chromium
      List directory contents
  
  %(prog)s pkgs/by-name/he/hello/package.nix
      Show file contents
  
  %(prog)s --ref nixos-24.11 pkgs/top-level/all-packages.nix
      Use specific branch
"""
    )
    parser.add_argument("path", help="Path in nixpkgs repo (e.g., pkgs/by-name/he/hello)")
    parser.add_argument("--ref", "-r", default=DEFAULT_REF,
                        help=f"Git ref (branch/tag), default: {DEFAULT_REF}")
    parser.add_argument("--list", "-l", action="store_true",
                        help="Force directory listing (auto-detected by default)")
    
    args = parser.parse_args()
    
    # Clean up path
    path = args.path.strip("/")
    
    # Remove line number suffix if present (e.g., "foo.nix:42" -> "foo.nix")
    if ":" in path.split("/")[-1]:
        path = path.rsplit(":", 1)[0]
    
    if args.list:
        success = list_directory(path, args.ref)
    elif path.endswith(".nix") or path.endswith(".py") or path.endswith(".md") or "." in path.split("/")[-1]:
        # Looks like a file
        success = get_file(path, args.ref)
    else:
        # Try as directory first
        success = list_directory(path, args.ref)
        if not success:
            # Maybe it's a file without extension?
            success = get_file(path, args.ref)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
