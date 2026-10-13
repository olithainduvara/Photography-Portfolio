# Olitha Induvara Photography

A portfolio site for photography, videography, editing and aerial cinematography.
It is plain HTML/CSS/JS, so it runs on GitHub Pages with no build tools.

- **Home (`index.html`)**: a 3D hero built with Three.js. Album frames orbit a camera lens: drag to spin them, click a frame to open its album. The lens aperture closes as you scroll. Below the hero is a studio dashboard based on the Dribbble "Photography Community" shot: a feed of albums, an orbit of disciplines, a featured photographer card, latest content and a "Now booking" card.
- **Explore (`explore.html`)**: every album shown as a 3D folder stack. Filter by discipline, search, open an album to see a masonry gallery, and view photos or videos full-screen in the lightbox.
- **Booking**: the contact form, the composer bar and every "Book similar" button open WhatsApp with the message already written. Nothing is stored on the site.

## Adding your work: just add folders

```
portfolio/
  photography/                 ← one folder per discipline
    category.json              ← name, tagline, description, tags (optional)
    01-graduation-day/         ← one folder per album (the number only sets the order)
      album.json               ← title, location, description… (optional)
      walking-together.jpg
      under-the-trees.jpg
  videography/
    01-engex-2025-control-room/
      control-room-1.mp4
      control-room-1.jpg       ← same name as the video = its poster frame
  aerial/
  editing/
```

1. Create a folder such as `portfolio/aerial/05-kandy-lake-sunrise/` and drop in your photos or videos.
2. Run the build script from this folder:

   ```bash
   python tools/build.py
   ```

   It scans `portfolio/`, makes small thumbnails in `thumbs/` (this needs `pip install pillow`) and writes `js/data.js`.
3. Refresh the site. The new album appears on the home feed, in the 3D orbit and on Explore.

File names become captions (`sunrise-over-the-lake.jpg` becomes "Sunrise over the lake"). To add a whole new discipline, create another folder next to `photography/`.

### Reels

`portfolio/reels/` is a special section: its `category.json` has `"layout": "reels"`, so the site shows vertical 9:16 players instead of folders. They preview on hover and play with sound in the viewer. The home-page **Reels** row also picks up every other vertical video on the site, such as the drone reels in `aerial/`.

### Big photos and videos

Keep your raw exports somewhere outside `portfolio/` (`Assets 2/` is git-ignored for this). Copy in web-sized versions instead: photos about 2000 px on the long side, and videos as 720p H.264 MP4 with a `.jpg` poster of the same name. Large files make the site slow, and GitHub rejects any single file over 100 MB.

### `album.json` (all fields optional)

```json
{
  "title": "Kandy Lake Sunrise",
  "location": "Kandy",
  "date": "March 2026",
  "description": "First light over the lake, flown at 5:40 am.",
  "order": ["wide.jpg", "close.jpg", "clip.mp4"],
  "captions": { "wide.jpg": "The whole lake from 120 m" },
  "link": "https://www.facebook.com/…",
  "more": 24
}
```

- `order` sets the photo order. The first photo becomes the album cover.
- `"featured": false` keeps an album in Explore but off the home page: not in the feed, the 3D orbit, the thumbnails or the Reels row.
- `"spotlight": true` puts an album in the 3D showcase on the home page, and its first 4 images lead the 3D orbit. Set it on one album only (currently `editing/01-collage-designs`).
- `"reelsOrder": 99` moves an album's clips to the end of the home Reels row (default 0; lower numbers come first).
- `"pin": 1` (2, 3 …) makes an album one of the first posts in the home feed, in that order.
- `"feed": false` gives an album no feed post; its clips still appear in the Reels row.
- `link` + `more` add a "+24 more frames on Facebook" button.

### Your details

Edit `js/site.js` to change your name, WhatsApp number, email, social links, bio, stats and the "Now booking" list.

## Starter photos still to replace

Two photography albums, *Convocation Portraits* and *Personality Development Workshop*, are still cut from Facebook screenshots. They're about 330 px wide. Swap in the originals when you have them, then run `python tools/build.py` again.

## Preview locally

The 3D scene needs a local web server; opening the HTML file directly won't load it.

```bash
python -m http.server 8080
```

Then open http://localhost:8080.

## Deploy on GitHub Pages

1. Push this folder to a GitHub repository.
2. Go to **Settings → Pages**, choose **Deploy from a branch**, pick `main` and `/ (root)`.
3. Run `python tools/build.py` before every push, so `js/data.js` matches your folders.

## Files

| Path | What it is |
|---|---|
| `index.html` | Home: 3D hero, studio feed, about, contact |
| `explore.html` | Album folders, album galleries, search |
| `css/style.css` | All styles (dark studio theme, amber accent) |
| `js/hero3d.js` | Three.js scene (lens, orbiting frames, dust, interaction) |
| `js/app.js` | Feed, orbit widget, explore views, lightbox, WhatsApp booking |
| `js/site.js` | **Your details**: edit freely |
| `js/data.js` | Generated by `tools/build.py`; don't edit by hand |
| `tools/build.py` | Folder scanner and thumbnail maker |
| `portfolio/` | **Your work**, one folder per album |
