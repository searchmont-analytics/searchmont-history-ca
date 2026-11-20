"""Build the static Searchmont History website from data/site.json.

    python build.py

Writes one real HTML page per topic and section (so search engines can index them),
plus search-index.json, sitemap.xml and robots.txt. Re-run after editing data/site.json.
"""
import json, os, re, html, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
# Public address of the site. Change this (and re-run) when the custom domain is switched over.
BASE_URL = 'https://searchmont-analytics.github.io/searchmont-history-ca/'
SITE_NAME = "Searchmont History"
TAGLINE = "Uncovering Searchmont's History"

# Old Wix addresses that were renamed: old path -> new path (redirect pages keep old links working)
OLD_PATHS = {
    'citizens/copy-of-bob-beck': 'citizens/prominent-citizens',
    'recreation/copy-of-hockey': 'recreation/automobile',
    'neighbours/gaudette': 'neighbours/glendale',
    'neighbours/belleview': 'neighbours/bellevue',
}

data = json.load(open(os.path.join(ROOT, 'data', 'site.json'), encoding='utf-8'))
TOPICS = data['topics']
e = lambda s: html.escape(str(s or ''), quote=True)


def thumb(f): return 'thumbs/' + re.sub(r'\.png$', '.jpg', f)
def photos(page): return [m for s in page['stories'] for m in s['media'] if 'src' in m]
def films(page): return [m for s in page['stories'] for m in s['media'] if 'video' in m]
def first_photo(page): return (photos(page) or [{}])[0].get('src')


def count_label(page):
    p, v = len(photos(page)), len(films(page))
    bits = ([f"{p} photo{'s' if p != 1 else ''}"] if p else []) + ([f"{v} film{'s' if v != 1 else ''}"] if v else [])
    return ' · '.join(bits) or 'Coming soon'


def first_line(s): return (s or '').strip().split('\n')[0].strip()


def describe(*texts, limit=155):
    t = ' '.join(re.sub(r'\s+', ' ', x or '').strip() for x in texts if x).strip()
    return t if len(t) <= limit else t[:limit - 1].rsplit(' ', 1)[0] + '…'


def layout(rel, path, title, desc, body, image=None, current_topic=None):
    """rel: prefix back to site root ('' or '../' ...); path: page path for canonical ('' for home)."""
    url = BASE_URL + (path + '/' if path else '')
    full_title = f"{title} · {SITE_NAME}" if title != SITE_NAME else f"{TAGLINE} · {SITE_NAME}"
    og_img = f'<meta property="og:image" content="{BASE_URL}{image}">' if image else ''
    nav = f'<a href="{rel or "./"}" {"aria-current=page" if path == "" else ""}>Home</a>' + ''.join(
        f'<a href="{rel}{t["id"]}/" {"aria-current=true" if current_topic == t["id"] else ""}>{e(t["title"])}</a>' for t in TOPICS)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
{og_img}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{rel}style.css">
</head>
<body data-root="{rel or './'}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="bar">
    <a class="brand" href="{rel or './'}"><span class="brand-small">Uncovering</span><span class="brand-big">Searchmont's History</span></a>
    <div class="bar-tools">
      <form class="search-form" action="{rel}search/" role="search">
        <label class="sr-only" for="q">Search the collection</label>
        <input id="q" name="q" type="search" placeholder="Search names, places, years…">
        <button type="submit">Search</button>
      </form>
      <button class="menu-btn" aria-expanded="false" aria-controls="topnav"><span aria-hidden="true">☰</span> Topics</button>
    </div>
  </div>
  <nav id="topnav" class="topnav" aria-label="Topics">{nav}</nav>
</header>
<main id="main" tabindex="-1">
{body}
</main>
<footer class="site-footer">
  <p>Searchmont History · Photos and documents shared by the Searchmont community.</p>
  <p>Text shown under newspaper clippings and documents was read automatically from the images and may contain errors.</p>
</footer>
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Photo viewer" hidden>
  <div class="lb-top">
    <span class="lb-count" id="lb-count"></span>
    <div class="lb-zoom" role="group" aria-label="Zoom">
      <button class="lb-btn" id="lb-zoom-out" aria-label="Zoom out">−</button>
      <button class="lb-btn lb-level" id="lb-zoom-reset" aria-label="Reset zoom" title="Reset zoom"><span id="lb-zoom-level">100%</span></button>
      <button class="lb-btn" id="lb-zoom-in" aria-label="Zoom in">+</button>
    </div>
    <a class="lb-btn" id="lb-full" target="_blank" rel="noopener">Full size ↗</a>
    <button class="lb-btn" id="lb-close" aria-label="Close viewer">✕ Close</button>
  </div>
  <div class="lb-stage" id="lb-stage">
    <button class="lb-nav prev" id="lb-prev" aria-label="Previous photo">‹</button>
    <img id="lb-img" alt="">
    <button class="lb-nav next" id="lb-next" aria-label="Next photo">›</button>
  </div>
  <p class="lb-hint">Scroll, pinch or double-click to zoom · drag to move</p>
  <p class="lb-caption" id="lb-caption"></p>
</div>
<script src="{rel}app.js"></script>
</body>
</html>
"""


def card(href, title, img, meta, rel):
    style = f' style="background-image:url(\'{rel}{thumb(img)}\')"' if img else ''
    return (f'<a class="card" href="{href}"><div class="thumb{"" if img else " empty"}"{style}>'
            f'{"" if img else "Photos coming soon"}</div><div class="body"><h3>{e(title)}</h3>'
            f'<div class="meta">{e(meta)}</div></div></a>')


def write(path, content):
    full = os.path.join(ROOT, path, 'index.html') if path else os.path.join(ROOT, 'index.html')
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8', newline='\n').write(content)


# ---------------- Home ----------------
home = data['home']
total = sum(len(photos(p)) for t in TOPICS for p in t['pages'])
cards = ''.join(card(f"{t['id']}/", t['title'], t['hero'] or first_photo(t['pages'][0]),
                     f"{len(t['pages'])} sections · {sum(len(photos(p)) for p in t['pages'])} photos", '') for t in TOPICS)
posters = ''.join(
    f'<button class="photo" data-full="images/{f}" data-caption="" aria-label="View event poster {i + 1}">'
    f'<img loading="lazy" src="{thumb(f)}" alt="Community event poster"><span class="zoom">⤢ Enlarge</span></button>'
    for i, f in enumerate(home['images'][1:]))
body = f"""
<section class="hero" style="background-image:url('images/{home['hero']}')">
  <div class="wrap"><h1>{TAGLINE}</h1>
  <p>Photos, newspaper clippings and films from the early days of Searchmont, Ontario.</p></div>
</section>
<div class="wrap section">
  <h2>Explore by topic</h2>
  <p class="lead">Choose a topic to see its photos. Click or tap any photo to view it full screen, then use the arrows (or swipe) to move between photos. Use the search box to find a name, place or year.</p>
  <div class="grid" style="margin-top:20px">{cards}</div>
  <p class="meta" style="color:var(--muted);margin-top:24px">{total} photos in the collection.</p>
</div>
<div class="wrap section events">
  <img class="logo" src="images/{home['images'][0]}" alt="Searchmont Historical Society logo" width="300" height="200">
  <div><h2>What's on at the Community Centre</h2><div class="posters">{posters}</div></div>
</div>"""
write('', layout('', '', SITE_NAME, describe(
    "Photos, newspaper clippings and films from the early days of Searchmont, Ontario: the townsite, citizens, logging dams, "
    "the lumber industry, neighbouring communities, recreation, the railway and natural resources."), body, 'images/' + home['hero']))

# ---------------- Topics & sections ----------------
search_index, urls = [], ['']
for t in TOPICS:
    hero = t['hero'] or first_photo(t['pages'][0])
    cards = ''.join(card(f"{p['id']}/", p['title'], first_photo(p), count_label(p), '../') for p in t['pages'])
    body = f"""
<section class="hero" style="background-image:url('../images/{hero}')"><div class="wrap"><h1>{e(t['title'])}</h1></div></section>
<div class="wrap section">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="../">Home</a><span>›</span>{e(t['title'])}</nav>
  {''.join(f'<p class="lead">{e(x)}</p>' for x in t['intro'])}
  <div class="grid" style="margin-top:22px">{cards}</div>
</div>"""
    write(t['id'], layout('../', t['id'], t['title'],
                          describe(' '.join(t['intro']) or f"{t['title']} in Searchmont, Ontario.",
                                   'Sections: ' + ', '.join(p['title'] for p in t['pages']) + '.'),
                          body, 'images/' + hero, t['id']))
    urls.append(t['id'])

    for idx, p in enumerate(t['pages']):
        rel, path = '../../', f"{t['id']}/{p['id']}"
        arts = []
        for si, s in enumerate(p['stories']):
            many = len(s['media']) > 1
            media, transcripts = [], []
            for m in s['media']:
                r = round(m['w'] / m['h'], 3) if m.get('w') and m.get('h') else 1.33
                flex = f' style="flex:{r} {r} {round(r * 260)}px"' if many else ''
                if 'video' in m:
                    poster = f' poster="{rel}images/{m["poster"]}"' if m.get('poster') else ''
                    media.append(f'<div{flex}><div class="film-label">Film</div><video controls preload="none" playsinline{poster} '
                                 f'src="{rel}video/{m["video"]}.mp4"></video></div>')
                    continue
                alt = m.get('alt') or first_line(s['caption']) or f"{p['title']} photo"
                if m.get('article'): alt = (first_line(s['caption']) + ' (full newspaper article)').strip()
                size = f' width="{m["w"]}" height="{m["h"]}"' if m.get('w') else ''
                src = rel + (thumb(m['src']) if many else 'images/' + m['src'])
                tag = '<span class="tag">Full article</span>' if m.get('article') else ''
                num = sum(1 for x in s['media'][:s['media'].index(m) + 1] if 'src' in x)
                if m.get('text'):
                    which = f' (image {num})' if len([x for x in s['media'] if x.get('text')]) > 1 else ''
                    transcripts.append(f'<details class="transcript"><summary>Read the text in this image{which}</summary>'
                                       f'<div class="transcript-text">{e(m["text"])}</div></details>')
                media.append(f'<figure class="item"{flex}><button class="photo" data-full="{rel}images/{m["src"]}" '
                             f'data-caption="{e(s["caption"])}" aria-label="View larger: {e(alt)}">'
                             f'<img loading="lazy" src="{src}" alt="{e(alt)}"{size}>{tag}<span class="zoom">⤢ Enlarge</span></button>'
                             f'</figure>')
            single = (len(s['media']) == 1 and 'src' in s['media'][0] and s['caption'] and not s['media'][0].get('text')
                      and s['media'][0].get('w') and s['media'][0]['w'] / s['media'][0]['h'] > 0.9)
            cap = ''
            if s['caption']:
                head, _, rest = s['caption'].partition('\n')
                cap = f'<div class="caption"><h2 class="story-title">{e(head)}</h2>{e(rest.strip())}</div>'
            media_html = f'<div class="media{" row" if many else ""}">{"".join(media)}</div>' if media else ''
            if transcripts:
                media_html += f'<div class="transcripts">{"".join(transcripts)}</div>'
            arts.append(f'<article class="story{" side" if single else ""}" id="story-{si + 1}">{cap}{media_html}</article>')
            search_index.append({'u': f"{path}/#story-{si + 1}", 'p': p['title'], 't': t['title'],
                                 'c': s['caption'], 'x': ' '.join(m.get('text', '') for m in s['media']),
                                 'i': thumb(next((m['src'] for m in s['media'] if 'src' in m), '')) if any('src' in m for m in s['media']) else ''})
        prev = t['pages'][idx - 1] if idx else None
        nxt = t['pages'][idx + 1] if idx + 1 < len(t['pages']) else None
        chips = ''.join(f'<a href="../{q["id"]}/"{" aria-current=true" if q is p else ""}>{e(q["title"])}</a>' for q in t['pages'])
        stories = f'<div class="stories">{"".join(arts)}</div>' if photos(p) or films(p) else \
            '<div class="empty-note" style="margin-top:24px">Photos for this section are coming soon.</div>'
        body = f"""
<div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{rel}">Home</a><span>›</span><a href="../">{e(t['title'])}</a><span>›</span>{e(p['title'])}</nav>
  <h1>{e(p['heading'] or p['title'])}</h1>
  {''.join(f'<p class="lead">{e(x)}</p>' for x in p['intro'])}
  <nav class="chips" aria-label="{e(t['title'])} sections">{chips}</nav>
  {stories}
  <div class="pager">
    {f'<a href="../{prev["id"]}/">‹ {e(prev["title"])}</a>' if prev else f'<a href="../">‹ {e(t["title"])}</a>'}
    {f'<a class="next" href="../{nxt["id"]}/">{e(nxt["title"])} ›</a>' if nxt else ''}
  </div>
</div>"""
        caps = [first_line(s['caption']) for s in p['stories'] if s['caption']]
        desc = describe(' '.join(p['intro']), f"{p['title']} – {t['title']}, Searchmont, Ontario.", '; '.join(caps))
        write(path, layout(rel, path, p['title'], desc, body, first_photo(p) and 'images/' + first_photo(p), t['id']))
        urls.append(path)

# ---------------- Search page ----------------
body = """
<div class="wrap section">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="../">Home</a><span>›</span>Search</nav>
  <h1>Search the collection</h1>
  <p class="lead">Searches photo captions and the text of newspaper clippings and documents.</p>
  <form class="search-big" role="search"><label class="sr-only" for="q2">Search</label>
    <input id="q2" name="q" type="search" placeholder="e.g. Sundstrom, Goulais River, 1930"><button type="submit">Search</button></form>
  <p id="search-status" class="meta" aria-live="polite"></p>
  <div id="results" class="results"></div>
</div>"""
write('search', layout('../', 'search', 'Search', 'Search photos, captions and newspaper articles from Searchmont history.', body))
json.dump(search_index, open(os.path.join(ROOT, 'search-index.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

# ---------------- Redirects for old Wix addresses ----------------
for old, new in OLD_PATHS.items():
    depth = '../' * (old.count('/') + 1)
    write(old, f'<!doctype html><meta charset="utf-8"><title>Moved</title><link rel="canonical" href="{BASE_URL}{new}/">'
               f'<meta name="robots" content="noindex"><meta http-equiv="refresh" content="0; url={depth}{new}/">'
               f'<a href="{depth}{new}/">This page has moved.</a>')

# ---------------- 404, sitemap, robots ----------------
open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(
    '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page not found · Searchmont History</title>'
    '<body style="font:18px system-ui;padding:40px;background:#f6f1e7;color:#2a241d"><h1>Page not found</h1>'
    f'<p><a href="{BASE_URL}">Go to the Searchmont History home page</a></p></body>')
today = datetime.date.today().isoformat()
open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    ''.join(f'  <url><loc>{BASE_URL}{u + "/" if u else ""}</loc><lastmod>{today}</lastmod></url>\n' for u in urls) + '</urlset>\n')
open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8').write(f'User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n')
print(f'Built {len(urls)} pages, {len(search_index)} searchable stories.')
