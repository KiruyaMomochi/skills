#!/usr/bin/env bash
set -e

# (。・ω・。)ノ Target Directories
TARGET_DIRS=(
	"$HOME/.gemini/skills"
	"$HOME/.config/opencode/skills"
	"$HOME/.claude/skills"
)

for TARGET_DIR in "${TARGET_DIRS[@]}"; do
	echo "============================================"
	echo "Installing Skills to $TARGET_DIR... (｀・ω・´)ゞ"
	echo "============================================"

	# Ensure target directory exists
	if [ ! -d "$TARGET_DIR" ]; then
		echo "Creating directory: $TARGET_DIR"
		mkdir -p "$TARGET_DIR"
	fi

	# Copy skills
	for skill in skills/*; do
		if [ -d "$skill" ]; then
			skill_name=$(basename "$skill")
			echo "Installing $skill_name..."

			# Remove existing skill to ensure clean update
			rm -rf "$TARGET_DIR/$skill_name"

			# Copy the skill directory
			cp -r "$skill" "$TARGET_DIR/"
		fi
	done
done

echo "============================================"
echo "All skills installed successfully! (≧∇≦)/"
echo "============================================"

