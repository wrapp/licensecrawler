import os
import urllib.error
import urllib.request
import json
import os.path
import glob
import sys
import re 

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
    url = ("http://api.github.com/repos/{}/{}/license?access_token={access_token}".format(*parts, access_token=os.environ["GITHUB_API_TOKEN"]))
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
        for l in open (g):
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
                url = "http://metrics.cocoapods.org/api/v1/pods/{}".format(package)
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




from pyquery import PyQuery as pq

def gradle(path):
    gradles = glob.glob(path + "/**/build.gradle", recursive=True)
    for g in gradles:
        for l in open(g):
            if l.strip().startswith("//"):
                continue
            if "implementation" in l:
                # print(l)
                package = re.split("[( ]", l.strip())[1].strip("\'\)\"")
                
                if package == "fileTree":
                    continue
                package = package.split("@")[0]
                url = "https://mvnrepository.com/artifact/{}/{}/{}".format(*package.split(":"))
                print(url)
                req = urllib.request.Request(
                    url, 
                    data=None, 
                    headers={
                    'User-Agent': 'licensecrawl'
                    }
                )
                print(package)
                res = urllib.request.urlopen(req)
                print(package.split(":"))
                print (url)
                print(pq(res)('.version-section h2:contains("License")')) #TODO
                sleep(1)
                1/0
    print(gradles)
    pass

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