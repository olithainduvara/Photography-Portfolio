/* Olitha Induvara Photography: shared UI (home feed, explore, lightbox, booking) */
(() => {
  const SITE = window.SITE || {};
  const DATA = window.PORTFOLIO || { categories: [] };
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = (s = '') => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------- icons (24px stroke set) ---------------- */
  const P = {
    home: '<path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',
    grid: '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
    photography: '<path d="M4 7h3l2-3h6l2 3h3a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1V8a1 1 0 0 1 1-1z"/><circle cx="12" cy="13" r="4"/>',
    videography: '<rect x="2" y="6" width="14" height="12" rx="2"/><path d="m16 10 6-3.5v11L16 14"/>',
    aerial: '<rect x="9" y="10" width="6" height="4" rx="1.2"/><path d="M9 11 6 8m9 3 3-3M9 13l-3 3m9-3 3 3"/><ellipse cx="5" cy="7" rx="3" ry="1"/><ellipse cx="19" cy="7" rx="3" ry="1"/><ellipse cx="5" cy="17" rx="3" ry="1"/><ellipse cx="19" cy="17" rx="3" ry="1"/>',
    editing: '<path d="m14 4 6 6M4 20l4.5-1 11-11a2.1 2.1 0 0 0-3-3l-11 11z"/><path d="M3 3v4M1 5h4M19 15v4m-2-2h4"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    mail: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    chat: '<path d="M21 12a8 8 0 0 1-11.9 7L3 21l2-6A8 8 0 1 1 21 12z"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
    arrow: '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    back: '<path d="M19 12H5m6 6-6-6 6-6"/>',
    left: '<path d="m15 18-6-6 6-6"/>',
    right: '<path d="m9 18 6-6-6-6"/>',
    close: '<path d="M18 6 6 18M6 6l12 12"/>',
    play: '<path d="M7 4v16l13-8z" fill="currentColor"/>',
    pin: '<path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="9" r="2.5"/>',
    mobile: '<rect x="6" y="2" width="12" height="20" rx="3"/><circle cx="12" cy="7" r="2"/><path d="M11 18h2"/>',
    reels: '<rect x="6" y="2" width="12" height="20" rx="3"/><path d="m10.5 9 4 3-4 3z" fill="currentColor"/>',
    images: '<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="9" cy="9" r="2"/><path d="m21 15-5-5L5 21"/>',
    share: '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4m0-11-6.8 4"/>',
    calendar: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4m8-4v4"/>',
    send: '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4z"/>',
    dots: '<circle cx="5" cy="12" r="1.3" fill="currentColor"/><circle cx="12" cy="12" r="1.3" fill="currentColor"/><circle cx="19" cy="12" r="1.3" fill="currentColor"/>',
    external: '<path d="M14 4h6v6m0-6-9 9"/><path d="M19 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h5"/>',
    whatsapp: '<path d="M3 21l1.6-4.7A8.5 8.5 0 1 1 8 19.6z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1.3-1.3-2-1-1 .8a4 4 0 0 1-2.3-2.3l.8-1-1-2z" fill="currentColor" stroke="none"/>',
    facebook: '<path d="M15 3h-2.5A3.5 3.5 0 0 0 9 6.5V10H6v4h3v7h4v-7h3l1-4h-4V7a1 1 0 0 1 1-1h2z"/>',
    linkedin: '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 10v7M8 7v.01M12 17v-4a2 2 0 0 1 4 0v4m-4-7v7"/>',
  };
  const icon = (n, cls = 'icon') =>
    `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${P[n] || P.images}</svg>`;
  const catIcon = id => (P[id] ? id : 'images');
  window.UI_ICON = icon;

  /* ---------------- data helpers ---------------- */
  const cats = DATA.categories;
  const catById = id => cats.find(c => c.id === id);
  const albums = cats.flatMap(c => c.albums.map(a => Object.assign(a, { cat: c })));
  const albumUrl = a => `explore.html#${encodeURIComponent(a.category)}/${encodeURIComponent(a.id)}`;
  const frames = a => a.items.length + (a.more || 0);
  const totalFrames = albums.reduce((n, a) => n + frames(a), 0);
  const thumb = it => it.thumb || it.poster || it.src;
  const onHome = a => a.featured !== false;          // album.json "featured": false keeps it off the home page
  const isTall = it => it.h > it.w * 1.05;
  // Interleave categories so the "All" lists mix disciplines
  const interleave = keep => {
    const out = [], lists = cats.map(c => c.albums.filter(keep));
    while (lists.some(l => l.length)) lists.forEach(l => l.length && out.push(l.shift()));
    return out;
  };
  const mixed = interleave(() => true);              // Explore: everything
  const homeMixed = interleave(onHome);              // home feed: featured albums only
  const firstOnHome = c => c.albums.find(onHome);
  // feed order: pinned albums first (pin 1, 2, 3 ...), then the interleaved mix; "feed": false albums get no post
  const feedList = homeMixed.filter(a => a.pin).sort((a, b) => a.pin - b.pin)
    .concat(homeMixed.filter(a => !a.pin && a.inFeed !== false));
  const spotlight = albums.find(a => a.spotlight);
  // every vertical clip shown on the home page, reels first, then drone reels and the rest
  const reelsOf = list => list.flatMap(a => a.items
    .filter(it => it.type === 'video' && isTall(it))
    .map(it => Object.assign({}, it, { album: a, sub: `${a.cat.name} · ${a.title}` })));
  const allReels = (() => {
    const own = cats.filter(c => c.layout === 'reels');
    const pick = list => reelsOf(list.flatMap(c => c.albums).filter(onHome));
    const list = pick(own).concat(pick(cats.filter(c => !own.includes(c))));
    return list.sort((a, b) => (a.album.reelsOrder || 0) - (b.album.reelsOrder || 0));   // stable: keeps order within a group
  })();
  // frames for the 3D orbit: the first four spotlight pieces, then album covers
  const heroPicks = (() => {
    const out = (spotlight ? spotlight.items.slice(0, 4) : []).map(it => ({
      category: spotlight.category, cat: spotlight.cat, title: it.title, cover: thumb(it),
      url: albumUrl(spotlight), frames: frames(spotlight) }));
    for (const a of homeMixed) {
      if (out.length >= 12) break;
      if (a !== spotlight) out.push({ category: a.category, cat: a.cat, title: a.title, cover: a.cover, url: albumUrl(a), frames: frames(a) });
    }
    return out;
  })();
  window.PF = { cats, albums, mixed, albumUrl, frames, thumb, catById, allReels, heroPicks };

  const wa = text => `https://wa.me/${SITE.whatsapp}?text=${encodeURIComponent(text)}`;
  const openWA = text => window.open(wa(text), '_blank', 'noopener');

  let toastTimer;
  function toast(msg) {
    let t = $('.toast');
    if (!t) { t = document.createElement('div'); t.className = 'toast'; t.setAttribute('role', 'status'); document.body.append(t); }
    t.textContent = msg; t.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 2200);
  }

  async function share(title, path) {
    const link = new URL(path, location.href).href;
    try {
      if (navigator.share) return await navigator.share({ title, url: link });
      await navigator.clipboard.writeText(link);
      toast('Link copied');
    } catch (_) { /* dismissed */ }
  }

  /* ---------------- shell: rail, tab bar, topbar ---------------- */
  function shell() {
    const page = document.body.dataset.page;
    const rail = document.createElement('nav');
    rail.className = 'rail'; rail.setAttribute('aria-label', 'Sections');
    rail.innerHTML = `
      <a href="index.html" data-label="Home" data-k="home">${icon('home')}</a>
      <a href="explore.html" data-label="Explore all" data-k="all">${icon('grid')}</a>
      <hr>
      ${cats.map(c => `<a href="explore.html#${c.id}" data-label="${esc(c.name)}" data-k="${c.id}">${icon(catIcon(c.id))}</a>`).join('')}
      <hr>
      <a href="index.html#about" data-label="About" data-k="about">${icon('user')}</a>
      <a href="index.html#contact" data-label="Book a session" data-k="contact">${icon('chat')}</a>`;
    document.body.append(rail);

    const bar = document.createElement('nav');
    bar.className = 'tabbar'; bar.setAttribute('aria-label', 'Quick navigation');
    bar.innerHTML = `
      <a href="index.html" data-k="home">${icon('home')}Home</a>
      <a href="explore.html" data-k="all">${icon('grid')}Explore</a>
      <a href="explore.html#reels" data-k="reels">${icon('reels')}Reels</a>
      <a href="index.html#about" data-k="about">${icon('user')}About</a>
      <a href="index.html#contact" data-k="contact">${icon('chat')}Book</a>`;
    document.body.append(bar);

    const mark = () => {
      const k = page === 'home' ? (location.hash.slice(1) || 'home')
        : (decodeURIComponent(location.hash.slice(1)).split('/')[0] || 'all');
      $$('.rail a, .tabbar a').forEach(a => a.classList.toggle('active', a.dataset.k === k));
    };
    mark(); addEventListener('hashchange', mark);

    const top = $('.topbar');
    const onScroll = () => top && top.classList.toggle('scrolled', scrollY > 30);
    onScroll(); addEventListener('scroll', onScroll, { passive: true });

    const s = $('#siteSearch');
    if (s) s.addEventListener('keydown', e => {
      if (e.key !== 'Enter') return;
      const q = s.value.trim();
      if (page === 'explore') { history.replaceState(null, '', `explore.html${q ? '?q=' + encodeURIComponent(q) : ''}`); window.dispatchEvent(new Event('hashchange')); }
      else location.href = `explore.html${q ? '?q=' + encodeURIComponent(q) : ''}`;
    });

    $$('[data-site]').forEach(n => { n.textContent = SITE[n.dataset.site] || ''; });
    $$('[data-wa]').forEach(a => { a.href = wa(a.dataset.wa || `Hi ${SITE.name}!`); a.target = '_blank'; a.rel = 'noopener'; });
    $$('[data-href]').forEach(a => { const v = SITE[a.dataset.href]; if (v) a.href = a.dataset.href === 'email' ? `mailto:${v}` : v; });
    const y = $('#year'); if (y) y.textContent = new Date().getFullYear();
  }

  /* ---------------- reveal on scroll ---------------- */
  function reveal() {
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
    }), { threshold: .12, rootMargin: '0px 0px -40px 0px' });
    $$('.reveal').forEach(n => io.observe(n));
  }

  /* ---------------- lightbox ---------------- */
  const LB = (() => {
    let root, items = [], idx = 0, meta = {}, lastFocus;
    function build() {
      root = document.createElement('div');
      root.className = 'lightbox'; root.setAttribute('role', 'dialog'); root.setAttribute('aria-modal', 'true'); root.setAttribute('aria-label', 'Media viewer');
      root.innerHTML = `
        <div class="lb-top">
          <div><div class="lb-title"></div><div class="lb-sub"></div></div>
          <span class="lb-count"></span>
          <button class="sq-btn lb-close" aria-label="Close">${icon('close')}</button>
        </div>
        <div class="lb-stage">
          <button class="lb-nav lb-prev" aria-label="Previous">${icon('left')}</button>
          <div class="lb-media"></div>
          <button class="lb-nav lb-next" aria-label="Next">${icon('right')}</button>
        </div>
        <div class="lb-strip"></div>`;
      document.body.append(root);
      $('.lb-close', root).onclick = close;
      $('.lb-prev', root).onclick = () => go(idx - 1);
      $('.lb-next', root).onclick = () => go(idx + 1);
      $('.lb-stage', root).addEventListener('click', e => { if (e.target.classList.contains('lb-stage')) close(); });
      addEventListener('keydown', e => {
        if (!root.classList.contains('open')) return;
        if (e.key === 'Escape') close();
        if (e.key === 'ArrowLeft') go(idx - 1);
        if (e.key === 'ArrowRight') go(idx + 1);
      });
      let x0 = null;
      root.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
      root.addEventListener('touchend', e => {
        if (x0 === null) return;
        const dx = e.changedTouches[0].clientX - x0; x0 = null;
        if (Math.abs(dx) > 50) go(idx + (dx < 0 ? 1 : -1));
      });
    }
    function render() {
      const it = items[idx], m = $('.lb-media', root);
      m.style.cssText = 'display:grid;place-items:center;width:100%;height:100%;min-height:0';
      m.innerHTML = it.type === 'video'
        ? `<video src="${it.src}" ${it.poster ? `poster="${it.poster}"` : ''} controls autoplay playsinline style="max-height:calc(100svh - 190px)"></video>`
        : `<img src="${it.src}" alt="${esc(it.title)}" style="max-height:calc(100svh - 190px)">`;
      $('.lb-title', root).textContent = it.title || meta.title || '';
      $('.lb-sub', root).textContent = it.sub || meta.sub || '';
      $('.lb-count', root).textContent = `${idx + 1} / ${items.length}`;
      $$('.lb-strip button', root).forEach((b, i) => b.classList.toggle('active', i === idx));
      const act = $('.lb-strip .active', root);
      act && act.scrollIntoView({ block: 'nearest', inline: 'center', behavior: reduceMotion ? 'auto' : 'smooth' });
      const multi = items.length > 1;
      $('.lb-prev', root).hidden = $('.lb-next', root).hidden = !multi;
      $('.lb-strip', root).hidden = !multi;
    }
    function go(i) { idx = (i + items.length) % items.length; render(); }
    function open(list, i = 0, m = {}) {
      if (!root) build();
      items = list; meta = m; idx = i; lastFocus = document.activeElement;
      $('.lb-strip', root).innerHTML = items.map((it, j) =>
        `<button aria-label="Show ${esc(it.title)}" data-i="${j}"><img src="${thumb(it)}" alt="" loading="lazy"></button>`).join('');
      $$('.lb-strip button', root).forEach(b => b.onclick = () => go(+b.dataset.i));
      render();
      root.classList.add('open'); document.documentElement.style.overflow = 'hidden';
      $('.lb-close', root).focus();
    }
    function close() {
      root.classList.remove('open'); document.documentElement.style.overflow = '';
      const v = $('video', root); v && v.pause();
      setTimeout(() => { if (!root.classList.contains('open')) $('.lb-media', root).innerHTML = ''; }, 300);
      lastFocus && lastFocus.focus();
    }
    return { open };
  })();
  const openAlbum = (a, i = 0) => LB.open(a.items, i, { title: a.title, sub: `${a.cat.name}${a.location ? ' · ' + a.location : ''}` });

  /* ---------------- reels (vertical players) ---------------- */
  const canHover = matchMedia('(hover: hover)').matches;
  function reelCard(r, i) {
    return `
      <article class="reel" data-i="${i}" tabindex="0" role="button" aria-label="Play ${esc(r.title)}">
        <video muted loop playsinline preload="none" poster="${r.thumb || r.poster || ''}" data-src="${r.src}"></video>
        <span class="reel-play">${icon('play')}</span>
        <div class="reel-meta">
          <span class="chip">${esc(r.album.cat.short)}</span>
          <b>${esc(r.title)}</b>
          <small>${esc(r.album.title)}</small>
        </div>
        <span class="reel-bar"><i></i></span>
      </article>`;
  }
  function wireReels(box, list) {
    const cards = $$('.reel', box);
    const play = card => {
      const v = $('video', card);
      if (!v.src) v.src = v.dataset.src;
      v.play().then(() => card.classList.add('playing')).catch(() => {});
    };
    const stop = card => { const v = $('video', card); v.pause(); card.classList.remove('playing'); };
    cards.forEach(card => {
      const v = $('video', card), bar = $('.reel-bar i', card);
      v.addEventListener('timeupdate', () => { bar.style.width = `${(v.currentTime / (v.duration || 1)) * 100}%`; });
      const open = () => { stop(card); LB.open(list, +card.dataset.i, { title: 'Reels' }); };
      card.addEventListener('click', open);
      card.addEventListener('keydown', e => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), open()));
      if (canHover && !reduceMotion) {
        card.addEventListener('mouseenter', () => play(card));
        card.addEventListener('mouseleave', () => stop(card));
      }
    });
    if (!canHover && !reduceMotion) { // touch: preview whichever reel is mostly on screen
      const io = new IntersectionObserver(es => es.forEach(e => (e.intersectionRatio > 0.8 ? play : stop)(e.target)), { threshold: [0, 0.8] });
      cards.forEach(c => io.observe(c));
    }
  }
  function reelsHome() {
    const row = $('#reelsRow');
    if (!row) return;
    row.innerHTML = allReels.map(reelCard).join('');
    wireReels(row, allReels);
    const n = $('#reelCount'); if (n) n.textContent = allReels.length;

    const stage = $('#reelsStage'), cards = $$('.reel', row), bar = $('#reelsProgress');
    const prev = $('.reels-side.prev', stage), next = $('.reels-side.next', stage);
    cards.forEach((c, i) => c.style.setProperty('--i', i));
    const smooth = reduceMotion ? 'auto' : 'smooth';
    const stepPx = () => (cards[0] ? cards[0].offsetWidth + 18 : 250);
    const page = () => Math.max(stepPx(), Math.floor(row.clientWidth / stepPx()) * stepPx() - stepPx());

    // 3D curve: cards lean away and dim slightly as they move toward the edges
    let raf = 0;
    function shape() {
      raf = 0;
      const max = row.scrollWidth - row.clientWidth, x = row.scrollLeft;
      const r = row.getBoundingClientRect(), mid = r.left + r.width / 2;
      cards.forEach(c => {
        const b = c.getBoundingClientRect();
        const t = Math.max(-1, Math.min(1, (b.left + b.width / 2 - mid) / (r.width / 2)));  // -1 left edge … 1 right edge
        c.style.setProperty('--ry', `${reduceMotion ? 0 : -t * 16}deg`);
        c.style.setProperty('--sc', reduceMotion ? 1 : (1 - Math.abs(t) * 0.07).toFixed(3));
        c.style.setProperty('--edge', (1 - Math.abs(t) * 0.25).toFixed(3));
      });
      prev.classList.toggle('off', x < 8);
      next.classList.toggle('off', x > max - 8);
      row.style.setProperty('--fl', x < 8 ? '0px' : '80px');
      row.style.setProperty('--fr', x > max - 8 ? '0px' : '80px');
      const shown = row.clientWidth / row.scrollWidth;
      bar.style.width = `${shown * 100}%`;
      bar.style.marginLeft = `${max ? (x / max) * (1 - shown) * 100 : 0}%`;
    }
    const queue = () => { if (!raf) raf = requestAnimationFrame(shape); };
    row.addEventListener('scroll', queue, { passive: true });
    addEventListener('resize', queue);

    // auto-advance one reel at a time; pauses on hover, touch and while a reel previews
    let pausedUntil = 0, visible = false;
    const hold = ms => { pausedUntil = performance.now() + ms; };
    stage.addEventListener('mouseenter', () => hold(Infinity));
    stage.addEventListener('mouseleave', () => hold(1500));
    row.addEventListener('pointerdown', () => hold(8000), { passive: true });
    row.addEventListener('wheel', () => hold(6000), { passive: true });
    setInterval(() => {
      if (reduceMotion || !visible || document.hidden || performance.now() < pausedUntil || $('.reel.playing', row)) return;
      const atEnd = row.scrollLeft > row.scrollWidth - row.clientWidth - 8;
      atEnd ? row.scrollTo({ left: 0, behavior: smooth }) : row.scrollBy({ left: stepPx(), behavior: smooth });
    }, 3600);

    [prev, next].forEach(b => b.addEventListener('click', () => {
      hold(7000);
      row.scrollBy({ left: +b.dataset.scroll * page(), behavior: smooth });
    }));
    row.tabIndex = 0;
    row.addEventListener('keydown', e => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); hold(7000); row.scrollBy({ left: (e.key === 'ArrowRight' ? 1 : -1) * stepPx(), behavior: smooth }); }
    });

    new IntersectionObserver(([e]) => {
      visible = e.isIntersecting;
      if (visible) { stage.classList.add('in'); queue(); }
    }, { threshold: 0.25 }).observe(stage);
    shape();
  }

  /* ---------------- HOME: films (landscape & square videos, player + playlist) ---------------- */
  function filmsHome() {
    const screen = $('#filmScreen');
    if (!screen) return;
    const groups = cats.filter(c => c.layout !== 'reels').flatMap(c => c.albums).filter(onHome)
      .map(a => ({ a, list: a.items.filter(it => it.type === 'video' && !isTall(it))
        .map(it => Object.assign({}, it, { album: a, sub: `${a.cat.name} · ${a.title}` })) }))
      .filter(g => g.list.length);
    if (!groups.length) { $('#films').hidden = true; return; }
    $('#filmCount').textContent = groups.reduce((n, g) => n + g.list.length, 0);

    const v = $('#filmVideo'), list = $('#filmList'), tabs = $('#filmTabs'), bar = $('#filmProgress');
    let gi = 0, ii = 0, inView = false, swapTimer;
    tabs.innerHTML = groups.map((g, k) =>
      `<button class="pill${k ? '' : ' active'}" data-g="${k}" role="tab">${icon(catIcon(g.a.category))}${esc(g.a.title)} <span class="count">${g.list.length}</span></button>`).join('');

    function drawList() {
      list.innerHTML = groups[gi].list.map((it, k) => `
        <li class="film-item${k === ii ? ' active' : ''}" data-i="${k}" tabindex="0" style="animation-delay:${k * 40}ms">
          <span class="film-thumb"><img src="${thumb(it)}" alt="" loading="lazy"><span class="num">${String(k + 1).padStart(2, '0')}</span></span>
          <span><b>${esc(it.title)}</b><small>${esc(it.album.cat.name)}</small></span>
        </li>`).join('');
    }
    function load(play) {
      const it = groups[gi].list[ii];
      v.poster = it.poster || thumb(it);
      v.src = it.src;
      // absolute URL: a relative url() inside a custom property resolves against css/, not the page
      screen.style.setProperty('--poster', `url("${new URL(it.poster || thumb(it), location.href).href}")`);
      $('#filmChip').textContent = it.album.cat.short;
      $('#filmTitle').textContent = it.title;
      $('#filmAlbum').textContent = `${it.album.title}${it.album.location ? ' · ' + it.album.location : ''}`;
      $('#filmOpen').href = albumUrl(it.album);
      $$('.film-item', list).forEach(li => li.classList.toggle('active', +li.dataset.i === ii));
      const act = $('.film-item.active', list);
      if (act) list.scrollTo({ top: act.offsetTop - list.clientHeight / 2 + act.offsetHeight / 2, behavior: reduceMotion ? 'auto' : 'smooth' });
      bar.style.width = '0%';
      if (play && inView && !reduceMotion) v.play().catch(() => {});
    }
    function show(g, i) {
      const changedGroup = g !== gi;
      gi = g; ii = i;
      $$('.pill', tabs).forEach(p => p.classList.toggle('active', +p.dataset.g === gi));
      if (changedGroup) drawList();
      if (reduceMotion) return load(false);
      screen.classList.add('switching');
      clearTimeout(swapTimer);
      swapTimer = setTimeout(() => { load(true); setTimeout(() => screen.classList.remove('switching'), 120); }, 420);
    }
    tabs.addEventListener('click', e => { const b = e.target.closest('.pill'); b && show(+b.dataset.g, 0); });
    list.addEventListener('click', e => { const li = e.target.closest('.film-item'); li && show(gi, +li.dataset.i); });
    list.addEventListener('keydown', e => {
      const li = e.target.closest('.film-item');
      if (li && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); show(gi, +li.dataset.i); }
    });
    // previews play muted and roll on to the next film in the collection
    v.addEventListener('ended', () => show(gi, (ii + 1) % groups[gi].list.length));
    v.addEventListener('timeupdate', () => { bar.style.width = `${(v.currentTime / (v.duration || 1)) * 100}%`; });
    $('#filmPlay').addEventListener('click', () => { v.pause(); LB.open(groups[gi].list, ii, { title: groups[gi].a.title }); });
    new IntersectionObserver(([e]) => {
      inView = e.isIntersecting;
      if (inView && !reduceMotion) v.play().catch(() => {}); else v.pause();
    }, { threshold: 0.35 }).observe(screen);

    drawList();
    load(false);
  }

  /* ---------------- HOME: spotlight coverflow (album.json "spotlight": true) ---------------- */
  function spotlightHome() {
    const box = $('#coverflow');
    if (!box) return;
    if (!spotlight) { $('#spotlight').hidden = true; return; }
    const items = spotlight.items, n = items.length;
    $('#spotTitle').textContent = spotlight.title;
    $('#spotDesc').textContent = spotlight.description;
    $('#spotOpen').href = albumUrl(spotlight);
    box.innerHTML = items.map((it, i) =>
      `<button class="cf-card" data-i="${i}" aria-label="${esc(it.title)}" data-ar="${it.w / it.h}"><img src="${thumb(it)}" alt="${esc(it.title)}" loading="lazy" draggable="false"></button>`).join('');
    const cards = $$('.cf-card', box);
    let active = 0, timer = null, hovering = false, inView = false;
    function layout() {
      const H = box.clientHeight * 0.86, step = Math.min(box.clientWidth * 0.2, H * 0.48);
      cards.forEach((c, i) => {
        let o = i - active;
        if (o > n / 2) o -= n;
        if (o < -n / 2) o += n;                      // loop around
        const a = Math.abs(o), w = Math.min(H * +c.dataset.ar, H * 1.5);
        c.style.width = `${w}px`; c.style.height = `${H}px`;
        c.style.transform = `translate(-50%, -50%) translateX(${o * step + Math.sign(o) * w * 0.22}px) translateZ(${-a * 170}px) rotateY(${-Math.sign(o) * Math.min(a, 1) * 38}deg) scale(${1 - Math.min(a, 3) * 0.1})`;
        c.style.opacity = a > 3 ? 0 : 1 - a * 0.16;
        c.style.filter = `brightness(${1 - Math.min(a, 3) * 0.22})`;
        c.style.zIndex = 50 - a;
        c.classList.toggle('active', o === 0);
        c.tabIndex = o === 0 ? 0 : -1;
      });
      $('#spotCaption').textContent = items[active].title;
      $('#spotCount').textContent = `${String(active + 1).padStart(2, '0')} / ${String(n).padStart(2, '0')}`;
    }
    const go = i => { active = (i + n) % n; layout(); };
    const tick = () => { clearInterval(timer); if (!reduceMotion && inView && !hovering) timer = setInterval(() => go(active + 1), 4200); };
    let x0 = null, swiped = false;
    box.addEventListener('pointerdown', e => { x0 = e.clientX; swiped = false; });
    box.addEventListener('pointerup', e => {
      if (x0 !== null && Math.abs(e.clientX - x0) > 40) { swiped = true; go(active + (e.clientX < x0 ? 1 : -1)); }
      x0 = null;
    });
    box.addEventListener('click', e => {
      const c = e.target.closest('.cf-card');
      if (!c || swiped) return;
      const i = +c.dataset.i;
      i === active ? LB.open(items, i, { title: spotlight.title, sub: `${spotlight.cat.name} · ${spotlight.title}` }) : go(i);
    });
    $('#spotPrev').onclick = () => go(active - 1);
    $('#spotNext').onclick = () => go(active + 1);
    box.addEventListener('keydown', e => { if (e.key === 'ArrowLeft') go(active - 1); if (e.key === 'ArrowRight') go(active + 1); });
    box.addEventListener('mouseenter', () => { hovering = true; tick(); });
    box.addEventListener('mouseleave', () => { hovering = false; tick(); });
    new IntersectionObserver(([e]) => { inView = e.isIntersecting; tick(); }).observe(box);
    addEventListener('resize', layout);
    layout();
  }

  /* ---------------- HOME: studio feed ---------------- */
  function postHTML(a) {
    const shown = a.items.slice(0, 3);
    const rest = frames(a) - shown.length;
    const media = shown.map((it, i) => `
      <button class="m" data-i="${i}" aria-label="Open ${esc(it.title)}">
        <img src="${thumb(it)}" alt="${esc(it.title)}" loading="lazy">
        ${it.type === 'video' ? `<span class="play-badge">${icon('play')}Clip</span>` : ''}
        ${i === shown.length - 1 && rest > 0 ? `<span class="plus">+${rest}</span>` : ''}
      </button>`).join('');
    return `
      <article class="panel post" data-album="${a.category}/${a.id}">
        <header class="post-head">
          <img src="assets/avatar.jpg" alt="">
          <div class="who"><b>${esc(SITE.name)}</b> posted in <a href="explore.html#${a.category}">${esc(a.cat.name)}</a>
            <small>${a.location ? esc(a.location) + ' · ' : ''}${frames(a)} frames</small></div>
          <a class="sq-btn more" href="${albumUrl(a)}" aria-label="Open album">${icon('dots')}</a>
        </header>
        <h3 class="post-title">${esc(a.title)}</h3>
        ${a.description ? `<p class="post-text">${esc(a.description)}</p>` : ''}
        <div class="post-media n${Math.min(shown.length, 3)}${isTall(shown[0]) && shown.filter(isTall).length * 2 > shown.length ? ' tall' : ''}">${media}</div>
        <footer class="post-foot">
          <span class="count">${a.items.length} on site${a.more ? ` · +${a.more} on Facebook` : ''}</span>
          <a class="act" href="${albumUrl(a)}">${icon('images')}<span>Open album</span></a>
          <button class="act" data-share>${icon('share')}<span>Share</span></button>
          <a class="act" data-book>${icon('calendar')}<span>Book similar</span></a>
        </footer>
      </article>`;
  }

  function home() {
    const tabs = $('#feedTabs');
    if (!tabs) return;
    const FIRST = 3, MORE = 4;
    let filter = 'all', limit = FIRST;

    tabs.innerHTML = [{ id: 'all', short: 'All', n: feedList.length }]
      .concat(cats.map(c => ({ id: c.id, short: c.short, n: feedList.filter(a => a.category === c.id).length, c })).filter(t => t.n))
      .map(t => `<button class="pill${t.id === 'all' ? ' active' : ''}" data-f="${t.id}" role="tab">${t.c ? icon(catIcon(t.id)) : ''}${esc(t.id === 'all' ? 'All work' : t.c.name)} <span class="count">${t.n}</span></button>`).join('');

    function draw() {
      const list = filter === 'all' ? feedList : feedList.filter(a => a.category === filter);
      $('#posts').innerHTML = list.slice(0, limit).map(postHTML).join('');
      const more = $('#feedMore');
      more.hidden = list.length <= limit;
      more.innerHTML = `Show more ${filter === 'all' ? '' : esc(catById(filter).short.toLowerCase()) + ' '}albums ${icon('arrow')}`;
      $$('.pill', tabs).forEach(p => p.classList.toggle('active', p.dataset.f === filter));
      $$('.orbit-sat').forEach(s => s.classList.toggle('active', s.dataset.f === filter));
    }
    function setFilter(f, scroll) {
      filter = f; limit = FIRST; draw();
      if (scroll) $('#studio').scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth' });
    }
    tabs.addEventListener('click', e => { const b = e.target.closest('.pill'); b && setFilter(b.dataset.f); });
    $('#feedMore').onclick = () => { limit += MORE; draw(); };

    $('#posts').addEventListener('click', e => {
      const post = e.target.closest('.post'); if (!post) return;
      const [c, id] = post.dataset.album.split('/');
      const a = albums.find(x => x.category === c && x.id === id);
      const m = e.target.closest('.m');
      if (m) return openAlbum(a, +m.dataset.i);
      if (e.target.closest('[data-share]')) return share(a.title, albumUrl(a));
      if (e.target.closest('[data-book]')) { e.preventDefault(); openWA(`Hi ${SITE.name}! I saw your "${a.title}" album (${a.cat.name}) and I'd love something similar. `); }
    });

    // composer → WhatsApp
    const comp = $('#composer');
    comp.addEventListener('submit', e => {
      e.preventDefault();
      const v = $('input', comp).value.trim();
      openWA(`Hi ${SITE.name}! ${v || "I'd like to book a session."}`);
    });

    // orbit of disciplines
    const orbit = $('#orbit');
    const sats = cats.map((c, i) => {
      const b = document.createElement('button');
      b.className = 'orbit-sat'; b.dataset.f = c.id; b.title = c.name;
      b.innerHTML = `<img src="${firstOnHome(c) ? firstOnHome(c).cover : ''}" alt=""><span>${esc(c.short)}</span>`;
      b.onclick = () => setFilter(filter === c.id ? 'all' : c.id, innerWidth < 1060);
      orbit.append(b);
      return { b, phase: (i / cats.length) * Math.PI * 2 };
    });
    let t = 0, last = performance.now(), orbitOn = true;
    new IntersectionObserver(([e]) => { orbitOn = e.isIntersecting; }).observe(orbit);
    (function spin(now) {
      const dt = Math.min(50, now - last); last = now;
      if (orbitOn && !reduceMotion && !orbit.matches(':hover')) t += dt * 0.00018;
      const w = orbit.clientWidth, h = orbit.clientHeight, rx = w * 0.46, ry = h * 0.29;
      sats.forEach(({ b, phase }) => {
        const a = t + phase, z = Math.sin(a);           // z: -1 back … 1 front
        const s = 0.78 + (z + 1) * 0.16;
        b.style.transform = `translate(${w / 2 + Math.cos(a) * rx}px, ${h / 2 + z * ry}px) scale(${s})`;
        b.style.zIndex = z > 0 ? 6 : 4;
        b.style.opacity = 0.6 + (z + 1) * 0.2;
      });
      requestAnimationFrame(spin);
    })(last);

    // featured photographer
    $('#featuredStats').textContent = `${albums.length} albums · ${totalFrames}+ frames`;

    // latest: first album of each discipline
    $('#latest').innerHTML = cats.filter(firstOnHome).slice(0, 4).map(c => {
      const a = firstOnHome(c);
      return `<a class="row" href="${albumUrl(a)}"><img src="${a.cover}" alt="" loading="lazy"><div><b>${esc(a.title)}</b><small>${esc(c.name)} · ${frames(a)} frames</small></div></a>`;
    }).join('');

    // booking
    $('#booking').innerHTML = (SITE.booking || []).map((b, i) =>
      `<a class="row" href="${wa(`Hi ${SITE.name}! I'd like to ask about ${b.title.toLowerCase()}.`)}" target="_blank" rel="noopener"><span class="ic">${icon(['photography', 'videography', 'aerial'][i] || 'calendar')}</span><div><b>${esc(b.title)}</b><small>${esc(b.note)}</small></div></a>`).join('');

    draw();

    // hero area chips + fallback
    $('#heroAreas').innerHTML = cats.map(c => `<a href="explore.html#${c.id}" data-cat="${c.id}">${icon(catIcon(c.id))}${esc(c.name)}</a>`).join('');
    $$('#heroAreas a').forEach(a => a.addEventListener('mouseenter', () => window.hero3d && window.hero3d.focus(a.dataset.cat)));
    $('#heroFan').innerHTML = homeMixed.slice(0, 3).reverse().map((a, i) =>
      `<img src="${a.cover}" alt="" style="transform: translate3d(${(i - 1) * 70}px, ${(1 - i) * 18}px, ${i * 40}px) rotate(${(i - 1) * 6}deg)">`).join('');

    // about
    $('#bio').innerHTML = (SITE.bio || []).map(p => `<p>${esc(p)}</p>`).join('');
    $('#stats').innerHTML = (SITE.stats || []).map(s => `<div class="stat"><b>${esc(s.value)}</b><small>${esc(s.label)}</small></div>`).join('');
    $('#aboutTags').innerHTML = cats.flatMap(c => c.tags || []).map(t => `<span class="tag">${esc(t)}</span>`).join('');
    const card = $('.portrait-card');
    if (card && !reduceMotion) {
      card.parentElement.addEventListener('pointermove', e => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        card.style.setProperty('--ry', `${x * 16}deg`); card.style.setProperty('--rx', `${-y * 12}deg`);
      });
      card.parentElement.addEventListener('pointerleave', () => { card.style.removeProperty('--ry'); card.style.removeProperty('--rx'); });
    }

    // contact form → WhatsApp
    const sel = $('#cf-service');
    sel.innerHTML = '<option value="">Choose a service</option>' + cats.map(c => `<option>${esc(c.name)}</option>`).join('') + '<option>Something else</option>';
    $('#contactForm').addEventListener('submit', e => {
      e.preventDefault();
      const f = new FormData(e.target);
      const lines = [`Hi ${SITE.name}! I'm ${f.get('name')}.`];
      if (f.get('service')) lines.push(`Service: ${f.get('service')}`);
      if (f.get('date')) lines.push(`Date: ${f.get('date')}`);
      lines.push('', f.get('message'));
      openWA(lines.join('\n'));
    });
  }

  /* ---------------- EXPLORE ---------------- */
  function albumCard(a, i) {
    const pics = a.items.slice(0, 3);
    const vids = a.items.filter(x => x.type === 'video').length;
    return `
      <a class="album${a.coverH > a.coverW * 1.05 ? ' tall' : ''}" href="${albumUrl(a)}" style="animation-delay:${i * 60}ms">
        <div class="stack">
          ${pics.map((it, j) => `<div class="f"><img src="${j === 0 ? a.cover : thumb(it)}" alt="" loading="lazy"></div>`).join('')}
          <span class="badge">${icon(vids ? 'videography' : 'images')}${frames(a)}${vids ? ` · ${vids} clip${vids > 1 ? 's' : ''}` : ''}</span>
        </div>
        <div class="album-meta">
          <span class="chip">${esc(a.cat.short)}</span>
          <h3>${esc(a.title)}</h3>
          ${a.location ? `<small>${icon('pin')}${esc(a.location)}</small>` : ''}
        </div>
      </a>`;
  }

  function explore() {
    const view = $('#view');
    if (!view) return;
    const tabsHTML = active => `
      <div class="tabs" role="tablist">
        <a class="pill${active === 'all' ? ' active' : ''}" href="explore.html">All <span class="count">${albums.length}</span></a>
        ${cats.map(c => `<a class="pill${active === c.id ? ' active' : ''}" href="explore.html#${c.id}">${icon(catIcon(c.id))}${esc(c.name)} <span class="count">${c.albums.length}</span></a>`).join('')}
      </div>`;

    function route() {
      const q = new URLSearchParams(location.search).get('q') || '';
      const [cId, aId] = decodeURIComponent(location.hash.slice(1)).split('/');
      const c = catById(cId);
      const a = c && aId && c.albums.find(x => x.id === aId);
      const s = $('#siteSearch'); if (s && document.activeElement !== s) s.value = q;
      scrollTo({ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' });

      if (a) {
        document.title = `${a.title} · ${SITE.brand}`;
        view.innerHTML = `
          <header class="page-head"><div class="wrap">
            <nav class="crumbs"><a href="explore.html">Explore</a>${icon('right')}<a href="explore.html#${c.id}">${esc(c.name)}</a>${icon('right')}<span>${esc(a.title)}</span></nav>
            <div class="album-head">
              <div>
                <span class="chip">${esc(c.name)}</span>
                <h1 class="h2">${esc(a.title)}</h1>
                ${a.description ? `<p class="lead">${esc(a.description)}</p>` : ''}
                <div class="meta">
                  ${a.location ? `<span>${icon('pin')}${esc(a.location)}</span>` : ''}
                  ${a.date ? `<span>${icon('calendar')}${esc(a.date)}</span>` : ''}
                  <span>${icon('images')}${a.items.length} on site${a.more ? ` · +${a.more} on Facebook` : ''}</span>
                </div>
              </div>
              <div class="album-actions">
                <a class="btn btn-ghost btn-sm" href="explore.html#${c.id}">${icon('back')}All ${esc(c.short.toLowerCase())} albums</a>
                <button class="btn btn-ghost btn-sm" id="shareAlbum">${icon('share')}Share</button>
                <a class="btn btn-gold btn-sm" href="${wa(`Hi ${SITE.name}! I saw your "${a.title}" album and I'd love something similar.`)}" target="_blank" rel="noopener">${icon('calendar')}Book similar</a>
              </div>
            </div>
          </div></header>
          <div class="wrap">
            <div class="masonry">
              ${a.items.map((it, i) => `
                <figure class="tile" tabindex="0" role="button" data-i="${i}" style="animation-delay:${Math.min(i, 12) * 50}ms">
                  <img src="${thumb(it)}" alt="${esc(it.title)}" loading="lazy" width="${it.w}" height="${it.h}">
                  ${it.type === 'video' ? `<span class="play-badge">${icon('play')}Play clip</span>` : ''}
                  <figcaption>${esc(it.title)}</figcaption>
                </figure>`).join('')}
            </div>
            ${a.link ? `
              <div class="fb-more">
                <div><b>${a.more ? `+${a.more} more frames on Facebook` : 'See the full set on Facebook'}</b><p>The complete album lives on the ${esc(SITE.brand)} page.</p></div>
                <a class="btn btn-ghost" href="${esc(a.link)}" target="_blank" rel="noopener">${icon('facebook')}Open full album${icon('external')}</a>
              </div>` : '<div style="height:40px"></div>'}
          </div>`;
        $$('.tile', view).forEach(t => {
          const go = () => openAlbum(a, +t.dataset.i);
          t.onclick = go; t.onkeydown = e => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), go());
        });
        $('#shareAlbum').onclick = () => share(a.title, albumUrl(a));
        return;
      }

      if (c && c.layout === 'reels' && !q) {
        document.title = `${c.name} · ${SITE.brand}`;
        const own = reelsOf(c.albums);
        const groups = cats.filter(o => o !== c).map(o => ({ c: o, list: allReels.filter(r => r.album.category === o.id) })).filter(g => g.list.length);
        const others = groups.flatMap(g => g.list);
        const block = (title, sub, list, offset) => list.length ? `
          <div class="reels-block">
            <div class="reels-block-head"><h2>${title}</h2><span>${sub}</span></div>
            <div class="reels-grid">${list.map((r, i) => reelCard(r, i + offset)).join('')}</div>
          </div>` : '';
        view.innerHTML = `
          <header class="page-head"><div class="wrap">
            <nav class="crumbs"><a href="index.html">Home</a>${icon('right')}<a href="explore.html">Explore</a>${icon('right')}<span>${esc(c.name)}</span></nav>
            <div class="cat-intro">
              <div>
                <span class="eyebrow">${esc(c.tagline)}</span>
                <h1 class="h2">Stories in <em>motion</em></h1>
                <p class="lead">${esc(c.description)} ${canHover ? 'Hover to preview, click to watch with sound.' : 'Tap to watch with sound.'}</p>
              </div>
              <div class="tags">${c.tags.map(t => `<span class="tag">${esc(t)}</span>`).join('')}</div>
            </div>
            <div class="explore-bar">${tabsHTML(c.id)}</div>
          </div></header>
          <div class="wrap" id="reelsWrap">
            ${block('Reels', `${own.length} films`, own, 0)}
            ${groups.map((g, k) => block(g.c.id === 'aerial' ? 'Drone reels' : `${esc(g.c.name)} clips`, `From ${esc(g.c.name)}`, g.list,
                own.length + groups.slice(0, k).reduce((n, x) => n + x.list.length, 0))).join('')}
            <div style="height:60px"></div>
          </div>`;
        wireReels($('#reelsWrap'), own.concat(others));
        return;
      }

      const needle = q.toLowerCase();
      let list = c ? c.albums : mixed;
      if (needle) list = list.filter(x => [x.title, x.description, x.location, x.cat.name, ...x.items.map(i => i.title)].join(' ').toLowerCase().includes(needle));
      document.title = `${c ? c.name : 'Explore'} · ${SITE.brand}`;
      view.innerHTML = `
        <header class="page-head"><div class="wrap">
          <nav class="crumbs"><a href="index.html">Home</a>${icon('right')}<span>Explore</span>${c ? `${icon('right')}<span>${esc(c.name)}</span>` : ''}</nav>
          <div class="cat-intro">
            <div>
              <span class="eyebrow">${c ? esc(c.tagline || 'Albums') : 'The archive'}</span>
              <h1 class="h2">${c ? esc(c.name) : 'Explore the <em>work</em>'}</h1>
              <p class="lead">${c ? esc(c.description) : 'Every album, folder by folder: photography, videography, aerial cinematography and editing. Open a stack to see the frames inside.'}</p>
            </div>
            ${c && c.tags.length ? `<div class="tags">${c.tags.map(t => `<span class="tag">${esc(t)}</span>`).join('')}</div>` : ''}
          </div>
          <div class="explore-bar">${tabsHTML(c ? c.id : 'all')}</div>
          ${needle ? `<p class="result-note">${list.length} album${list.length === 1 ? '' : 's'} matching “${esc(q)}” · <a class="link-gold" href="explore.html">Clear search</a></p>` : ''}
        </div></header>
        <div class="wrap">
          ${list.length ? `<div class="albums">${list.map(albumCard).join('')}</div>` : `<div class="empty">Nothing here yet. Try another search or <a class="link-gold" href="explore.html">browse everything</a>.</div>`}
          <div style="height:60px"></div>
        </div>`;
    }
    addEventListener('hashchange', route);
    route();
  }

  shell();
  reelsHome();
  filmsHome();
  spotlightHome();
  home();
  explore();
  reveal();
})();
