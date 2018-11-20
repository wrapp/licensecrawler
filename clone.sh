curl -s "https://$GITHUB_API_TOKEN:@api.github.com/orgs/wrapp/repos?per_page=200" | jq .[].ssh_url| xargs -n 1 git clone
