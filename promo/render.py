"""Render promo/compose.html to a video, frame by frame (no dropped frames, no real-time jitter).

    python promo/render.py                       # full film -> promo/olitha-portfolio-reveal.mp4
    python promo/render.py --stills 1.2 8 14.5   # just those moments -> promo/stills/*.jpg
    python promo/render.py --from 20 --to 30     # a section only (silent) -> promo/section.mp4
    python promo/render.py --portrait            # the 60 s vertical film -> promo/olitha-portfolio-portrait.mp4
                                                 # (combine with --stills / --from / --to)
    python promo/render.py --cinema              # the 60 s cinematic trailer -> promo/olitha-portfolio-cinematic.mp4

Needs the site served at http://localhost:8080 (python -m http.server 8080 in the project folder)
and promo/music.wav for the soundtrack (python promo/music.py).
"""
import asyncio, os, subprocess, sys, time

from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
FILMS = {  # flag: (composition, output, viewport, soundtrack, stills folder)
    None: ('compose.html', 'olitha-portfolio-reveal.mp4', (1920, 1080), 'music.wav', 'stills'),
    '--portrait': ('compose_portrait.html', 'olitha-portfolio-portrait.mp4', (1080, 1920), 'music_portrait.wav', 'stills_portrait'),
    '--cinema': ('compose_cinema.html', 'olitha-portfolio-cinematic.mp4', (1080, 1920), 'music_cinema.wav', 'stills_cinema'),
}
FLAG = next((f for f in FILMS if f and f in sys.argv), None)
if FLAG:
    sys.argv.remove(FLAG)
_page, _out, _view, _music, _stills = FILMS[FLAG]
URL = 'http://localhost:8080/promo/' + _page
OUT = os.path.join(HERE, _out)
VIEW = {'width': _view[0], 'height': _view[1]}
MUSIC = os.path.join(HERE, _music)
STILLS = os.path.join(HERE, _stills)


def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return 'ffmpeg'


def arg(name, default=None):
    return float(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


async def main():
    stills = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1:]] if '--stills' in sys.argv else None
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='chrome', headless=True, args=[
            '--enable-gpu', '--ignore-gpu-blocklist', '--use-angle=d3d11', '--autoplay-policy=no-user-gesture-required',
            '--force-color-profile=srgb'])
        page = await browser.new_page(viewport=VIEW)
        page.on('console', lambda m: print('[page]', m.text) if m.type == 'error' else None)
        page.on('pageerror', lambda e: print('[page error]', e))
        await page.goto(URL, wait_until='load', timeout=180000)
        await page.wait_for_function('window.ready === true', timeout=300000)
        dur, fps = await page.evaluate('[DUR, FPS]')

        if stills is not None:
            os.makedirs(STILLS, exist_ok=True)
            for t in stills:
                await page.evaluate('t => renderAt(t)', t)
                await page.screenshot(path=os.path.join(STILLS, f't{t:05.1f}.jpg'), type='jpeg', quality=88)
            print('stills:', ', '.join(f'{t:g}s' for t in stills))
            await browser.close()
            return

        t_from, t_to = arg('--from', 0), arg('--to', dur)
        section = '--from' in sys.argv or '--to' in sys.argv
        out = os.path.join(HERE, 'section.mp4') if section else OUT
        music = MUSIC
        cmd = [ffmpeg_exe(), '-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', str(fps), '-c:v', 'mjpeg', '-i', '-']
        if not section and os.path.exists(music):
            cmd += ['-i', music, '-c:a', 'aac', '-b:a', '192k', '-shortest']
        cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out]
        enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n0, n1 = int(t_from * fps), int(t_to * fps)
        t0 = time.time()
        for n in range(n0, n1):
            await page.evaluate('t => renderAt(t)', n / fps)
            enc.stdin.write(await page.screenshot(type='jpeg', quality=97))
            if (n - n0) % 150 == 0 and n > n0:
                print(f'  {n / fps:5.1f}s / {t_to:g}s   ({(time.time() - t0) / (n - n0) * 1000:.0f} ms per frame)', flush=True)
        enc.stdin.close()
        enc.wait()
        await browser.close()
        print(f'> {os.path.relpath(out, os.path.dirname(HERE))}: {(n1 - n0) / fps:.1f}s, {os.path.getsize(out) / 1e6:.1f} MB, rendered in {time.time() - t0:.0f}s')


if __name__ == '__main__':
    asyncio.run(main())
