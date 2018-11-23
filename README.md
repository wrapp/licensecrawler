# licensecrawler
## Usage
    export GITHUB_API_TOKEN=<your GitHub API token>
    export GITHUB_ORG=<your GitHub organization>
    bash copy.sh
    pipenv install
    pipenv run licensecrawl.py
    pipenv run licensecrawl.py <folder>

## licensecrawler.py

This will attempt to find the license for all dependencies in subfolders. It currently has license resolvers for:
* Glide (Go)
* Go modules
* Npm
* Cocoapods
* Gradle
* requirements.txt (Python)

## License
GPLv3
