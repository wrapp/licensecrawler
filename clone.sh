url="https://api.github.com/orgs/wrapp/repos"

while [ -n "$url" ]; do
    curl $url --user $GITHUB_API_TOKEN: | jq .[].ssh_url| xargs -n 1 git clone
    url=$( curl --user $GITHUB_API_TOKEN: -I $url | grep -oP '(?<=<)([^<]*)(?=>; rel="next")' )
    echo $url
done
