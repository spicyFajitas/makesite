# Blog

Personal blog built with [makesite.py](https://github.com/sunainapai/makesite).

## Repository structure

```text
├── content/        # Blog posts and pages (markdown)
│   ├── _index.md
│   ├── about.md
│   ├── contact.md
│   ├── blog/       # Blog posts
│   └── news/       # News posts
└── build/              # Build system
    ├── makesite.py     # Static site generator
    ├── layout/         # HTML/XML templates
    ├── static/         # CSS and static assets
    ├── test/           # Unit tests
    └── website_update.sh  # Server-side pull script
```

## Writing content

Add markdown files to `content/blog/` or `content/news/`. File names follow the pattern `YYYY-MM-DD-slug.md`. Each file can include optional HTML comment headers:

```markdown
<!-- title: My Post Title -->
<!-- subtitle: Optional subtitle -->

Post content here...
```

Push to `master` and GitHub Actions will build and deploy automatically.

## Local development

`make` manages a venv in `build/.venv` automatically — no manual `pip install` needed.

| Command      | What it does                                        |
|--------------|-----------------------------------------------------|
| `make build` | Build the site into `_site/`                        |
| `make serve` | Build then serve at <http://localhost:8000>         |
| `make test`  | Run the test suite                                  |
| `make clean` | Remove `_site/` and compiled Python files           |

First run creates the venv and installs dependencies; subsequent runs skip that step.

## Deployment

GitHub Actions builds the site on every push to `master` and force-pushes the output to the `built` branch.

[build/website_update.sh](build/website_update.sh) runs on the server and handles pulling that output into `public_html`. On first run it clones the `built` branch; on subsequent runs it pulls. It also registers itself as an hourly cron job automatically.

Initial server setup:

```bash
chmod +x ~/makesite/build/website_update.sh
~/makesite/build/website_update.sh
```
