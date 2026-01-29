---
name: nix
description: Expert assistance for working with the Nix ecosystem, including NixOS, Home Manager, and Nix Flakes. Provides package/option search capabilities, flake templates, debugging guides, and comprehensive documentation for Nix language and Nixpkgs. Use this skill when: (1) Searching for NixOS packages or options, (2) Creating or configuring Nix flakes, (3) Setting up development environments with Nix, (4) Writing Nix expressions or debugging Nix code, (5) Working with NixOS configurations, Home Manager, or any Nix-related tasks.
---

# Nix & NixOS Expert

## Description
This skill provides tools and documentation for working with the Nix ecosystem, including NixOS, Home Manager, and Nix Flakes. It includes local search capabilities and rapid prototyping templates.

## Instructions

### 1. Searching Packages & Options
**Always** use the bundled `search_nixos.py` script instead of `nix search`. It queries the web API directly and is much faster.

```bash
# Search for packages
./skills/nix/scripts/search_nixos.py firefox

# Search for NixOS options (by keyword)
./skills/nix/scripts/search_nixos.py -t options "postgresql"

# List ALL options under a prefix (great for exploring a service)
./skills/nix/scripts/search_nixos.py --prefix services.postgresql -n 50

# Options:
#   -t, --type {packages,options}  Type of search (default: packages)
#   -p, --prefix                   List all options starting with query
#   -n, --size NUM                 Number of results (default: 20)
#   -c, --channel CHANNEL          NixOS channel (unstable, 24.11, 24.05)
#   -j, --json                     Output raw JSON for processing
```

Output includes: name, version, type, default value, example, source file path, and full description.

### 2. Viewing Nixpkgs Source Code
Use `nixpkgs_source.py` to browse and read source files from the nixpkgs repository:

```bash
# List a package directory (uses search result's Source path)
./skills/nix/scripts/nixpkgs_source.py pkgs/applications/networking/browsers/chromium

# Read a specific file
./skills/nix/scripts/nixpkgs_source.py pkgs/by-name/he/hello/package.nix

# Works with paths from search results (line numbers are stripped)
./skills/nix/scripts/nixpkgs_source.py "pkgs/foo/bar.nix:42"

# Use a specific channel
./skills/nix/scripts/nixpkgs_source.py --ref nixos-24.11 pkgs/top-level/all-packages.nix
```

### 3. Creating New Projects (Flakes)
When the user wants to start a new project or "add nix support", offer these templates located in `skills/nix/assets/templates/`:

*   **Simple Project (`simple.nix`)**: Best for basic usage. Minimal inputs.
*   **DevShell (`devshell.nix`)**: Best for interactive environments. Uses `numtide/devshell` for custom commands and menus.

**To apply a template:**
1.  Read the template content.
2.  Write it to `flake.nix` in the user's directory.
3.  Remind the user to run `git add flake.nix` (Flakes require git tracking).
4.  Suggest running `nix develop` or `nix flake lock`.

### 4. Debugging & Troubleshooting
Refer to `references/cheat-sheet.md` for:
*   Using `builtins.trace` and `lib.debug.traceSeq`.
*   Using `nix repl` to inspect flakes (`:lf .`).
*   Resolving "Infinite recursion" errors.

### 5. Language & Syntax Help
*   **Quick Syntax**: Check `references/nix-1p.md`.
*   **Deep Dive**: Check `references/tutorials/nix-language.md`.
*   **Nixpkgs Manual**: The full manual is available in `references/manual/`.
    *   **Languages**: `references/manual/languages-frameworks/` (Python, Go, Rust, etc.)
    *   **Standard Environment**: `references/manual/stdenv/`
    *   **Hooks**: `references/manual/hooks/` (makeWrapper, etc.)
    *   **Builders**: `references/manual/build-helpers/`

## Available Resources

### Scripts (`skills/nix/scripts/`)
*   `search_nixos.py`: Search packages and options via `search.nixos.org` API.
*   `nixpkgs_source.py`: Browse and fetch nixpkgs source files from GitHub.

### Templates (`skills/nix/assets/templates/`)
*   `simple.nix`: Basic flake with `mkShell`.
*   `devshell.nix`: Advanced flake with `devshell`.

### References (`skills/nix/references/`)
*   `cheat-sheet.md`: Kaoru's special guide for debugging, builtins, and CLI tips.
*   `nix-1p.md`: Tazjin's Nix 1-pager.
*   `manual/`: The complete Nixpkgs manual.
