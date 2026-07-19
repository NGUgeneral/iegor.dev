#!/usr/bin/env python3

import shutil
import re
from datetime import datetime
from pathlib import Path
import markdown
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent
CONTENT_DIR = BASE_DIR / "content"
POSTS_DIR = CONTENT_DIR / "posts"
PROJECTS_DIR = CONTENT_DIR / "projects"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "docs"
SRC_ASSETS_DIR = BASE_DIR / "assets"
LAYOUT_TEMPLATE = "layout.html"

SITE_URL = "https://iegor.dev"
BASE_URL = ""

# Ensure paths exist
TEMPLATES_DIR.mkdir(exist_ok=True)
CONTENT_DIR.mkdir(exist_ok=True)
POSTS_DIR.mkdir(exist_ok=True)


def parse_front_matter(content):
    """Parse YAML-style front-matter from markdown."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    front_matter_text = parts[1].strip()
    markdown_content = parts[2].strip()

    metadata = {}
    for line in front_matter_text.split("\n"):
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    return metadata, markdown_content


def render_markdown(content):
    """Convert markdown to HTML and fix absolute paths for subdirectories using Regex."""
    html = markdown.markdown(content, extensions=["fenced_code", "tables", "toc", "nl2br"])
    
    if BASE_URL:
        # 1. Finds ANY src="/..." or href="/..." and prepends BASE_URL
        html = re.sub(r'(src|href)=([\'"])/(?!\/)', rf'\1=\2{BASE_URL}/', html)
        
        # 2. Safety catch: If you accidentally forgot the leading slash for an asset (e.g. src="assets/...")
        html = re.sub(r'(src)=([\'"])assets/', rf'\1=\2{BASE_URL}/assets/', html)
        
    return html


def read_file(path):
    """Read file content."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    """Write file content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def clear_docs_dir():
    """Clear the docs directory completely."""
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Cleared {OUTPUT_DIR}")


def copy_assets():
    """Copy static assets from the root assets/ directory to docs/assets/."""
    if SRC_ASSETS_DIR.exists():
        dst_assets_dir = OUTPUT_DIR / "assets"
        shutil.copytree(SRC_ASSETS_DIR, dst_assets_dir, dirs_exist_ok=True)
        print(f"✓ Copied assets to {dst_assets_dir.relative_to(BASE_DIR)}")
    else:
        print("⚠ No root assets directory found. Skipping asset copy.")


def process_post(post_path):
    """Process a single post markdown file."""
    content = read_file(post_path)
    metadata, markdown_content = parse_front_matter(content)
    html_content = render_markdown(markdown_content)
    slug = post_path.stem

    return {
        "slug": slug,
        "title": metadata.get("title", slug.replace("-", " ").title()),
        "date": metadata.get("date", ""),
        "excerpt": metadata.get("excerpt", ""),
        "content": html_content,
        "file_path": post_path,
    }


def parse_date(date_str):
    """Parse date string to datetime object for sorting."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return datetime.min


def build_projects_page(projects):
    """Build a dedicated projects listing page at /projects/index.html."""
    if not projects:
        print("⚠ No projects to list.")
        return

    projects_list_html = '<ul class="project-list">'
    for project in projects:
        projects_list_html += f'''
            <li class="project-item">
                <div class="project-title">
                    <a href="{BASE_URL}/project/{project["slug"]}/">{project["title"]}</a>
                </div>
                <div class="project-date">{project["date"]}</div>
                <div class="project-excerpt">{project["excerpt"]}</div>
            </li>
        '''
    projects_list_html += "</ul>"

    projects_page_html = env.get_template(LAYOUT_TEMPLATE).render(
        base_url=BASE_URL,
        canonical_url=f"{SITE_URL}{BASE_URL}/projects/",
        title="Projects",
        description="A list of implemented and supported projects.",
        content=f"<h1>Projects</h1>\n{projects_list_html}",
        meta_tags='<meta name="og:type" content="website">',
    )

    output_path = OUTPUT_DIR / "projects" / "index.html"
    write_file(output_path, projects_page_html)
    print(f"✓ Generated projects page: {output_path.relative_to(BASE_DIR)}")


def build_posts_page(posts):
    """Build a dedicated posts listing page at /posts/index.html."""
    if not posts:
        print("⚠ No posts to list.")
        return

    posts_list_html = '<ul class="post-list">'
    for post in posts:
        posts_list_html += f'''
            <li class="post-item">
                <div class="post-title">
                    <a href="{BASE_URL}/post/{post["slug"]}/">{post["title"]}</a>
                </div>
                <div class="post-date">{post["date"]}</div>
                <div class="post-excerpt">{post["excerpt"]}</div>
            </li>
        '''
    posts_list_html += "</ul>"

    posts_page_html = env.get_template(LAYOUT_TEMPLATE).render(
        base_url=BASE_URL,
        canonical_url=f"{SITE_URL}{BASE_URL}/posts/",
        title="Posts",
        description="A collection of posts about backend engineering, system design, and technical insights.",
        content=f"<h1>Posts</h1>\n{posts_list_html}",
        meta_tags='<meta name="og:type" content="website">',
    )

    output_path = OUTPUT_DIR / "posts" / "index.html"
    write_file(output_path, posts_page_html)
    print(f"✓ Generated posts page: {output_path.relative_to(BASE_DIR)}")


def build_projects():
    """Build all project pages and return sorted list of projects."""
    projects = []

    if not PROJECTS_DIR.exists():
        print("⚠ No projects directory found.")
        return projects

    for project_file in sorted(PROJECTS_DIR.glob("*.md")):
        content = read_file(project_file)
        metadata, markdown_content = parse_front_matter(content)
        html_content = render_markdown(markdown_content)
        slug = project_file.stem

        project = {
            "slug": slug,
            "title": metadata.get("title", slug.replace("-", " ").title()),
            "date": metadata.get("date", ""),
            "excerpt": metadata.get("excerpt", ""),
            "content": html_content,
            "file_path": project_file,
        }
        projects.append(project)
        print(f"✓ Processed: {project['title']} ({project_file.name})")

    projects.sort(key=lambda p: parse_date(p["date"]), reverse=True)

    for project in projects:
        output_path = OUTPUT_DIR / "project" / project["slug"] / "index.html"

        project_html = env.get_template(LAYOUT_TEMPLATE).render(
            base_url=BASE_URL,
            canonical_url=f"{SITE_URL}{BASE_URL}/project/{project['slug']}/",
            title=project["title"],
            description=project.get("excerpt", ""),
            content=project["content"],
            meta_tags=f'<meta name="date" content="{project["date"]}">',
        )

        write_file(output_path, project_html)
        print(f"  → Generated: {output_path.relative_to(BASE_DIR)}")

    return projects


def build_posts():
    """Build all post pages and return sorted list of posts."""
    posts = []

    if not POSTS_DIR.exists():
        print("⚠ No posts directory found.")
        return posts

    for post_file in sorted(POSTS_DIR.glob("*.md")):
        post = process_post(post_file)
        posts.append(post)
        print(f"✓ Processed: {post['title']} ({post_file.name})")

    posts.sort(key=lambda p: parse_date(p["date"]), reverse=True)

    for post in posts:
        output_path = OUTPUT_DIR / "post" / post["slug"] / "index.html"

        post_html = env.get_template(LAYOUT_TEMPLATE).render(
            base_url=BASE_URL,
            canonical_url=f"{SITE_URL}{BASE_URL}/post/{post['slug']}/",
            title=post["title"],
            description=post.get("excerpt", ""),
            content=post["content"],
            meta_tags=f'<meta name="date" content="{post["date"]}">',
        )

        write_file(output_path, post_html)
        print(f"  → Generated: {output_path.relative_to(BASE_DIR)}")

    return posts


def build_home(posts):
    """Build the home page (about.md)."""
    about_path = CONTENT_DIR / "about.md"

    if not about_path.exists():
        print("⚠ No about.md found. Skipping home page generation.")
        return

    content = read_file(about_path)
    metadata, markdown_content = parse_front_matter(content)
    html_content = render_markdown(markdown_content)

    home_html = env.get_template(LAYOUT_TEMPLATE).render(
        base_url=BASE_URL,
        canonical_url=f"{SITE_URL}{BASE_URL}/",
        title="Home",
        description="Backend engineer, system design enthusiast, and technical writer.",
        content=html_content,
        meta_tags='<meta name="og:type" content="website">',
    )

    output_path = OUTPUT_DIR / "index.html"
    write_file(output_path, home_html)
    print(f"✓ Generated home page: {output_path.relative_to(BASE_DIR)}")


def build_contact():
    """Build the contact page."""
    contact_path = CONTENT_DIR / "contact.md"

    if not contact_path.exists():
        print("⚠ No contact.md found. Skipping contact page generation.")
        return

    content = read_file(contact_path)
    metadata, markdown_content = parse_front_matter(content)
    html_content = render_markdown(markdown_content)

    contact_html = env.get_template(LAYOUT_TEMPLATE).render(
        base_url=BASE_URL,
        canonical_url=f"{SITE_URL}{BASE_URL}/contact/",
        title="Contact",
        description="Get in touch for backend architecture, system design, and technical consulting.",
        content=html_content,
        meta_tags='<meta name="og:type" content="website">',
    )

    output_path = OUTPUT_DIR / "contact" / "index.html"
    write_file(output_path, contact_html)
    print(f"✓ Generated contact page: {output_path.relative_to(BASE_DIR)}")


def create_robots_txt():
    """Create a robots.txt file for SEO."""
    robots_content = """User-agent: *
Allow: /

Sitemap: https://iegor.dev/sitemap.xml
"""
    write_file(OUTPUT_DIR / "robots.txt", robots_content)
    print(f"✓ Generated: robots.txt")


def main():
    """Main build process."""
    print("\n🔨 Building static site...\n")

    clear_docs_dir()
    copy_assets()

    global env
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    env.globals["current_year"] = datetime.now().year

    posts = build_posts()
    projects = build_projects()
    print()

    build_posts_page(posts)
    build_projects_page(projects)
    build_home(posts)
    build_contact()
    create_robots_txt()

    print(f"\n✅ Build complete! Output: {OUTPUT_DIR}\n")


if __name__ == "__main__":
    main()