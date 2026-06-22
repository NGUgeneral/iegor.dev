# iegor.dev – Ultra-Lightweight Static Site Generator

A pragmatic, zero-runtime static site generator written in pure Python. Converts Markdown content with YAML front-matter into clean, performant HTML served from GitHub Pages.

## ✨ Features

- **Pure Static** – No JavaScript, no runtime servers. Pure HTML/CSS served directly from GitHub Pages
- **Minimal Dependencies** – Only Jinja2 and Markdown (plus Python stdlib)
- **Fast Build** – Entire site builds in milliseconds
- **Clean URLs** – Posts accessible at `/post/{slug}/` (no `.html` extensions needed)
- **Dark Mode Support** – Automatic dark/light mode via CSS media queries
- **SEO Ready** – Proper meta tags, semantic HTML, Open Graph support
- **Simple Pipeline** – One Python script, no complex configuration

## 📁 Project Structure

```
.
├── build.py                        # Main build script
├── templates/
│   └── layout.html                 # Jinja2 base template (header, nav, footer, CSS)
├── content/
│   ├── about.md                    # Home page content
│   └── posts/
│       ├── hello-world.md          # Sample post 1
│       └── system-design-notes.md  # Sample post 2
│   └── projects/
│       ├── hello-world.md          # Sample project 1
│       └── system-design-notes.md  # Sample project 2
├── docs/                           # OUTPUT - Generated static site (GitHub Pages)
│   ├── index.html
│   ├── robots.txt
│   └── post/
│       ├── hello-world/
│       │   └── index.html
│       └── system-design-notes/
│           └── index.html
└── .venv/                           # Python virtual environment
```

## 🚀 Quick Start

### 1. Setup Python Environment

The virtual environment is already configured. To activate it:

**On PowerShell (Windows):**
```powershell
.venv\Scripts\Activate.ps1
```

**On bash (macOS/Linux):**
```bash
source .venv/bin/activate
```

### 2. Install Dependencies

Dependencies are already installed. To verify:
```bash
pip list | grep -E "jinja2|markdown"
```

Or reinstall if needed:
```bash
pip install jinja2 markdown
```

### 3. Build the Site

```bash
python build.py
```

**Expected output:**
```
🔨 Building static site...

✓ Cleared C:\Users\name\source\repos\iegor.dev\docs
✓ Processed: Hello World (hello-world.md)
✓ Processed: System Design Notes (system-design-notes.md)
  → Generated: docs\post\hello-world\index.html
  → Generated: docs\post\system-design-notes\index.html
✓ Processed: Hello World (hello-world.md)
✓ Processed: System Design Notes (system-design-notes.md)
  → Generated: docs\project\hello-world\index.html
  → Generated: docs\project\system-design-notes\index.html

✓ Generated posts page: docs\posts\index.html
✓ Generated projects page: docs\projects\index.html
✓ Generated home page: docs\index.html
✓ Generated contact page: docs\contact\index.html
✓ Generated: robots.txt

✅ Build complete!
```

### 4. Preview Locally

Python 3.7+:
```bash
python -m http.server 8000 --directory docs
```

Then open http://localhost:8000 in your browser.

## 📝 Creating Content

### Adding a Post

1. Create a new `.md` file in `content/posts/`:
```bash
content/posts/my-new-post.md
```

2. Add front-matter and markdown:
```markdown
---
title: My New Post
date: 2026-06-18
excerpt: A brief description of the post for the homepage listing.
---

# My New Post

This is the main content...

## Section

More markdown here.
```

3. Rebuild:
```bash
python build.py
```

Your post will be generated at `/post/my-new-post/index.html`.

### Front-Matter Fields

- **title** (required) – Post title displayed in header and listings
- **date** (recommended) – Publication date in `YYYY-MM-DD` format (used for sorting)
- **excerpt** (optional) – Brief description shown in post listings

### Front-Matter Format

The front-matter uses a simple YAML-like format:
```yaml
---
key: value
key2: value with spaces
key3: 123
---

# Then your markdown content starts here
```

## 🎨 Customization

### Modifying the Template

Edit `templates/layout.html` to:
- Change colors, fonts, or spacing
- Add/remove navigation links
- Modify header and footer
- Adjust CSS media queries for dark mode

Template variables available:
- `{{ title }}` – Page title
- `{{ description }}` – Meta description
- `{{ content }}` – Rendered HTML content
- `{{ meta_tags }}` – Additional meta tags (OG, Twitter cards, etc.)

### Styling

All CSS is embedded in `templates/layout.html` for maximum portability. Modify the `<style>` block to customize:
- Color scheme (light/dark mode via `@media (prefers-color-scheme: dark)`)
- Typography (currently using system fonts)
- Spacing and layout
- Responsive breakpoints

## 🔧 Build Script Details

`build.py` performs these steps:

1. **Clears `/docs`** – Removes all previous output to prevent stale files
2. **Parses Content** – Reads markdown files and extracts YAML front-matter
3. **Renders Posts** – Converts markdown to HTML using Jinja2 templates
4. **Generates Listings** – Creates sorted post list on home page
5. **Outputs HTML** – Writes clean, self-contained HTML files

All generated HTML includes embedded CSS and is completely self-contained.

## 📦 Deployment to GitHub Pages

1. Push all files (including `/docs`) to your repository:
```bash
git add .
git commit -m "Build site"
git push origin main
```

2. In your GitHub repository settings:
   - Go to **Settings → Pages**
   - Set **Source** to "Deploy from a branch"
   - Set **Branch** to `main`, folder to `/docs`
   - Click Save

3. GitHub Pages will now serve your site at `https://yourusername.github.io/`

## 🔄 Workflow

**For daily writing:**

```bash
# 1. Write a new post
# content/posts/new-article.md

# 2. Build the site
python build.py

# 3. Preview
python -m http.server 8000 --directory docs

# 4. Check at http://localhost:8000/post/new-article/

# 5. Deploy
git add .
git commit -m "Add new post"
git push
```

## 📚 Markdown Features Supported

- Headers (`#`, `##`, `###`, etc.)
- **Bold** and *italic*
- Lists (ordered and unordered)
- [Links](https://example.com)
- `Code` and `code blocks`
- > Blockquotes
- Tables
- Images: `![alt](path/to/image.png)`

Example:
````markdown
---
title: Example
date: 2026-06-18
excerpt: Demo post
---

# Example Post

This is **bold** and this is *italic*.

## Lists

- Item 1
- Item 2
  - Nested item

## Code

```python
def hello():
    print("world")
```

## Table

| Feature | Status |
|---------|--------|
| Speed   | ✅     |
| Size    | Small  |
````

## 🎯 Philosophy

This generator embodies pragmatic engineering:

- **Minimal** – No unnecessary layers of abstraction
- **Fast** – Static output means near-zero latency
- **Transparent** – All code is readable Python and HTML
- **Maintainable** – Easy to modify and extend
- **Reliable** – No runtime dependencies or databases

Perfect for personal blogs, portfolios, and technical writing.

## 📖 License

Feel free to fork, modify, and use this for your own site.

---

**Happy writing!** 🚀
