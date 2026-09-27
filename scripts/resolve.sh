# Sourced by justfile recipes: resolve an exercise path given relative to where `just` was invoked.
# usage: source scripts/resolve.sh <invocation_dir> <path>
# sets: rel (repo-relative, e.g. python/exercises/lc0053-x), lang, slug, pkg, tier
root="$(pwd)"
rel="$(cd "$1" && realpath -m --relative-to="$root" "$2")"
if [[ ! "$rel" =~ ^(python|rust|cpp)/exercises/[a-z][a-z0-9-]*$ || ! -f "$rel/.meta/exercise.toml" ]]; then
  echo "not an exercise directory: $2 (expected <lang>/exercises/<slug>)" >&2
  exit 2
fi
IFS=/ read -r lang _ slug <<< "$rel"
pkg="${slug//-/_}"
tier="$(sed -n 's/^tier *= *"\(.*\)"/\1/p' "$rel/.meta/exercise.toml")"
