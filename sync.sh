#!/usr/bin/env bash
# (。・ω・。)ノ Sync all resources using the python script
nix run nixpkgs#python3 -- "$(dirname "$0")/scripts/sync_resources.py"
