"""Generate README SVGs in the style of mrayandika15.github.io/rayandika.
usage: python3 -I gen.py <assets_dir> <out_dir>
"""
import base64, sys, os, math
from fontTools.ttLib import TTFont

A, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

C = dict(paper="#f8f7f2", ink="#191610", muted="#56524b", rule="#e5e4dd", line="#d8d8d3",
         yellow="#f7c73c", blue="#1c4ed0", pink="#f779ba", green="#008554", mint="#a1e2c2",
         butter="#f8e09b", lavender="#c2c7f0", blush="#ffc4da", orange="#e8684f", desk="#8d8e87",
         note_y="#f8e6a0", note_g="#c9e8d5", note_l="#dcd8f1")

def b64(p): return base64.b64encode(open(os.path.join(A, p), "rb").read()).decode()
FONT_FILES = {"J": "J.woff2", "K": "K.woff2", "M5": "M5.woff2", "M8": "M8.woff2"}
FONT_DATA = {k: b64(v) for k, v in FONT_FILES.items()}
PHOTO = b64("photo.jpg")

# text measuring from real advance widths
_m = {}
def width(text, font, size, ls=0):
    if font == "mono": return len(text) * (size * 0.6 + ls)
    if font not in _m:
        t = TTFont(os.path.join(A, FONT_FILES[font]))
        _m[font] = (t.getBestCmap(), t["hmtx"].metrics, t["head"].unitsPerEm)
    cmap, hm, upm = _m[font]
    return sum(hm[cmap[ord(c)]][0] if ord(c) in cmap else upm * 0.5 for c in text) * size / upm + len(text) * ls

FAM = {"J": "J", "K": "K", "M5": "M5", "M8": "M8", "mono": "'Courier New',Courier,monospace"}
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def T(x, y, s, font, size, fill=C["ink"], anchor="start", extra="", ls=0):
    w = "font-weight:700;" if font == "mono" else ""
    l = f"letter-spacing:{ls}px;" if ls else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" fill="{fill}" '
            f'style="font-family:{FAM[font]};font-size:{size}px;{w}{l}" {extra}>{esc(s)}</text>')

def svg(w, h, body, fonts, css="", title=""):
    ff = "".join(f"@font-face{{font-family:{k};src:url(data:font/woff2;base64,{FONT_DATA[k]}) format('woff2');}}" for k in fonts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
            f'<title>{esc(title)}</title><style>{ff}{css}'
            "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>"
            f"{body}</svg>")

def save(name, s):
    open(os.path.join(OUT, name), "w").write(s)
    print(name, len(s) // 1024, "KB")

# ---------- reusable shapes ----------
def paper(x, y, w, h, lines_from=None, r=0, shadow=True):
    out = []
    if shadow: out.append(f'<rect x="{x+3}" y="{y+4}" width="{w}" height="{h}" rx="{r}" fill="#000" opacity=".07"/>')
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{C["paper"]}" stroke="{C["line"]}"/>')
    y0 = lines_from if lines_from is not None else y + 30
    out += [f'<line x1="{x+1}" x2="{x+w-1}" y1="{yy}" y2="{yy}" stroke="{C["rule"]}"/>' for yy in range(int(y0), int(y + h), 28)]
    return "".join(out)

def desk(w, h):
    g = "".join(f'<line x1="{i}" x2="{i}" y1="0" y2="{h}" stroke="#fff" opacity=".28"/>' for i in range(0, w + 1, 56))
    g += "".join(f'<line x1="0" x2="{w}" y1="{j}" y2="{j}" stroke="#fff" opacity=".28"/>' for j in range(0, h + 1, 56))
    return f'<rect width="{w}" height="{h}" fill="{C["desk"]}"/>' + g

def sticker(cx, cy, text, font, size, bg, fg=C["ink"], rot=0, padx=12, h=None, ls=0, shadow=True):
    w = width(text, font, size, ls) + padx * 2
    h = h or size * 2.1
    s = f'<g transform="translate({cx},{cy}) rotate({rot})">'
    if shadow: s += f'<rect x="{-w/2+2}" y="{-h/2+3}" width="{w}" height="{h}" rx="3" fill="#000" opacity=".1"/>'
    s += f'<rect x="{-w/2}" y="{-h/2}" width="{w}" height="{h}" rx="3" fill="{bg}"/>'
    s += T(0, size * 0.36, text, font, size, fg, "middle", ls=ls) + "</g>"
    return s

def star4(cx, cy, r, fill):
    k = r * 0.28
    return (f'<path d="M{cx},{cy-r} Q{cx+k},{cy-k} {cx+r},{cy} Q{cx+k},{cy+k} {cx},{cy+r} '
            f'Q{cx-k},{cy+k} {cx-r},{cy} Q{cx-k},{cy-k} {cx},{cy-r}Z" fill="{fill}"/>')

def asterisk(cx, cy, r, stroke, sw=2.4):
    return "".join(f'<line x1="{cx+r*math.cos(a):.1f}" y1="{cy+r*math.sin(a):.1f}" x2="{cx-r*math.cos(a):.1f}" '
                   f'y2="{cy-r*math.sin(a):.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"/>'
                   for a in (0, math.pi/4, math.pi/2, 3*math.pi/4))

def arrow_ne(x, y, s, stroke, sw=2):
    return (f'<path d="M{x},{y+s} L{x+s},{y} M{x+s*0.35},{y} L{x+s},{y} L{x+s},{y+s*0.65}" fill="none" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="square"/>')

def ring(cx, cy, r, color):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{r*0.22:.1f}"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*0.52:.1f}" fill="none" stroke="{color}" stroke-width="{r*0.22:.1f}"/>')

def flower(cx, cy, r, color):
    p = "".join(f'<circle cx="{cx+r*0.55*math.cos(a):.1f}" cy="{cy+r*0.55*math.sin(a):.1f}" r="{r*0.42:.1f}" fill="{color}"/>'
                for a in [i * 2 * math.pi / 5 - math.pi / 2 for i in range(5)])
    return p + f'<circle cx="{cx}" cy="{cy}" r="{r*0.22:.1f}" fill="{C["paper"]}"/>'

def tape(cx, cy, w, rot, color=C["lavender"], op=.75):
    return f'<rect x="{cx-w/2}" y="{cy-9}" width="{w}" height="18" fill="{color}" opacity="{op}" transform="rotate({rot} {cx} {cy})"/>'

def photo(x, y, w, h, clip_id, circle=False):
    clip = (f'<clipPath id="{clip_id}"><circle cx="{x+w/2}" cy="{y+h/2}" r="{w/2}"/></clipPath>' if circle
            else f'<clipPath id="{clip_id}"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>')
    return (f'<defs>{clip}</defs><image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" '
            f'clip-path="url(#{clip_id})" href="data:image/jpeg;base64,{PHOTO}" xlink:href="data:image/jpeg;base64,{PHOTO}"/>')

def boxed_title(cx, cy, text, size=26):
    w = width(text, "M5", size) + 28
    h = size * 1.55
    return (f'<rect x="{cx-w/2+3}" y="{cy-h/2+3}" width="{w}" height="{h}" fill="{C["ink"]}"/>'
            f'<rect x="{cx-w/2}" y="{cy-h/2}" width="{w}" height="{h}" fill="{C["paper"]}" stroke="{C["ink"]}" stroke-width="1.5"/>'
            + T(cx, cy + size * 0.35, text, "M5", size, C["ink"], "middle"))

W = 840

# ---------- 1. hero ----------
def hero():
    H = 640
    b = [desk(W, H), paper(28, 28, W - 56, H - 28, lines_from=104, shadow=False)]
    # top bar
    b.append(f'<line x1="28" x2="{W-28}" y1="76" y2="76" stroke="{C["line"]}"/>')
    b.append(f'<circle cx="56" cy="52" r="10" fill="none" stroke="{C["pink"]}" stroke-width="2"/>'
             f'<circle cx="52.5" cy="49.5" r="1.4" fill="{C["pink"]}"/><circle cx="59.5" cy="49.5" r="1.4" fill="{C["pink"]}"/>'
             f'<path d="M51,55 Q56,60 61,55" fill="none" stroke="{C["pink"]}" stroke-width="1.8" stroke-linecap="round"/>')
    x = 78
    for i, item in enumerate(["HOME", "ABOUT", "SELECTED WORK", "PLAYGROUND"]):
        w = width(item, "mono", 9) + 34
        if i == 0: b.append(f'<rect x="{x}" y="33" width="{w}" height="38" fill="{C["yellow"]}"/>')
        b.append(star4(x + 12, 52, 3.5, C["ink"]) + T(x + 21, 55, item, "mono", 9))
        x += w + 4
    for i, col in enumerate([C["yellow"], C["pink"], C["green"]]):
        b.append(f'<circle cx="{W-226+i*30}" cy="52" r="12" fill="{col}"/>')
    b.append(T(W - 226 + 60, 57, "m", "M8", 15, "#fff", "middle"))
    b.append(asterisk(W - 196, 52, 5.5, C["ink"], 1.5))
    b.append(f'<path d="M{W-230},{57} q4,-14 8,0" fill="none" stroke="{C["ink"]}" stroke-width="1.6"/>')
    b.append(f'<rect x="{W-128}" y="38" width="88" height="28" fill="none" stroke="{C["ink"]}" stroke-width="1.3"/>' + T(W - 84, 56, "CONTACT", "mono", 9, anchor="middle"))
    # name block
    cx = W / 2
    b.append(f'<g transform="rotate(-3 {cx} 128)">' + T(cx, 134, "my name is", "K", 21, C["ink"], "middle") + "</g>")
    b.append(f'<path d="M{cx-6},148 l5,-4 l0,7 l6,-5" fill="none" stroke="{C["ink"]}" stroke-width="1.8"/>')
    nw = width("MRAYANDIKA", "J", 128)
    b.append(f'<g transform="rotate(-1.2 {cx} 220)"><rect x="{cx-nw/2-18}" y="166" width="{nw+36}" height="118" fill="none" stroke="{C["orange"]}" stroke-width="1.3"/></g>')
    b.append(T(cx, 266, "MRAYANDIKA", "J", 128, C["ink"], "middle", ls=1))
    b.append(sticker(cx - nw / 2 + 4, 156, "MAKE THINGS", "mono", 8.5, C["mint"], rot=-4, h=20))
    b.append(sticker(cx + nw / 2 + 6, 156, "SWEAT THE DETAILS", "mono", 8.5, C["butter"], rot=4, h=20))
    b.append(sticker(cx - nw / 2 + 10, 300, "AI Agent Engineer", "K", 18, C["yellow"], rot=-4, h=38))
    b.append(sticker(cx + nw / 2 - 4, 300, "Bandung, ID", "K", 18, C["mint"], rot=5, h=38))
    b.append(f'<path d="M{cx-nw/2+70},287 l18,-16 M{cx-nw/2+80},271 h8 v8" fill="none" stroke="{C["ink"]}" stroke-width="1.8"/>')
    b.append(f'<path d="M{cx+nw/2-58},287 l-18,-16 M{cx+nw/2-68},271 h-8 v8" fill="none" stroke="{C["ink"]}" stroke-width="1.8"/>')
    tag = "MULTI-AGENT SYSTEMS & WORKFLOW AUTOMATION"
    tw = width(tag, "mono", 9.5, 0.6)
    b.append(f'<circle class="pulse" cx="{cx-tw/2-12}" cy="345" r="4" fill="{C["blue"]}"/>' + T(cx + 8, 349, tag, "mono", 9.5, anchor="middle", ls=0.6))
    # headline
    l1, l2 = "I build AI teams that", "make work flow."
    w1, w2 = width(l1, "M8", 44), width(l2, "M8", 44)
    b.append(T(cx - 18, 418, l1, "M8", 44, anchor="middle", ls=-1.2) + ring(cx - 18 + w1 / 2 + 18, 403, 17, C["green"]))
    b.append(T(cx - 18, 472, l2, "M8", 44, anchor="middle", ls=-1.2) + flower(cx - 18 + w2 / 2 + 22, 458, 17, C["pink"]))
    # avatars
    b.append(f'<g class="float"><circle cx="126" cy="410" r="35" fill="{C["orange"]}"/><circle cx="126" cy="410" r="31" fill="{C["mint"]}"/>' + photo(97, 381, 58, 58, "av", circle=True) + "</g>")
    b.append(f'<g class="float2"><circle cx="{W-126}" cy="430" r="31" fill="{C["orange"]}"/><circle cx="{W-126}" cy="430" r="27" fill="{C["lavender"]}"/>' + T(W - 126, 437, "</>", "M8", 19, anchor="middle") + "</g>")
    # sub + cta
    b.append(T(cx, 522, "4+ years in software engineering. Now building intelligent agents,", "M5", 16, C["muted"], "middle"))
    b.append(T(cx, 547, "connected tools, and workflows that lighten your workload.", "M5", 16, C["muted"], "middle"))
    cta = "LET'S BUILD YOUR WORKFLOW"
    cw = width(cta, "mono", 10.5, 1) + 74
    b.append(f'<rect x="{cx-cw/2}" y="574" width="{cw}" height="46" fill="{C["ink"]}"/><rect x="{cx-cw/2+10}" y="584" width="26" height="26" fill="{C["blue"]}"/>'
             + arrow_ne(cx - cw / 2 + 16, 590, 13, "#fff", 1.8) + T(cx - cw / 2 + 50, 601, cta, "mono", 10.5, "#fff", ls=1))
    css = (".float{animation:f 5s ease-in-out infinite}.float2{animation:f 6s ease-in-out -2s infinite}"
           "@keyframes f{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}"
           ".pulse{animation:p 2.4s ease-in-out infinite}@keyframes p{0%,100%{opacity:1}50%{opacity:.25}}")
    save("hero.svg", svg(W, H, "".join(b), ["J", "K", "M5", "M8"], css,
         "mrayandika. AI Agent Engineer, Bandung. I build AI teams that make work flow."))

# ---------- 2. about ----------
def about():
    H = 520
    b = [paper(8, 8, W - 20, H - 20)]
    b.append(T(44, 62, "about me!", "K", 19))
    b.append(boxed_title(260, 112, "what's up", 26))
    lines = ["I'm an AI Agent Engineer with 4+ years", "in software engineering. I build agent",
             "teams that collaborate, connect with your", "business tools, and take repetitive work",
             "off your plate. Thoughtful interfaces and", "reliable software are still at the heart",
             "of everything I build."]
    for i, l in enumerate(lines):
        b.append(T(260, 178 + i * 33, l, "K", 21, anchor="middle"))
    b.append(star4(260 + width(lines[1], "K", 21) / 2 + 16, 205, 7, "#c9a227"))
    # chips
    chips = [("Multi-Agent Systems", C["yellow"], C["ink"], -1.5), ("Agent Tooling", C["green"], "#fff", 1.5),
             ("Workflow Automation", C["pink"], C["ink"], 1), ("Software Engineering", C["blue"], "#fff", -1)]
    pos = [(150, 430), (360, 428), (150, 474), (360, 472)]
    for (t, bg, fg, r), (x, y) in zip(chips, pos):
        b.append(sticker(x, y, t, "M8", 12.5, bg, fg, rot=r, h=32, shadow=False))
    b.append(f'<rect x="246" y="414" width="26" height="30" fill="{C["yellow"]}" transform="rotate(2 259 429)"/>' + star4(259, 429, 7, C["ink"]))
    b.append(f'<rect x="246" y="458" width="26" height="30" fill="{C["butter"]}"/>' + asterisk(259, 473, 6.5, C["ink"], 1.6))
    # polaroid
    px, py, pw, ph = 560, 70, 230, 300
    b.append(f'<g transform="rotate(4 {px+pw/2} {py+ph/2})"><rect x="{px+4}" y="{py+6}" width="{pw}" height="{ph+56}" fill="#000" opacity=".12"/>'
             f'<rect x="{px}" y="{py}" width="{pw}" height="{ph+56}" fill="#fff" stroke="{C["line"]}"/>'
             + photo(px + 14, py + 14, pw - 28, ph - 14, "pol")
             + T(px + pw / 2, py + ph + 34, "yep, that's me :)", "K", 17, anchor="middle") + "</g>")
    b.append(tape(px + 30, py - 2, 70, -32) + tape(px + pw - 10, py + 2, 70, 28, C["butter"]))
    b.append(T(675, 470, "A LITTLE MORE ABOUT ME", "mono", 9.5, anchor="middle", ls=0.8))
    b.append(f'<line x1="600" x2="752" y1="480" y2="480" stroke="{C["ink"]}" stroke-width="1.3"/>' + arrow_ne(762, 460, 8, C["ink"], 1.4))
    save("about.svg", svg(W, H, "".join(b), ["K", "M5", "M8"], "",
         "About me: AI Agent Engineer with 4+ years in software engineering. Multi-agent systems, agent tooling, workflow automation, software engineering."))

# ---------- 3. how I can help ----------
def build():
    H = 500
    b = [paper(8, 8, W - 20, H - 20)]
    b.append(T(44, 62, "how I can help", "K", 19))
    b.append(T(44, 112, "From a business process", "K", 32) + T(44, 152, "to a working agent system.", "K", 32))
    notes = [("01", "AI agent teams", ["Specialized agents that", "coordinate, delegate tasks,", "and work toward a shared", "business outcome."], "MULTI-AGENT ORCHESTRATION", C["note_y"], -2),
             ("02", "Workflows that", ["Agents connected to your", "tools and data, with", "evaluation and human", "checkpoints where needed."], "TOOLS & AUTOMATION", C["note_g"], 1.5),
             ("03", "Software that", ["Full-stack apps and", "integrations that turn an", "agent workflow into a", "product people use."], "FULL-STACK DEVELOPMENT", C["note_l"], -1)]
    sub = {"02": "do the work", "03": "holds it together"}
    for i, (n, t, body, tag, col, rot) in enumerate(notes):
        x, y, w, h = 36 + i * 262, 194, 246, 270
        cx, cy = x + w / 2, y + h / 2
        g = f'<g transform="rotate({rot} {cx} {cy})"><rect x="{x+3}" y="{y+5}" width="{w}" height="{h}" fill="#000" opacity=".1"/><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}"/>'
        g += T(x + 20, y + 42, n, "K", 20) + T(x + 20, y + 80, t, "K", 25)
        off = 0
        if n in sub: g += T(x + 20, y + 110, sub[n], "K", 25); off = 30
        for j, l in enumerate(body): g += T(x + 20, y + 112 + off + j * 21, l, "M5", 13.5, C["ink"])
        g += T(x + 20, y + h - 22, tag, "mono", 8.5, ls=0.6) + "</g>"
        b.append(g + tape(cx, y - 2, 64, rot * 2, "#fff", .7))
    save("build.svg", svg(W, H, "".join(b), ["K", "M5"], "",
         "How I can help: AI agent teams, workflows that do the work, software that holds it together."))

# ---------- 4. section labels ----------
def label(name, small, big, alt):
    H = 120
    b = [paper(8, 8, W - 20, H - 16, lines_from=36)]
    b.append(T(44, 50, small, "K", 19) + T(44, 96, big, "M8", 30, ls=-0.8))
    b.append(asterisk(W - 60, 64, 12, C["pink"], 3))
    save(name, svg(W, H, "".join(b), ["K", "M8"], "", alt))

# ---------- 5. project cards ----------
def project(name, num, tabcol, tabfg, cat, title, desc, stack, art, alt):
    H = 300
    b = []
    # tab
    tw = 150
    b.append(f'<rect x="8" y="8" width="{tw}" height="34" fill="{tabcol}"/>' + star4(26, 25, 4, tabfg) + T(38, 29, f"PROJECT {num}", "mono", 9, tabfg, ls=0.8))
    b.append(f'<rect x="8" y="42" width="{W-20}" height="{H-52}" fill="{C["ink"]}"/>')
    b.append(f'<circle cx="38" cy="78" r="3.5" fill="{tabcol if tabcol != C["ink"] else C["yellow"]}"/>' + T(50, 82, cat, "mono", 9, "#fff", ls=0.8))
    b.append(T(30, 128, title, "M8", 32, "#fff", ls=-0.8))
    for j, l in enumerate(desc): b.append(T(30, 164 + j * 22, l, "M5", 14.5, "#d9d6cc"))
    b.append(T(30, 252, stack, "mono", 8.5, "#a7a39a", ls=0.6))
    b.append(T(30, 278, "EXPLORE PROJECT", "mono", 9.5, "#fff", ls=1) + f'<line x1="30" x2="150" y1="285" y2="285" stroke="#fff"/>' + arrow_ne(158, 268, 9, "#fff", 1.5))
    b.append(art)
    save(name, svg(W, H, "".join(b), ["K", "M5", "M8"], "", alt))

def art_harness():
    x, y, w, h = 440, 66, 372, 210
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{C["paper"]}"/>'
    s += "".join(f'<circle cx="{x+16+i*12}" cy="{y+14}" r="3.5" fill="{c}"/>' for i, c in enumerate([C["pink"], C["yellow"], C["green"]]))
    s += T(x + 56, y + 18, "harness / a place for your agents", "mono", 8.5, C["muted"])
    s += f'<line x1="{x}" x2="{x+w}" y1="{y+28}" y2="{y+28}" stroke="{C["line"]}"/>'
    # coordinator node + three children
    s += f'<rect x="{x+136}" y="{y+42}" width="100" height="32" rx="4" fill="{C["ink"]}"/>' + T(x + 186, y + 62, "Coordinator", "M8", 11, "#fff", "middle")
    kids = [("Research", "find the context", C["mint"]), ("Build", "make it happen", C["butter"]), ("Review", "keep it useful", C["blush"])]
    for i, (t, sub, col) in enumerate(kids):
        kx = x + 18 + i * 118
        s += f'<path d="M{x+186},{y+74} C{x+186},{y+98} {kx+50},{y+92} {kx+50},{y+114}" fill="none" stroke="{C["ink"]}" stroke-width="1.2" stroke-dasharray="3 3"/>'
        s += f'<rect x="{kx}" y="{y+114}" width="100" height="44" rx="4" fill="{col}" stroke="{C["ink"]}" stroke-width="1"/>'
        s += T(kx + 10, y + 132, t, "M8", 11) + T(kx + 10, y + 148, sub, "M5", 9.5, C["muted"])
        s += f'<circle cx="{kx+88}" cy="{y+128}" r="3" fill="{C["green"]}"/>'
    s += f'<rect x="{x+18}" y="{y+172}" width="{w-36}" height="26" rx="13" fill="#fff" stroke="{C["line"]}"/>' + T(x + 32, y + 189, "What would you like to build?", "M5", 10.5, C["muted"])
    s += f'<circle cx="{x+w-32}" cy="{y+185}" r="9" fill="{C["blue"]}"/><path d="M{x+w-32},{y+190} v-9 m-4,4 l4,-4 l4,4" fill="none" stroke="#fff" stroke-width="1.5"/>'
    return s

def art_ipms():
    x, y = 470, 62
    s = f'<rect x="{x}" y="{y}" width="320" height="218" rx="6" fill="{C["blue"]}"/>'
    s += T(x + 22, y + 44, "INTI PAY", "M8", 22, "#fff") + T(x + 22, y + 66, "online payment point", "M5", 11, "#dbe3ff")
    s += f'<rect x="{x+22}" y="{y+86}" width="130" height="30" rx="15" fill="{C["yellow"]}"/>' + T(x + 87, y + 105, "PAY BILLS", "mono", 9, anchor="middle", ls=0.8)
    s += T(x + 22, y + 146, "corporate site · CMS", "M5", 11, "#dbe3ff") + T(x + 22, y + 164, "real-time transactions", "M5", 11, "#dbe3ff")
    px, py = x + 196, y + 18
    s += f'<rect x="{px}" y="{py}" width="104" height="196" rx="14" fill="{C["ink"]}"/><rect x="{px+6}" y="{py+14}" width="92" height="168" rx="6" fill="{C["paper"]}"/>'
    s += T(px + 14, py + 34, "Balance", "M5", 9, C["muted"]) + T(px + 14, py + 52, "Rp 1.250.000", "M8", 11)
    for i, (t, c) in enumerate([("Electricity", C["butter"]), ("Water", C["mint"]), ("Phone", C["blush"]), ("Internet", C["lavender"])]):
        s += f'<rect x="{px+14}" y="{py+66+i*26}" width="76" height="20" rx="4" fill="{c}"/>' + T(px + 22, py + 80 + i * 26, t, "M5", 9)
    return s

def art_soccer():
    x, y = 470, 62
    s = f'<rect x="{x}" y="{y}" width="320" height="218" rx="6" fill="{C["paper"]}"/>'
    s += T(x + 20, y + 32, "Book a field", "M8", 17) + T(x + 20, y + 50, "Mini soccer · Jakarta", "M5", 10.5, C["muted"])
    days = ["MON", "TUE", "WED", "THU", "FRI"]
    for i, d in enumerate(days): s += T(x + 86 + i * 46, y + 78, d, "mono", 8, C["muted"], "middle")
    slots = ["16:00", "18:00", "20:00"]
    taken = {(0, 1), (1, 0), (2, 2), (3, 1), (4, 0), (1, 2)}
    for r, t in enumerate(slots):
        s += T(x + 20, y + 104 + r * 34, t, "mono", 8.5, C["muted"])
        for i in range(5):
            col = C["line"] if (i, r) in taken else C["mint"]
            sel = (i, r) == (2, 1)
            s += f'<rect x="{x+68+i*46}" y="{y+88+r*34}" width="38" height="24" rx="4" fill="{C["green"] if sel else col}"/>'
            if sel: s += f'<path d="M{x+80+i*46},{y+100+r*34} l5,5 l9,-10" fill="none" stroke="#fff" stroke-width="2"/>'
    s += f'<rect x="{x+20}" y="{y+188}" width="280" height="20" rx="10" fill="{C["ink"]}"/>' + T(x + 160, y + 202, "CONFIRM BOOKING  WED 18:00", "mono", 8, "#fff", "middle", ls=0.6)
    return s

# ---------- 6. toolbox ----------
def toolbox():
    H = 300
    b = [paper(8, 8, W - 20, H - 20)]
    b.append(T(44, 62, "a few things in my toolbox", "K", 19))
    rows = [["OpenAI Agents SDK", "Claude", "MCP", "RAG", "Multi-agent orchestration", "Evaluation harnesses"],
            ["TypeScript", "Python", "Java", "React", "Next.js", "Vue", "Node.js", "Express"],
            ["PostgreSQL", "MongoDB", "Docker", "Tailwind CSS", "Git", "Linux", "Neovim", "MapLibre"]]
    cols = [[C["yellow"], C["mint"], C["pink"], C["lavender"], C["butter"], C["blush"]],
            [C["paper"]] * 8, [C["paper"]] * 8]
    y = 110
    for ri, row in enumerate(rows):
        x = 44
        for i, t in enumerate(row):
            w = width(t, "mono", 10.5) + 26
            rot = [-2, 1.5, -1, 2, -1.5, 1][i % 6]
            bg = cols[ri][i] if ri == 0 else C["paper"]
            stroke = f' stroke="{C["ink"]}" stroke-width="1.2"' if ri else ""
            b.append(f'<g transform="rotate({rot} {x+w/2} {y})"><rect x="{x}" y="{y-16}" width="{w}" height="32" rx="3" fill="{bg}"{stroke}/>'
                     + T(x + w / 2, y + 4, t, "mono", 10.5, anchor="middle") + "</g>")
            x += w + 12
        y += 56
    b.append(T(44, 280, "AI first, then the engineering that makes it hold up.", "K", 16, C["muted"]))
    save("toolbox.svg", svg(W, H, "".join(b), ["K"], "",
         "Toolbox: OpenAI Agents SDK, Claude, MCP, RAG, multi-agent orchestration, evaluation harnesses, TypeScript, Python, Java, React, Next.js, Vue, Node.js, Express, PostgreSQL, MongoDB, Docker, Tailwind CSS, Git, Linux, Neovim, MapLibre."))

# ---------- 7. footer + buttons ----------
def talk():
    H = 230
    b = [paper(8, 8, W - 20, H - 16)]
    b.append(boxed_title(W / 2, 70, "LET'S TALK", 30))
    b.append(T(W / 2, 142, "Have a workflow to automate or an agent team to build?", "M5", 18, anchor="middle"))
    b.append(T(W / 2, 170, "Let's connect the tools, the people, and the software.", "M5", 18, C["muted"], "middle"))
    b.append(T(W / 2, 206, "small pieces, big possibilities", "K", 17, C["muted"], "middle") + asterisk(W / 2 + 128, 200, 7, C["pink"], 2))
    save("talk.svg", svg(W, H, "".join(b), ["K", "M5"], "", "Let's talk. Have a workflow to automate or an agent team to build?"))

def button(name, text, sq, alt):
    w = width(text, "mono", 11, 1) + 70
    H = 56
    b = (f'<rect x="4" y="6" width="{w}" height="46" fill="{C["ink"]}"/><rect x="14" y="16" width="26" height="26" fill="{sq}"/>'
         + arrow_ne(20, 22, 13, "#fff" if sq != C["yellow"] else C["ink"], 1.8) + T(54, 33, text, "mono", 11, "#fff", ls=1))
    save(name, svg(int(w + 8), H, b, [], "", alt))

hero(); about(); build(); toolbox(); talk()
label("label-work.svg", "some things I've made", "Selected projects", "Selected projects")
label("label-stats.svg", "the numbers, roughly", "GitHub activity", "GitHub activity")
project("project-harness.svg", "01", C["blue"], "#fff", "AGENT TOOLING", "Harness Agent Canvas",
        ["Design an agent's steps on a node canvas,", "trigger it from chat, and watch tool", "output stream back. A visual workspace", "for agent workflows."],
        "NEXT.JS / TYPESCRIPT / REACT FLOW / ZUSTAND", art_harness(),
        "Project 01, Harness Agent Canvas: a visual workspace for designing AI agent workflows.")
project("project-ipms.svg", "02", C["ink"], "#fff", "PAYMENTS & CMS", "IPMS + INTI PAY",
        ["Corporate site, CMS, and an online", "payment point for a Bandung", "manufacturing company. Built the full", "stack, front to database."],
        "REACT / EXPRESS / POSTGRESQL / CMS", art_ipms(),
        "Project 02, IPMS and INTI PAY: corporate website and online payment platform.")
project("project-soccer.svg", "03", C["yellow"], C["ink"], "BOOKING PLATFORM", "Soccer Chief",
        ["Online field booking for a Jakarta", "mini soccer venue: live availability,", "facility info, and reservations,", "led end to end."],
        "NEXT.JS / REACT / EXPRESS / MONGODB", art_soccer(),
        "Project 03, Soccer Chief: online booking platform for a mini soccer venue.")
button("btn-upwork.svg", "HIRE ME ON UPWORK", C["green"], "Hire me on Upwork")
button("btn-portfolio.svg", "SEE MY PORTFOLIO", C["blue"], "See my portfolio")
button("btn-github.svg", "MORE ON GITHUB", C["yellow"], "More on GitHub")
