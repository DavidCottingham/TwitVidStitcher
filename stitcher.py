#!/usr/bin/env python3

import sys
import os
import shutil
import re
from contextlib import closing
import requests

def main():
    urlStart = "https://video.twimg.com"

    if len(sys.argv) <= 1:
        slashedURL = getSlashedURL()
    else:
        slashedURL = sys.argv[1]
    playlist1URL = slashedURL.replace("\\", "")
    #print(playlist1URL)
    print("Gathering URLs")

    r = requests.get(playlist1URL)
    if r.status_code != requests.codes.ok:
        print("Could not reach URL")
        sys.exit(1)
    fullPlaylist1 = r.text
    fullPlaylist1 = fullPlaylist1[:-1]
    playlist2URL = urlStart + fullPlaylist1.split("\n")[-1]

    r = requests.get(playlist2URL)
    if r.status_code != requests.codes.ok:
        print("Could not reach URL")
        sys.exit(1)
    pattern = re.compile("^/\S+\.ts$", re.MULTILINE)
    urls = re.findall(pattern, r.text)

    dir = makePiecesDir()
    fileList = []
    finalFilename = urls[0].split("/")[2] + ".ts"

    print("Downloading video pieces")
    for url in urls:
        url = urlStart + url
        #print(url)
        with closing(requests.get(url, stream=True)) as p:
            if p.status_code == requests.codes.ok:
                filename = url.split("/")[-1]
                fileList.append(filename)
                with open(os.path.join(dir, filename), "wb") as file:
                    for chunk in p:
                        file.write(chunk)
    print("Stitching pieces")
    with open(finalFilename, 'wb') as stitched:
        for filename in fileList:
            with open(os.path.join(dir, filename), 'rb') as part:
                shutil.copyfileobj(part, stitched)
    print("Removing pieces")
    shutil.rmtree(dir)
    print("Full video: " + finalFilename)

def makePiecesDir():
    curPath = os.path.dirname(os.path.realpath(sys.argv[0]))
    dir = os.path.join(curPath, "pieces")
    try:
        #pieces shouldn't exist but may if script exited early. still use it
        os.makedirs(dir, exist_ok=True)
        return dir
    except OSError:
        print("Insufficient permissions to save files")
        sys.exit(1)

def getSlashedURL():
    try:
        u = input("Playlist URL: ")
        if u: return u
        else: sys.exit()
    except EOFError:
        sys.exit()

if __name__ == "__main__":
    main()
