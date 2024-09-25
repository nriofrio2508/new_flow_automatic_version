set -x
repository_name=$1
prefix_repo=$2
result_next_last_tag="$prefix_repo-v0.0.0"
tags=$(git tag -l "$prefix_repo-v*" --sort=-taggerdate | grep -E "^$prefix_repo-v[0-9]+\.[0-9]+\.[0-9]+$" || true)

if [ -n "$tags" ]; then
    for tag in $tags; do
        echo "Antes respuesta"
        response_release=$(gh api -H "Accept: application/vnd.github.v3+json" "/repos/$repository_name/releases/tags/$tag" || true)
        echo "Obtuvo respuesta"
        if echo "$response_release" | jq -e '.status' > /dev/null 2>&1; then
            continue
        fi
        echo $tag
        filter_only_release=$(echo "$response_release" | jq 'select(.prerelease == false) | select(.draft == false) | .tag_name')
        if [ -n "$filter_only_release" ]; then
            echo "name=$filter_only_release" >> $GITHUB_OUTPUT
        break
        fi
    done
else
    echo "name=$result_next_last_tag" >> $GITHUB_OUTPUT
fi