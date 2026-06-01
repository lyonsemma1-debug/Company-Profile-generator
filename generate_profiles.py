#!/usr/bin/env python3
"""
generate_profiles.py
Reads GC-Company-Profiles(Company Profiles)-2.csv and produces profiles-output.html
"""

import csv
import re
import html
import os
import io
import argparse
import tempfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "input.csv")
OUTPUT_PATH = os.path.join(tempfile.gettempdir(), "profiles-output.html")

SVG_ARROWS = """<svg width="45" height="14" viewBox="0 0 45 14" fill="none" xmlns="http://www.w3.org/2000/svg" style="display:block; flex-shrink:0;">
  <rect width="2.65033" height="2.65033" transform="matrix(-4.37114e-08 1 1 4.37114e-08 37.049 6.10352e-05)" fill="#F25103"/>
  <rect width="2.65033" height="2.65033" transform="matrix(-4.37114e-08 1 1 4.37114e-08 39.6993 2.65039)" fill="#F25103"/>
  <rect x="42.3497" y="7.95117" width="2.65033" height="2.65033" transform="rotate(90 42.3497 7.95117)" fill="#F25103"/>
  <rect x="39.6993" y="10.6015" width="2.65033" height="2.65033" transform="rotate(90 39.6993 10.6015)" fill="#F25103"/>
  <rect width="2.65033" height="2.65033" transform="matrix(-4.37114e-08 1 1 4.37114e-08 42.3497 5.30072)" fill="#F25103"/>
  <rect width="2.65033" height="2.65033" transform="matrix(-4.37114e-08 1 1 4.37114e-08 12.3497 0)" fill="#F25103"/>
  <rect width="2.65033" height="2.65033" transform="matrix(-4.37114e-08 1 1 4.37114e-08 15 2.65051)" fill="#F25103"/>
  <rect x="17.6503" y="7.95117" width="2.65033" height="2.65033" transform="rotate(90 17.6503 7.95117)" fill="#F25103"/>
  <rect x="15" y="10.6015" width="2.65033" height="2.65033" transform="rotate(90 15 10.6015)" fill="#F25103"/>
  <rect width="2.65033" height="2.65033" transform="matrix(-4.37114e-08 1 1 4.37114e-08 17.6503 5.30084)" fill="#F25103"/>
  <rect width="2.65033" height="2.65033" transform="matrix(-4.37114e-08 1 1 4.37114e-08 24.6993 6.10352e-05)" fill="#F25103"/>
  <rect width="2.65033" height="2.65033" transform="matrix(-4.37114e-08 1 1 4.37114e-08 27.3497 2.65039)" fill="#F25103"/>
  <rect x="30" y="7.95117" width="2.65033" height="2.65033" transform="rotate(90 30 7.95117)" fill="#F25103"/>
  <rect x="27.3497" y="10.6015" width="2.65033" height="2.65033" transform="rotate(90 27.3497 10.6015)" fill="#F25103"/>
  <rect width="2.65033" height="2.65033" transform="matrix(-4.37114e-08 1 1 4.37114e-08 30 5.30072)" fill="#F25103"/>
  <rect width="2.65033" height="2.65033" transform="matrix(-4.37114e-08 1 1 4.37114e-08 0 0)" fill="#F25103"/>
  <rect width="2.65033" height="2.65033" transform="matrix(-4.37114e-08 1 1 4.37114e-08 2.65033 2.65051)" fill="#F25103"/>
  <rect x="5.30066" y="7.95117" width="2.65033" height="2.65033" transform="rotate(90 5.30066 7.95117)" fill="#F25103"/>
  <rect x="2.65033" y="10.6015" width="2.65033" height="2.65033" transform="rotate(90 2.65033 10.6015)" fill="#F25103"/>
  <rect width="2.65033" height="2.65033" transform="matrix(-4.37114e-08 1 1 4.37114e-08 5.30066 5.30084)" fill="#F25103"/>
</svg>"""

CSS = """
/* ─────────────────────────────────────────────
   Reset & base
───────────────────────────────────────────── */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

body {
  background: #aaa;
  padding: 32px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

/* ─────────────────────────────────────────────
   A4 page  (595 × 842 px = A4 @ 72 dpi, exact
   match to Figma canvas)
───────────────────────────────────────────── */
.page {
  position: relative;
  width: 595px;
  height: 842px;
  background: #fff;
  overflow: hidden;
  flex-shrink: 0;
}

/* ─────────────────────────────────────────────
   Frame lines
───────────────────────────────────────────── */
.fl {
  position: absolute;
  background: #E1E1E1;
}
.fl.v { width: 1px; }
.fl.h { height: 1px; }

/* ─────────────────────────────────────────────
   Section heading  [ LABEL ]
───────────────────────────────────────────── */
.sh {
  font-family: 'Geist', sans-serif;
  font-weight: 500;
  font-size: 10px;
  letter-spacing: 0.2px;
  line-height: 12px;
  color: #f25103;
}
.sh .tx { color: #111112; }

/* Large-bracket variant used on page 2 */
.sh2 {
  font-family: 'Geist Mono', monospace;
  font-weight: 400;
  font-size: 13px;
  line-height: 1;
  color: #161616;
}
.sh2 .br { color: #f25103; }

/* ─────────────────────────────────────────────
   Chips / pills
───────────────────────────────────────────── */
.chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border: 1px solid #7d7d7d;
  border-radius: 100px;
  font-family: 'Geist Mono', monospace;
  font-size: 8px;
  font-weight: 400;
  color: #7d7d7d;
  text-transform: uppercase;
  white-space: normal;
  line-height: 1.3;
  max-width: 100%;
}

/* ─────────────────────────────────────────────
   Career timeline
───────────────────────────────────────────── */
.career-list {
  position: absolute;
  left: 44px;
  top: 399px;
  width: 271px;
}

.career-item {
  position: relative;
  padding-left: 16px;
  margin-bottom: 16px;
}

/* Square marker on the timeline */
.career-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 8px;
  height: 8px;
  background: #161616;
}

/* Vertical line connecting markers */
.career-list::before {
  content: '';
  position: absolute;
  left: 3.5px;
  top: 8px;
  width: 1px;
  height: calc(100% - 8px);
  background: #161616;
}

.career-header {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-bottom: 4px;
}

.career-company {
  font-family: 'Geist Mono', monospace;
  font-weight: 500;
  font-size: 9px;
  line-height: 12px;
  color: #161616;
  white-space: nowrap;
}

.career-dots {
  flex: 1;
  border-bottom: 1px dotted #7d7d7d;
  margin-bottom: 0;
  min-width: 8px;
}

.career-years {
  font-family: 'Geist Mono', monospace;
  font-weight: 500;
  font-size: 9px;
  line-height: 12px;
  color: #161616;
  white-space: nowrap;
}

.career-desc {
  font-family: 'Geist Mono', monospace;
  font-weight: 500;
  font-size: 9px;
  line-height: 12px;
  color: #7d7d7d;
}

/* ─────────────────────────────────────────────
   Right column – tools & skills
───────────────────────────────────────────── */
.right-section {
  position: absolute;
  left: 346px;
  width: 219px;
  overflow: hidden;
}

.chip-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 8px;
}

/* ─────────────────────────────────────────────
   Orange dot-diamond decoration  >>>>
   (matches Figma corner ornament)
───────────────────────────────────────────── */
.ornament {
  position: absolute;
  display: flex;
  gap: 4px;
  align-items: center;
}

.diamond {
  display: grid;
  grid-template-columns: repeat(3, 2.65px);
  grid-template-rows: repeat(3, 2.65px);
  gap: 0;
}
.diamond span {
  width: 2.65px;
  height: 2.65px;
}
.diamond span.dot { background: #f25103; }

/* ─────────────────────────────────────────────
   Footer bar
───────────────────────────────────────────── */
.footer-tagline {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  top: 802px;
  font-family: 'Geist Mono', monospace;
  font-weight: 400;
  font-size: 9px;
  line-height: 11.4px;
  color: #030303;
  white-space: nowrap;
}
.footer-tagline .sep { color: #ff6a34; }

.footer-left {
  position: absolute;
  left: 44px;
  top: 802px;
  font-family: 'Geist Mono', monospace;
  font-weight: 400;
  font-size: 9px;
  line-height: 11.4px;
  color: #7d7d7d;
  text-transform: uppercase;
}

.footer-right {
  position: absolute;
  right: 38px;
  top: 802px;
  font-family: 'Geist Mono', monospace;
  font-weight: 400;
  font-size: 9px;
  line-height: 11.4px;
  color: #7d7d7d;
  text-transform: uppercase;
}

/* ─────────────────────────────────────────────
   Page 2 skill sections
───────────────────────────────────────────── */
.skill-section {
  margin-bottom: 24px;
}

.skill-section .chip-wrap {
  margin-top: 8px;
}

/* Two-column grid for page 2 (TESTING | BUILD STORAGE) */
.skill-cols {
  display: flex;
  gap: 0;
}
.skill-col {
  flex: 1;
}
.skill-col + .skill-col {
  margin-left: 0;
}

/* ─────────────────────────────────────────────
   Print — force Chrome to match our 595×842 px
   canvas exactly so all absolute positions are
   correct in the PDF output.
───────────────────────────────────────────── */
@page {
  size: 595px 842px;
  margin: 0;
}
@media print {
  body { background: white; padding: 0; gap: 0; }
  .page {
    page-break-after: always;
    width: 595px;
    height: 842px;
  }
}
"""

HTML_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Developer Profiles</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
{css}
</style>
</head>
<body>
""".format(css=CSS)

HTML_FOOT = """</body>
</html>
"""


def e(text):
    """HTML-escape a string, also replacing None with empty string."""
    if not text:
        return ""
    return html.escape(str(text))


def chips_html(items):
    """Return chip span elements for a list of items."""
    return "".join(f'<span class="chip">{e(item.strip())}</span>\n      ' for item in items if item.strip())


def parse_skills_blocks(raw, platform):
    """
    Split raw skills text by 2+ blank lines into blocks.
    Map blocks to section names based on platform (iOS=8 blocks, Android/other=7 blocks).
    Returns dict with keys: lang_ui, arch, testing, build_storage, network_auth, platform_svc, distribution.
    """
    blocks = [b.strip() for b in re.split(r'\n[ \t]*\n+', raw) if b.strip()]

    def block_to_chips(block):
        return [line.strip() for line in block.splitlines() if line.strip()]

    result = {
        'lang_ui': [],
        'arch': [],
        'testing': [],
        'build_storage': [],
        'network_auth': [],
        'platform_svc': [],
        'distribution': [],
    }

    if len(blocks) >= 8:
        # iOS mapping:
        # [0]=Lang/UI, [1]=Arch, [2]=Testing, [3]+[4]=Build Storage (merged), [5]=Network/Auth, [6]=Platform Svc, [7]=Distribution
        result['lang_ui'] = block_to_chips(blocks[0])
        result['arch'] = block_to_chips(blocks[1])
        result['testing'] = block_to_chips(blocks[2])
        # merge blocks[3] and blocks[4] for Build Storage
        merged = blocks[3] + '\n' + blocks[4]
        result['build_storage'] = block_to_chips(merged)
        result['network_auth'] = block_to_chips(blocks[5])
        result['platform_svc'] = block_to_chips(blocks[6])
        result['distribution'] = block_to_chips(blocks[7])
    elif len(blocks) >= 7:
        # Android mapping:
        # [0]=Lang/UI, [1]=Arch, [2]=Testing, [3]=Build Storage, [4]=Network/Auth, [5]=Platform Svc, [6]=Distribution
        result['lang_ui'] = block_to_chips(blocks[0])
        result['arch'] = block_to_chips(blocks[1])
        result['testing'] = block_to_chips(blocks[2])
        result['build_storage'] = block_to_chips(blocks[3])
        result['network_auth'] = block_to_chips(blocks[4])
        result['platform_svc'] = block_to_chips(blocks[5])
        result['distribution'] = block_to_chips(blocks[6])
    else:
        # fallback: assign whatever blocks exist in order
        keys = ['lang_ui', 'arch', 'testing', 'build_storage', 'network_auth', 'platform_svc', 'distribution']
        for i, b in enumerate(blocks):
            if i < len(keys):
                result[keys[i]] = block_to_chips(b)

    return result


def parse_tools(raw):
    """Split by newlines then by commas → one chip per tool."""
    if not raw:
        return []
    items = []
    for line in raw.splitlines():
        for part in line.split(','):
            part = part.strip()
            if part:
                items.append(part)
    return items


STAT_FONT = '16px'   # consistent size across all four stats — fits 'Intermediate' (12 chars) in 120px


def parse_additional_skills(raw):
    """Split by comma, strip whitespace."""
    if not raw:
        return []
    return [s.strip() for s in raw.split(',') if s.strip()]


def extract_stat_level(job_title):
    if not job_title:
        return ''
    jt = job_title.lower()
    if 'senior' in jt:
        return 'Senior'
    if 'intermediate' in jt:
        return 'Intermediate'
    if 'junior' in jt:
        return 'Junior'
    return ''


def extract_stat_platform(job_title):
    if not job_title:
        return ''
    jt = job_title.lower()
    if 'ios' in jt:
        return 'iOS'
    if 'android' in jt:
        return 'Android'
    if 'full stack' in jt or 'fullstack' in jt:
        return 'Full Stack'
    return ''


def build_bio_paras(description):
    """
    Split bio on paragraph breaks (\n\n or \n) and return up to two paragraphs.
    The template has two <p> slots; extra paragraphs are dropped.
    """
    if not description:
        return ['', '']
    # Split on blank lines first, then single newlines
    paras = [p.strip() for p in re.split(r'\n\s*\n', description) if p.strip()]
    if len(paras) == 1:
        # try splitting on single newlines
        sub = [p.strip() for p in paras[0].split('\n') if p.strip()]
        if len(sub) > 1:
            paras = sub
    # Return exactly 2 slots
    p1 = paras[0] if len(paras) > 0 else ''
    p2 = paras[1] if len(paras) > 1 else ''
    return [p1, p2]


# ──────────────────────────────────────────────────────────────────────────────
# Hand-edited career descriptions for people whose originals overflow page 1.
# Key: "First Surname"  →  list of (timeline, company, description) tuples.
# ──────────────────────────────────────────────────────────────────────────────


def render_career_item(timeline, company, desc):
    """Return HTML for one career item, or empty string if no data."""
    if not company.strip() and not timeline.strip():
        return ''
    return f"""    <div class="career-item">
      <div class="career-header">
        <span class="career-company">{e(company.strip())}</span>
        <span class="career-dots"></span>
        <span class="career-years">{e(timeline.strip())}</span>
      </div>
      <p class="career-desc">{e(desc.strip())}</p>
    </div>
"""


def render_page1(person):
    name = f"{person['first']} {person['surname']}".strip()
    role = person['job_title']
    bio_paras = build_bio_paras(person['description'])

    stat_level = extract_stat_level(role)
    stat_platform = extract_stat_platform(role)
    stat_years = person['years_exp']
    stat_roles = person['stat_roles']

    tools_chips = chips_html(person['tools'])
    addskills_chips = chips_html(person['additional_skills'])

    career_items_html = ''
    timeline_data = person['timeline']
    for tl, co, desc in timeline_data:
        career_items_html += render_career_item(tl, co, desc)

    return f"""<!-- ══════════════════════════════════════════════════════════
     PAGE 1 – {e(name)}
     ══════════════════════════════════════════════════════════ -->
<div class="page">

  <!-- Frame lines -->
  <div class="fl v" style="left:20px; top:20px; height:802px;"></div>
  <div class="fl v" style="left:575px; top:20px; height:802px;"></div>
  <div class="fl h" style="left:20px; top:20px; width:555px;"></div>
  <div class="fl h" style="left:20px; top:109px; width:555px;"></div>
  <div class="fl h" style="left:20px; top:274px; width:555px;"></div>
  <div class="fl h" style="left:20px; top:354px; width:555px;"></div>
  <div class="fl v" style="left:335px; top:354px; height:440px;"></div>
  <div class="fl h" style="left:336px; top:593px; width:239px;"></div>
  <div class="fl h" style="left:336px; top:749px; width:239px;"></div>
  <div class="fl h" style="left:20px; top:793px; width:556px;"></div>
  <div class="fl h" style="left:20px; top:821px; width:556px;"></div>

  <!-- Header -->
  <p style="position:absolute; left:44px; top:36px;
            font-family:'Geist',sans-serif; font-weight:400; font-size:28px;
            line-height:35px; color:#000; letter-spacing:0; text-transform:uppercase;">{e(name)}</p>

  <p style="position:absolute; left:44px; top:75px;
            font-family:'Geist',sans-serif; font-weight:500; font-size:10px;
            line-height:12px; letter-spacing:0.2px; white-space:nowrap;">
    <span style="color:#f25103;">/// </span><span style="color:#7c7c7c; text-transform:uppercase;">{e(role)}</span>
  </p>

  <!-- Bio -->
  <div style="position:absolute; left:44px; top:126px; width:508px;
              font-family:'Geist Mono',monospace; font-weight:500; font-size:9px;
              line-height:12px; color:#7d7d7d;">
    <p>{e(bio_paras[0])}</p>
    <p style="margin-top:12px;">{e(bio_paras[1])}</p>
  </div>

  <!-- Stats bar -->
  <div style="position:absolute; left:44px; top:274px; height:80px; display:flex; gap:48px; align-items:center; text-transform:uppercase; overflow:hidden; width:513px;">
    <div style="width:76px; flex-shrink:0; overflow:hidden;">
      <p style="font-family:'Geist Mono',monospace; font-weight:400; font-size:{STAT_FONT}; color:#161616; line-height:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{e(stat_years)}</p>
      <p style="font-family:'Geist Mono',monospace; font-weight:500; font-size:9px; color:#f25103; line-height:11.4px; margin-top:4px;">YRS EXPERIENCE</p>
    </div>
    <div style="width:120px; flex-shrink:0; overflow:hidden;">
      <p style="font-family:'Geist Mono',monospace; font-weight:400; font-size:{STAT_FONT}; color:#161616; line-height:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{e(stat_level)}</p>
      <p style="font-family:'Geist Mono',monospace; font-weight:500; font-size:9px; color:#f25103; line-height:11.4px; margin-top:4px;">Level</p>
    </div>
    <div style="width:102px; flex-shrink:0; overflow:hidden;">
      <p style="font-family:'Geist Mono',monospace; font-weight:400; font-size:{STAT_FONT}; color:#161616; line-height:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{e(stat_platform)}</p>
      <p style="font-family:'Geist Mono',monospace; font-weight:500; font-size:9px; color:#f25103; line-height:11.4px; margin-top:4px;">Platform</p>
    </div>
    <div style="width:71px; flex-shrink:0; overflow:hidden;">
      <p style="font-family:'Geist Mono',monospace; font-weight:400; font-size:{STAT_FONT}; color:#161616; line-height:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{e(str(stat_roles))}</p>
      <p style="font-family:'Geist Mono',monospace; font-weight:500; font-size:9px; color:#f25103; line-height:11.4px; margin-top:4px;">Career Stages</p>
    </div>
  </div>

  <!-- LEFT COLUMN: Career Trajectory -->
  <p style="position:absolute; left:44px; top:369px;" class="sh">
    <span>[ </span><span class="tx">CAREER TRAJECTORY</span><span> ]</span>
  </p>

  <div class="career-list">
{career_items_html}  </div>

  <!-- RIGHT COLUMN: Tools -->
  <div class="right-section" style="top:369px;">
    <p class="sh"><span>[  </span><span class="tx">TOOLS</span><span>  ]</span></p>
    <div class="chip-wrap" style="margin-top:8px;">
      {tools_chips}
    </div>
  </div>

  <!-- RIGHT COLUMN: Additional Skills (only if present) -->
  {'<div class="right-section" style="top:610px;"><p class="sh"><span>[  </span><span class="tx">ADDITIONAL SKILLS</span><span>  ]</span></p><div class="chip-wrap" style="margin-top:8px;">' + addskills_chips + '</div></div>' if addskills_chips.strip() else ''}

  <!-- RIGHT COLUMN: Skills heading + arrows -->
  <div style="position:absolute; left:346px; top:764px; right:38px; display:flex; align-items:center; justify-content:space-between;">
    <p class="sh"><span>[  </span><span class="tx">SKILLS</span><span>  ]</span></p>
    {SVG_ARROWS}
  </div>

  <!-- Footer -->
  <p class="footer-left">DESIGN <span style="color:#ff6a34;">///</span> ENGINEER <span style="color:#ff6a34;">///</span> DELIVER</p>
  <p class="footer-tagline">GLUCODE</p>
  <p class="footer-right">DEVELOPER PROFILES</p>

</div>
"""


def render_page2(person):
    name = f"{person['first']} {person['surname']}".strip()
    sk = person['skills']

    lang_ui_chips = chips_html(sk['lang_ui'])
    arch_chips = chips_html(sk['arch'])
    testing_chips = chips_html(sk['testing'])
    build_chips = chips_html(sk['build_storage'])
    net_auth_chips = chips_html(sk['network_auth'])
    plat_chips = chips_html(sk['platform_svc'])
    dist_chips = chips_html(sk['distribution'])

    return f"""<!-- ══════════════════════════════════════════════════════════
     PAGE 2 – {e(name)} (Skills)
     ══════════════════════════════════════════════════════════ -->
<div class="page">

  <!-- Frame lines -->
  <div class="fl v" style="left:20px; top:20px; height:802px;"></div>
  <div class="fl v" style="left:575px; top:20px; height:802px;"></div>
  <div class="fl h" style="left:20px; top:20px; width:555px;"></div>
  <div class="fl h" style="left:20px; top:793px; width:556px;"></div>
  <div class="fl h" style="left:20px; top:821px; width:556px;"></div>

  <!-- Skill sections: flex column so spacing adapts to content height -->
  <div style="position:absolute; left:44px; top:44px; right:40px; bottom:52px;
              display:flex; flex-direction:column; gap:28px; overflow:hidden;">

    <!-- LANGUAGES AND UI -->
    <div>
      <p class="sh2"><span class="br">[ </span>LANGUAGES AND UI<span class="br"> ]</span></p>
      <div class="chip-wrap" style="margin-top:12px;">{lang_ui_chips}</div>
    </div>

    <!-- ARCHITECTURE -->
    <div>
      <p class="sh2"><span class="br">[ </span>ARCHITECTURE<span class="br"> ]</span></p>
      <div class="chip-wrap" style="margin-top:12px;">{arch_chips}</div>
    </div>

    <!-- TESTING + BUILD STORAGE (two-column) -->
    <div style="display:flex; gap:0; flex-shrink:0;">
      <div style="width:280px; flex-shrink:0;">
        <p class="sh2"><span class="br">[ </span>TESTING<span class="br"> ]</span></p>
        <div class="chip-wrap" style="margin-top:12px;">{testing_chips}</div>
      </div>
      <div style="flex:1; padding-right:40px;">
        <p class="sh2"><span class="br">[ </span>BUILD STORAGE<span class="br"> ]</span></p>
        <div class="chip-wrap" style="margin-top:12px;">{build_chips}</div>
      </div>
    </div>

    <!-- DISTRIBUTION -->
    <div>
      <p class="sh2"><span class="br">[ </span>DISTRIBUTION<span class="br"> ]</span></p>
      <div class="chip-wrap" style="margin-top:12px;">{dist_chips}</div>
    </div>

    <!-- NETWORK & AUTH -->
    <div>
      <p class="sh2"><span class="br">[ </span>NETWORK &amp; AUTH<span class="br"> ]</span></p>
      <div class="chip-wrap" style="margin-top:12px;">{net_auth_chips}</div>
    </div>

    <!-- PLATFORM SERVICES -->
    <div>
      <p class="sh2"><span class="br">[ </span>PLATFORM SERVICES<span class="br"> ]</span></p>
      <div class="chip-wrap" style="margin-top:12px;">{plat_chips}</div>
    </div>

  </div>

  <!-- Footer -->
  <p class="footer-left">DESIGN <span style="color:#ff6a34;">///</span> ENGINEER <span style="color:#ff6a34;">///</span> DELIVER</p>
  <p class="footer-tagline">GLUCODE</p>
  <p class="footer-right">DEVELOPER PROFILES</p>

</div>
"""


def should_skip(row):
    """Return True if the row should be skipped."""
    first = row[0].strip() if len(row) > 0 else ''
    if not first:
        return True
    job_title = row[2].strip() if len(row) > 2 else ''
    description = row[3].strip() if len(row) > 3 else ''
    # Check timeline data (cols 5, 8, 11, 14)
    timeline_cols = [5, 8, 11, 14]
    has_timeline = any(len(row) > c and row[c].strip() for c in timeline_cols)
    if not job_title and not description and not has_timeline:
        return True
    return False


def get_safe(row, idx, default=''):
    if idx < len(row):
        return row[idx]
    return default


def generate_profiles_from_rows(data_rows):
  """Build compiled HTML and profile count from CSV data rows (header already removed)."""
  pages_html = []
  profile_count = 0

  for row in data_rows:
    if should_skip(row):
      continue

    first = get_safe(row, 0, '').strip()
    surname = get_safe(row, 1, '').strip()
    job_title = get_safe(row, 2, '').strip()
    description = get_safe(row, 3, '').strip()
    years_exp = get_safe(row, 4, '').strip()

    # Timeline groups: (timeline, company, desc) at cols (5,6,7), (8,9,10), (11,12,13), (14,15,16)
    timeline = []
    for base in [5, 8, 11, 14]:
      tl = get_safe(row, base, '').strip()
      co = get_safe(row, base + 1, '').strip()
      desc = get_safe(row, base + 2, '').strip()
      timeline.append((tl, co, desc))

    # Count non-empty timeline entries (by timeline date field)
    stat_roles = sum(1 for tl, co, desc in timeline if tl.strip() or co.strip())

    skills_raw = get_safe(row, 19, '').strip()          # col 19 = Skills New (full standardised)
    additional_skills_raw = get_safe(row, 20, '').strip()  # col 20 = Additional Skills
    tools_raw = get_safe(row, 21, '').strip()             # col 21 = Tools New (full standardised)

    platform = extract_stat_platform(job_title)
    skills = parse_skills_blocks(skills_raw, platform)
    tools = parse_tools(tools_raw)
    additional_skills = parse_additional_skills(additional_skills_raw)

    person = {
      'first': first,
      'surname': surname,
      'job_title': job_title,
      'description': description,
      'years_exp': years_exp,
      'timeline': timeline,
      'stat_roles': stat_roles,
      'skills': skills,
      'tools': tools,
      'additional_skills': additional_skills,
    }

    pages_html.append(render_page1(person))
    pages_html.append(render_page2(person))
    profile_count += 1

  compiled_html = HTML_HEAD + '\n'.join(pages_html) + HTML_FOOT
  return compiled_html, profile_count


def generate_profiles_from_csv_text(csv_text):
  """Read CSV text and return (compiled_html, profile_count)."""
  reader = csv.reader(io.StringIO(csv_text))
  rows = list(reader)
  data_rows = rows[1:] if rows else []
  return generate_profiles_from_rows(data_rows)


def decode_csv_bytes(csv_bytes):
  """Decode uploaded CSV bytes with common encodings."""
  for encoding in ('utf-8-sig', 'cp1252', 'latin-1'):
    try:
      return csv_bytes.decode(encoding)
    except UnicodeDecodeError:
      continue
  return csv_bytes.decode('utf-8', errors='replace')


def generate_profiles_from_csv_bytes(csv_bytes):
  """Read CSV bytes and return (compiled_html, profile_count)."""
  return generate_profiles_from_csv_text(decode_csv_bytes(csv_bytes))


def generate_profiles_from_csv_file(csv_path):
  """Read CSV from disk and return (compiled_html, profile_count)."""
  with open(csv_path, 'rb') as f:
    return generate_profiles_from_csv_bytes(f.read())


def write_compiled_html(output_path, compiled_html):
  """Write compiled HTML to disk and return output file size."""
  with open(output_path, 'w', encoding='utf-8') as f:
    f.write(compiled_html)
  return os.path.getsize(output_path)


def main():
    parser = argparse.ArgumentParser(description='Generate developer profile HTML from CSV.')
    parser.add_argument('--csv', default=CSV_PATH, help='Path to input CSV file.')
    parser.add_argument('--output', default=OUTPUT_PATH, help='Path to output HTML file.')
    args = parser.parse_args()

    if not os.path.exists(args.csv):
        parser.error(
            f"Input CSV not found: {args.csv}. "
            "Provide a file with --csv, or use the Streamlit uploader in app.py."
        )

    compiled_html, profile_count = generate_profiles_from_csv_file(args.csv)
    file_size = write_compiled_html(args.output, compiled_html)

    print(f"Done. Generated {profile_count} profiles ({profile_count * 2} pages).")
    print(f"Output: {args.output}")
    print(f"File size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")


if __name__ == '__main__':
    main()
