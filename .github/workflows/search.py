print("Searching...")
import requests
import json
import os
from datetime import datetime

fromisoformat = datetime.fromisoformat
now = datetime.now
from time import sleep, time

donestuff = 0
start = time()
for page in range(150):
    resp = requests.get(
        "https://api.github.com/search/code",
        headers={
            "Authorization": "token " + os.getenv("gh_token")
        },
        params={"q": "filename:hacs.json path:/", "page": str(page)},
    )
    sleep(1)
    resp = resp.json()
    if "items" in resp:
        resp = resp["items"]
    else:
        sleep(60)
        print("Page:", page)
        print(resp)
        print("Start", start)
        print("End", time())
        exit()
    for result in resp:
        reponame = result["repository"]["full_name"]
        print(reponame)
        if (
            "component" not in reponame
            and "home-assistant-community-themes" not in reponame
            and "integration" not in reponame
        ):
            repopart = result["repository"]["name"]
            commits = requests.get(
                "https://api.github.com/repos/" + reponame + "/commits",
                headers={
                    "Authorization": "token " + os.getenv("gh_token")
                },
            )
            commits = commits.json()
            print(commits[0])
            commitsha = commits[0]["sha"]
            files = requests.get(
                "https://api.github.com/repos/"
                + reponame
                + "/git/trees/"
                + commitsha,
                headers={
                    "Authorization": "token " + os.getenv("gh_token")
                },
                params={"recursive": "1"},
            )
            files = files.json()
            print(files)
            files = [file["path"] for file in files["tree"]]
            files = [
                file.split("/")[len(file.split("/")) - 1] for file in files
            ]
            works = False
            for file in files:
                if file.lower() == repopart.lower() + ".js":
                    works = True
                if "lovelace-" in repopart and repopart[:9] == "lovelace-":
                    if (
                        file.lower()
                        == repopart.replace("lovelace-", "").lower() + ".js"
                    ):
                        works = True
            if works:
                info = requests.get(
                    "https://api.github.com/repos/" + reponame,
                    headers={
                        "Authorization": "token " + os.getenv("gh_token")
                    },
                )
                info = info.json()
                last_updated = fromisoformat(info["pushed_at"][:-1])
                last_updated = last_updated.timestamp()
                if (
                    now().timestamp() - last_updated < 60 * 60 * 24 * 30 * 6
                    and not info["archived"]
                ):
                    print(reponame)
                    with open("cards.txt", "a") as cards:
                        cards.write(reponame + "\n")
                else:
                    print(reponame, "OLD")
                    with open("oldcards.txt", "a") as cards:
                        cards.write(reponame + "\n")
        sleep(3.5)
