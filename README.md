# Searchmont History: rebuilt site

A simple, fast rebuild of searchmonthistory.ca that works on a PC, a phone, and the
community-centre touch screen. It is plain HTML/CSS/JavaScript, hosted free on GitHub Pages.

Every topic and section is a real web page with its own address, title and description,
so search engines can find it. Text in newspaper clippings and documents has been read
from the images automatically (OCR) and appears under each one ("Read the text in this
image"), so it can be read, searched on the site, and found by Google.

## What's here

| File / folder | What it is |
|---|---|
| `data/site.json` | **All the content**: topics → sections → stories (caption + photos/films + text read from each image) |
| `build.py`       | Turns `data/site.json` into the web pages. Run it after any content change |
| `index.html`, `townsite/`, `lumber/`, … | The generated pages (don't edit by hand; they're overwritten by `build.py`) |
| `search/`, `search-index.json` | The site search page and its data |
| `sitemap.xml`, `robots.txt` | Help search engines find every page |
| `style.css`, `app.js` | Styling; photo viewer, menu, search and kiosk mode |
| `images/`, `thumbs/`, `video/` | Full-size photos, small versions, and films |

## Changing content

1. Edit `data/site.json`: captions are in `caption`, the text read from an image is in that photo's `text`.
   Correcting OCR mistakes there improves both the page and search results.
2. To add a photo, put it in `images/` and a smaller copy (about 640px) with the same name in `thumbs/`,
   then add `{"src": "name.jpg", "w": width, "h": height}` to a story's `media` list.
3. Run `python build.py`, then commit and push.

## When the domain moves to searchmonthistory.ca

Change `BASE_URL` at the top of `build.py` to `https://searchmonthistory.ca/`, run
`python build.py`, commit and push. Then submit `https://searchmonthistory.ca/sitemap.xml`
in Google Search Console so Google indexes every page quickly.

## Touch screen (kiosk) mode

Open the site with `?kiosk` on the end of the address. After 15 minutes with no touches
it returns to the home page.

## Viewing locally

```bash
python -m http.server 8000
```

Then open http://localhost:8000
