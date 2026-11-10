# -*- coding: utf-8 -*-
"""
Generador estático del sitio LUIS MORENO FILM.
Uso:  python3 tools/build.py            (regenera todo el HTML)
Editar contenido: tools/site_data.py — NUNCA el HTML generado.
Compatible GitHub Pages (/portfolio/) y dominio propio en raíz.
"""
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from site_data import SITE, PROJECTS, FEATURED, CATEGORIES, CREDITS, T, SEO  # noqa: E402

BUILD_DATE = '2026-11-09'
S = SITE
BASE = S['base']

esc = html.escape


def thumb(p, size='-d_640x360'):
    return f"https://i.vimeocdn.com/video/{p['thumb']}{size}"


# Fallback si el sufijo de tamaño fallara: cae al patrón base '-d' (verificado).
THUMB_FALLBACK = "this.onerror=null;this.src=this.src.replace(/-d_.+$/,'-d')"


def yt_thumb(yt, res='maxres'):
    return f"https://i.ytimg.com/vi/{yt}/{res}default.jpg"


def absu(path):
    return BASE + '/' + path if path != '' else BASE + '/'


def depth_of(rel):
    return len([s for s in rel.split('/') if s and s != 'index.html'])


def prefix_for(rel):
    d = depth_of(rel)
    return '' if d == 0 else '../' * d


def page_href(lang, key):
    """Ruta raíz-relativa de una sección canónica."""
    m = {
        'home': {'es': '', 'en': 'en/'},
        'projects': {'es': 'proyectos/', 'en': 'en/projects/'},
        'other': {'es': 'otros-trabajos/', 'en': 'en/other-work/'},
        'services': {'es': 'servicios/', 'en': 'en/services/'},
        'about': {'es': 'sobre-mi/', 'en': 'en/about/'},
        'contact': {'es': 'contacto/', 'en': 'en/contact/'},
    }
    return m[key][lang]


def detail_dir(lang, slug):
    return f"proyecto/{slug}/" if lang == 'es' else f"en/project/{slug}/"


def alternates_for(kind, slug=None):
    es = page_href('es', kind) if kind != 'detail' else detail_dir('es', slug)
    en = page_href('en', kind) if kind != 'detail' else detail_dir('en', slug)
    return {'es': absu(es), 'en': absu(en)}


# ---------------------------------------------------------------- LAYOUT
FONTS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Inter:wght@400;500;600&display=swap">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Inter:wght@400;500;600&display=swap">"""

FAVICON = ("<link rel=\"icon\" type=\"image/svg+xml\" href=\"data:image/svg+xml,"
           "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E"
           "%3Crect width='100' height='100' rx='14' fill='%23111111'/%3E"
           "%3Ctext x='50' y='67' text-anchor='middle' font-family='Georgia,serif' "
           "font-size='46' fill='%23F5F3EF'%3ELM%3C/text%3E%3C/svg%3E\">")


def head(lang, rel, title, desc, og_type='website', og_image=None, ld=None, preload_image=None):
    alts = alternates_for(rel[1]) if rel[1] != 'detail' else alternates_for('detail', rel[2])
    canonical = alts[lang]
    og_img = og_image or absu(S['og_image'])
    ld_json = ''
    if ld:
        if isinstance(ld, dict):
            ld = [ld]
        graph = ld if len(ld) > 1 else ld
        if len(ld) > 1:
            ld_json = ('<script type="application/ld+json">' +
                       json.dumps({"@context": "https://schema.org", "@graph": graph},
                                  ensure_ascii=False, separators=(',', ':')) +
                       '</script>')
        else:
            ld_json = ('<script type="application/ld+json">' +
                       json.dumps(ld[0], ensure_ascii=False, separators=(',', ':')) +
                       '</script>')
    og_locale = 'es_ES' if lang == 'es' else 'en_US'
    hreflang = (f'<link rel="alternate" hreflang="es" href="{alts["es"]}">\n'
                f'<link rel="alternate" hreflang="en" href="{alts["en"]}">\n'
                f'<link rel="alternate" hreflang="x-default" href="{alts["es"]}">')
    preload = f'<link rel="preload" as="image" href="{preload_image}">' if preload_image else ''
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index, follow">
<meta name="theme-color" content="#111111">
<meta name="author" content="Luis Moreno Film">
<link rel="canonical" href="{canonical}">
{hreflang}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Luis Moreno Film">
<meta property="og:locale" content="{og_locale}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{esc(og_img)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(og_img)}">
{FAVICON}
{preload}
{FONTS}
<link rel="stylesheet" href="{{P}}assets/css/style.css">
{ld_json}"""


def header(lang, prefix, current):
    t = T[lang]
    links = []
    for label, path in t['nav']:
        href = prefix + (path if path else './')
        cur = ' aria-current="page"' if current == label.lower() else ''
        links.append(f'<a href="{href}"{cur}>{esc(label)}</a>')
    es_cur = ' aria-current="true"' if lang == 'es' else ''
    en_cur = ' aria-current="true"' if lang == 'en' else ''
    lang_html = (f'<span class="lang-switch" role="navigation" aria-label="Language">'
                 f'<a href="{prefix}./"{es_cur}>ES</a>'
                 f'<span class="sep" aria-hidden="true">/</span>'
                 f'<a href="{prefix}en/./"{en_cur}>EN</a></span>')
    contact_href = 'contacto/' if lang == 'es' else 'en/contact/'
    mobile_links = []
    for i, (label, path) in enumerate(t['nav']):
        href = prefix + (path if path else './')
        mobile_links.append(f'<a class="m-link" href="{href}"><span>{esc(label)}</span><span class="idx">0{i+1}</span></a>')
    home_href = prefix + './'
    en_href = prefix + 'en/./'
    m_lang = f'<a href="{home_href}">ES</a><a href="{en_href}">EN</a>'
    return f"""<a class="skip-link" href="#main">{'Saltar al contenido' if lang == 'es' else 'Skip to content'}</a>
<header class="site-header">
  <div class="container header-row">
    <a class="logo" href="{prefix}./">LUIS MORENO <em>FILM</em></a>
    <nav class="main-nav" aria-label="{'Principal' if lang == 'es' else 'Main'}">{''.join(links)}</nav>
    <div class="header-actions">
      {lang_html}
      <a class="btn btn--solid header-cta" href="{prefix}{contact_href}">{esc(t['nav_cta'])}</a>
      <button class="menu-btn" aria-expanded="false" aria-controls="mobileMenu" aria-label="Menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>
<nav class="mobile-menu" id="mobileMenu" aria-label="{'Móvil' if lang == 'es' else 'Mobile'}">
  {''.join(mobile_links)}
  <div class="m-foot">
    <a href="mailto:{S['email']}">{esc(S['email'])}</a>
    <a href="{S['instagram']}" rel="noopener">Instagram ↗</a>
    {m_lang}
  </div>
</nav>"""


def footer(lang, prefix):
    t = T[lang]['footer']
    nav_html = ''
    for label, path in T[lang]['nav']:
        href = prefix + (path if path else './')
        nav_html += f'<a href="{href}">{esc(label)}</a>'
    legal = esc(t['legal']).replace('2026', '<span data-year="true">2026</span>')
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="logo" href="{prefix}./">LUIS MORENO <em>FILM</em></a>
        <p>{esc(t['tagline'])}</p>
      </div>
      <div class="footer-col"><h2>{esc(t['nav'])}</h2>{nav_html}</div>
      <div class="footer-col"><h2>{esc(t['contact'])}</h2>
        <a href="mailto:{S['email']}">{esc(S['email'])}</a>
        <a href="tel:{S['phone']}">{esc(S['phone_label'])}</a>
      </div>
      <div class="footer-col"><h2>{esc(t['follow'])}</h2>
        <a href="{S['instagram']}" rel="noopener">Instagram ↗</a>
        <a href="{S['vimeo']}" rel="noopener">Vimeo ↗</a>
      </div>
    </div>
    <div class="footer-bottom">
      <p>{legal}</p>
      <p>{esc(t['based'])}</p>
    </div>
  </div>
</footer>
<script src="{prefix}assets/js/site.js" defer></script>"""


def layout(lang, rel, title, desc, body, prefix, current=None,
           og_type='website', og_image=None, ld=None, preload_image=None):
    doc = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
{head(lang, rel, title, desc, og_type, og_image, ld, preload_image)}
</head>
<body>
{header(lang, prefix, current or '')}
<main id="main">
{body}
</main>
{footer(lang, prefix)}
</body>
</html>
"""
    return doc.replace('{P}', prefix)


# ---------------------------------------------------------------- PIEZAS
def card_html(p, lang, prefix, dcls=''):
    t = T[lang]
    d = p[lang]
    href = prefix + detail_dir(lang, p['slug'])
    loc = f'<span class="pl">{esc(d["place"])}</span>' if d['place'] else ''
    return f"""<a class="card reveal {dcls}" data-cat="{p['cat']}" href="{href}">
      <div class="frame"><img src="{thumb(p)}" onerror="{THUMB_FALLBACK}" width="640" height="360" loading="lazy" decoding="async"
        alt="{esc(p['title'])} — {esc(d['cat_label'])}, Luis Moreno Film"></div>
      <span class="shade" aria-hidden="true"></span>
      <span class="play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span>
      <span class="cap">
        <span class="c">{esc(d['cat_label'])}</span>
        <span class="t">{esc(p['title'])}</span>
        {loc}
      </span>
    </a>"""


def person_ld(lang):
    return {
        "@type": "Person",
        "@id": f"{BASE}/#person",
        "name": "Luis Moreno",
        "alternateName": "LUIS MORENO FILM",
        "jobTitle": "Realizador y productor audiovisual" if lang == 'es' else "Filmmaker and audiovisual producer",
        "email": f"mailto:{S['email']}",
        "telephone": S['phone'],
        "url": f"{BASE}/",
        "sameAs": [S['instagram'], S['vimeo']],
        "address": {"@type": "PostalAddress", "addressRegion": "Huelva", "addressCountry": "ES"},
        "areaServed": ["Huelva", "Sevilla", "Andalucía", "España", "Algarve", "Portugal"],
        "knowsLanguage": ["es", "en"],
        "knowsAbout": ["Producción audiovisual", "Wedding films", "Realización de vídeo",
                       "Dirección de fotografía", "Operador de cámara", "Sonido directo",
                       "Iluminación", "Montaje"],
    }


def website_ld(lang):
    return {
        "@type": "WebSite",
        "@id": f"{BASE}/#website",
        "name": "Luis Moreno Film",
        "url": f"{BASE}/",
        "inLanguage": "es" if lang == 'es' else "en",
        "publisher": {"@id": f"{BASE}/#person"},
    }


def breadcrumb_ld(lang, items):
    m = []
    n = len(items)
    for i, (label, path) in enumerate(items):
        m.append({
            "@type": "ListItem", "position": i + 1,
            "name": label,
            **({"item": path} if i < n - 1 else {}),
        })
    return {"@type": "BreadcrumbList", "itemListElement": m}


def video_ld(p, lang):
    return {
        "@type": "VideoObject",
        "name": p['video_name'],
        "description": p[lang]['blurb'],
        "thumbnailUrl": thumb(p, '-d_1280x720'),
        "uploadDate": p['date'],
        "embedUrl": f"https://player.vimeo.com/video/{p['vimeo']}?h={p['hash']}",
        "publisher": {"@id": f"{BASE}/#person"},
        "author": {"@id": f"{BASE}/#person"},
        "inLanguage": "es" if lang == 'es' else "en",
    }


# ---------------------------------------------------------------- PÁGINAS
def home(lang, prefix, rel):
    t = T[lang]
    hero_img = prefix + 'assets/img/hero'
    srcset_webp = ', '.join(f'{hero_img}-{w}.webp {w}w' for w in (768, 1024, 1440, 1920, 2560))
    srcset_jpg = ', '.join(f'{hero_img}-{w}.jpg {w}w' for w in (960, 1440, 2560))
    featured = FEATURED[:6]
    fcards = '\n'.join(card_html(p, lang, prefix, ('d1' if i % 2 else '')) for i, p in enumerate(featured))
    cat_rows = ''
    for i, (slug, es, en, sec, _img) in enumerate(CATEGORIES):
        n = len([p for p in PROJECTS if p['cat'] == slug])
        cat_rows += f"""<a class="cat-row" href="{prefix}{page_href(lang,'projects')}?f={slug}">
        <span class="n">0{i+1}</span><span class="nm">{esc(es if lang=='es' else en)}</span>
        <span class="ct">{n} {'proyectos' if lang=='es' and n>1 else ('proyecto' if lang=='es' else ('projects' if n>1 else 'project'))}</span>
        <span class="go" aria-hidden="true">→</span></a>"""
    frchips = ''.join(f'<li>{esc(r)}</li>' for r in t['freelance']['roles'])
    sv = t['serv']
    ab = t['about']
    cta = t['cta']
    intro = t['intro']
    feat = t['featured']
    body = f"""
<section class="hero">
  <div class="hero-media" aria-hidden="true">
    <picture>
      <source type="image/webp" srcset="{srcset_webp}" sizes="100vw">
      <img src="{hero_img}-1440.jpg" srcset="{srcset_jpg}" sizes="100vw"
           width="2560" height="1440" fetchpriority="high" decoding="async"
           alt="Fotograma de una película de boda de Luis Moreno Film — ceremonia frente al mar en el Algarve">
    </picture>
  </div>
  <div class="container hero-inner">
    <h1 class="title-xl">{esc(t['hero']['l1'])} <span class="l2">{esc(t['hero']['l2'])}</span></h1>
    <span class="tag">{esc(t['hero']['tag'])}</span>
    <p class="sub">{esc(t['hero']['sub'])}</p>
    <div class="hero-meta">
      <span class="loc">{esc(t['hero']['loc'])}</span>
      <div class="hero-ctas">
        <a class="btn btn--solid" href="{prefix}{page_href(lang,'projects')}">{esc(t['hero']['cta1'])} <span class="arr">→</span></a>
        <a class="btn" href="{prefix}{page_href(lang,'contact')}">{esc(t['hero']['cta2'])}</a>
      </div>
    </div>
  </div>
  <span class="scroll-cue" aria-hidden="true"></span>
</section>

<section class="section">
  <div class="container">
    <p class="section-label reveal"><span class="num">01</span> {esc(intro['label'])}</p>
    <div class="editorial">
      <div class="reveal">
        <h2 class="h-section">{esc(intro['h'])}</h2>
      </div>
      <div class="reveal d1">
        {''.join(f'<p style="color:var(--text-2);margin-top:1.1em">{esc(x)}</p>' for x in intro['p'])}
      </div>
    </div>
  </div>
</section>

<section class="section section--tight rule">
  <div class="container">
    <p class="section-label reveal"><span class="num">02</span> {esc(feat['label'])}</p>
    <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:end;gap:24px;margin-bottom:clamp(28px,4vw,52px)">
      <h2 class="h-section reveal">{esc(feat['h'])}</h2>
      <a class="textlink" href="{prefix}{page_href(lang,'projects')}" style="flex-shrink:0">{esc(feat['link'])} <span aria-hidden="true">→</span></a>
    </div>
    <div class="grid-2">
      {fcards}
    </div>
  </div>
</section>

<section class="section section--tight">
  <div class="container">
    <p class="section-label reveal"><span class="num">03</span> {esc(t['cats']['label'])}</p>
    <div class="cat-list reveal">{cat_rows}</div>
  </div>
</section>

<section class="section rule">
  <div class="container">
    <p class="section-label reveal"><span class="num">04</span> {esc(sv['label'])}</p>
    <h2 class="h-section reveal" style="margin-bottom:clamp(32px,4vw,56px)">{esc(sv['h'])}</h2>
    <div class="tracks">
      <div class="track reveal">
        <h3>{esc(sv['a_t'])}</h3>
        <p>{esc(sv['a_p'])}</p>
        <a class="textlink" href="{prefix}{page_href(lang,'services')}">{esc(sv['a_link'])} <span aria-hidden="true">→</span></a>
      </div>
      <div class="track reveal d1">
        <h3>{esc(sv['b_t'])}</h3>
        <p>{esc(sv['b_p'])}</p>
        <a class="textlink" href="{prefix}{page_href(lang,'other')}">{esc(sv['b_link'])} <span aria-hidden="true">→</span></a>
      </div>
    </div>
  </div>
</section>

<section class="section band">
  <div class="container band-grid">
    <div class="reveal">
      <p class="eyebrow" style="color:var(--accent);margin-bottom:18px">{esc(t['freelance']['label'])}</p>
      <h2 class="h-section">{esc(t['freelance']['h'])}</h2>
      <ul class="role-chips">{frchips}</ul>
      <p class="band-note">{esc(t['freelance']['note'])}</p>
      <p style="margin-top:30px">
        <a class="btn btn--solid" href="{prefix}{page_href(lang,'contact')}?t=crew">{esc(t['freelance']['cta'])} <span class="arr">→</span></a>
      </p>
    </div>
    <p class="lead reveal d1">{esc(t['freelance']['p'])}</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <p class="section-label reveal"><span class="num">05</span> {esc(ab['label'])}</p>
    <div class="editorial rev">
      <div class="reveal">
        <p class="pull-quote">“{esc(ab['q'])}”</p>
        <p class="body">{esc(ab['p'])}</p>
        <p style="margin-top:30px"><a class="textlink" href="{prefix}{page_href(lang,'about')}">{esc(ab['link'])} <span aria-hidden="true">→</span></a></p>
      </div>
      <div class="media reveal d1">
        <img src="{prefix}assets/img/editorial-melisa.webp" width="1400" height="787" loading="lazy" decoding="async"
             alt="Fotograma de la boda de Melisa y Jorge en Isla Canela, Huelva — Luis Moreno Film">
      </div>
    </div>
  </div>
</section>

<section class="cta-band rule">
  <div class="container">
    <h2 class="reveal">{esc(cta['h'])}</h2>
    <p class="reveal d1">{esc(cta['p'])}</p>
    <a class="btn btn--solid reveal d2" href="mailto:{S['email']}">{esc(cta['btn'])} <span class="arr">→</span></a>
  </div>
</section>"""
    ld = [person_ld(lang), website_ld(lang)]
    title, desc = SEO[lang]['home']
    return layout(lang, rel, title, desc, body, prefix, current='inicio', ld=ld,
                  preload_image=f'{hero_img}-1440.webp')


def projects_page(lang, prefix, rel):
    t = T[lang]['projects']
    chips = ''.join(f'<button class="chip{" is-active" if f== "all" else ""}" data-filter="{f}" type="button">{esc(lbl)}</button>'
                    for f, lbl in t['filters'])
    cards = '\n'.join(card_html(p, lang, prefix) for p in PROJECTS)
    empty_lbl = esc(t['empty'])
    body = f"""
<div class="container"><nav class="breadcrumb" aria-label="Breadcrumb">{bc_html(lang, prefix, [('Inicio' if lang=='es' else 'Home', prefix+'./'), (t['h'], None)])}</nav></div>
<section class="section--tight" style="padding-bottom:clamp(36px,5vw,64px)">
  <div class="container">
    <p class="section-label reveal"><span class="num">01</span> {esc(t['label'])}</p>
    <h1 class="h-display reveal">{esc(t['h'])}</h1>
    <p class="lead reveal d1" style="margin-top:24px">{esc(t['intro'])}</p>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="container">
    <div class="filters reveal" role="group" aria-label="{'Filtros' if lang=='es' else 'Filters'}">{chips}</div>
    <div class="grid-3">
      {cards}
    </div>
    <p data-empty style="display:none;color:var(--text-3);padding-block:40px">{empty_lbl}</p>
  </div>
</section>"""
    title, desc = SEO[lang]['projects']
    ld = breadcrumb_ld(lang, [
        ('Inicio' if lang == 'es' else 'Home', absu(page_href(lang, 'home'))),
        (t['h'], absu(page_href(lang, 'projects'))),
    ])
    return layout(lang, rel, title, desc, body, prefix, current='proyectos', ld=[ld])


def detail_page(lang, p, prefix, rel):
    t = T[lang]['proj']
    d = p[lang]
    idx = PROJECTS.index(p)
    prev_p = PROJECTS[idx - 1]
    next_p = PROJECTS[(idx + 1) % len(PROJECTS)]
    player_src = f"https://player.vimeo.com/video/{p['vimeo']}?h={p['hash']}&title=0&byline=0&portrait=0&autoplay=1"
    loc_html = f'<span class="loc">{esc(d["place"])}</span>' if d['place'] else ''
    svc_es = ['Concepto y guion', 'Dirección y cámara', 'Sonido directo', 'Montaje', 'Etalonaje']
    svc_en = ['Concept & script', 'Direction & camera', 'Location sound', 'Edit', 'Colour grade']
    svc = svc_es if lang == 'es' else svc_en
    if p['slug'] == 'tanqueray-spec-ad':
        svc = (['Concepto especulativo (spec)'] if lang == 'es' else ['Spec concept']) + svc[1:]
    svc_li = ''.join(f'<li>{esc(x)}</li>' for x in svc)
    body = f"""
<div class="container"><nav class="breadcrumb" aria-label="Breadcrumb">{bc_html(lang, prefix, [
    ('Inicio' if lang=='es' else 'Home', prefix+'./'),
    (t['breadcrumb'], prefix+page_href(lang,'projects')),
    (p['title'], None)])}</nav></div>
<section class="detail-head">
  <div class="container">
    <p class="eyebrow reveal" style="color:var(--accent)">{esc(t['own'] if p['slug']!='tanqueray-spec-ad' else t['spec'])}</p>
    <h1 class="detail-title reveal" style="margin-top:14px">{esc(p['title'])}</h1>
    <div class="detail-meta reveal d1">
      <span class="cat">{esc(d['cat_label'])}</span>{loc_html}
      <span class="loc">{p['date'][:4]}</span>
    </div>
    <p class="lead detail-lead reveal d1">{esc(d['blurb'])}</p>
    <div class="player reveal d2" data-video-src="{player_src}" data-video-title="{esc(p['video_name'])}">
      <img src="{thumb(p,'-d_1280x720')}" onerror="{THUMB_FALLBACK}" width="1280" height="720" loading="eager" fetchpriority="high" decoding="async"
           alt="Miniatura de {esc(p['title'])}, {esc(d['cat_label'])} de Luis Moreno Film">
      <button class="launch" type="button" aria-label="{('Reproducir' if lang=='es' else 'Play')} {esc(p['title'])}">
        <span class="play"><svg viewBox="0 0 24 24" width="22" height="22" fill="currentColor"><path d="M8 5v14l11-7z"/></svg></span>
      </button>
    </div>
  </div>
</section>
<section style="padding-bottom:clamp(30px,4vw,50px)">
  <div class="container detail-body">
    <div class="text reveal">
      {''.join(f'<p>{esc(par)}</p>' for par in d['body'])}
      <p style="margin-top:2.4em">
        <a class="textlink" href="{prefix}{page_href(lang,'contact')}">{esc(T[lang]['cta']['h'])} <span aria-hidden="true">→</span></a>
      </p>
    </div>
    <aside class="detail-aside reveal d1">
      <p class="k">{esc(t['services'])}</p>
      <ul>{svc_li}</ul>
      {f'<p class="k">{esc(t["loc"])}</p><ul><li>{esc(d["place"])}</li></ul>' if d['place'] else ''}
      <p class="k">Vídeo</p>
      <ul><li><a href="https://vimeo.com/{p['vimeo']}" rel="noopener" style="border-bottom:1px solid var(--hairline)">Vimeo ↗</a></li></ul>
    </aside>
  </div>
</section>
<section class="section section--tight" style="padding-top:0">
  <div class="container">
    <div class="pager">
      <a class="prev" href="{prefix}{detail_dir(lang, prev_p['slug'])}">
        <span class="d">← {esc(t['prev'])}</span><span class="n">{esc(prev_p['title'])}</span></a>
      <a class="next" href="{prefix}{detail_dir(lang, next_p['slug'])}">
        <span class="d">{esc(t['next'])} →</span><span class="n">{esc(next_p['title'])}</span></a>
    </div>
    <p style="text-align:center;margin-top:clamp(16px,3vw,32px)">
      <a class="textlink" href="{prefix}{page_href(lang,'projects')}">{esc(t['back'])} <span aria-hidden="true">→</span></a>
    </p>
  </div>
</section>"""
    title = f"{p['title']} — {d['cat_label']} {SEO[lang]['detail_suffix']}"
    desc = d['blurb']
    ld = [video_ld(p, lang),
          breadcrumb_ld(lang, [
              ('Inicio' if lang == 'es' else 'Home', absu(page_href(lang, 'home'))),
              (t['breadcrumb'], absu(page_href(lang, 'projects'))),
              (p['title'], absu(detail_dir(lang, p['slug']))),
          ]),
          person_ld(lang)]
    return layout(lang, rel, title, desc, body, prefix, current='proyectos',
                  og_type='video.other', og_image=thumb(p, '-d_1280x720'), ld=ld)


def bc_html(lang, prefix, items):
    out = []
    for label, href in items:
        if href:
            out.append(f'<a href="{href}">{esc(label)}</a><span aria-hidden="true">/</span>')
        else:
            out.append(f'<span aria-current="page">{esc(label)}</span>')
    return ' '.join(out)


def other_page(lang, prefix, rel):
    t = T[lang]['other']
    rows = ''
    for c in CREDITS:
        if c.get('img'):
            img = f"{prefix}assets/img/hermandad-640.jpg"
            fallback = ''
            w, h = 640, 360
            alt = f"{c['t']} — Luis Moreno Film"
        elif c['plat'] == 'yt':
            img = yt_thumb(c['yt'], 'hq')
            fallback = ''
            w, h = 480, 360
            alt = f"{c['t']} — {c['role_es']}"
        else:
            img = f"https://i.vimeocdn.com/video/{c['thumb']}-d_640x360"
            fallback = ''
            w, h = 640, 360
            alt = f"{c['t']} — {c['role_es']}"
        plat_lbl = {'yt': 'YouTube', 'vimeo': 'Vimeo', 'fb': 'Facebook'}[c['plat']]
        role = c['role_es'] if lang == 'es' else c['role_en']
        rows += f"""<a class="credit reveal" href="{c['url']}" target="_blank" rel="noopener">
      <span class="th"><img src="{img}"{fallback} width="{w}" height="{h}" loading="lazy" decoding="async" alt="{esc(c['t'] + ' — ' + role)}"></span>
      <span><span class="t">{esc(c['t'])}</span>
        <span class="r">{esc(role)}</span></span>
      <span class="go"><span class="plat">{plat_lbl}</span><span class="arr">↗</span></span>
    </a>"""
    body = f"""
<div class="container"><nav class="breadcrumb" aria-label="Breadcrumb">{bc_html(lang, prefix, [('Inicio' if lang=='es' else 'Home', prefix+'./'), (t['h'], None)])}</nav></div>
<section class="section--tight" style="padding-bottom:clamp(36px,5vw,64px)">
  <div class="container">
    <p class="section-label reveal"><span class="num">01</span> {esc(t['label'])}</p>
    <h1 class="h-display reveal">{esc(t['h'])}</h1>
    <p class="lead reveal d1" style="margin-top:24px">{esc(t['intro'])}</p>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="container">
    <div class="credits">{rows}</div>
  </div>
</section>
<section class="cta-band rule" style="padding-block:clamp(64px,9vw,110px)">
  <div class="container">
    <h2 class="reveal" style="font-size:clamp(2rem,4.6vw,3.4rem)">{esc(T[lang]['freelance']['h'])}</h2>
    <p class="reveal d1">{esc(T[lang]['freelance']['p'])}</p>
    <a class="btn btn--solid reveal d2" href="{prefix}{page_href(lang,'contact')}?t=crew">{esc(T[lang]['freelance']['cta'])} <span class="arr">→</span></a>
  </div>
</section>"""
    title, desc = SEO[lang]['other']
    ld = breadcrumb_ld(lang, [
        ('Inicio' if lang == 'es' else 'Home', absu(page_href(lang, 'home'))),
        (t['h'], absu(page_href(lang, 'other'))),
    ])
    return layout(lang, rel, title, desc, body, prefix, current='otros trabajos', ld=[ld])


def services_page(lang, prefix, rel):
    t = T[lang]['services']
    def items(rows):
        out = ''
        for i, (h, p) in enumerate(rows):
            out += f"""<div class="svc reveal"><span class="no">0{i+1}</span>
              <div><h3>{esc(h)}</h3><p>{esc(p)}</p></div></div>"""
        return out
    body = f"""
<div class="container"><nav class="breadcrumb" aria-label="Breadcrumb">{bc_html(lang, prefix, [('Inicio' if lang=='es' else 'Home', prefix+'./'), (t['h'], None)])}</nav></div>
<section class="section--tight" style="padding-bottom:clamp(36px,5vw,64px)">
  <div class="container">
    <p class="section-label reveal"><span class="num">01</span> {esc(t['label'])}</p>
    <h1 class="h-display reveal">{esc(t['h'])}</h1>
    <p class="lead reveal d1" style="margin-top:24px">{esc(t['intro'])}</p>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="container">
    <h2 class="h-section reveal" style="margin-bottom:14px">{esc(t['a_h'])}</h2>
    <p class="lead reveal d1" style="margin-bottom:clamp(28px,4vw,48px)">{esc(t['a_p'])}</p>
    <div class="svc-list">{items(t['a_items'])}</div>
  </div>
</section>
<section class="section band">
  <div class="container">
    <p class="eyebrow reveal" style="color:var(--accent);margin-bottom:16px">{esc(T[lang]['freelance']['label'])}</p>
    <h2 class="h-section reveal" style="margin-bottom:14px">{esc(t['b_h'])}</h2>
    <p class="lead reveal d1" style="margin-bottom:clamp(28px,4vw,48px)">{esc(t['b_p'])}</p>
    <div class="svc-list">{items(t['b_items'])}</div>
    <ul class="role-chips reveal" style="margin-top:36px">{''.join(f'<li>{esc(r)}</li>' for r in T[lang]['freelance']['roles'])}</ul>
    <p class="band-note reveal">{esc(T[lang]['freelance']['note'])}</p>
  </div>
</section>
<section class="cta-band rule">
  <div class="container">
    <h2 class="reveal" style="font-size:clamp(2.2rem,5vw,3.8rem)">{esc(t['rate_title'])}</h2>
    <p class="reveal d1">{esc(t['rate_p'])}</p>
    <a class="btn btn--solid reveal d2" href="{prefix}{page_href(lang,'contact')}">{esc(t['cta'])} <span class="arr">→</span></a>
  </div>
</section>"""
    title, desc = SEO[lang]['services']
    ld = [breadcrumb_ld(lang, [
        ('Inicio' if lang == 'es' else 'Home', absu(page_href(lang, 'home'))),
        (t['h'], absu(page_href(lang, 'services'))),
    ])]
    return layout(lang, rel, title, desc, body, prefix, current='servicios', ld=ld)


def about_page(lang, prefix, rel):
    t = T[lang]['aboutpage']
    facts = ''.join(f'<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k, v in t['facts'])
    body = f"""
<div class="container"><nav class="breadcrumb" aria-label="Breadcrumb">{bc_html(lang, prefix, [('Inicio' if lang=='es' else 'Home', prefix+'./'), (t['h'], None)])}</nav></div>
<section class="section--tight" style="padding-bottom:clamp(36px,5vw,64px)">
  <div class="container">
    <p class="section-label reveal"><span class="num">01</span> {esc(t['label'])}</p>
    <h1 class="h-display reveal">{esc(t['h'])}</h1>
    <p class="lead reveal d1" style="margin-top:24px;font-size:clamp(1.15rem,2vw,1.5rem);color:var(--text)">{esc(t['lead'])}</p>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="container editorial">
    <div class="reveal">
      <div class="media" style="aspect-ratio:16/10;background:var(--surface-2);display:flex;align-items:center;justify-content:center;border:1px solid var(--hairline-soft);border-radius:2px;overflow:hidden;position:relative">
        <img src="{prefix}assets/img/eric-1600.jpg" width="1600" height="900" loading="lazy" decoding="async"
             style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.85"
             alt="Fotograma de la pedida de mano de Eric y Cristina en el Algarve — dirección de Luis Moreno Film">
      </div>
      <p style="font-size:12px;color:var(--text-3);margin-top:12px">{'Fotograma de trabajo propio. Retrato profesional disponible a petición.' if lang=='es' else 'Still from my own work. Professional portrait available on request.'}</p>
    </div>
    <div class="reveal d1">
      {''.join(f'<p style="color:var(--text-2);font-size:16.5px">{esc(par)}</p>' for par in t['p'])}
      <dl class="facts" style="margin-top:40px">{facts}</dl>
      <p style="margin-top:34px">
        <a class="btn btn--solid" href="{prefix}{page_href(lang,'contact')}">{esc(T[lang]['cta']['btn'])} <span class="arr">→</span></a>
      </p>
    </div>
  </div>
</section>"""
    title, desc = SEO[lang]['about']
    ld = [person_ld(lang), breadcrumb_ld(lang, [
        ('Inicio' if lang == 'es' else 'Home', absu(page_href(lang, 'home'))),
        (t['h'], absu(page_href(lang, 'about'))),
    ])]
    return layout(lang, rel, title, desc, body, prefix, current='sobre mí', ld=ld)


def contact_page(lang, prefix, rel):
    t = T[lang]['contact']
    f = t['form']
    opts = ''.join(f'<option value="{esc(o)}">{esc(o)}</option>' for o in f['types'])
    body = f"""
<div class="container"><nav class="breadcrumb" aria-label="Breadcrumb">{bc_html(lang, prefix, [('Inicio' if lang=='es' else 'Home', prefix+'./'), (t['h'], None)])}</nav></div>
<section class="section--tight" style="padding-bottom:clamp(36px,5vw,64px)">
  <div class="container">
    <p class="section-label reveal"><span class="num">01</span> {esc(t['label'])}</p>
    <h1 class="h-display reveal">{esc(t['h'])}</h1>
    <p class="lead reveal d1" style="margin-top:24px">{esc(t['p'])}</p>
  </div>
</section>
<section class="section" style="padding-top:0">
  <div class="container editorial">
    <div class="reveal">
      <a class="contact-big" href="mailto:{S['email']}">
        <span class="eyebrow">{esc(t['email_t'])}</span>
        <span class="val">{esc(S['email'])}</span>
        <span class="d">{esc(t['email_d'])}</span></a>
      <a class="contact-big" href="tel:{S['phone']}">
        <span class="eyebrow">{esc(t['phone_t'])}</span>
        <span class="val">{esc(S['phone_label'])}</span>
        <span class="d">{esc(t['phone_d'])}</span></a>
      <a class="contact-big" href="{S['instagram']}" rel="noopener">
        <span class="eyebrow">{esc(t['ig_t'])}</span>
        <span class="val">@luismorenofilm ↗</span>
        <span class="d">{esc(t['ig_d'])}</span></a>
      <p style="margin-top:26px;font-size:13px;color:var(--text-3)">{'España y Algarve (Portugal). Proyectos en toda Europa.' if lang=='es' else 'Spain and the Algarve (Portugal). Projects across Europe.'}</p>
    </div>
    <div class="form reveal d1">
      <h2 class="h-card" style="margin-bottom:8px">{esc(f['title'])}</h2>
      <p style="font-size:13.5px;color:var(--text-3);margin-bottom:26px">{esc(f['sub'])}</p>
      <form id="mailtoForm" data-to="{S['email']}">
        <div class="field"><label for="f-name">{esc(f['name'])}</label>
          <input id="f-name" name="name" autocomplete="name" required></div>
        <div class="field"><label for="f-email">{esc(f['email'])}</label>
          <input id="f-email" name="email" type="email" autocomplete="email" required></div>
        <div class="field"><label for="f-type">{esc(f['type'])}</label>
          <select id="f-type" name="type">{opts}</select></div>
        <div class="field"><label for="f-msg">{esc(f['msg'])}</label>
          <textarea id="f-msg" name="message" required></textarea></div>
        <button class="btn btn--solid" type="submit">{esc(f['submit'])} <span class="arr">→</span></button>
        <p class="note">{esc(f['note'])}</p>
      </form>
    </div>
  </div>
</section>"""
    title, desc = SEO[lang]['contact']
    ld = [person_ld(lang), breadcrumb_ld(lang, [
        ('Inicio' if lang == 'es' else 'Home', absu(page_href(lang, 'home'))),
        (t['h'], absu(page_href(lang, 'contact'))),
    ])]
    return layout(lang, rel, title, desc, body, prefix, current='contacto', ld=ld)


def error_page():
    """404 autocontenida: sin assets relativos (se sirve bajo cualquier ruta)."""
    es = T['es']['err']
    en = T['en']['err']
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, follow">
<title>404 — Página no encontrada | Luis Moreno Film</title>
<style>
:root{{--t:#F5F3EF;--m:#8F8A80}}
*{{margin:0;box-sizing:border-box}}
body{{background:#111;color:var(--t);font-family:Georgia,serif;display:grid;place-items:center;min-height:100svh;text-align:center;padding:32px}}
code{{font-family:ui-monospace,monospace;color:var(--m);font-size:13px;letter-spacing:.3em}}
h1{{font-size:clamp(2.4rem,8vw,4.6rem);font-weight:500;margin:18px 0 10px}}
p{{color:var(--m);font-family:system-ui,sans-serif;font-size:15px;max-width:34em;margin:0 auto 6px}}
a.btn{{display:inline-block;margin-top:34px;padding:14px 34px;border:1px solid rgba(245,243,239,.3);border-radius:999px;color:var(--t);text-decoration:none;font:600 12px/1 system-ui,sans-serif;letter-spacing:.18em;text-transform:uppercase}}
a.btn:hover{{background:#D7D3CC;color:#111}}
.en{{margin-top:26px;font-size:13px}}
.en a{{color:var(--t)}}
</style>
</head>
<body>
<div>
<code>404</code>
<h1>{es['h']}</h1>
<p>{es['p']}</p>
<a class="btn" href="{BASE}/">{es['back']}</a>
<p class="en">{en['p2']} <a href="{BASE}/en/">English home</a></p>
</div>
</body>
</html>"""


def sitemap_xml():
    clusters = []
    for k in ['home', 'projects', 'other', 'services', 'about', 'contact']:
        clusters.append(alternates_for(k))
    for p in PROJECTS:
        clusters.append(alternates_for('detail', p['slug']))
    body = ''
    for alts in clusters:
        al = (f'<xhtml:link rel="alternate" hreflang="es" href="{alts["es"]}"/>'
              f'<xhtml:link rel="alternate" hreflang="en" href="{alts["en"]}"/>'
              f'<xhtml:link rel="alternate" hreflang="x-default" href="{alts["es"]}"/>')
        for loc in (alts['es'], alts['en']):
            body += f'<url><loc>{loc}</loc>{al}<lastmod>{BUILD_DATE}</lastmod></url>'
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + body + '\n</urlset>\n')


def robots_txt():
    return f"""User-agent: *
Allow: /

Sitemap: {BASE}/sitemap.xml
"""


# ---------------------------------------------------------------- MAIN
def write(rel, content):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as fh:
        fh.write(content)
    return rel


def main():
    written = []
    for lang in ('es', 'en'):
        # home
        rel_home = 'index.html' if lang == 'es' else 'en/index.html'
        pre = prefix_for(rel_home)
        written.append(write(rel_home, home(lang, pre, (lang, 'home'))))
        for key in ('projects', 'other', 'services', 'about', 'contact'):
            rel = page_href(lang, key) + 'index.html'
            written.append(write(rel, dict(
                projects=projects_page, other=other_page, services=services_page,
                about=about_page, contact=contact_page)[key](lang, prefix_for(rel), (lang, key))))
        for p in PROJECTS:
            rel = detail_dir(lang, p['slug']) + 'index.html'
            written.append(write(rel, detail_page(lang, p, prefix_for(rel), (lang, 'detail', p['slug']))))
    written.append(write('404.html', error_page()))
    written.append(write('sitemap.xml', sitemap_xml()))
    written.append(write('robots.txt', robots_txt()))
    written.append(write('.nojekyll', ''))
    print(f'OK: {len(written)} archivos generados')
    for w in written:
        print(' ', w)


if __name__ == '__main__':
    main()
