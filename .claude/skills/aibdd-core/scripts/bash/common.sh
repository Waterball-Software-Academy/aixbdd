#!/usr/bin/env bash
# Common functions and variables for all scripts
# No git operations — feature detection is based on SPECIFY_FEATURE env var or specs/ directory.

# Get repository root by searching for project markers
get_repo_root() {
    # First try git (just for finding the root path, not for branch operations)
    if git rev-parse --show-toplevel >/dev/null 2>&1; then
        git rev-parse --show-toplevel
        return
    fi

    # Fall back to searching for project markers
    local script_dir="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local dir="$script_dir"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.specify" ] || [ -d "$dir/.git" ]; then
            echo "$dir"
            return
        fi
        dir="$(dirname "$dir")"
    done

    # Last resort: assume 3 levels up from script
    (cd "$script_dir/../../.." && pwd)
}

# Get current feature name from SPECIFY_FEATURE env var or latest specs/ directory
get_current_feature() {
    # First check if SPECIFY_FEATURE environment variable is set
    if [[ -n "${SPECIFY_FEATURE:-}" ]]; then
        echo "$SPECIFY_FEATURE"
        return
    fi

    # Search specs/ directory for the latest (highest numbered) feature
    local repo_root=$(get_repo_root)
    local specs_dir="$repo_root/specs"

    if [[ -d "$specs_dir" ]]; then
        local latest_feature=""
        local highest=0

        for dir in "$specs_dir"/*; do
            if [[ -d "$dir" ]]; then
                local dirname=$(basename "$dir")
                if [[ "$dirname" =~ ^([0-9]{3})- ]]; then
                    local number=${BASH_REMATCH[1]}
                    number=$((10#$number))
                    if [[ "$number" -gt "$highest" ]]; then
                        highest=$number
                        latest_feature=$dirname
                    fi
                fi
            fi
        done

        if [[ -n "$latest_feature" ]]; then
            echo "$latest_feature"
            return
        fi
    fi

    echo ""  # No feature found
}

# Validate that we have a valid feature name (NNN-something pattern)
check_feature_name() {
    local feature="$1"

    if [[ -z "$feature" ]]; then
        echo "ERROR: No feature detected. Set SPECIFY_FEATURE env var or create a feature first." >&2
        return 1
    fi

    if [[ ! "$feature" =~ ^[0-9]{3}- ]]; then
        echo "ERROR: Invalid feature name: $feature" >&2
        echo "Feature names should match: NNN-feature-name (e.g., 001-user-auth)" >&2
        return 1
    fi

    return 0
}

get_feature_dir() { echo "$1/specs/$2"; }

# Find feature directory by numeric prefix
# Allows SPECIFY_FEATURE to differ from the exact spec directory name
find_feature_dir_by_prefix() {
    local repo_root="$1"
    local feature_name="$2"
    local specs_dir="$repo_root/specs"

    # Extract numeric prefix (e.g., "004" from "004-whatever")
    if [[ ! "$feature_name" =~ ^([0-9]{3})- ]]; then
        echo "$specs_dir/$feature_name"
        return
    fi

    local prefix="${BASH_REMATCH[1]}"

    # Search for directories in specs/ that start with this prefix
    local matches=()
    if [[ -d "$specs_dir" ]]; then
        for dir in "$specs_dir"/"$prefix"-*; do
            if [[ -d "$dir" ]]; then
                matches+=("$(basename "$dir")")
            fi
        done
    fi

    if [[ ${#matches[@]} -eq 0 ]]; then
        echo "$specs_dir/$feature_name"
    elif [[ ${#matches[@]} -eq 1 ]]; then
        echo "$specs_dir/${matches[0]}"
    else
        echo "ERROR: Multiple spec directories found with prefix '$prefix': ${matches[*]}" >&2
        echo "$specs_dir/$feature_name"
    fi
}

get_feature_paths() {
    local repo_root=$(get_repo_root)
    local current_feature=$(get_current_feature)

    # Use prefix-based lookup
    local feature_dir=$(find_feature_dir_by_prefix "$repo_root" "$current_feature")

    cat <<EOF
REPO_ROOT='$repo_root'
CURRENT_BRANCH='$current_feature'
HAS_GIT='false'
FEATURE_DIR='$feature_dir'
FEATURE_SPEC='$feature_dir/spec.md'
IMPL_PLAN='$feature_dir/plan.md'
TASKS='$feature_dir/tasks.md'
RESEARCH='$feature_dir/research.md'
DATA_MODEL='$feature_dir/data-model.md'
QUICKSTART='$feature_dir/quickstart.md'
CONTRACTS_DIR='$feature_dir/contracts'
EOF
}

check_file() { [[ -f "$1" ]] && echo "  ✓ $2" || echo "  ✗ $2"; }
check_dir() { [[ -d "$1" && -n $(ls -A "$1" 2>/dev/null) ]] && echo "  ✓ $2" || echo "  ✗ $2"; }
