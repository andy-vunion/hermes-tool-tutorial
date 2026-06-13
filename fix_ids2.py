#!/usr/bin/env python3
"""Fix chain chapter IDs - round 2: handle h4 and fuzzy text matching."""
import re

with open('/home/admin/tool-tutorial/10x-tracker-claude.html') as f:
    html = f.read()

nav_section = html.split('── 产业链拆解体系 ──')
nav_links = re.findall(r'href="#([^"]+)"[^>]*>([^<]+)</a>', nav_section[1])

def find_heading(html, text, slug):
    """Find a heading element containing this text and set its id."""
    # Normalize: remove emoji prefixes that might not be in HTML
    search_text = text.strip()
    
    # Try exact match on h2/h3/h4
    for tag in ['h4', 'h3', 'h2']:
        escaped = re.escape(search_text)
        # Match heading with or without existing id
        patterns = [
            rf'<{tag}\s+id="([^"]*)"[^>]*>\s*{escaped}\s*</{tag}>',
            rf'<{tag}[^>]*>\s*{escaped}\s*</{tag}>',
        ]
        for pat in patterns:
            m = re.search(pat, html)
            if m:
                old = m.group(0)
                new = f'<{tag} id="{slug}">{search_text}</{tag}>'
                return html.replace(old, new, 1), True
    
    # Try with emoji removed from search text
    text_no_emoji = re.sub(r'[✅❌⚠️🎯📊💰📋🚨⚙🧬🔗📄📐📖🟢]', '', search_text).strip()
    if text_no_emoji != search_text:
        for tag in ['h4', 'h3', 'h2']:
            escaped = re.escape(text_no_emoji)
            patterns = [
                rf'<{tag}\s+id="([^"]*)"[^>]*>\s*{escaped}\s*</{tag}>',
                rf'<{tag}[^>]*>\s*{escaped}\s*</{tag}>',
            ]
            for pat in patterns:
                m = re.search(pat, html)
                if m:
                    old = m.group(0)
                    # Build replacement with id
                    if 'id=' in m.group(0):
                        new = m.group(0).replace('id="' + m.group(1) + '"', 'id="' + slug + '"')
                    else:
                        new = m.group(0).replace('<' + tag, '<' + tag + ' id="' + slug + '"', 1)
                    return html.replace(old, new, 1), True
    
    # Try substring match (nav text may be truncated)
    words = search_text.split()[:5]  # First 5 words
    if len(words) >= 2:
        key = ' '.join(words[:3])
        escaped = re.escape(key)
        for tag in ['h4', 'h3', 'h2']:
            pat = rf'<{tag}\s+id="([^"]*)"[^>]*>([^<]*{escaped}[^<]*)</{tag}>'
            m = re.search(pat, html)
            if m:
                old = m.group(0)
                actual_text = m.group(2).strip()
                new = f'<{tag} id="{slug}">{actual_text}</{tag}>'
                return html.replace(old, new, 1), True
    
    return html, False

fixed = 0
not_found = []
for slug, text in nav_links:
    if '设计文档' in text:
        continue
    html, ok = find_heading(html, text, slug)
    if ok:
        fixed += 1
    else:
        not_found.append((slug, text))

print(f"Fixed: {fixed}")
if not_found:
    print(f"Still not found ({len(not_found)}):")
    for slug, text in not_found:
        print(f"  #{slug} → '{text}'")

# Also add IDs to .chapter divs for chain chapters
# Find chain chapter divs and add matching IDs
chain_start = html.find('── 产业链拆解体系 ──')
if chain_start > 0:
    # Find all chapter divs after the chain nav
    remainder = html[chain_start:]
    chapter_pattern = r'<div class="chapter"(?:\s+id="([^"]*)")?\s*>'
    
# Actually, let's just ensure the .chapter divs have the same id as their first h2
def add_chapter_ids(html):
    """Add id to .chapter divs that contain h2/h3 with ids."""
    chapters = list(re.finditer(r'<div class="chapter"(?:\s+id="[^"]*")?\s*>', html))
    for i, ch in enumerate(chapters):
        # Find the next chapter or end
        end = chapters[i+1].start() if i+1 < len(chapters) else len(html)
        content = html[ch.start():end]
        # Find first h2/h3/h4 with id
        h_match = re.search(r'<(h[234])\s+id="([^"]+)"', content)
        if h_match and 'id=' not in ch.group(0):
            new_div = f'<div class="chapter" id="{h_match.group(2)}">'
            html = html[:ch.start()] + new_div + html[ch.end():]
            # Adjust positions
            chapters = list(re.finditer(r'<div class="chapter"(?:\s+id="[^"]*")?\s*>', html))
    return html

html = add_chapter_ids(html)

with open('/home/admin/tool-tutorial/10x-tracker-claude.html', 'w') as f:
    f.write(html)

print(f"Final size: {len(html)} chars")
