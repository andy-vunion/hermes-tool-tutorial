#!/usr/bin/env python3
"""Fix chain chapter IDs in merged 10x-tracker-claude.html to match nav links."""
import re

with open('/home/admin/tool-tutorial/10x-tracker-claude.html') as f:
    html = f.read()

# Find all chain nav links (after "── 产业链拆解体系 ──" separator)
nav_section = html.split('── 产业链拆解体系 ──')
if len(nav_section) < 2:
    print("ERROR: chain nav section not found")
    exit(1)

nav_links = re.findall(r'href="#([^"]+)"[^>]*>([^<]+)</a>', nav_section[1])

fixed = 0
for slug, text in nav_links:
    # Skip the main design doc link
    if '设计文档' in text:
        continue
    
    clean_text = text.strip()
    
    # Find the h2 or h3 with this text content and fix its id
    # Escape special regex chars in text
    escaped = re.escape(clean_text)
    pattern = rf'<(h[23])\s+id="([^"]*)"[^>]*>\s*{escaped}\s*</\1>'
    
    m = re.search(pattern, html)
    if m:
        old_id = m.group(2)
        tag = m.group(1)
        # Replace the id
        html = html.replace(f'<{tag} id="{old_id}">{clean_text}</{tag}>', 
                           f'<{tag} id="{slug}">{clean_text}</{tag}>')
        fixed += 1
    else:
        # Try without existing id
        pattern2 = rf'<(h[23])[^>]*>\s*{escaped}\s*</\1>'
        m2 = re.search(pattern2, html)
        if m2:
            tag = m2.group(1)
            html = html.replace(f'<{tag}>{clean_text}</{tag}>',
                               f'<{tag} id="{slug}">{clean_text}</{tag}>')
            fixed += 1
        else:
            print(f"  NOT FOUND: {clean_text[:50]}")

# Also ensure the .chapter divs have matching IDs where possible
# For chain chapters, add id to the .chapter div
for slug, text in nav_links:
    if '设计文档' in text:
        continue
    clean_text = text.strip()
    escaped = re.escape(clean_text)
    # Find chapter div containing this h2
    pattern = rf'(<div class="chapter">[^<]*<h[23] id="{re.escape(slug)}"[^>]*>{escaped}</h[23]>)'
    if re.search(pattern, html):
        # Replace the chapter div to include the id
        html = re.sub(
            rf'<div class="chapter">([^<]*<h[23] id="{re.escape(slug)}")',
            rf'<div class="chapter" id="{slug}">\1',
            html,
            count=1
        )

with open('/home/admin/tool-tutorial/10x-tracker-claude.html', 'w') as f:
    f.write(html)

print(f"Fixed {fixed} heading IDs")
print(f"Total size: {len(html)} chars")
