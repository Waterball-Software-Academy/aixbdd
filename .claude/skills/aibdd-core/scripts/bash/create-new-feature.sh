#!/usr/bin/env bash

# Create a new feature spec directory.
# This script does NOT perform any git operations (no branch creation, no fetch, no checkout).
# The user is responsible for managing their own git branches.

set -e

JSON_MODE=false
SHORT_NAME=""
FEATURE_NUMBER=""
ARGS=()
i=1
while [ $i -le $# ]; do
    arg="${!i}"
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --short-name)
            if [ $((i + 1)) -gt $# ]; then
                echo 'Error: --short-name requires a value' >&2
                exit 1
            fi
            i=$((i + 1))
            next_arg="${!i}"
            if [[ "$next_arg" == --* ]]; then
                echo 'Error: --short-name requires a value' >&2
                exit 1
            fi
            SHORT_NAME="$next_arg"
            ;;
        --number)
            if [ $((i + 1)) -gt $# ]; then
                echo 'Error: --number requires a value' >&2
                exit 1
            fi
            i=$((i + 1))
            next_arg="${!i}"
            if [[ "$next_arg" == --* ]]; then
                echo 'Error: --number requires a value' >&2
                exit 1
            fi
            FEATURE_NUMBER="$next_arg"
            ;;
        --help|-h)
            echo "Usage: $0 [--json] [--short-name <name>] [--number N] <feature_description>"
            echo ""
            echo "Creates a new feature spec directory under specs/. No git operations are performed."
            echo ""
            echo "Options:"
            echo "  --json              Output in JSON format"
            echo "  --short-name <name> Provide a custom short name (2-4 words) for the feature"
            echo "  --number N          Specify feature number manually (overrides auto-detection)"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 'Add user authentication system' --short-name 'user-auth'"
            echo "  $0 'Implement OAuth2 integration for API' --number 5"
            exit 0
            ;;
        *)
            ARGS+=("$arg")
            ;;
    esac
    i=$((i + 1))
done

FEATURE_DESCRIPTION="${ARGS[*]}"
if [ -z "$FEATURE_DESCRIPTION" ]; then
    echo "Usage: $0 [--json] [--short-name <name>] [--number N] <feature_description>" >&2
    exit 1
fi

# Find the repository root by searching for project markers (no git required)
find_repo_root() {
    local dir="$1"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.specify" ] || [ -d "$dir/.git" ]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

# Get highest feature number from specs directory
get_highest_from_specs() {
    local specs_dir="$1"
    local highest=0

    if [ -d "$specs_dir" ]; then
        for dir in "$specs_dir"/*; do
            [ -d "$dir" ] || continue
            dirname=$(basename "$dir")
            number=$(echo "$dirname" | grep -o '^[0-9]\+' || echo "0")
            number=$((10#$number))
            if [ "$number" -gt "$highest" ]; then
                highest=$number
            fi
        done
    fi

    echo "$highest"
}

# Clean and format a feature name
clean_feature_name() {
    local name="$1"
    echo "$name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-//' | sed 's/-$//'
}

# Resolve repository root
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(find_repo_root "$SCRIPT_DIR")"
if [ -z "$REPO_ROOT" ]; then
    echo "Error: Could not determine repository root. Please run this script from within the repository." >&2
    exit 1
fi

cd "$REPO_ROOT"

SPECS_DIR="$REPO_ROOT/specs"
mkdir -p "$SPECS_DIR"

# Generate feature name with stop word filtering
generate_feature_name() {
    local description="$1"

    # Common stop words to filter out
    local stop_words="^(i|a|an|the|to|for|of|in|on|at|by|with|from|is|are|was|were|be|been|being|have|has|had|do|does|did|will|would|should|could|can|may|might|must|shall|this|that|these|those|my|your|our|their|want|need|add|get|set)$"

    # Convert to lowercase and split into words
    local clean_name=$(echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/ /g')

    # Filter words: remove stop words and words shorter than 3 chars (unless they're uppercase acronyms in original)
    local meaningful_words=()
    for word in $clean_name; do
        [ -z "$word" ] && continue
        if ! echo "$word" | grep -qiE "$stop_words"; then
            if [ ${#word} -ge 3 ]; then
                meaningful_words+=("$word")
            elif echo "$description" | grep -q "\b${word^^}\b"; then
                meaningful_words+=("$word")
            fi
        fi
    done

    # Use first 3-4 meaningful words
    if [ ${#meaningful_words[@]} -gt 0 ]; then
        local max_words=3
        if [ ${#meaningful_words[@]} -eq 4 ]; then max_words=4; fi

        local result=""
        local count=0
        for word in "${meaningful_words[@]}"; do
            if [ $count -ge $max_words ]; then break; fi
            if [ -n "$result" ]; then result="$result-"; fi
            result="$result$word"
            count=$((count + 1))
        done
        echo "$result"
    else
        local cleaned=$(clean_feature_name "$description")
        echo "$cleaned" | tr '-' '\n' | grep -v '^$' | head -3 | tr '\n' '-' | sed 's/-$//'
    fi
}

# Generate feature suffix
if [ -n "$SHORT_NAME" ]; then
    FEATURE_SUFFIX=$(clean_feature_name "$SHORT_NAME")
else
    FEATURE_SUFFIX=$(generate_feature_name "$FEATURE_DESCRIPTION")
fi

# Determine feature number (only from specs/ directory)
if [ -z "$FEATURE_NUMBER" ]; then
    HIGHEST=$(get_highest_from_specs "$SPECS_DIR")
    FEATURE_NUMBER=$((HIGHEST + 1))
fi

# Force base-10 interpretation to prevent octal conversion
FEATURE_NUM=$(printf "%03d" "$((10#$FEATURE_NUMBER))")
FEATURE_NAME="${FEATURE_NUM}-${FEATURE_SUFFIX}"

# Truncate if too long (244 char limit for compatibility)
MAX_LENGTH=244
if [ ${#FEATURE_NAME} -gt $MAX_LENGTH ]; then
    MAX_SUFFIX_LENGTH=$((MAX_LENGTH - 4))
    TRUNCATED_SUFFIX=$(echo "$FEATURE_SUFFIX" | cut -c1-$MAX_SUFFIX_LENGTH | sed 's/-$//')

    >&2 echo "[specify] Warning: Feature name exceeded 244-byte limit, truncated"
    FEATURE_NAME="${FEATURE_NUM}-${TRUNCATED_SUFFIX}"
fi

# Create the spec directory and initialize spec file
FEATURE_DIR="$SPECS_DIR/$FEATURE_NAME"
mkdir -p "$FEATURE_DIR"

TEMPLATE="$REPO_ROOT/.claude/skills/aibdd-core/templates/spec-template.md"
SPEC_FILE="$FEATURE_DIR/spec.md"
if [ -f "$TEMPLATE" ]; then cp "$TEMPLATE" "$SPEC_FILE"; else touch "$SPEC_FILE"; fi

# Set the SPECIFY_FEATURE environment variable for the current session
export SPECIFY_FEATURE="$FEATURE_NAME"

# Output results
if $JSON_MODE; then
    printf '{"BRANCH_NAME":"%s","SPEC_FILE":"%s","FEATURE_NUM":"%s","FEATURE_DIR":"%s"}\n' \
        "$FEATURE_NAME" "$SPEC_FILE" "$FEATURE_NUM" "$FEATURE_DIR"
else
    echo "FEATURE_NAME: $FEATURE_NAME"
    echo "SPEC_FILE: $SPEC_FILE"
    echo "FEATURE_NUM: $FEATURE_NUM"
    echo "FEATURE_DIR: $FEATURE_DIR"
    echo ""
    echo "SPECIFY_FEATURE environment variable set to: $FEATURE_NAME"
fi
