"""
Scan the portfolio/ folders and generate js/data.js (+ thumbnails).

    portfolio/
      <category>/            photography, videography, aerial, editing ... (any folder works)
        category.json        optional: name, tagline, description, tags, order
        <album-folder>/      e.g. 07-kandy-wedding  (leading numbers only set the order)
          album.json         optional: title, location, date, description, cover, link, more, captions
          *.jpg / *.png / *.webp / *.mp4 / *.webm
          _cover.jpg         optional: a portrait crop used ONLY as the album cover (not shown in the gallery)
        loose files here go into an album called "More <category>"

Videos: put a poster image with the same name next to the video
(clip.mp4 + clip.jpg) and it will be used as the cover frame.

Run from the project folder:   python tools/build.py
"""
import json
import os
import re
import sys
import time
from urllib.parse import quote, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTFOLIO = os.path.join(ROOT, 'portfolio')
THUMBS = os.path.join(ROOT, 'thumbs')
OUT = os.path.join(ROOT, 'js', 'data.js')

IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif'}
VIDEO_EXT = {'.mp4', '.webm', '.mov', '.m4v'}
THUMB_SIZE = 1200          # long side of cover / feed images (shown at up to ~600 px, sharp on 2x screens)

try:
    from PIL import Image, ImageOps
except ImportError:  # thumbnails are optional
    Image = None
    print('! Pillow not installed: skipping thumbnails (pip install pillow)')


def read_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            sys.exit(f'x Could not read {os.path.relpath(path, ROOT)}: {e}')


def pretty(name):
    """'03-graduation-in-the-rain' -> 'Graduation in the rain'"""
    name = re.sub(r'^\d+[\s._-]*', '', os.path.splitext(name)[0])
    name = re.sub(r'[_-]+', ' ', name).strip()
    return name[:1].upper() + name[1:] if name else ''


def url(path):
    return quote(os.path.relpath(path, ROOT).replace(os.sep, '/'))


def make_thumb(src, rel):
    """Return (thumb_url, width, height) for an image."""
    if Image is None:
        return url(src), 4, 3
    dst = os.path.join(THUMBS, os.path.splitext(rel)[0] + '.jpg')
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        w, h = im.size
        if w <= THUMB_SIZE and h <= THUMB_SIZE and src.lower().endswith(('.jpg', '.jpeg')):
            return url(src), w, h
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            t = im.convert('RGB')
            t.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
            t.save(dst, quality=88, optimize=True, progressive=True)
    return url(dst), w, h


_face = None


def cover_focus(path, w, h):
    """Album cards are portrait. For a landscape cover, say where to anchor the crop ('x% y%').

    Uses OpenCV face detection when it is installed (pip install opencv-python); otherwise the centre.
    """
    global _face
    if h >= w * 1.05:
        return '50% 30%'
    try:
        import cv2
        if _face is None:
            _face = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        img = cv2.imread(path)
        if img is None:
            return '50% 40%'
        k = 640 / img.shape[1]
        g = cv2.cvtColor(cv2.resize(img, None, fx=k, fy=k), cv2.COLOR_BGR2GRAY)
        faces = _face.detectMultiScale(g, 1.1, 6, minSize=(int(g.shape[0] * .08),) * 2)
        if len(faces):
            # centre of all faces, weighted by size, so a group stays together
            area = sum(fw * fh for _, _, fw, fh in faces)
            cx = sum((x + fw / 2) * fw * fh for x, _, fw, fh in faces) / area
            return f'{min(80, max(20, round(cx / g.shape[1] * 100)))}% 35%'
    except Exception:
        pass
    return '50% 40%'


def scan_album(folder, cat_id, album_id, title_fallback):
    meta = read_json(os.path.join(folder, 'album.json'))
    captions = meta.get('captions', {})
    files = sorted(f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)))
    # "_cover.jpg": cover only, never a gallery item
    cover_file = next((f for f in files if os.path.splitext(f)[0].lower() == '_cover'
                       and os.path.splitext(f)[1].lower() in IMAGE_EXT), None)
    files = [f for f in files if not f.startswith('_')]
    stems = {}
    for f in files:
        stems.setdefault(os.path.splitext(f)[0], []).append(f)

    items, posters = [], set()
    for f in files:
        stem, ext = os.path.splitext(f)
        if ext.lower() in VIDEO_EXT:
            poster = next((p for p in stems[stem] if os.path.splitext(p)[1].lower() in IMAGE_EXT), None)
            item = {'type': 'video', 'src': url(os.path.join(folder, f)), 'file': f,
                    'title': captions.get(f) or pretty(f), 'w': 16, 'h': 9}
            if poster:
                item['_img'] = poster
                posters.add(poster)
                thumb, w, h = make_thumb(os.path.join(folder, poster), os.path.join(cat_id, album_id, poster))
                item.update(poster=url(os.path.join(folder, poster)), thumb=thumb, w=w, h=h)
            items.append(item)
    for f in files:
        if os.path.splitext(f)[1].lower() in IMAGE_EXT and f not in posters:
            thumb, w, h = make_thumb(os.path.join(folder, f), os.path.join(cat_id, album_id, f))
            items.append({'type': 'image', 'src': url(os.path.join(folder, f)), 'file': f, '_img': f,
                          'thumb': thumb, 'title': captions.get(f) or pretty(f), 'w': w, 'h': h})

    order = meta.get('order')
    if order:
        rank = {f: i for i, f in enumerate(order)}
        items.sort(key=lambda it: rank.get(it['file'], len(rank)))
    else:  # photos first, then clips, keeping name order
        items.sort(key=lambda it: (it['type'] == 'video', it['file']))
    if not items:
        return None

    cover = next((it for it in items if it['file'] == meta.get('cover')), items[0])
    cover_img = cover.pop('_img', None) if cover is not None else None
    if cover_file:
        thumb, w, h = make_thumb(os.path.join(folder, cover_file), os.path.join(cat_id, album_id, cover_file))
        cover, cover_img = {'thumb': thumb, 'src': url(os.path.join(folder, cover_file)), 'w': w, 'h': h}, cover_file
    for it in items:
        it.pop('_img', None)
    focus = meta.get('coverFocus')
    if not focus:
        local = os.path.join(ROOT, unquote(cover['thumb'])) if cover.get('thumb') else None
        if not (local and os.path.exists(local)):
            local = os.path.join(folder, cover_img) if cover_img else None
        focus = cover_focus(local, cover['w'], cover['h']) if local else '50% 40%'
    return {
        'id': album_id,
        'category': cat_id,
        'title': meta.get('title') or title_fallback,
        'location': meta.get('location', ''),
        'date': meta.get('date', ''),
        'description': meta.get('description', ''),
        'link': meta.get('link', ''),
        'more': meta.get('more', 0),
        'cover': cover.get('thumb') or cover['src'],
        'coverW': cover['w'],
        'coverH': cover['h'],
        'coverFocus': focus,                         # where a landscape cover is anchored in the portrait card
        'featured': meta.get('featured', True),    # false = Explore only, never on the home page
        'spotlight': meta.get('spotlight', False),  # true = the 3D showcase on the home page
        'reelsOrder': meta.get('reelsOrder', 0),     # higher = later in the home Reels row
        'pin': meta.get('pin', 0),                   # 1, 2, 3 ... = first posts in the home feed, in that order
        'inFeed': meta.get('feed', True),            # false = no feed post (still in Reels, orbit etc.)
        'items': items,
    }


def main():
    if not os.path.isdir(PORTFOLIO):
        sys.exit('x No portfolio/ folder found next to tools/')
    categories = []
    for cat_id in sorted(os.listdir(PORTFOLIO)):
        cdir = os.path.join(PORTFOLIO, cat_id)
        if not os.path.isdir(cdir) or cat_id.startswith(('.', '_')):
            continue
        meta = read_json(os.path.join(cdir, 'category.json'))
        name = meta.get('name') or pretty(cat_id)
        albums = []
        for a in sorted(os.listdir(cdir)):
            adir = os.path.join(cdir, a)
            if os.path.isdir(adir) and not a.startswith(('.', '_')):
                album = scan_album(adir, cat_id, a, pretty(a))
                if album:
                    albums.append(album)
        loose = scan_album(cdir, cat_id, '_more', f'More {name}')
        if loose:
            albums.append(loose)
        categories.append({
            'id': cat_id,
            'name': name,
            'short': meta.get('short') or name.split()[0],
            'tagline': meta.get('tagline', ''),
            'description': meta.get('description', ''),
            'tags': meta.get('tags', []),
            'layout': meta.get('layout', 'albums'),   # "reels" shows vertical players instead of folders
            'order': meta.get('order', 99),
            'albums': albums,
        })
    categories.sort(key=lambda c: (c['order'], c['id']))

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('// Generated by tools/build.py: edit the portfolio/ folders and re-run, not this file.\n')
        f.write('window.PORTFOLIO = ')
        json.dump({'categories': categories}, f, indent=1, ensure_ascii=False)
        f.write(';\n')

    # bump ?v= on css/js links so browsers fetch the new files after every build
    stamp = str(int(time.time()))
    for page in ('index.html', 'explore.html'):
        path = os.path.join(ROOT, page)
        if os.path.exists(path):
            html = open(path, encoding='utf-8').read()
            html = re.sub(r'((?:src|href)="(?:js|css)/[\w.-]+\.(?:js|css))(?:\?v=\d+)?"', lambda m: f'{m.group(1)}?v={stamp}"', html)
            open(path, 'w', encoding='utf-8').write(html)

    for c in categories:
        n = sum(len(a['items']) for a in c['albums'])
        print(f"  {c['name']:<24} {len(c['albums'])} albums, {n} files")
    print(f'> wrote {os.path.relpath(OUT, ROOT)}')


if __name__ == '__main__':
    main()
