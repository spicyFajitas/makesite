#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2018-2022 Sunaina Pai
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""Make static website/blog with Python."""


import os
import shutil
import re
import glob
import sys
import json
import datetime

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def fread(filename):
    """Read file and close the file."""
    with open(filename, 'r') as f:
        return f.read()


def fwrite(filename, text):
    """Write content to file and close the file."""
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)

    with open(filename, 'w') as f:
        f.write(text)


def log(msg, *args):
    """Log message with specified arguments."""
    sys.stderr.write(msg.format(*args) + '\n')


def truncate(text, words=25):
    """Remove tags and truncate text to the specified number of words."""
    return ' '.join(re.sub('(?s)<.*?>', ' ', text).split()[:words])


def make_tag_slug(tag):
    """Convert tag name to a URL-safe slug."""
    return re.sub(r'[^a-z0-9]+', '-', tag.lower().strip()).strip('-')


def render_tags(tags_str, base_path=''):
    """Convert a comma-separated tags string to HTML links."""
    if not tags_str or not tags_str.strip():
        return ''
    tags = [t.strip() for t in tags_str.split(',') if t.strip()]
    links = ['<a class="tag" href="{}/tags/{}/">{}</a>'.format(
        base_path, make_tag_slug(t), t) for t in tags]
    return '<span class="tags">' + ''.join(links) + '</span>'


def read_headers(text):
    """Parse headers in text and yield (key, value, end-index) tuples."""
    for match in re.finditer(r'\s*<!--\s*(.+?)\s*:\s*(.+?)\s*-->\s*|.+', text):
        if not match.group(1):
            break
        yield match.group(1), match.group(2), match.end()


def rfc_2822_format(date_str):
    """Convert yyyy-mm-dd date string to RFC 2822 format date string."""
    d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return d.strftime('%a, %d %b %Y %H:%M:%S +0000')


def read_content(filename):
    """Read content and metadata from file into a dictionary."""
    # Read file content.
    text = fread(filename)

    # Read metadata and save it in a dictionary.
    date_slug = os.path.basename(filename).split('.')[0]
    match = re.search(r'^(?:(\d\d\d\d-\d\d-\d\d)-)?(.+)$', date_slug)
    content = {
        'date': match.group(1) or '1970-01-01',
        'slug': match.group(2),
    }

    # Read headers.
    end = 0
    for key, val, end in read_headers(text):
        content[key] = val

    # Separate content from headers.
    text = text[end:]

    # Convert Markdown content to HTML.
    if filename.endswith(('.md', '.mkd', '.mkdn', '.mdown', '.markdown')):
        try:
            if _test == 'ImportError':
                raise ImportError('Error forced by test')
            import commonmark
            text = commonmark.commonmark(text)
        except ImportError as e:
            log('WARNING: Cannot render Markdown in {}: {}', filename, str(e))

    # Update the dictionary with content and RFC 2822 date.
    content.update({
        'content': text,
        'rfc_2822_date': rfc_2822_format(content['date'])
    })

    return content


def render(template, **params):
    """Replace placeholders in template with values from params."""
    return re.sub(r'{{\s*([^}\s]+)\s*}}',
                  lambda match: str(params.get(match.group(1), match.group(0))),
                  template)


def rewrite_links(html, base_path):
    """Prepend base_path to root-relative href and src values in HTML."""
    if not base_path:
        return html
    return re.sub(r'(href|src)="(/[^"]*)"',
                  lambda m: '{}="{}{}"'.format(m.group(1), base_path, m.group(2)),
                  html)


def make_pages(src, dst, layout, **params):
    """Generate pages from page content."""
    items = []

    for src_path in glob.glob(src):
        content = read_content(src_path)

        # Process tags: store list for grouping and render HTML links for templates.
        raw_tags = content.get('tags', '')
        tags_list = [t.strip() for t in raw_tags.split(',') if t.strip()] if raw_tags else []
        content['tags_list'] = tags_list
        content['tags'] = render_tags(raw_tags, params.get('base_path', ''))

        page_params = dict(params, **content)

        # Populate placeholders in content if content-rendering is enabled.
        if page_params.get('render') == 'yes':
            rendered_content = render(page_params['content'], **page_params)
            page_params['content'] = rendered_content
            content['content'] = rendered_content

        # Rewrite root-relative links in content to include base_path.
        rewritten = rewrite_links(page_params['content'], params.get('base_path', ''))
        page_params['content'] = rewritten
        content['content'] = rewritten

        items.append(content)

        dst_path = render(dst, **page_params)
        output = render(layout, **page_params)

        log('Rendering {} => {} ...', src_path, dst_path)
        fwrite(dst_path, output)

    return sorted(items, key=lambda x: x['date'], reverse=True)


def make_tags_index(tag_map, dst, layout, **params):
    """Generate an index page listing all tags with post counts."""
    base_path = params.get('base_path', '')
    items = []
    for slug in sorted(tag_map.keys()):
        info = tag_map[slug]
        count = len(info['posts'])
        items.append(
            '<a class="tag" href="{}/tags/{}/"> {}'
            ' <span class="tag-count">{}</span></a>'.format(
                base_path, slug, info['name'], count))
    content = '<h1>Tags</h1>\n<div class="tags-index">\n{}\n</div>'.format('\n'.join(items))
    output = render(layout, content=content, title='Tags', slug='tags', **params)
    log('Rendering tags index => {} ...', dst)
    fwrite(dst, output)


def make_tag_pages(posts, dst, list_layout, item_layout, **params):
    """Generate a filtered list page for each tag found across all posts."""
    tag_map = {}
    for post in posts:
        for tag in post.get('tags_list', []):
            slug = make_tag_slug(tag)
            if slug not in tag_map:
                tag_map[slug] = {'name': tag, 'posts': []}
            tag_map[slug]['posts'].append(post)

    for tag_slug, info in tag_map.items():
        make_list(info['posts'], dst, list_layout, item_layout,
                  tag=tag_slug, title='Posts tagged "' + info['name'] + '"', **params)

    return tag_map


def make_list(posts, dst, list_layout, item_layout, **params):
    """Generate list page for a blog."""
    items = []
    for post in posts:
        item_params = dict(params, **post)
        item_params['summary'] = truncate(post['content'])
        item = render(item_layout, **item_params)
        items.append(item)

    params['content'] = ''.join(items)
    dst_path = render(dst, **params)
    output = render(list_layout, **params)

    log('Rendering list => {} ...', dst_path)
    fwrite(dst_path, output)


def main():
    # Create a new _site directory from scratch.
    if os.path.isdir('_site'):
        shutil.rmtree('_site')
    shutil.copytree(os.path.join(_SCRIPT_DIR, 'static'), '_site')
    if os.path.isdir('images'):
        shutil.copytree('images', os.path.join('_site', 'images'))

    # Default parameters.
    params = {
        'base_path': '',
        'subtitle': '',
        'author': 'spicyFajitas',
        'site_url': '',
        'current_year': datetime.datetime.now().year
    }

    # If params.json exists, load it.
    if os.path.isfile('params.json'):
        params.update(json.loads(fread('params.json')))

    # Load layouts.
    page_layout = fread(os.path.join(_SCRIPT_DIR, 'layout/page.html'))
    post_layout = fread(os.path.join(_SCRIPT_DIR, 'layout/post.html'))
    list_layout = fread(os.path.join(_SCRIPT_DIR, 'layout/list.html'))
    item_layout = fread(os.path.join(_SCRIPT_DIR, 'layout/item.html'))
    feed_xml = fread(os.path.join(_SCRIPT_DIR, 'layout/feed.xml'))
    item_xml = fread(os.path.join(_SCRIPT_DIR, 'layout/item.xml'))

    # Combine layouts to form final layouts.
    post_layout = render(page_layout, content=post_layout)
    list_layout = render(page_layout, content=list_layout)

    # Create site pages.
    make_pages('content/_index.md', '_site/index.html',
               page_layout, **params)
    make_pages('content/[!_]*.md', '_site/{{ slug }}/index.html',
               page_layout, **params)

    # Create blogs.
    blog_posts = make_pages('content/blog/*.md',
                            '_site/blog/{{ slug }}/index.html',
                            post_layout, blog='blog', **params)
    # news_posts = make_pages('content/news/*.md',
    #                         '_site/news/{{ slug }}/index.html',
    #                         post_layout, blog='news', **params)

    # Create blog list pages.
    make_list(blog_posts, '_site/blog/index.html',
              list_layout, item_layout, blog='blog', title='Blog', **params)

    # Create tag pages and index.
    tag_map = make_tag_pages(blog_posts, '_site/tags/{{ tag }}/index.html',
                              list_layout, item_layout, blog='blog', **params)
    make_tags_index(tag_map, '_site/tags/index.html', page_layout, **params)
    # make_list(news_posts, '_site/news/index.html',
    #           list_layout, item_layout, blog='news', title='News', **params)

    # Create RSS feeds.
    make_list(blog_posts, '_site/blog/rss.xml',
              feed_xml, item_xml, blog='blog', title='Blog', **params)
    # make_list(news_posts, '_site/news/rss.xml',
    #           feed_xml, item_xml, blog='news', title='News', **params)


# Test parameter to be set temporarily by unit tests.
_test = None


if __name__ == '__main__':
    main()
