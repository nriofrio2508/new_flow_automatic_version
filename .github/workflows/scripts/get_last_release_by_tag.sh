result_next_last_tag="${{ env.PREFIX_REPO }}-v0.0.0"
tags=$(git tag -l '${{ env.PREFIX_REPO }}-v*' --sort=-taggerdate | grep -E "^${{ env.PREFIX_REPO }}-v[0-9]+\.[0-9]+\.[0-9]+$" || true)

if [ -n "$tags" ]; then
    for tag in $filtered_tags; do
        response_release=$(gh api -H "Accept: application/vnd.github.v3+json" "/repos/${{github.repository}}/releases/tags/$tag" || true)

        if echo "$response_release" | jq -e '.status' > /dev/null 2>&1; then
        continue
        fi
        filter_only_release=$(echo "$response_release" | jq 'select(.prerelease == false) | select(.draft == false) | .tag_name')
        if [ -n "$filter_only_release" ]; then
        echo "name=$filter_only_release" >> $GITHUB_OUTPUT
        break
        fi
    done
else
    echo "name=$result_next_last_tag" >> $GITHUB_OUTPUT
fi