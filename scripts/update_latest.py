#!/usr/bin/env python3
"""Put the channel's latest long video (not a Short) on the bio page.
Reads the public YouTube RSS feed, skips Shorts, updates index.html.
Prints 'changed' or 'unchanged'."""
import html, re, sys, urllib.request

CHANNEL = "UCmmgrJ-m0qlGdMzETUl1pbw"
FEED = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL}"
PAGE = "index.html"

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None

def is_short(vid):
    opener = urllib.request.build_opener(NoRedirect)
    try:
        r = opener.open(urllib.request.Request(f"https://www.youtube.com/shorts/{vid}", method="HEAD"), timeout=20)
        return r.status == 200          # a Short opens at /shorts/
    except urllib.error.HTTPError as e:
        return False                    # 303 redirect = regular video

def latest_long():
    xml = urllib.request.urlopen(FEED, timeout=20).read().decode("utf-8")
    for entry in re.findall(r"<entry>(.*?)</entry>", xml, re.S):
        vid = re.search(r"<yt:videoId>(.*?)</yt:videoId>", entry).group(1)
        title = html.unescape(re.search(r"<title>(.*?)</title>", entry).group(1))
        if not is_short(vid):
            return vid, title
    sys.exit("no long video found in feed")

def main():
    vid, title = latest_long()
    s = open(PAGE, encoding="utf-8").read()
    old = s
    s = re.sub(r"(youtube\.com/watch\?v=)[\w-]{11}", rf"\g<1>{vid}", s)
    s = re.sub(r"(i\.ytimg\.com/vi/)[\w-]{11}(/)", rf"\g<1>{vid}\g<2>", s)
    s = re.sub(r'(<div class="title">).*?(</div>)', lambda m: m.group(1) + html.escape(title, quote=False) + m.group(2), s, count=1)
    if s != old:
        open(PAGE, "w", encoding="utf-8").write(s)
        print("changed", vid, title)
    else:
        print("unchanged", vid)

if __name__ == "__main__":
    main()
