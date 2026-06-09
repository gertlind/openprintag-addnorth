#!/bin/zsh
for f in data/materials/addnorth/*.yaml; do              
  if grep -q "^type: $1$" "$f" && grep -q "^properties: {}$" "$f"; then
    basename "$f"
  fi
done
