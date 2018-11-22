from pyquery import PyQuery as pq
import os
import urllib.error
import urllib.request
import json
import os.path
import glob
import sys
import re
import time


def python(path):
    requirements = glob.glob(path + "/**/requirements.txt", recursive=True)
    for r in requirements:
        for l in open(r):
            # Skip comments
            if l.startswith("#"):
                continue
            # Skip internal packages
            if "wrapp" in l:
                continue
            # Skip empty lines and current project
            if l.strip() in (".", ""):
                continue

            url = "https://pypi.org/pypi/"+l.split("==")[0]+"/json"
            try:
                with urllib.request.urlopen(url) as url:
                    data = json.loads(url.read().decode())
                    license = data["info"]["license"]
                    print(path, "package:", l.strip(), license)
            except urllib.error.HTTPError as e:
                print(url, e)


def github(repo_url):
    parts = repo_url.split("/")[1:]
    url = ("http://api.github.com/repos/{}/{}/license?access_token={access_token}".format(*
                                                                                          parts, access_token=os.environ["GITHUB_API_TOKEN"]))
    try:
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())
            license = data["license"]["name"]
            return license
    except urllib.error.HTTPError:
        return "Fail"


def gomod(path):
    mods = glob.glob(path + "/**/go.mod", recursive=True)
    for m in mods:
        for l in open(m):
            if l.strip().startswith("github"):
                package = l.strip().split()[0]
                license = github(package)
                print(path, package, license)


def glide(path):
    glidefiles = glob.glob(path + "/**/glide.yaml", recursive=True)
    for g in glidefiles:
        for l in open(g):
            if not "package:" in l:
                continue
            package = l.split(":")[1].strip()
            license = github(package)
            print(path, package, license)


def cocoa(path):
    podfiles = glob.glob(path + "/**/Podfile", recursive=True)
    for p in podfiles:
        for l in open(p):
            if "pod" in l:
                package = l.strip("").split()[1].strip(",\'")
                url = "http://metrics.cocoapods.org/api/v1/pods/{}".format(
                    package)
                req = urllib.request.Request(
                    url,
                    data=None,
                    headers={
                        'User-Agent': 'licensecrawl'
                    }
                )

                try:
                    with urllib.request.urlopen(req) as response:
                        data = json.loads(response.read().decode())
                        print(package, data["cocoadocs"]["license_short_name"])
                except Exception as e:
                    print(e.reason)


def gradle(path):
    gradles = glob.glob(path + "/**/build.gradle", recursive=True)
    for g in gradles:
        for l in open(g):
            if l.strip().startswith("//"):
                continue
            if "compileSdkVersion" in l:
                continue 
            if "implementation" in l or "compile" in l:
                # print(l)
                print(l)
                package = re.split("[( ]", l.strip())[1].strip("\'\)\"")

                if package == "fileTree":
                    continue
                package = package.split("@")[0]
                try:
                    url = "https://mvnrepository.com/artifact/{}/{}".format(
                        *package.split(":"))
                except Exception as e:
                    print(package)
                    continue

                req = urllib.request.Request(
                    url,
                    data=None,
                    headers={
                        'User-Agent': 'licensecrawl'
                    }
                )
                body = urllib.request.urlopen(req).read()
                latest_version = pq(body)(".vbtn.release:first").text()

                url = url+"/"+latest_version

                req = urllib.request.Request(
                    url,
                    data=None,
                    headers={
                        'User-Agent': 'licensecrawl'
                    }
                )
                body = urllib.request.urlopen(req).read()
                try:
                    license, license_url = (d.text for d in pq(body)(
                        '.version-section h2:contains("Licenses")').nextAll()(
                            "tbody tr td"
                    ))
                except Exception as e:
                    license=url
                time.sleep(0.1)  # Avoid being rate-limited
                print(path, package, license)


def npm(path):
    pass


def licenses(path):
    print("\n#", path)
    python(path)
    gradle(path)
    gomod(path)
    glide(path)
    npm(path)
    cocoa(path)


if len(sys.argv[1:]) == 0:
    for f in os.listdir("./"):
        licenses(f)
else:
    for d in sys.argv[1:]:
        licenses(d)
