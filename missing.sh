#!/bin/zsh

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <material> <brand>"
    exit 1
fi

material="$1"
brand="$2"

for f in "openprinttag-database/data/materials/$brand"/*.yaml; do
    [[ -f "$f" ]] || continue

    awk -v material="$material" '
        /^type:/ {
            if ($2 == material) type_ok = 1
        }

        /^properties: \{\}/ {
            empty_props = 1
        }

        /^properties:/ {
            in_props = 1
            next
        }

        in_props && /^[^[:space:]]/ {
            in_props = 0
        }

        in_props && /^[[:space:]]+[a-zA-Z_]+:/ {
            prop_count++
            if ($1 == "density:") density_only = 1
        }

        END {
            if (type_ok && (empty_props || (prop_count == 1 && density_only))) {
                print FILENAME
            }
        }
    ' "$f" | xargs -n1 basename
done
