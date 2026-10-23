/* 3D hero: a camera lens with album frames orbiting it (Three.js) */
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const canvas = document.getElementById('hero3d');
const hero = canvas && canvas.closest('.hero');
const tip = document.getElementById('heroTip');
const PF = window.PF;
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const GOLD = 0xf3b53f;

function webglOK() {
  try { const c = document.createElement('canvas'); return !!(c.getContext('webgl2') || c.getContext('webgl')); }
  catch (_) { return false; }
}

if (!canvas || !PF || !webglOK()) document.documentElement.classList.add('no-webgl');
else {
  try { init(); } catch (e) { console.error(e); document.documentElement.classList.add('no-webgl'); }
}

function init() {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(renderer), 0.04).texture;

  const camera = new THREE.PerspectiveCamera(32, 1, 0.1, 100);
  camera.position.set(0, 0.6, 15);

  scene.add(new THREE.AmbientLight(0xffffff, 0.25));
  const key = new THREE.DirectionalLight(0xffe2b8, 2.4); key.position.set(5, 6, 7); scene.add(key);
  const rimLight = new THREE.PointLight(GOLD, 40, 22); rimLight.position.set(-4, 2, -3); scene.add(rimLight);
  const fill = new THREE.PointLight(0x8aa4ff, 12, 20); fill.position.set(4, -3, 3); scene.add(fill);

  const world = new THREE.Group();
  scene.add(world);

  /* ---------------- lens ---------------- */
  const lensPivot = new THREE.Group();
  const lens = new THREE.Group();
  lens.rotation.x = Math.PI / 2;           // lathe axis (+Y) now points at the viewer (+Z)
  lensPivot.add(lens);
  world.add(lensPivot);

  const body = new THREE.MeshStandardMaterial({ color: 0x141416, metalness: 0.75, roughness: 0.32 });
  const satin = new THREE.MeshStandardMaterial({ color: 0x1d1d21, metalness: 0.4, roughness: 0.55 });
  const gold = new THREE.MeshStandardMaterial({ color: GOLD, metalness: 1, roughness: 0.22, emissive: 0x3a2400, emissiveIntensity: 0.4 });

  const v = (r, y) => new THREE.Vector2(r, y);
  const shell = new THREE.LatheGeometry([
    v(0.95, -1.55), v(1.02, -1.5), v(1.02, -1.38), v(1.16, -1.32), v(1.18, -1.15),
    v(1.18, -0.42), v(1.24, -0.36), v(1.24, 0.3), v(1.3, 0.38), v(1.42, 0.88),
    v(1.46, 0.96), v(1.46, 1.04), v(1.34, 1.06), v(1.24, 1.0), v(1.16, 0.74),
  ], 128);
  lens.add(new THREE.Mesh(shell, body));

  // ribbed focus ring
  const ribs = document.createElement('canvas'); ribs.width = 512; ribs.height = 8;
  const rc = ribs.getContext('2d');
  for (let x = 0; x < 512; x += 8) { rc.fillStyle = '#fff'; rc.fillRect(x, 0, 4, 8); rc.fillStyle = '#000'; rc.fillRect(x + 4, 0, 4, 8); }
  const ribTex = new THREE.CanvasTexture(ribs);
  ribTex.wrapS = THREE.RepeatWrapping; ribTex.repeat.set(6, 1);
  const grip = new THREE.Mesh(
    new THREE.CylinderGeometry(1.28, 1.28, 0.72, 128, 1, true),
    new THREE.MeshStandardMaterial({ color: 0x0c0c0d, roughness: 0.9, metalness: 0.1, bumpMap: ribTex, bumpScale: 3 })
  );
  grip.position.y = -0.62;
  lens.add(grip);
  const zoom = new THREE.Mesh(new THREE.CylinderGeometry(1.25, 1.25, 0.36, 128, 1, true), satin);
  zoom.position.y = 0.06;
  lens.add(zoom);

  const goldRing = new THREE.Mesh(new THREE.TorusGeometry(1.25, 0.035, 16, 160), gold);
  goldRing.rotation.x = Math.PI / 2; goldRing.position.y = 0.33;
  lens.add(goldRing);
  const goldRing2 = new THREE.Mesh(new THREE.TorusGeometry(1.03, 0.025, 12, 140), gold);
  goldRing2.rotation.x = Math.PI / 2; goldRing2.position.y = -1.44;
  lens.add(goldRing2);

  // engraved name ring on the front
  const ringCanvas = document.createElement('canvas'); ringCanvas.width = ringCanvas.height = 1024;
  const ringTex = new THREE.CanvasTexture(ringCanvas);
  ringTex.colorSpace = THREE.SRGBColorSpace;
  const front = new THREE.Mesh(
    new THREE.RingGeometry(1.17, 1.34, 128),
    new THREE.MeshStandardMaterial({ map: ringTex, metalness: 0.5, roughness: 0.4, transparent: true })
  );
  front.rotation.x = -Math.PI / 2; front.position.y = 1.005;
  lens.add(front);
  function drawRingText() {
    const g = ringCanvas.getContext('2d'), c = 512, rad = c * (1.255 / 1.34);
    g.clearRect(0, 0, 1024, 1024);
    g.fillStyle = '#121214'; g.beginPath(); g.arc(c, c, c, 0, Math.PI * 2); g.fill();
    const txt = 'OLITHA INDUVARA PHOTOGRAPHY  •  EVERY PICTURE TELLS A STORY  •  ';
    g.font = '600 30px "Plus Jakarta Sans", sans-serif'; g.textAlign = 'center'; g.textBaseline = 'middle';
    const step = (Math.PI * 2) / txt.length;
    [...txt].forEach((ch, i) => {
      const a = i * step - Math.PI / 2;
      g.save(); g.translate(c + Math.cos(a) * rad, c + Math.sin(a) * rad); g.rotate(a + Math.PI / 2);
      g.fillStyle = ch === '•' ? '#f3b53f' : '#cfcac0'; g.fillText(ch, 0, 0); g.restore();
    });
    ringTex.needsUpdate = true;
  }
  drawRingText();
  if (document.fonts) document.fonts.ready.then(drawRingText);

  // aperture blades (rebuilt when it opens/closes)
  const aperture = new THREE.Mesh(new THREE.BufferGeometry(), new THREE.MeshStandardMaterial({ color: 0x08080a, metalness: 0.6, roughness: 0.45, side: THREE.DoubleSide }));
  aperture.position.y = 0.42;
  lens.add(aperture);
  let apertureOpen = -1;
  function setAperture(o) {
    o = Math.round(o * 40) / 40;
    if (o === apertureOpen) return;
    apertureOpen = o;
    const sh = new THREE.Shape(); sh.absarc(0, 0, 1.17, 0, Math.PI * 2, false);
    const hole = new THREE.Path(), r = 0.18 + o * 0.78, n = 7, twist = (1 - o) * 0.5;
    for (let i = 0; i <= n; i++) {
      const a = (i / n) * Math.PI * 2 + twist;
      i ? hole.lineTo(Math.cos(a) * r, Math.sin(a) * r) : hole.moveTo(Math.cos(a) * r, Math.sin(a) * r);
    }
    sh.holes.push(hole);
    aperture.geometry.dispose();
    aperture.geometry = new THREE.ShapeGeometry(sh, 48).rotateX(-Math.PI / 2);
  }
  setAperture(1);

  // the "eye" glow deep inside
  const eye = new THREE.Mesh(new THREE.CircleGeometry(0.95, 64), new THREE.MeshBasicMaterial({ map: radialTexture('#f3b53f', 'rgba(243,181,63,0)'), transparent: true, depthWrite: false }));
  eye.rotation.x = -Math.PI / 2; eye.position.y = 0.05;
  lens.add(eye);
  const pupil = new THREE.Mesh(new THREE.CircleGeometry(1.17, 64), new THREE.MeshBasicMaterial({ color: 0x050507 }));
  pupil.rotation.x = -Math.PI / 2; pupil.position.y = 0.0;
  lens.add(pupil);

  // front glass with iridescent coating
  const R = 2.0, theta = Math.asin(1.15 / R);
  const glass = new THREE.Mesh(
    new THREE.SphereGeometry(R, 96, 32, 0, Math.PI * 2, 0, theta),
    new THREE.MeshPhysicalMaterial({
      color: 0x0a0c18, metalness: 0, roughness: 0.04, transparent: true, opacity: 0.55,
      clearcoat: 1, clearcoatRoughness: 0.02, iridescence: 1, iridescenceIOR: 1.7,
      iridescenceThicknessRange: [180, 820], envMapIntensity: 2.4,
    })
  );
  glass.position.y = 0.64 - R * Math.cos(theta);
  lens.add(glass);

  /* ---------------- orbit rings ---------------- */
  const ring = new THREE.Group();          // tilted plane the frames travel on
  ring.rotation.set(0.24, 0, -0.1);
  world.add(ring);
  const spinner = new THREE.Group();       // spins inside the tilted plane
  ring.add(spinner);

  const RADIUS = 4.3;
  const lineMat = new THREE.MeshBasicMaterial({ color: GOLD, transparent: true, opacity: 0.28 });
  const orbitLine = new THREE.Mesh(new THREE.TorusGeometry(RADIUS, 0.008, 6, 256), lineMat);
  orbitLine.rotation.x = Math.PI / 2;
  ring.add(orbitLine);

  const dotTex = radialTexture('#ffffff', 'rgba(255,255,255,0)');
  const outer = new THREE.Group();
  outer.rotation.set(-0.35, 0, 0.32);
  world.add(outer);
  {
    const n = 220, pts = new Float32Array(n * 3), r = RADIUS + 1.6;
    for (let i = 0; i < n; i++) { const a = (i / n) * Math.PI * 2; pts.set([Math.cos(a) * r, 0, Math.sin(a) * r], i * 3); }
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pts, 3));
    outer.add(new THREE.Points(g, new THREE.PointsMaterial({ size: 0.05, map: dotTex, color: 0xffffff, transparent: true, opacity: 0.35, depthWrite: false })));
  }
  const sats = [0, 2.1, 4.2].map((p, i) => {
    const m = new THREE.Mesh(new THREE.SphereGeometry(i ? 0.07 : 0.1, 20, 20), new THREE.MeshBasicMaterial({ color: GOLD }));
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({ map: dotTex, color: GOLD, transparent: true, opacity: 0.6, depthWrite: false }));
    halo.scale.setScalar(0.8); m.add(halo);
    outer.add(m);
    return { m, p, speed: 0.12 + i * 0.05 };
  });

  /* ---------------- frames (album covers) ---------------- */
  const small = () => innerWidth < 760;
  const picks = PF.heroPicks;   // { title, cover, cat, category, url, frames }: spotlight pieces first, then album covers

  const CARD_W = 1.35, CARD_H = 1.8;
  const cardGeo = new THREE.PlaneGeometry(CARD_W, CARD_H);
  const cards = picks.map((album, i) => {
    const tex = new THREE.CanvasTexture(document.createElement('canvas'));
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
    const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: true, alphaTest: 0.02 });
    const mesh = new THREE.Mesh(cardGeo, mat);
    const angle = (i / picks.length) * Math.PI * 2;
    mesh.userData = { album, angle, hover: 0, tex };
    spinner.add(mesh);
    drawCard(tex, album, null);
    const img = new Image();
    img.decoding = 'async';
    img.onload = () => (document.fonts ? document.fonts.ready : Promise.resolve()).then(() => drawCard(tex, album, img));
    img.src = album.cover;
    return mesh;
  });

  function drawCard(tex, album, img) {
    const W = 600, H = 800, r = 44;
    const c = tex.image.width === W ? tex.image : Object.assign(tex.image, { width: W, height: H });
    const g = c.getContext('2d');
    g.clearRect(0, 0, W, H);
    g.save();
    roundRect(g, 4, 4, W - 8, H - 8, r); g.clip();
    g.fillStyle = '#1d1d22'; g.fillRect(0, 0, W, H);
    if (img) {
      const s = Math.max(W / img.width, H / img.height);
      g.drawImage(img, (W - img.width * s) / 2, (H - img.height * s) / 2, img.width * s, img.height * s);
    }
    const grad = g.createLinearGradient(0, H * 0.5, 0, H);
    grad.addColorStop(0, 'rgba(0,0,0,0)'); grad.addColorStop(1, 'rgba(0,0,0,.85)');
    g.fillStyle = grad; g.fillRect(0, 0, W, H);
    // category chip
    const label = album.cat.short.toUpperCase();
    g.font = '700 24px "Plus Jakarta Sans", sans-serif';
    const tw = g.measureText(label).width + 36;
    roundRect(g, 32, H - 182, tw, 46, 23); g.fillStyle = '#f3b53f'; g.fill();
    g.fillStyle = '#1a1306'; g.textBaseline = 'middle'; g.fillText(label, 50, H - 158);
    // title (2 lines max)
    g.fillStyle = '#fff'; g.font = '700 40px "Plus Jakarta Sans", sans-serif'; g.textBaseline = 'alphabetic';
    const lines = wrap(g, album.title, W - 64).slice(0, 2);
    lines.forEach((ln, j) => g.fillText(ln, 32, H - 92 + j * 46 - (lines.length - 1) * 46 + 46));
    g.restore();
    roundRect(g, 4, 4, W - 8, H - 8, r);
    g.lineWidth = 3; g.strokeStyle = 'rgba(255,255,255,.18)'; g.stroke();
    tex.needsUpdate = true;
  }

  /* ---------------- dust ---------------- */
  const dust = (() => {
    const n = small() ? 380 : 750, pos = new Float32Array(n * 3), col = new Float32Array(n * 3);
    const cGold = new THREE.Color(GOLD), cWhite = new THREE.Color(0xffffff);
    for (let i = 0; i < n; i++) {
      const r = 5 + Math.random() * 11, t = Math.random() * Math.PI * 2, p = Math.acos(2 * Math.random() - 1);
      pos.set([r * Math.sin(p) * Math.cos(t), r * Math.cos(p) * 0.6, r * Math.sin(p) * Math.sin(t) - 3], i * 3);
      const c = Math.random() < 0.55 ? cGold : cWhite;
      col.set([c.r, c.g, c.b], i * 3);
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    const pts = new THREE.Points(g, new THREE.PointsMaterial({
      size: 0.06, map: dotTex, vertexColors: true, transparent: true, opacity: 0.75,
      depthWrite: false, blending: THREE.AdditiveBlending,
    }));
    scene.add(pts);
    return pts;
  })();

  /* ---------------- layout ---------------- */
  let W = 0, H = 0;
  const base = { x: 0, y: 0, s: 1 };
  function resize() {
    W = hero.clientWidth; H = hero.clientHeight;
    renderer.setSize(W, H, false);
    camera.aspect = W / H;
    camera.updateProjectionMatrix();
    // fit the orbit into the free area beside the copy (desktop) or above it (phones)
    const hh = camera.position.z * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    const hw = hh * camera.aspect, extent = RADIUS + 0.9;
    if (W > 1100 && camera.aspect > 1.05) {
      const region = hw * 2 * (camera.aspect > 1.45 ? 0.56 : 0.62);
      base.s = Math.min(1.1, (region / (2 * extent)) * 1.12, (hh * 2 * 0.8) / 4);
      base.x = hw - region / 2 + 0.2;
      base.y = -0.1;
    } else {
      // pixel gap between the top bar and the copy, converted to world units
      const copy = document.querySelector('.hero-copy');
      const top = 84, bottom = copy ? copy.getBoundingClientRect().top - hero.getBoundingClientRect().top - 8 : H * 0.5;
      const unit = (hh * 2) / H;
      base.s = Math.max(0.36, Math.min(0.9, ((hw * 2) / (2 * extent)) * 1.2, ((bottom - top) * unit) / 4));
      base.x = 0;
      base.y = hh - ((top + bottom) / 2) * unit;
    }
  }
  resize();
  addEventListener('resize', resize);

  /* ---------------- interaction ---------------- */
  const mouse = new THREE.Vector2(0, 0), ndc = new THREE.Vector2(-9, -9);
  const ray = new THREE.Raycaster();
  let spin = 0, vel = reduceMotion ? 0 : 0.06, dragging = false, dragX = 0, moved = 0, hovered = null, idleUntil = 0, target = null;
  const AUTO = reduceMotion ? 0 : 0.06;

  const toNdc = e => {
    const r = canvas.getBoundingClientRect();
    ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  };
  const pick = () => {
    ray.setFromCamera(ndc, camera);
    const hit = ray.intersectObjects([lens, ...cards], true)[0];
    return hit && cards.includes(hit.object) ? hit.object : null;
  };
  canvas.addEventListener('pointermove', e => {
    toNdc(e);
    mouse.copy(ndc);
    if (dragging) {
      const dx = e.clientX - dragX; dragX = e.clientX; moved += Math.abs(dx);
      vel = dx * 0.35; target = null;
    }
    if (tip) { tip.style.left = e.clientX + 'px'; tip.style.top = e.clientY + 'px'; }
  });
  canvas.addEventListener('pointerleave', () => { ndc.set(-9, -9); mouse.set(0, 0); setHover(null); });
  canvas.addEventListener('pointerdown', e => {
    toNdc(e);
    dragging = true; dragX = e.clientX; moved = 0;
    canvas.classList.add('dragging');
    canvas.setPointerCapture(e.pointerId);
  });
  const endDrag = () => { dragging = false; canvas.classList.remove('dragging'); idleUntil = performance.now() + 2500; };
  canvas.addEventListener('pointerup', e => {
    endDrag();
    const m = moved < 6 && pick();
    if (m) location.href = m.userData.album.url;
  });
  canvas.addEventListener('pointercancel', endDrag);

  function setHover(m) {
    if (m === hovered) return;
    hovered = m;
    canvas.classList.toggle('pointing', !!m);
    document.querySelectorAll('#heroAreas a').forEach(a => a.classList.toggle('hot', !!m && a.dataset.cat === m.userData.album.category));
    if (!tip) return;
    if (m) {
      const a = m.userData.album;
      tip.innerHTML = `<span>${a.cat.name}</span><b></b><small>${a.frames} frames · click to open</small>`;
      tip.querySelector('b').textContent = a.title;
      tip.classList.add('show');
    } else tip.classList.remove('show');
  }

  // bring a discipline's first frame to the front
  window.hero3d = {
    focus(catId) {
      const m = cards.find(c => c.userData.album.category === catId);
      if (!m) return;
      // front of the ring faces +z: angle + spin = PI/2
      let goal = Math.PI / 2 - m.userData.angle;
      goal += Math.round((spin - goal) / (Math.PI * 2)) * Math.PI * 2;
      target = goal; idleUntil = performance.now() + 4000;
    },
  };

  /* ---------------- loop ---------------- */
  let visible = true, running = false, last = performance.now(), t = 0;
  const introStart = performance.now();
  new IntersectionObserver(([e]) => { visible = e.isIntersecting; if (visible) start(); }, { threshold: 0 }).observe(hero);
  document.addEventListener('visibilitychange', () => { if (!document.hidden) start(); });

  const tmpV = new THREE.Vector3(), camWorld = new THREE.Vector3();
  const ease = x => 1 - Math.pow(1 - x, 3);
  const lerp = (a, b, k) => a + (b - a) * k;

  function frame(now) {
    if (!visible || document.hidden) { running = false; return; }
    requestAnimationFrame(frame);
    const dt = Math.min(0.05, (now - last) / 1000); last = now; t += dt;
    const intro = reduceMotion ? 1 : ease(Math.min(1, (now - introStart) / 1800));
    const scroll = Math.min(1, Math.max(0, scrollY / (H || 1)));

    // spin: drag inertia → auto drift, or ease to a focused frame
    if (target !== null && !dragging) {
      spin = lerp(spin, target, 1 - Math.pow(0.002, dt));
      if (Math.abs(spin - target) < 0.001) target = null;
    } else if (!dragging) {
      // stop on a hovered frame, drift slowly while the pointer is anywhere over the scene
      const goal = now < idleUntil || hovered ? 0 : ndc.x > -2 ? AUTO * 0.3 : AUTO;
      vel = lerp(vel, goal, 1 - Math.pow(0.15, dt));
      spin += vel * dt;
    } else spin += vel * dt * 0.6;
    spinner.rotation.y = -spin;

    // world placement + scroll parallax
    const s = base.s * (0.85 + intro * 0.15);
    world.scale.setScalar(s);
    world.position.set(base.x, base.y + scroll * 2.2, 0);
    ring.rotation.x = 0.24 + scroll * 0.5 + mouse.y * 0.05;
    camera.position.x = lerp(camera.position.x, mouse.x * 0.6, 0.05);
    camera.position.y = lerp(camera.position.y, 0.6 + mouse.y * 0.4, 0.05);
    camera.position.z = 15 + scroll * 3;
    camera.lookAt(0, scroll * 1.2, 0);

    // lens: follow the pointer, float, aperture closes as you scroll
    const bob = reduceMotion ? 0 : Math.sin(t * 1.2) * 0.12;
    lensPivot.position.y = bob;
    lensPivot.rotation.y = lerp(lensPivot.rotation.y, -0.5 + mouse.x * 0.45, 0.06);
    lensPivot.rotation.x = lerp(lensPivot.rotation.x, 0.22 - mouse.y * 0.3, 0.06);
    lensPivot.rotation.z = reduceMotion ? 0 : Math.sin(t * 0.6) * 0.04;
    lensPivot.scale.setScalar(1.1 * (0.6 + intro * 0.4));
    setAperture(Math.max(0, 1 - scroll * 1.6) * (0.55 + 0.45 * intro) * (hovered ? 0.7 : 1));
    eye.material.opacity = 0.35 + (hovered ? 0.45 : 0.15) + Math.sin(t * 2) * 0.05;

    // frames: place on the ring, face the camera, depth-shade
    camera.getWorldPosition(camWorld);
    cards.forEach((m, i) => {
      const d = m.userData;
      const k = reduceMotion ? 1 : ease(Math.min(1, Math.max(0, (now - introStart - 200 - i * 70) / 1100)));
      const r = RADIUS * k;
      m.position.set(Math.cos(d.angle) * r, Math.sin(t * 0.9 + i) * 0.12, Math.sin(d.angle) * r);
      m.lookAt(camWorld);
      m.getWorldPosition(tmpV);
      const front = THREE.MathUtils.clamp((tmpV.z - world.position.z + RADIUS * s) / (2 * RADIUS * s), 0, 1);
      d.hover = lerp(d.hover, hovered === m ? 1 : 0, 0.15);
      m.scale.setScalar((0.82 + front * 0.28 + d.hover * 0.14) * k);
      m.material.color.setScalar(0.32 + front * 0.68 + d.hover * 0.2);
      m.material.opacity = k;
    });

    sats.forEach(o => {
      const a = o.p + t * o.speed, r = RADIUS + 1.6;
      o.m.position.set(Math.cos(a) * r, 0, Math.sin(a) * r);
    });
    outer.rotation.y = t * 0.02;
    dust.rotation.y = t * 0.012;
    dust.position.y = scroll * 1.5;

    // hover picking (the lens can block frames behind it)
    if (!dragging && ndc.x > -2) {
      setHover(pick());
    }

    renderer.render(scene, camera);
  }
  function start() { if (!running && visible && !document.hidden) { running = true; last = performance.now(); requestAnimationFrame(frame); } }
  start();
  document.documentElement.classList.add('webgl-ready');
}

/* ---------------- helpers ---------------- */
function radialTexture(inner, outer) {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const g = c.getContext('2d'), grad = g.createRadialGradient(64, 64, 0, 64, 64, 64);
  grad.addColorStop(0, inner); grad.addColorStop(1, outer);
  g.fillStyle = grad; g.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
function roundRect(g, x, y, w, h, r) {
  g.beginPath();
  g.moveTo(x + r, y); g.arcTo(x + w, y, x + w, y + h, r); g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r); g.arcTo(x, y, x + w, y, r); g.closePath();
}
function wrap(g, text, max) {
  const words = text.split(' '), lines = [];
  let line = '';
  words.forEach(w => {
    const test = line ? line + ' ' + w : w;
    if (g.measureText(test).width > max && line) { lines.push(line); line = w; } else line = test;
  });
  if (line) lines.push(line);
  return lines;
}
