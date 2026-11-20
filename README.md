# Searchmont History — rebuilt site

A simple, fast rebuild of searchmonthistory.ca that works on a PC, a phone, and the
community-centre touch screen. It is plain HTML/CSS/JavaScript: no build step, no Wix.

## What's here

| File / folder | What it is |
|---|---|
| `index.html`  | The page shell (header, menu, photo viewer) |
| `style.css`   | All styling |
| `app.js`      | Builds the pages from `data.js` and runs the photo viewer |
| `data.js`     | All the content: topics → sections → captions + photos/films |
| `images/`     | Full-size photos (max 2000px) |
| `thumbs/`     | Small versions used in grids |
| `video/`      | The short films (720p) |

## Editing content

Open `data.js`. Each section has a list of `stories`; each story has a `caption`
and a list of `media` (photos use `"src": "<file in images/>"`). To add a photo, put
the file in `images/` (and a smaller copy with the same name in `thumbs/`), then add an
entry to the right story.

## Touch screen (kiosk) mode

Open the site with `?kiosk` on the end of the address, e.g. `https://example.org/?kiosk`.
After 15 minutes with no touches it returns to the home page.

## Viewing locally

```bash
python -m http.server 8000
```

Then open http://localhost:8000

## Publishing on GitHub Pages

1. Push this folder to a GitHub repository.
2. In the repository, go to Settings → Pages, choose "Deploy from a branch", branch `main`, folder `/ (root)`.
3. The site appears at `https://<username>.github.io/<repo>/`. A custom domain
   (searchmonthistory.ca) can be pointed at it under the same settings page.
