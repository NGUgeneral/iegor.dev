# iegor.dev – Ultra-Lightweight Static Site Generator

A pragmatic, zero-runtime static site generator written in pure Python. Converts Markdown content with YAML front-matter into clean, performant HTML served from GitHub Pages.

## ✨ Features

- **Pure Static** – No JavaScript, no runtime servers. Pure HTML/CSS served directly from GitHub Pages
- **Small Python Build** – Dependencies are listed in `requirements.txt`; the deployed site has no runtime server
- **Fast Build** – Entire site builds in milliseconds
- **Clean URLs** – Posts and projects have extension-free routes
- **Dark Mode Support** – Automatic dark/light mode via CSS media queries
- **SEO Ready** – Proper meta tags, semantic HTML, Open Graph support
- **Simple Pipeline** – One Python script, no complex configuration

## 📁 Project Structure

```
.
├── build.py                        # Main build script
├── serve.py                        # Local preview server with custom 404 handling
├── requirements.txt                # Python build dependencies
├── .env.example                    # Example local build settings
├── templates/
│   └── layout.html                 # Jinja2 base template (header, nav, footer, CSS)
├── content/
│   ├── about.md                    # Home page content
│   ├── contact.md
│   ├── privacy.md
│   ├── posts/                      # Markdown posts
│   └── projects/                   # Markdown project pages
├── assets/                         # Static source assets copied into the build
└── docs/                           # Generated output; not committed
```

## 🚀 Quick Start

### 1. Create a Python Environment

From the repository root, create and activate a virtual environment:

**On PowerShell (Windows):**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

**On bash (macOS/Linux):**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

Install the packages used by the build script:
```sh
python -m pip install -r requirements.txt
```

### 3. Configure Local Build Settings

Copy `.env.example` to `.env`:

**PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Bash:**
```bash
cp .env.example .env
```

The example sets `ANALYTICS_ENABLED=false`, so local builds omit the analytics pixel. `.env` is ignored by Git. To test the enabled build locally, change the value to `true` in `.env`.

### 4. Build the Site

```bash
python build.py
```

The generated site is written to `docs/`, including the home, posts, projects, contact, privacy, and 404 pages, plus `robots.txt` and `sitemap.xml`.

### 5. Preview Locally

Run the local preview server from the repository root:
```bash
python serve.py
```

Open <http://127.0.0.1:8000>. The preview server serves files from `docs/` and uses the generated `404.html` for missing paths.

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
- `{{ current_year }}` – Current year for the footer
- `{{ analytics_enabled }}` – Controls whether the analytics pixel is rendered

### Styling

All CSS is embedded in `templates/layout.html` for maximum portability. Modify the `<style>` block to customize:
- Color scheme (light/dark mode via `@media (prefers-color-scheme: dark)`)
- Typography (currently using system fonts)
- Spacing and layout
- Responsive breakpoints

## 🔧 Build Script Details

`build.py` performs these steps:

1. **Clears `docs/`** – Removes all previous generated output
2. **Parses Content** – Reads markdown files and extracts YAML front-matter
3. **Renders Pages** – Converts Markdown posts, projects, and static content pages to HTML using the layout template
4. **Generates Indexes** – Creates posts and projects listings
5. **Generates SEO Files** – Writes `robots.txt` and `sitemap.xml`
6. **Copies Assets** – Copies `assets/` into `docs/assets/`

Generated pages include embedded CSS. Static images and other assets remain separate files under `docs/assets/`.

### Analytics Build Setting

The build reads `ANALYTICS_ENABLED` as an environment variable. `.env` supplies the local value; `load_dotenv` does not override a value already supplied by the process environment. The GitHub Actions workflow passes the GitHub Actions variable into the build.

To enable the pixel for production deployments, add the Actions **repository variable** `ANALYTICS_ENABLED` with value `true` under **Settings → Secrets and variables → Actions → Variables**. Leave it unset or set it to `false` to omit the pixel. This is a public boolean setting, not a secret.

## 📦 Deployment to GitHub Pages

The repository deploys through `.github/workflows/deploy.yml`. On pushes to `main` (or a manual workflow run), GitHub Actions installs the dependencies, builds the site, and deploys the `docs/` artifact to GitHub Pages. Generated `docs/` output does not need to be committed.

To configure Pages for this workflow:

1. In GitHub, open **Settings → Pages**.
2. Set **Build and deployment → Source** to **GitHub Actions**.
3. Push changes to `main` or run **Build and Deploy Portfolio** from the Actions tab.

The site is published at <https://iegor.dev>.

To deploy a content change:
```bash
git add content/ templates/ assets/
git commit -m "Update site content"
git push origin main
```

## 🔄 Workflow

**For daily writing:**

```bash
# 1. Write a new post
# content/posts/new-article.md

# 2. Build the site
python build.py

# 3. Preview using the local server (includes custom 404 handling)
python serve.py

# 4. Check at http://127.0.0.1:8000/post/new-article/

# 5. Deploy by pushing to main
git add content/posts/new-article.md
git commit -m "Add new post"
git push origin main
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

**Happy writing!** 🚀
