import os
import sys
from urllib.request import urlopen, Request # get html
import re
import datetime


localFileOrigin = ""
"""
def getHtml(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urlopen(req).read()"""
# returns html (string)
def getHtml(url):
    global localFile
    global localFileOrigin
    global mainUrl
    if localFile and url[0:4] != "http":
        html = " ".join( open(url, "r").readlines() )
        try: localFileOrigin = html.split("#")[1]
        except: localFileOrigin = ""
        if localFileOrigin[0:5] == "https":
            localFileOrigin = "http" + localFileOrigin[5:]
        return html
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'})
        html = str(urlopen(req).read())
        if localFile:
            mainUrl = url
            localFile = False
            localFileOrigin = ""
        return html
    except:
        return ""

def output(txt, echo=True):
    if echo: print(txt)
    #with open("/home/karlo/python/playalloutput", "a") as outputFile:
    #    outputFile.write(txt + "\n")

# returns processed html array with elements that are maybe links (array)
def prepHtml(html):
    html = html.replace("\\", "").replace("'", "\"").replace("src=\"", "href=\"").replace("meta property=\"og:video\" content=\"", "href=\"").replace("class=\"upload_info\" about=\"", "href=\"").split("href=\"")[1:]
    return html

# returns fixed url (string)
def generalFixes(url):
    url = url.strip()    # remove leading and trailing spaces
    url = url.replace(" ", "%20")    # vlc didnt work with spaces, in urls "%20" is code for space
    if "#" in url and url[0] != "#":
        url = url.split("#")[0]
    if 'https:' in url:
        url = url.replace("https", "http", 1)
    elif url[0:2] == "//":    # 4chan.org
        url = "http:" + url
    elif url[0:4] != "http":
        if localFile:
            domain = "http://" + localFileOrigin.split("//")[1].split("/")[0]
        else:
            domain = "http://" + oldContentLinks[-1].split("//")[1].split("/")[0]
        #if url[0] == "/":
        #    url = url[1:]
        url = domain + url
    return url

# returns url type (string)
def checkUrl(url):
    url = url.lower()
    ret = ""
    if url[:7] != "http://":
        return False
    if ".php" in url:
        ret = "avoid"
    if ('watch?v=' in url or 'youtu.be' in url or 'youtube.com/embed/' in url) and 'm.youtube' not in url:
        return ret + "youtube"
    for ext in [".webm", ".ogg", ".mp3", ".mp4", ".wav", ".avi"]:
        if ext in url:
            return ret + "mediafile"
    if re.match(".*vimeo\.com/(video/)?\d\d\d\d\d\d\d\d", url):    # regex for: "vimeo.com/12345678", "vimeo.com/video/12345678"
        return ret + "vimeo"
    if "streamable.com/" in url:
        return ret + "streamable"
    if ".gifv" in url:
        return ret + "gifv"
    if "gfycat.com/" in url:
        return ret + "gfycat"
    for ext in [".jpeg", ".jpg", ".png", ".gif", ".tiff", ".bmp", ".ico", ".svg", ".css", ".js"]:
        if ext in url:
            return ret + "etcfile"
    return "none"

# get more content
def getContent(url, ar=""):
    global allHtml
    global leng
    global oldContentLinks
    global ignoreContentLinks
    if url not in oldContentLinks:
        oldContentLinks.append(url)
        output("\n -------- downloading content from "+ ar + url)
        html0 = getHtml(url)
        html = prepHtml(html0)
        plusHtml = ""
        if "youtube.com" in url:
            if "class=\"watch-card-view-all-row\"><td colspan=\"3\"><a href=\"" in html0:
                output("\n> found Top Tracks")
                plusUrl = "http://www.youtube.com" + html0.split("class=\"watch-card-view-all-row\"><td colspan=\"3\"><a href=\"")[1].split("\"")[0]
                plusHtml = getHtml(plusUrl)
                plusHtml = prepHtml(plusHtml)
                ignoreContentLinks = len(allHtml) + len(plusHtml)
        allHtml += plusHtml
        allHtml += html
        leng = len(allHtml)

def playOne(url, urlType):
    global countLinks
    global jump
    global allLinks
    countLinks += 1
    output("\n" + urlType + "\n " + str(countLinks) + "-------- " + url)
    if jump == 0:
        if download:
            downloadLink(url)
        else:
            os.system(player +" "+ arg +" \"" + url + "\" > /dev/null 2>&1")
    else:
        output(" -------- jump "+ str(jump))
        jump -= 1
    allLinks.append(url)

def playMany():
    global links
    global jump
    output("\n -------- " + str(len(links)) + " links    ( " + str(countLinks-len(links)+1) +  " - " + str(countLinks) + " )")
    output("\n" + '\n'.join(links))
    if download:
        for link in links:
            downloadLink(link)
    else:
        os.system(player +" "+ arg +" \""+ '" "'.join(links) + "\" > /dev/null 2>&1")
    links = []

def downloadLink(url):
    if "youtube.com" in url:
        if arg_a:
            os.system("youtube-dl -f bestaudio --audio-quality 0 --audio-format mp3 -i -x --extract-audio \"" + url + "\"")
        else:
            os.system("youtube-dl \"" + url + "\"")
    else:
        os.system("wget \"" + url + "\"")



check = os.popen('dpkg -l | grep youtube-dl')
installed = False
for c in check:
    if c:
        installed = True
if not installed:
    print("This program requires youtube-dl\nsudo apt-get install youtube-dl\n")
check = os.popen('dpkg -l | grep vlc')
installed = False
for c in check:
    if c:
        installed = True
if not installed:
    print("This program requires vlc\nsudo apt-get install vlc\n")


if len(sys.argv) == 1:
    print("What URL do you want to be crawled?")
    print("Try `pall --help' for more information.")
    exit()
if sys.argv[1] == "--help":
    print("""  OPTIONS:
-a          audio
              play/download only audio
-p          playlist
              links from each website are played in one playlist
-f          fullscreen
              play videos in fullscreen
-j <int>    jump
              jump over a number of links
-n <int>    number
              crawl links until a number of links is reached
-d          download
              download links
-l          local
              crawl links from local file
-i          infinite
              if not set crawling is limited to one domain

--short     shortcuts
              list of URL shortcuts"""+
#--hist      history
#              history of output
"""
--about     about
              about this program""")
    exit()
elif sys.argv[1] == "--short":
    print("""  URL SHORTCUTS:
"y:string"
            search on youtube.com
            (http://www.youtube.com/results?search_query=string)
"y/string"
            channel on youtube.com
            (http://www.youtube.com/user/string)
"r:string"
            search on reddit.com
            (http://www.reddit.com/search?q=string)
"r/string"
            subreddit on reddit.com
            (http://www.reddit.com/r/string)""")
    exit()
elif sys.argv[1] == "--about":
    print("""Made by Karlo Babić
Mail: karlo.babic@gmail.com""")
    exit()
elif sys.argv[1] == "--hist":
    os.system("less " + "/home/karlo/python/playalloutput")
    exit()


arg_f = False
arg_a = False
arg_j = False
arg_i = False
arg_p = False
arg_d = False
arg_n = False
arg_l = False
unknownOption = False
for i in range(1, len(sys.argv)):
    if sys.argv[i][0] == '-':
        j = 1
        while sys.argv[i][j] != ' ':
            if sys.argv[i][j] == 'f':      # fullscreen
                arg_f = True
            elif sys.argv[i][j] == 'a':    # audio only
                arg_a = True
            elif sys.argv[i][j] == 'j':    # jump a number of times
                try: arg_j = int(sys.argv[i+1])
                except: unknownOption = sys.argv[i][j]
            elif sys.argv[i][j] == 'i':    # crawl outside the website (infinite)
                arg_i = True
            elif sys.argv[i][j] == 'p':    # on each website download create a playlist of links
                arg_p = True
            elif sys.argv[i][j] == 'd':    # download links
                arg_d = True
            elif sys.argv[i][j] == 'n':    # exit after reaching a number of links
                try: arg_n = int(sys.argv[i+1])
                except: unknownOption = sys.argv[i][j]
            elif sys.argv[i][j] == 'l':    # local file
                arg_l = True
            else:
                unknownOption = sys.argv[i][j]
            if len(sys.argv[i]) > j+1:
                j += 1
            else: break
if unknownOption:
    print("Unknown option or missing mandatory argument", "`"+str(unknownOption)+"'")
    print("Try `pall --help' for more information.")
    exit()

arg = ""
jump = 0
player = "vlc"
infinite = False
playlist = False
download = False
numberOfLinks = 0
localFile = False
if arg_f:
    arg = "--fullscreen"    # --fs
if arg_a:
    arg = "--no-video"    # -novideo
    player = "cvlc"
if arg_j:
    jump = arg_j
if arg_i:
    infinite = True
if arg_p:
    playlist = True
if arg_d:
    download = True
if arg_n:
    numberOfLinks = arg_n
if arg_l:
    localFile = True


# prepare url
mainUrl = sys.argv[len(sys.argv)-1]

if not localFile:
    if mainUrl[0:2] == "y/":
        mainUrl = "http://www.youtube.com/user/" + mainUrl[2:].replace(' ','+')
    elif mainUrl[0:2] == "y:":
        mainUrl = "http://www.youtube.com/results?search_query=" + mainUrl[2:].replace(' ','+')
    elif mainUrl[0:2] == "r/":
        mainUrl = "http://www.reddit.com/r/" + mainUrl[2:].replace(' ','+')
    elif mainUrl[0:2] == "r:":
        mainUrl = "http://www.reddit.com/search?q=" + mainUrl[2:].replace(' ','+')
    else:
        if mainUrl[0:4] != "http" and mainUrl[0:5] != "file:":
            mainUrl = "http://" + mainUrl

output("\n\n\n################################################\n" + str(datetime.datetime.now()) + "\n", echo=False)
output(mainUrl)

links = []    # links that are being processed
allLinks = []    # used links that were processed
contentLinks = []    # links saved for downloading new content
contentLinksP = []    # primary links saved for downloading new content
oldContentLinks = []    # used content links
ignoreContentLinks = 0

# prepare html
allHtml = []
getContent(mainUrl)

i = 0
leng = len(allHtml)
countLinks = 0
backupNextNode = 0
backupNextNodeP = 0

while i < leng:

# processing links -----------------------------------------------------------------

    x = allHtml[i].split("\"")[0]
    if x:
        x = generalFixes(x)
        urlType = checkUrl(x)
        play = False
        if urlType == "mediafile":
            play = True
        elif urlType == "youtube":
            blacklist = False
            for black in ["android-app:", "ios-app:"]:    # blacklist
                if black in x:
                    blacklist = True
                    break
            if not blacklist:
                play = True
                if 'youtu.be/' in x and len(x.split("youtu.be/")) > 1:
                    x = 'http://www.youtube.com/watch?v=' + x.split("youtu.be/")[1]
                elif 'youtube.com/embed/' in x:
                    x = 'http://www.youtube.com/watch?v=' + x.split("youtube.com/embed/")[1]
                if 'watch?v=' in x:
                    if x.split("watch?v=")[1] == "":
                        play = False
                    if 'youtube.com' not in x:
                        x = 'http://www.youtube.com' + x
                    if localFile or x.split("//")[1].split("/")[0] == mainUrl.split("//")[1].split("/")[0]:    # if in the same domain (www.youtube.com)
                        if '&amp;list=' in x and '&amp;index=' not in x:
                            getContent(x, "playlist ")    # content from playlist is taken right now and not later
                            play = False
                        else:
                            contentLinksP.append(x)    # content is taken from primary links
                    if '&amp;list=' in x:
                        x = x.split("&amp;list=")[0]
                    if '&amp;index=' in x:
                        x = x.split("&amp;index=")[0]
                    x = x.replace('http://', 'https://')  # http had problems with certifacates
        elif urlType == "vimeo":
            x = "http://player.vimeo.com/video/" + x.split("vimeo.com/")[1].replace("video/", "")
            play = True
        elif urlType == "streamable":
            html = getHtml(x)
            html = html.replace("meta property=\"og:video\" content=\"", "href=\"").split("href=\"")
            for h in html:
                h = h.split("\"")[0]
                if ".mp4" in h:
                    x = h
                    play = True
                    break
            if not play:
                urlType = "none"
        elif urlType == "gifv":
            x = x.replace(".gifv", ".mp4", 1)
            play = True
        elif urlType == "gfycat":
            html = getHtml(x)
            html = html.split("source id=\"webmSource\" src=\"")
            for h in html:
                h = h.split("\"")[0]
                if h[-5:] == ".webm":
                    x = h
                    play = True
                    break
            if not play:
                urlType = "none"
        elif urlType == "none":
            blacklist = False
            for black in [".wp.com", "googleapis.com"]:    # blacklist
                if black in x:
                    blacklist = True
                    break
            if not localFile and i > ignoreContentLinks and not blacklist and (infinite or mainUrl.split("//")[1].split("/")[0] in x.split("//")[1].split("/")[0]):    # if infinite crawling is not on, link must be on the same domain
                if oldContentLinks[-1].split("//")[1] in x:    # if link is in hierarchy under the node we are curretnly in
                    contentLinksP.append(x)
                else:
                    contentLinks.append(x)

        if x in allLinks:
            play = False

# playing -----------------------------------------------------------------

        if i <= ignoreContentLinks:    # vip playlist
            if play:
                if jump == 0:
                    links.append(x)
                else:
                    output(" -------- jump "+ str(jump))
                    jump -= 1
                allLinks.append(x)
                countLinks += 1
            if i == ignoreContentLinks and links or numberOfLinks and len(allLinks) == numberOfLinks:    # if last link in vip playlist
                playMany()
        elif playlist:    # if user set "-p"
            if play:
                if jump == 0:
                    links.append(x)
                else:
                    output(" -------- jump "+ str(jump))
                    jump -= 1
                allLinks.append(x)
                countLinks += 1
            if i == leng-1 and links or numberOfLinks and len(allLinks) == numberOfLinks:    # if last link
                playMany()
        elif play:
            playOne(x, urlType)

        if numberOfLinks and len(allLinks) == numberOfLinks:    # max number of links (limit)
            output("> reached the limit")
            exit()

# searching for more content -----------------------------------------------------------------

    while i == leng-1:    # checked whole html
        if backupNextNodeP < len(contentLinksP):    # content from primary links
            urlb = contentLinksP[backupNextNodeP]
            getContent(urlb)
            backupNextNodeP += 1
        elif backupNextNode < len(contentLinks):    # when no yt videos, content from everything else
            urlb = contentLinks[backupNextNode]
            getContent(urlb)
            backupNextNode += 1
        else:
            output("> out of links")
            exit()

    i += 1



output("> out of links")


'''
                if urlType == "youtube":
                    os.system("youtube-dl --quiet --get-title --no-warnings \"" + x + "\"")
                    os.system("youtube-dl --quiet --no-warnings -o - \"" + x + "\" | "+ player +" "+ arg +" - > /dev/null 2>&1")
                else:

if some youtube videos are not working update lua script
sudo rm /usr/lib/vlc/lua/playlist/youtube.*
sudo curl "http://git.videolan.org/?p=vlc.git;a=blob_plain;f=share/lua/playlist/youtube.lua;hb=HEAD" -o /usr/lib/vlc/lua/playlist/youtube.lua
'''
