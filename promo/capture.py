"""Record footage of the live site (http://localhost:8080) for the reveal video.

Each clip is a scripted visit in headless Chrome (your installed Chrome, driven by Playwright).
Frames come from Chrome's screencast with their timestamps and are re-timed to a constant
30 fps, all-intra H.264 clip in promo/clips/ (all-intra = exact, fast seeking when compositing).

    python promo/capture.py            # all clips
    python promo/capture.py home_desktop phone_reels
"""
import asyncio, base64, os, shutil, subprocess, sys, tempfile

from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(HERE, 'clips')
SITE = 'http://localhost:8080'
FPS = 30


def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return 'ffmpeg'


INIT = """
// clean footage: no scrollbars, and scripted eased scrolling
const addStyle = () => {
  const st = document.createElement('style');
  st.textContent = '::-webkit-scrollbar{display:none!important} html{scroll-behavior:auto!important}';
  document.head.appendChild(st);
};
document.head ? addStyle() : document.addEventListener('DOMContentLoaded', addStyle);
window.__scroll = (y, ms, el) => new Promise(res => {
  const node = el || document.scrollingElement, horiz = !!el;
  const y0 = horiz ? node.scrollLeft : node.scrollTop, t0 = performance.now();
  const ease = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  (function step(now) {
    const k = Math.min(1, (now - t0) / ms), v = y0 + (y - y0) * ease(k);
    horiz ? (node.scrollLeft = v) : (node.scrollTop = v);
    k < 1 ? requestAnimationFrame(step) : res();
  })(t0);
});
window.__top = sel => document.querySelector(sel).getBoundingClientRect().top + scrollY;
"""


class Recorder:
    def __init__(self, page, cdp):
        self.page, self.cdp, self.frames, self.on = page, cdp, [], False

    async def start(self, quality=92):
        self.cdp.on('Page.screencastFrame', self._frame)
        await self.cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': quality, 'everyNthFrame': 1})
        self.on = True

    def _frame(self, e):
        if self.on:
            self.frames.append((e['metadata']['timestamp'], e['data']))
        asyncio.ensure_future(self.cdp.send('Page.screencastFrameAck', {'sessionId': e['sessionId']}))

    async def stop(self):
        self.on = False
        await self.cdp.send('Page.stopScreencast')

    def save(self, name):
        """Re-time the captured frames to constant FPS and encode an all-intra clip."""
        os.makedirs(CLIPS, exist_ok=True)
        tmp = tempfile.mkdtemp(prefix='clip_')
        t0, t1 = self.frames[0][0], self.frames[-1][0]
        n_out = int((t1 - t0) * FPS)
        j = 0
        for i in range(n_out):
            t = t0 + i / FPS
            while j + 1 < len(self.frames) and self.frames[j + 1][0] <= t:
                j += 1
            with open(os.path.join(tmp, f'{i:05d}.jpg'), 'wb') as f:
                f.write(base64.b64decode(self.frames[j][1]))
        out = os.path.join(CLIPS, name + '.mp4')
        subprocess.run([ffmpeg_exe(), '-hide_banner', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', os.path.join(tmp, '%05d.jpg'),
                        '-vf', 'pad=ceil(iw/2)*2:ceil(ih/2)*2', '-c:v', 'libx264', '-preset', 'fast', '-crf', '15', '-g', '1',
                        '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], check=True)
        shutil.rmtree(tmp)
        src_fps = len(self.frames) / max(t1 - t0, .001)
        print(f'{name}: {n_out / FPS:.1f}s, captured at {src_fps:.0f} fps, {os.path.getsize(out) / 1e6:.1f} MB', flush=True)


async def open_page(browser, w, h, scale=1, mobile=False, theme='dark'):
    ctx = await browser.new_context(viewport={'width': w, 'height': h}, device_scale_factor=scale, is_mobile=mobile, has_touch=mobile)
    await ctx.add_init_script("try { localStorage.setItem('theme', '%s') } catch (e) {}" % theme)
    await ctx.add_init_script(INIT)
    page = await ctx.new_page()
    cdp = await ctx.new_cdp_session(page)
    return ctx, page, Recorder(page, cdp)


async def glide(page, x0, y0, x1, y1, ms):
    """Move the mouse smoothly (real pointer events: the 3D orbit and hover effects react)."""
    loop = asyncio.get_event_loop()
    t0 = loop.time()
    while True:
        k = min(1.0, (loop.time() - t0) * 1000 / ms)
        e = k * k * (3 - 2 * k)
        await page.mouse.move(x0 + (x1 - x0) * e, y0 + (y1 - y0) * e)
        if k >= 1:
            break
        await asyncio.sleep(0.008)


async def rect(page, js):
    """Centre and size of an element chosen by a JS expression: [x, y, w, h]."""
    return await page.evaluate("(() => { const r = (%s).getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2, r.width, r.height]; })()" % js)


# ------------------------------------------------------------------ clips
async def home_desktop(browser):
    """Laptop, dark: 3D hero -> reels row (hover preview) -> films player -> collage coverflow."""
    ctx, page, rec = await open_page(browser, 1440, 900)
    await page.goto(SITE + '/', wait_until='networkidle')
    await page.mouse.move(760, 470)
    await page.wait_for_timeout(2600)                      # the orbit's intro animation has settled
    await rec.start()
    await glide(page, 760, 470, 1120, 330, 1300)           # the lens follows the pointer
    await glide(page, 1120, 330, 930, 540, 1100)
    await page.evaluate("__scroll(__top('#reels') - 70, 1300)")
    await page.wait_for_timeout(250)
    await glide(page, 930, 540, 430, 560, 500)             # hover a reel: it previews
    await page.wait_for_timeout(1500)
    await glide(page, 430, 560, 700, 560, 400)
    await page.wait_for_timeout(900)
    await page.mouse.move(1390, 220)
    await page.evaluate("__scroll(__top('#films') - 60, 1300)")
    await page.wait_for_timeout(2400)
    await page.evaluate("__scroll(__top('#spotlight') - 40, 1300)")
    await page.wait_for_timeout(700)
    await page.click('#spotNext')
    await page.wait_for_timeout(900)
    await page.click('#spotNext')
    await page.wait_for_timeout(1200)
    await rec.stop()
    rec.save('home_desktop')
    await ctx.close()


async def photo_desktop(browser):
    """Laptop, dark: Photography albums -> filmstrip hover -> open an album -> lightbox."""
    ctx, page, rec = await open_page(browser, 1440, 900)
    await page.goto(SITE + '/explore.html#photography', wait_until='networkidle')
    await page.mouse.move(1380, 300)
    await page.wait_for_timeout(1500)
    await page.evaluate("__scroll(__top('.albums') - 96, 10)")
    await page.wait_for_timeout(700)
    await rec.start()
    await page.wait_for_timeout(700)
    # hover the 2nd album (Science inauguration): its filmstrip slides up; run along the thumbnails
    cx, cy, w, h = await rect(page, "document.querySelectorAll('.album .stack')[1]")
    await glide(page, 1380, 300, cx, cy, 600)
    await page.wait_for_timeout(500)
    thumbs = await page.evaluate("[...document.querySelectorAll('.album')[1].querySelectorAll('.strip img')].map(i => { const r = i.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })")
    x, y = cx, cy
    for tx, ty in thumbs[1:5]:
        await glide(page, x, y, tx, ty, 260)
        await page.wait_for_timeout(330)
        x, y = tx, ty
    # the third album too (PEFAA)
    cx3, cy3, _, _ = await rect(page, "document.querySelectorAll('.album .stack')[2]")
    await glide(page, x, y, cx3, cy3, 500)
    await page.wait_for_timeout(700)
    # open the Science album
    await glide(page, cx3, cy3, cx, cy - 40, 450)
    await page.mouse.click(cx, cy - 40)
    await page.wait_for_timeout(900)
    await page.mouse.move(1390, 500)
    await page.evaluate("__scroll(__top('.masonry') - 110, 900)")
    await page.wait_for_timeout(300)
    await page.evaluate("__scroll(__top('.masonry') + 520, 1500)")
    await page.wait_for_timeout(200)
    tx, ty, _, _ = await rect(page, "[...document.querySelectorAll('.tile')].find(t => { const r = t.getBoundingClientRect(); return r.top > 150 && r.bottom < 800 && r.left > 300; })")
    await glide(page, 1390, 500, tx, ty, 450)
    await page.mouse.click(tx, ty)
    await page.wait_for_timeout(1000)
    nx, ny, _, _ = await rect(page, "document.querySelector('.lb-next')")
    await glide(page, tx, ty, nx, ny, 400)
    for _ in range(3):
        await page.mouse.click(nx, ny)
        await page.wait_for_timeout(800)
    await rec.stop()
    rec.save('photo_desktop')
    await ctx.close()


async def phone_reels(browser):
    """Phone, dark: hero -> reels row swiping with previews -> the Reels page."""
    ctx, page, rec = await open_page(browser, 390, 844, scale=2, mobile=True)
    await page.goto(SITE + '/', wait_until='networkidle')
    await page.wait_for_timeout(2600)
    await rec.start()
    await page.wait_for_timeout(1300)
    await page.evaluate("__scroll(__top('#reelsStage') - 150, 1300)")
    await page.wait_for_timeout(1300)
    for i in (1, 2, 3):                                     # swipe along the row; each reel previews as it lands
        await page.evaluate("(() => { const r = document.querySelector('#reelsRow'); const w = r.querySelector('.reel').offsetWidth + 18; return __scroll(w * %d, 550, r); })()" % i)
        await page.wait_for_timeout(1150)
    await page.goto(SITE + '/explore.html#reels', wait_until='domcontentloaded')
    await page.wait_for_timeout(900)
    await page.evaluate("__scroll(__top('.reels-grid') - 110, 900)")
    await page.wait_for_timeout(500)
    await page.evaluate("__scroll(__top('.reels-grid') + 520, 1900)")
    await page.wait_for_timeout(600)
    await rec.stop()
    rec.save('phone_reels')
    await ctx.close()


async def phone_home(browser):
    """Phone, dark: 3D hero -> reels -> films player -> collage coverflow -> feed."""
    ctx, page, rec = await open_page(browser, 390, 844, scale=2, mobile=True)
    await page.goto(SITE + '/', wait_until='networkidle')
    await page.wait_for_timeout(2600)
    await rec.start()
    await page.wait_for_timeout(2300)
    await page.evaluate("__scroll(__top('#reelsStage') - 150, 1200)")
    await page.wait_for_timeout(1500)
    await page.evaluate("__scroll(__top('#filmScreen') - 130, 1300)")
    await page.wait_for_timeout(1900)
    await page.evaluate("__scroll(__top('#coverflow') - 150, 1200)")
    await page.wait_for_timeout(500)
    await page.evaluate("document.querySelector('#spotNext').click()")
    await page.wait_for_timeout(900)
    await page.evaluate("document.querySelector('#spotNext').click()")
    await page.wait_for_timeout(900)
    await page.evaluate("__scroll(__top('#posts') - 110, 1300)")
    await page.wait_for_timeout(1500)
    await rec.stop()
    rec.save('phone_home')
    await ctx.close()


async def tablet_films(browser):
    """Tablet, dark: films player -> collage coverflow -> the feed."""
    ctx, page, rec = await open_page(browser, 820, 1180, scale=1.5, mobile=True)
    await page.goto(SITE + '/', wait_until='networkidle')
    await page.wait_for_timeout(2200)
    await page.evaluate("__scroll(__top('#films') - 90, 10)")
    await page.wait_for_timeout(1500)
    await rec.start()
    await page.wait_for_timeout(1500)
    await page.evaluate("document.querySelectorAll('#filmTabs .pill')[1].click()")
    await page.wait_for_timeout(1700)
    await page.evaluate("__scroll(__top('#spotlight') - 60, 1400)")
    await page.wait_for_timeout(600)
    await page.evaluate("document.querySelector('#spotNext').click()")
    await page.wait_for_timeout(900)
    await page.evaluate("document.querySelector('#spotNext').click()")
    await page.wait_for_timeout(900)
    await page.evaluate("__scroll(__top('#posts') - 120, 1500)")
    await page.wait_for_timeout(1200)
    await rec.stop()
    rec.save('tablet_films')
    await ctx.close()


async def theme_switch(browser, name, w, h, scale=1, mobile=False):
    """Dark hero -> tap the sun/moon switch (circular reveal) -> light theme, then a short scroll."""
    ctx, page, rec = await open_page(browser, w, h, scale=scale, mobile=mobile)
    await page.goto(SITE + '/', wait_until='networkidle')
    await page.mouse.move(w * .55, h * .5)
    await page.wait_for_timeout(2600)
    await rec.start()
    await page.wait_for_timeout(1200)
    await page.evaluate("document.querySelector('#themeToggle').click()")
    await page.wait_for_timeout(1900)
    await page.evaluate("__scroll(__top('#reels') - 70, 1500)")
    await page.wait_for_timeout(1500)
    await page.evaluate("__scroll(__top('#posts') - 120, 1600)")
    await page.wait_for_timeout(1200)
    await rec.stop()
    rec.save(name)
    await ctx.close()


CLIPS_FN = {
    'home_desktop': home_desktop,
    'photo_desktop': photo_desktop,
    'phone_reels': phone_reels,
    'phone_home': phone_home,
    'tablet_films': tablet_films,
    'theme_desktop': lambda b: theme_switch(b, 'theme_desktop', 1440, 900),
    'theme_tablet': lambda b: theme_switch(b, 'theme_tablet', 820, 1180, 1.5, True),
    'theme_phone': lambda b: theme_switch(b, 'theme_phone', 390, 844, 2, True),
}


async def main():
    names = sys.argv[1:] or list(CLIPS_FN)
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='chrome', headless=True, args=[
            '--enable-gpu', '--ignore-gpu-blocklist', '--use-angle=d3d11', '--autoplay-policy=no-user-gesture-required'])
        for n in names:
            await CLIPS_FN[n](browser)
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())
