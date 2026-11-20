/* Searchmont History: small hash-routed site built from data.js
   Routes:  #/            home
            #/<topic>     topic overview
            #/<topic>/<page>  photos & captions                                  */
(function () {
  const SITE = window.SITE;
  const main = document.getElementById('main');
  const nav = document.getElementById('topnav');
  const menuBtn = document.querySelector('.menu-btn');

  const full = (f) => 'images/' + f;
  const thumb = (f) => 'thumbs/' + f.replace(/\.png$/, '.jpg');
  const esc = (s) => String(s || '').replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  const photosOf = (page) => page.stories.flatMap((s) => s.media.filter((m) => !m.video));
  const firstPhoto = (page) => (photosOf(page)[0] || {}).src;
  const countLabel = (page) => {
    const p = photosOf(page).length, v = page.stories.reduce((n, s) => n + s.media.filter((m) => m.video).length, 0);
    const parts = [];
    if (p) parts.push(p + (p === 1 ? ' photo' : ' photos'));
    if (v) parts.push(v + (v === 1 ? ' film' : ' films'));
    return parts.join(' · ') || 'Coming soon';
  };

  /* ---------- Navigation ---------- */
  nav.innerHTML = '<a href="#/">Home</a>' +
    SITE.topics.map((t) => `<a href="#/${t.id}">${esc(t.title)}</a>`).join('');
  menuBtn.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', open);
  });

  function card(href, title, img, meta) {
    const bg = img ? `style="background-image:url('${thumb(img)}')"` : '';
    return `<a class="card" href="${href}">
      <div class="thumb ${img ? '' : 'empty'}" ${bg}>${img ? '' : 'Photos coming soon'}</div>
      <div class="body"><h3>${esc(title)}</h3><div class="meta">${esc(meta)}</div></div></a>`;
  }

  /* ---------- Views ---------- */
  function home() {
    const total = SITE.topics.reduce((n, t) => n + t.pages.reduce((m, p) => m + photosOf(p).length, 0), 0);
    return `
      <section class="hero" style="background-image:url('${full(SITE.home.hero)}')">
        <div class="wrap">
          <h1>Uncovering Searchmont's History</h1>
          <p>Photos, newspaper clippings and films from the early days of Searchmont, Ontario.</p>
        </div>
      </section>
      <div class="wrap section">
        <h2>Explore by topic</h2>
        <p class="lead">Choose a topic to see its photos. Click or tap any photo to view it full screen, then use the arrows (or swipe) to move between photos.</p>
        <div class="grid" style="margin-top:20px">
          ${SITE.topics.map((t) => {
            const n = t.pages.reduce((m, p) => m + photosOf(p).length, 0);
            return card('#/' + t.id, t.title, t.hero || firstPhoto(t.pages[0]), `${t.pages.length} sections · ${n} photos`);
          }).join('')}
        </div>
        <p class="meta" style="color:var(--muted);margin-top:24px">${total} photos in the collection.</p>
      </div>
      <div class="wrap section events">
        <img class="logo" src="${full(SITE.home.images[0])}" alt="Searchmont Historical Society logo" width="300" height="200">
        <div>
          <h2>What's on at the Community Centre</h2>
          <div class="posters">
            ${SITE.home.images.slice(1).map((f, i) =>
              `<button class="photo" data-i="${i}" aria-label="View event poster ${i + 1}"><img loading="lazy" src="${thumb(f)}" alt="Community event poster"><span class="zoom">⤢ Enlarge</span></button>`).join('')}
          </div>
        </div>
      </div>`;
  }

  function topicView(t) {
    const heroImg = t.hero || firstPhoto(t.pages[0]);
    return `
      <section class="hero" style="background-image:url('${full(heroImg)}')">
        <div class="wrap"><h1>${esc(t.title)}</h1></div>
      </section>
      <div class="wrap section">
        <nav class="crumbs" aria-label="Breadcrumb"><a href="#/">Home</a><span>›</span>${esc(t.title)}</nav>
        ${t.intro.map((p) => `<p class="lead">${esc(p)}</p>`).join('')}
        <div class="grid" style="margin-top:22px">
          ${t.pages.map((p) => card(`#/${t.id}/${p.id}`, p.title, firstPhoto(p), countLabel(p))).join('')}
        </div>
      </div>`;
  }

  function pageView(t, p) {
    const idx = t.pages.indexOf(p);
    const prev = t.pages[idx - 1], next = t.pages[idx + 1];
    let n = 0; // running photo index for the viewer
    const stories = p.stories.map((s) => {
      const many = s.media.length > 1;
      const media = s.media.map((m) => {
        const r = m.w && m.h ? +(m.w / m.h).toFixed(3) : 1.33;
        const flex = many ? `style="flex:${r} ${r} ${Math.round(r * 260)}px"` : '';
        if (m.video) {
          return `<div ${flex}><div class="film-label">Film</div>
            <video controls preload="none" playsinline ${m.poster ? `poster="${full(m.poster)}"` : ''}
              src="video/${m.video}.mp4"></video></div>`;
        }
        const i = n++;
        const alt = m.alt || (s.caption ? s.caption.split('\n')[0] : p.title + ' photo');
        const ratio = m.w && m.h ? `width="${m.w}" height="${m.h}"` : '';
        return `<button class="photo" data-i="${i}" ${flex} aria-label="View larger: ${esc(alt)}">
          <img loading="lazy" src="${many ? thumb(m.src) : full(m.src)}" alt="${esc(alt)}" ${ratio}>
          ${m.article ? '<span class="tag">Full article</span>' : ''}<span class="zoom">⤢ Enlarge</span></button>`;
      });
      const single = s.media.length === 1 && !s.media[0].video && s.caption &&
                     s.media[0].w && s.media[0].h && s.media[0].w / s.media[0].h > 0.9;
      return `<article class="story ${single ? 'side' : ''}">
        ${s.caption ? `<div class="caption">${esc(s.caption)}</div>` : ''}
        ${media.length ? `<div class="media ${many ? 'row' : ''}">${media.join('')}</div>` : ''}
      </article>`;
    }).join('');

    const hasMedia = p.stories.some((s) => s.media.length);
    return `
      <div class="wrap">
        <nav class="crumbs" aria-label="Breadcrumb"><a href="#/">Home</a><span>›</span>
          <a href="#/${t.id}">${esc(t.title)}</a><span>›</span>${esc(p.title)}</nav>
        <h1>${esc(p.heading || p.title)}</h1>
        ${p.intro.map((x) => `<p class="lead">${esc(x)}</p>`).join('')}
        <div class="chips" aria-label="${esc(t.title)} sections">
          ${t.pages.map((q) => `<a href="#/${t.id}/${q.id}" ${q === p ? 'aria-current="true"' : ''}>${esc(q.title)}</a>`).join('')}
        </div>
        ${hasMedia ? `<div class="stories">${stories}</div>`
                   : `<div class="empty-note" style="margin-top:24px">Photos for this section are coming soon.</div>`}
        <div class="pager">
          ${prev ? `<a href="#/${t.id}/${prev.id}">‹ ${esc(prev.title)}</a>` : `<a href="#/${t.id}">‹ ${esc(t.title)}</a>`}
          ${next ? `<a class="next" href="#/${t.id}/${next.id}">${esc(next.title)} ›</a>` : ''}
        </div>
      </div>`;
  }

  function notFound() {
    return `<div class="wrap section"><h1>Page not found</h1><p><a href="#/">Back to the home page</a></p></div>`;
  }

  /* ---------- Router ---------- */
  let current = { photos: [] };
  function route() {
    const [tid, pid] = location.hash.replace(/^#\/?/, '').split('/');
    const t = SITE.topics.find((x) => x.id === tid);
    const p = t && pid ? t.pages.find((x) => x.id === pid) : null;
    let html, title = "Searchmont History";
    if (!tid) { html = home(); current.photos = SITE.home.images.slice(1).map((src) => ({ src, alt: 'Community event poster' })); }
    else if (t && !pid) { html = topicView(t); title = t.title + ' · ' + title; }
    else if (p) {
      html = pageView(t, p); title = p.title + ' · ' + title;
      current.photos = p.stories.flatMap((s) => s.media.filter((m) => !m.video).map((m) => ({ ...m, caption: s.caption })));
    } else html = notFound();

    main.innerHTML = html;
    document.title = title;
    nav.querySelectorAll('a').forEach((a) => {
      const id = a.getAttribute('href').slice(2);
      a.setAttribute('aria-current', id === (tid || '') ? 'true' : 'false');
    });
    nav.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false');
    window.scrollTo({ top: 0, behavior: 'instant' });
  }
  window.addEventListener('hashchange', route);
  route();

  /* ---------- Photo viewer ---------- */
  const lb = document.getElementById('lightbox');
  const lbImg = document.getElementById('lb-img');
  const lbCap = document.getElementById('lb-caption');
  const lbCount = document.getElementById('lb-count');
  const lbFull = document.getElementById('lb-full');
  let at = 0, lastFocus = null;

  function show(i) {
    const list = current.photos;
    at = (i + list.length) % list.length;
    const m = list[at];
    lbImg.src = full(m.src);
    lbImg.alt = m.alt || '';
    lbCap.textContent = m.caption || '';
    lbCount.textContent = `Photo ${at + 1} of ${list.length}`;
    lbFull.href = full(m.src);
    // preload neighbours
    [at + 1, at - 1].forEach((j) => { const n = list[(j + list.length) % list.length]; if (n) new Image().src = full(n.src); });
  }
  function open(i) { lastFocus = document.activeElement; lb.hidden = false; document.body.style.overflow = 'hidden'; show(i); document.getElementById('lb-close').focus(); }
  function close() { lb.hidden = true; document.body.style.overflow = ''; lbImg.src = ''; lastFocus && lastFocus.focus(); }

  main.addEventListener('click', (e) => {
    const b = e.target.closest('.photo');
    if (b) open(+b.dataset.i);
  });
  document.getElementById('lb-prev').onclick = () => show(at - 1);
  document.getElementById('lb-next').onclick = () => show(at + 1);
  document.getElementById('lb-close').onclick = close;
  document.getElementById('lb-stage').addEventListener('click', (e) => { if (e.target.id === 'lb-stage') close(); });
  document.addEventListener('keydown', (e) => {
    if (lb.hidden) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') show(at - 1);
    else if (e.key === 'ArrowRight') show(at + 1);
  });
  // swipe
  let x0 = null;
  lb.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', (e) => {
    if (x0 === null) return;
    const dx = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(dx) > 50) show(at + (dx < 0 ? 1 : -1));
  });

  /* ---------- Community-centre touch screen ----------
     Open the site with ?kiosk to return to the home page after 15 minutes idle. */
  if (/[?&]kiosk\b/.test(location.search)) {
    let timer;
    const reset = () => { clearTimeout(timer); timer = setTimeout(() => { if (!lb.hidden) close(); location.hash = '#/'; }, 15 * 60 * 1000); };
    ['pointerdown', 'keydown', 'touchstart', 'scroll'].forEach((ev) => window.addEventListener(ev, reset, { passive: true }));
    reset();
  }
})();
