#!/bin/zsh
if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <material> <brand>"
    exit 1
fi
material="$1"
brand="$2"
for f in "openprinttag-database/data/materials/$brand"/*.yaml; do
    if grep -q "^type: $material$" "$f" && grep -q "^properties: {}$" "$f"; then
        basename "$f"
    fi
done
