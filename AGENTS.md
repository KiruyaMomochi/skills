# Skills Project - Developer Guide

This document provides guidance for AI agents working with this skills repository.

## Project Structure

```
skills/
├── AGENTS.md              # This file - developer guide
├── resources.json         # Configuration for external resources to sync
├── sync.sh               # Wrapper script to run sync_resources.py
├── scripts/
│   └── sync_resources.py # Python script to sync git repos and download files
└── skills/               # Skills directory
    ├── skill-name/
    │   ├── SKILL.md      # Required: skill definition and instructions
    │   ├── references/   # Optional: documentation to be loaded as needed
    │   ├── scripts/      # Optional: executable scripts
    │   └── assets/       # Optional: templates, images, etc.
    └── ...
```

## Adding a New Skill

### Step 1: Decide if the skill needs external resources

**If no external resources needed** (pure instructions):
- Create `skills/skill-name/SKILL.md` directly
- Skip to Step 3

**If external resources needed** (docs from git repos, remote files):
- Continue to Step 2

### Step 2: Configure external resources in `resources.json`

The sync system supports two resource types:

#### Type 1: File Download
Download a single file from a URL:
```json
{
  "name": "Description",
  "type": "file",
  "url": "https://example.com/file.json",
  "path": "skills/skill-name/references/file.json"
}
```

#### Type 2: Git Repository (with optional sparse checkout and filtering)
Sync from a git repository:
```json
{
  "name": "Description",
  "type": "git",
  "url": "https://github.com/user/repo.git",
  "path": "skills/skill-name/references/docs",
  "sparse_checkout": ["docs/", "examples/"],    // Optional: only checkout these paths
  "move_from": "docs",                          // Optional: move files from this subdirectory
  "files_filter": "(\\.md$|\\.yaml$)"           // Optional: regex to filter files
}
```

**File Filter Examples**:
- `"\\.md$"` - Only markdown files
- `"(\\.md$|\\.yaml$)"` - Markdown and YAML files
- `"/testdata/config.*\\.ya?ml$"` - Only config*.yaml files in testdata directories
- `"(README\\.md|metadata\\.yaml)"` - Only README.md and metadata.yaml files

**How the file filter works**:
- Uses Python regex matching against full file paths
- If filter matches, file is copied; otherwise skipped
- Empty directories are automatically removed
- If no filter specified, all files are copied

After editing `resources.json`, run `./sync.sh` to download/sync resources.

### Step 3: Create the skill definition

For detailed guidance on creating effective SKILL.md files, **refer to `skills/skill-creator/SKILL.md`**. That skill provides comprehensive instructions on:

- Skill anatomy and structure
- YAML frontmatter (name, description)
- Progressive disclosure patterns
- When to use scripts/, references/, and assets/
- Best practices for keeping skills concise
- Using the init_skill.py and package_skill.py scripts

**Quick summary** for SKILL.md structure:
```markdown
---
name: skill-name
description: Clear description of what the skill does and when to use it. This is CRITICAL - it determines when the skill gets loaded. Include specific triggers and use cases.
---

# Skill Title

## Description
Brief explanation of the skill's purpose.

## Instructions
Step-by-step guidance for using the skill. Reference documentation in `references/` folder as needed.

## Available Resources
List what's in references/, scripts/, or assets/ folders if applicable.

## Tips
Best practices, common patterns, gotchas.
```

### Step 4: Test the skill

1. Reload OpenCode to pick up the new skill
2. Try queries that should trigger the skill
3. Verify that reference documents are being used correctly

## Updating External Resources

When documentation needs to be refreshed (e.g., upstream repos updated):

```bash
./sync.sh
```

This script:
1. Reads `resources.json`
2. For each resource:
   - Downloads files or clones git repos (with sparse checkout if specified)
   - Applies file filters if specified
   - Saves to the specified path
3. Reports success/failure for each resource

## File Filter Implementation Details

The `files_filter` feature in `sync_resources.py`:
- Compiles the regex pattern using Python's `re` module
- Recursively walks through directories
- Tests each file path against the pattern
- Only copies matching files, preserving directory structure
- Removes empty directories after filtering

This allows syncing large repos (like opentelemetry-collector-contrib at 231MB) while only keeping relevant documentation (10MB).

## Examples

### Example 1: Simple documentation skill
```json
{
  "name": "My API Docs",
  "type": "git",
  "url": "https://github.com/company/api-docs.git",
  "path": "skills/my-api/references",
  "sparse_checkout": ["api/"],
  "move_from": "api"
}
```

### Example 2: Multi-repo skill with filtering
```json
[
  {
    "name": "General Docs",
    "type": "git",
    "url": "https://github.com/project/docs.git",
    "path": "skills/my-skill/references/docs",
    "sparse_checkout": ["content/"],
    "move_from": "content"
  },
  {
    "name": "Component Docs",
    "type": "git",
    "url": "https://github.com/project/monorepo.git",
    "path": "skills/my-skill/references/components",
    "sparse_checkout": ["packages/"],
    "files_filter": "(\\.md$|README)"
  }
]
```

## Best Practices

1. **Keep SKILL.md concise** - Only include essential instructions; move detailed docs to `references/`
2. **Use file filters** - Don't sync entire repos if you only need documentation
3. **Descriptive names** - Use clear names in `resources.json` for better logs
4. **Test filters** - Verify file counts and sizes after syncing
5. **Document resources** - In SKILL.md, explain what's in `references/` and how to use it

## Troubleshooting

**Sync fails with git errors**: Check network connection and git repo URL
**Filter not working**: Ensure regex is properly escaped in JSON (use `\\` for `\`)
**Skill not loading**: Check YAML frontmatter syntax and description clarity
**Too many files synced**: Refine `files_filter` regex or add more specific `sparse_checkout` paths
