#!/usr/bin/env python3
"""Build crawlable static pages using Python's standard library. No runtime framework."""
from pathlib import Path
import json, html, re, xml.etree.ElementTree as ET
from content import PAGES, FAQ
ROOT = Path(__file__).resolve().parents[2]
RELEASE = json.loads(Path(__file__).with_name('release.json').read_text())
BASE = 'https://lumbrestudios.app'
ASSETS = '/assets/screenshots/chance-darts/premium/'
OUT = ROOT / 'chance-darts'
WATCH_IMAGES = json.loads(Path(__file__).with_name('watch-images.json').read_text())
SEO = json.loads(Path(__file__).with_name('seo.json').read_text())
E = html.escape

def route(slug=''):
    return '/chance-darts/' + (slug + '/' if slug else '')
def link(slug, label=None, cls=''):
    return f'<a class="{cls}" href="{route(slug)}">{E(label or PAGES[slug]["label"])}</a>'
def store(tv=False):
    product = RELEASE['tv' if tv else 'ios']
    if product['status'] != 'released':
        return '<p class="availability">Public release not yet verified.</p>'
    return f'<a class="button store" data-store href="{product["url"]}"><svg viewBox="0 0 24 28" aria-hidden="true"><path d="M19.3 14.8c0-3 2.5-4.5 2.6-4.6-1.4-2.1-3.6-2.4-4.4-2.4-1.9-.2-3.7 1.1-4.7 1.1-1 0-2.5-1.1-4.1-1.1C6.6 7.9 4.6 9.1 3.5 11c-2.2 3.8-.6 9.4 1.5 12.5 1 1.5 2.2 3.1 3.8 3 1.5-.1 2.1-1 4-1 1.9 0 2.4 1 4.1 1 1.7 0 2.8-1.5 3.8-3 1.2-1.7 1.7-3.4 1.7-3.5-.1 0-3.1-1.2-3.1-5.2ZM16.2 5.8c.9-1.1 1.5-2.6 1.3-4.1-1.3.1-2.9.9-3.8 2-.8.9-1.6 2.5-1.4 4 1.5.1 2.9-.8 3.9-1.9Z"/></svg><span><small>{"Apple TV · Download on the" if tv else "Download on the"}</small>App Store</span></a>'
def art(name, caption='', eager=False, cls='', sizes=None):
    files = sorted((ROOT / ASSETS.lstrip('/')).glob(name+'-*.webp'),key=lambda p:int(p.stem.rsplit('-',1)[1]))
    full = files[-1]
    dims = {'iphone-match':(1320,2868),'pots':(1320,2868),'training':(1320,2868),'darts-night':(1320,2868),'cricket':(1320,2868),'duo-portrait':(2007,2853),'ipad':(2752,2064)}
    w,h=dims.get(name,(2853,2007))
    if sizes is None:
        sizes = '(max-width: 760px) 230px, 260px' if cls == 'portrait' else ('250px' if name == 'pots' else '(max-width: 640px) calc(100vw - 40px), (max-width: 760px) 600px, (max-width: 1100px) calc((100vw - 101px) / 2), (max-width: 1416px) calc((100vw - 166px) / 2), 625px')
    srcset=', '.join(ASSETS+f.name+' '+f.stem.rsplit('-',1)[1]+'w' for f in files)
    return f'<figure class="art {cls}"><a href="{ASSETS+full.name}" data-viewer aria-label="Enlarge image: {E(caption)}"><img src="{ASSETS+name}-960.webp" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}" alt="{E(caption)}" {"fetchpriority=high" if eager else "loading=lazy"} decoding="async"></a><figcaption>{E(caption)}</figcaption></figure>'
def watch_art(index, eager=False):
    item = WATCH_IMAGES[index]
    path = '/assets/screenshots/chance-darts/watch/' + item['file']
    webp_path = path.removesuffix('.png') + '.webp'
    return f'<figure class="art watch-art"><a href="{path}" data-viewer aria-label="Enlarge image: {E(item["caption"])}"><picture><source type="image/webp" srcset="{webp_path}"><img src="{path}" width="{item["width"]}" height="{item["height"]}" alt="{E(item["alt"])}" {"fetchpriority=high" if eager else "loading=lazy"} decoding="async"></picture></a><figcaption>{E(item["caption"])}</figcaption></figure>'
def watch_gallery():
    return '<section class="watch-gallery" aria-labelledby="watch-gallery-heading"><div class="section-heading"><p class="eyebrow">A closer look</p><h2 id="watch-gallery-heading">THE MATCH,\nAT A GLANCE.</h2><p>Live scores, current-player focus and match details on Apple Watch. Select a screenshot to view it at full size.</p></div><div class="watch-gallery-grid">' + ''.join(watch_art(i) for i in range(len(WATCH_IMAGES))) + '</div></section>'

def nav(slug):
    groups={}
    for key,p in PAGES.items(): groups.setdefault(p['group'],[]).append((key,p))
    menu=''.join('<div><h3>'+group+'</h3>'+''.join(link(k,cls='current' if k==slug else '') for k,p in entries)+'</div>' for group,entries in groups.items())
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="studio-header"><div class="wrap"><a class="studio-brand" href="/"><img src="{ASSETS}studio-logo.webp" width="44" height="44" alt="Lumbre Studios"><span>INDEPENDENT APPS. DISTINCT PERSONALITIES.</span></a><nav aria-label="Lumbre Studios"><a href="/">Home</a><a href="/#apps">Apps</a><a href="/support.html">Support</a></nav></div></header>
<header class="product-header"><div class="wrap product-bar"><a class="product-brand" href="/chance-darts/"><img src="{ASSETS}chance-logo.webp" width="44" height="44" alt="">CHANCE DARTS</a><nav class="quick-nav" aria-label="Featured pages">{link('scoring')}{link('iphone-duo')}{link('pro')}{link('help')}</nav><div class="nav-actions"><a class="nav-download" data-store href="{RELEASE['ios']['url']}">Get the app</a><button class="menu-toggle" hidden aria-expanded="false" aria-controls="product-menu">Explore <span aria-hidden="true">＋</span></button></div></div><nav id="product-menu" class="mega-menu wrap" aria-label="All Chance Darts pages">{menu}</nav></header>'''
def footer():
    groups={}
    for k,p in PAGES.items(): groups.setdefault(p['group'],[]).append(k)
    columns=''.join('<div><h3>'+g+'</h3>'+''.join(link(k) for k in ks)+'</div>' for g,ks in groups.items())
    return f'''<footer><div class="wrap"><div class="footer-top"><a class="product-brand" href="/chance-darts/"><img src="{ASSETS}chance-logo.webp" width="48" height="48" alt="">CHANCE DARTS</a><p>A Lumbre Studios app.<br>Made for the way you play.</p></div><nav class="footer-grid" aria-label="Product directory">{columns}</nav><div class="footer-bottom"><span>© Lumbre Studios</span><nav aria-label="Studio and legal"><a href="/luma/">Luma</a><a href="/raybar/">RayBar</a><a href="/luma-kids/">Luma Kids</a><a href="/support.html">Support</a><a href="/chance-darts-privacy.html">Chance Darts privacy</a><a href="/privacy.html">Studio privacy</a><a href="mailto:support@lumbrestudios.app">Contact</a></nav></div></div></footer><dialog id="image-viewer" aria-label="Full-size promotional artwork"><div class="viewer-bar"><p id="viewer-caption"></p><button type="button" aria-label="Close image viewer">Close</button></div><img id="viewer-image" alt=""></dialog>'''
def closing():
    return f'<section class="closing wrap"><div><p class="eyebrow">Your next game starts here</p><h2>TAKE YOUR\nGAME FURTHER.</h2></div><div><p>Free to download. Try local play, join a friend online, and explore the optional lifetime Pro upgrade.</p>{store()}<p class="fine">{link("pro","See free allowances and Pro features")}</p></div></section>'
def availability():
    rows=[('iPhone & iPad','Available · '+RELEASE['ios']['version'],'scoring'),('Apple Watch','Included with the iPhone app','apple-watch'),('Apple TV','Free receiver · '+RELEASE['tv']['version'],'apple-tv'),('Browser','Live Display available','live-display'),('Mac',RELEASE['mac']['note'],None),('Android',RELEASE['android']['note'],None)]
    return '<section class="availability-section wrap" id="platforms"><div class="section-heading"><p class="eyebrow">Across your screens</p><h2>FIND YOUR SETUP.</h2><p>Scoring on your device. Spectators on theirs.</p></div><dl class="platforms" id="screens">'+''.join('<div><dt>'+ (link(s,n) if s else n)+'</dt><dd>'+E(t)+'</dd></div>' for n,t,s in rows)+f'</dl><p class="fine">Public availability checked in the UK App Store on {RELEASE["checked"]}. Availability can vary by region. {link("whats-new","Release details")}</p></section>'
def head(slug,p):
    meta=SEO['pages'][slug];title=meta['title'];desc=meta['description'];im=meta['image']
    url=BASE+route(slug); org=BASE+'/#organization'; site=BASE+'/#website'
    app=BASE+route('apple-tv' if slug=='apple-tv' else '')+'#app'
    schema=[
      {'@type':'Organization','@id':org,'name':'Lumbre Studios','url':BASE+'/'},
      {'@type':'WebSite','@id':site,'name':'Lumbre Studios','url':BASE+'/','publisher':{'@id':org}},
      {'@type':'WebPage','@id':url+'#webpage','name':title,'description':desc,'url':url,'inLanguage':'en-GB','isPartOf':{'@id':site},'publisher':{'@id':org},'about':{'@id':app},'breadcrumb':{'@id':url+'#breadcrumb'}},
      {'@type':'BreadcrumbList','@id':url+'#breadcrumb','itemListElement':[{'@type':'ListItem','position':1,'name':'Lumbre Studios','item':BASE+'/'},{'@type':'ListItem','position':2,'name':'Chance Darts','item':BASE+route()}]+([{'@type':'ListItem','position':3,'name':p['label'],'item':url}] if slug else [])}]
    if not slug or slug=='apple-tv':
        tv=slug=='apple-tv'; r=RELEASE['tv' if tv else 'ios']
        schema.append({'@type':'SoftwareApplication','@id':app,'name':'Chance Darts Live Display' if tv else 'Chance Darts','operatingSystem':'tvOS 16 or later' if tv else 'iOS 15 or later; iPadOS 15 or later','applicationCategory':'SportsApplication','softwareVersion':r['version'],'url':url,'downloadUrl':r['url'],'publisher':{'@id':org},'description':desc,'offers':{'@type':'Offer','price':'0','priceCurrency':'GBP','url':r['url'],'description':'Free Apple TV receiver download.' if tv else 'Free base app download with limited local play; optional Pro Lifetime purchase is separate and priced in the app.'}})
    schema={'@context':'https://schema.org','@graph':schema}
    social={'og:type':'website','og:site_name':'Lumbre Studios','og:locale':'en_GB','og:title':title,'og:description':desc,'og:url':url,'og:image':BASE+im['path'],'og:image:type':im['type'],'og:image:width':str(im['width']),'og:image:height':str(im['height']),'og:image:alt':im['alt']}
    tags=''.join(f'<meta property="{k}" content="{E(v)}">' for k,v in social.items())
    twitter={'card':'summary' if im['width']==im['height'] else 'summary_large_image','title':title,'description':desc,'image':BASE+im['path'],'image:alt':im['alt']}
    tags+=''.join(f'<meta name="twitter:{k}" content="{E(v)}">' for k,v in twitter.items())
    return f'''<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}"><meta name="apple-itunes-app" content="app-id={6837735748 if slug=='apple-tv' else 6760661230}">{tags}<link rel="icon" href="/favicon.ico" sizes="any"><link rel="stylesheet" href="/chance-darts/chance-darts.css"><script src="/chance-darts/chance-darts.js" defer></script><script type="application/ld+json">{json.dumps(schema)}</script></head><body class="page-{slug or 'home'}">'''

def home():
    p={'intro':'Play. Compete. Connect. Improve. Discover Chance Darts scoring, online video, Apple Watch, Duo, Live Display, training and leagues. Free download, optional lifetime Pro.'}
    features=[('scoring','The game, your way.','301, 501, 701. Singles, doubles, teams and a little Chance with Pots.'),('online-play','Two boards. One match.','Real-time scoring and optional live video. Host with Pro; join for free.'),('training','Make practice count.','Five focused training games, from finishing to friendly rivalry.'),('statistics','Know your progress.','Saved player profiles, recorded performance and advanced Pro statistics.')]
    rows=''.join(f'<a class="feature-row" href="{route(k)}"><span class="eyebrow">{PAGES[k]["label"]}</span><h3>{h}</h3><p>{t}</p><span class="row-action">Explore</span></a>' for k,h,t in features)
    return head('',p)+nav('')+f'''<main id="main"><section class="home-hero wrap"><div class="hero-copy"><a class="release-pill" href="{route('whats-new')}">NEW IN {RELEASE['ios']['version']} <span>Watch. Duo. More connected.</span></a><h1>YOUR DARTS.<br>YOUR RULES.<br><em>YOUR GAME.</em></h1><p class="hero-tagline">Play. Compete. Connect. Improve.</p><p class="lede">From the first throw to the final double. Your complete darts companion, made for the way you play.</p><div class="actions">{store()}{link('scoring','Explore the game','text-link')}</div><p class="fine">Free to download. Optional lifetime Pro. {link('pro','See what’s included.')}</p></div><div class="home-art">{art('duo-landscape','The Match Desk, unfolded on iPhone Duo.',True,sizes='(max-width: 640px) calc(100vw - 40px), (max-width: 760px) 600px, (max-width: 1100px) calc((100vw - 86px) * 0.51), (max-width: 1416px) calc((100vw - 146px) * 0.51), 648px')}<div class="art-label"><span>BUILT AROUND THE BOARD</span><span>iPhone · Duo · iPad</span></div></div></section>
<div class="manifesto wrap"><span>ONE COMPLETE DARTS COMPANION</span><p>From your first 501<br>to the whole room watching.</p></div>
<section class="wrap feature-index" id="play"><div class="section-heading"><p class="eyebrow">Make every visit count</p><h2>ALL THE WAYS\nYOU PLAY.</h2></div><div>{rows}</div></section>
<section class="spotlight" id="duo"><div class="wrap split"><div>{art('tabletop','A new angle on your game. Genuine Duo tabletop artwork.',sizes='(max-width: 760px) calc(100vw - 40px), (max-width: 1100px) calc((100vw - 101px) * 0.535), (max-width: 1416px) calc((100vw - 166px) * 0.535), 669px')}</div><div class="spotlight-copy"><p class="eyebrow">iPhone Duo</p><h2>ONE PHONE.\nBOTH SIDES\nOF THE GAME.</h2><p>Score on the inner screen. Let spectators follow on the outer screen. Adaptive layouts and local Live Display bring your setup together.</p>{link('iphone-duo','Meet Chance Darts on Duo','button outline')}<div class="screen-links" id="live-display">{link('apple-watch','Your match on Apple Watch')}{link('apple-tv','The big screen on Apple TV')}{link('ipad','More room on iPad')}{link('live-display','Connect browser Live Display')}</div></div></div></section>
<section class="wrap competition"><div><p class="eyebrow">Bring everyone to the board</p><h2>THE NIGHT.\nTHE SEASON.\nTHE RIVALRY.</h2></div><div><p>Friends at home. Teams at the pub. A club with a season to play for. Keep the fixtures, results and competition together.</p><div class="competition-links">{link('darts-night','Run a Darts Night')}{link('leagues','Build your league')}</div></div></section>
{availability()}{closing()}</main>{footer()}</body></html>'''
def prose(sections):
    return ''.join(f'<section class="story-section"><div class="story-heading"><h2>{E(title)}</h2><p>{E(body)}</p></div><div class="story-details">'+''.join(f'<article><h3>{E(h)}</h3><p>{E(b)}</p></article>' for h,b in details)+'</div></section>' for title,body,details in sections)
def pro_table():
    rows=[('Local play','3 completed matches','Unlimited local play'),('League Organiser','One starter, up to 4 entrants, across Local or Shared','Unlimited league creation, larger competitions and advanced organiser formats'),('Online Play','Join another player’s match','Host as well as join'),('Shared League participation','Join and play authorised fixtures','Same membership and role permissions apply'),('Performance','Local profiles and match results','Advanced stats, averages, detailed XP and achievements for supported saved profiles')]
    return '<section class="comparison"><p class="eyebrow">Free download · Optional upgrade</p><h2>CHOOSE YOUR GAME.</h2><div class="table-scroll" tabindex="0" role="region" aria-label="Free and Pro feature comparison"><table><caption>Chance Darts free access and Pro Lifetime</caption><thead><tr><th scope="col">Feature</th><th scope="col">Free</th><th scope="col">Pro Lifetime</th></tr></thead><tbody>'+''.join('<tr><th scope="row">'+a+'</th><td>'+b+'</td><td>'+c+'</td></tr>' for a,b,c in rows)+'</tbody></table></div><p class="fine">The local allowance is not a daily reset. One starter league is shared across both league types; deleting it does not reset use. Guest profiles do not receive Pro statistics. Current local price is shown inside the app.</p></section>'
def special_content(kind):
    if kind=='pro': return pro_table()
    if kind=='release':
        return '<div class="releases">'+''.join('<article class="release-entry"><div><span class="version">'+r['version']+'</span><p>'+r['date']+'</p></div><div><h2>'+r['title']+'</h2><ul>'+''.join('<li>'+x+'</li>' for x in r['items'])+'</ul></div></article>' for r in RELEASE['history'])+f'<article class="release-entry"><div><span class="version">TV {RELEASE["tv"]["version"]}</span><p>25 November 2026</p></div><div><h2>A dedicated view for Apple TV.</h2><p>The native Live Display receiver is a separate free download, with Match Play, Darts Night, remote controls and an offline demo.</p>{link("apple-tv","Explore the Apple TV app","text-link")}</div></article></div>'+availability()
    if kind=='help':
        groups={}
        for group,q,a in FAQ:groups.setdefault(group,[]).append((q,a))
        return '<section class="help-area"><div class="help-search" hidden><label for="help-search">Search help</label><input id="help-search" type="search" placeholder="Try “display code” or “restore Pro”" autocomplete="off"><p id="search-status" role="status" aria-live="polite"></p></div><div class="help-topics">'+''.join('<a href="#help-'+str(i)+'">'+g+'</a>' for i,g in enumerate(groups))+'</div>'+''.join('<section class="help-group" id="help-'+str(i)+'"><h2>'+g+'</h2>'+''.join('<details class="help-article"><summary>'+q+'</summary><p>'+a+'</p></details>' for q,a in entries)+'</section>' for i,(g,entries) in enumerate(groups.items()))+'<aside class="support-panel"><h2>Need a hand?</h2><p>Email <a href="mailto:support@lumbrestudios.app">support@lumbrestudios.app</a>. Include your app version, device and the steps that led to the issue.</p><div class="actions"><a class="text-link" href="/support.html">Lumbre Studios support</a><a class="text-link" href="/chance-darts-privacy.html">Chance Darts privacy</a></div></aside></section>'
    return ''
def editorial(kind):
    # Typography, not a simulated product UI. No fabricated application screens.
    words={'tv':('THE ROOM.','THE MATCH.','THE MOMENT.'),'watch':('LIVE SCORES.','ONE GLANCE.','ALL CHANCE.'),'stats':('EVERY VISIT.','EVERY DOUBLE.','YOUR PROGRESS.'),'league':('THE TEAMS.','THE FIXTURES.','THE SEASON.'),'pro':('PLAY MORE.','BUILD MORE.','ONE PURCHASE.')}
    if kind not in words:return ''
    return '<div class="editorial-art" aria-hidden="true"><img src="'+ASSETS+'chance-logo.webp" width="100" height="100" alt="">'+''.join('<span>'+w+'</span>' for w in words[kind])+'<i>CHANCE DARTS / LUMBRE STUDIOS</i></div>'
def page(slug,p):
    image=p.get('image'); special=p.get('special','')
    heroart=art(image,p['caption'],True,'portrait' if image in ['iphone-match','training','darts-night'] else '') if image else editorial(special)
    if slug=='apple-watch': heroart=watch_art(0,True)
    single=' single' if not heroart else ''
    action=store(slug=='apple-tv')
    if slug=='live-display':action=f'<a class="button" href="{RELEASE["receiver"]}">Open browser Live Display</a>'
    if slug=='help':action='<a class="text-link" href="mailto:support@lumbrestudios.app">Contact support</a>'
    if slug=='whats-new':action=link('apple-watch','Explore the Watch companion','text-link')
    fine='Free TV receiver. Requires a compatible scorer for live viewing.' if slug=='apple-tv' else 'Free to download. Optional lifetime Pro.'
    if slug=='apple-watch':fine=f'Included with iPhone app · {RELEASE["watch"]["minimum"]} or later · Paired iPhone required.'
    title=E(p['title']).replace('\n','<br>')
    hero=f'<div class="wrap"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">Lumbre Studios</a><span>/</span><a href="/chance-darts/">Chance Darts</a><span>/</span><span aria-current="page">{E(p["label"])}</span></nav><section class="page-hero{single}"><div><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{title}</h1><p class="lede">{E(p["intro"])}</p><div class="actions">{action}</div><p class="fine">{fine}</p></div>{heroart}</section></div>'
    steps=''
    if p.get('steps'): steps='<section class="steps-section"><h2>GET CONNECTED.</h2><ol class="steps">'+''.join('<li><h3>'+h+'</h3><p>'+b+'</p></li>' for h,b in p['steps'])+'</ol></section>'
    if slug=='darts-night': steps=steps.replace('GET CONNECTED.','SET UP THE NIGHT.')
    body=special_content(special)+steps+prose(p['sections'])
    if slug=='apple-watch': body+=watch_gallery()
    if slug=='iphone-duo':body+='<section class="duo-gallery"><h2>OPEN UP YOUR GAME.</h2><div>'+art('duo-landscape','Unfolded landscape. Approved Duo promotional artwork.',sizes='(max-width: 760px) calc(100vw - 40px), (max-width: 1100px) calc((100vw - 106px) * 0.637), (max-width: 1416px) calc((100vw - 146px) * 0.637), 809px')+art('duo-portrait','Unfolded portrait. Approved Duo promotional artwork.',sizes='(max-width: 760px) 300px, 320px')+'</div></section>'
    if slug=='scoring':body+='<section class="pots-feature">'+art('pots','Chance Darts Pots mode. Approved promotional artwork.')+'<div><p class="eyebrow">The Chance Darts difference</p><h2>A LITTLE CHANCE.\nA DIFFERENT GAME.</h2><p>Choose optional Pots when you want more at stake in every visit.</p></div></section>'
    if p.get('note'):body+='<aside class="note">'+E(p['note'])+'</aside>'
    related='<section class="related"><p class="eyebrow">Keep exploring</p><div>'+''.join(link(k) for k in p['related'])+'</div></section>'
    return head(slug,p)+nav(slug)+'<main id="main">'+hero+'<div class="wrap story-body">'+body+related+'</div>'+closing()+'</main>'+footer()+'</body></html>'
OUT.mkdir(exist_ok=True)
(OUT/'index.html').write_text(home())
for slug,p in PAGES.items():
    directory=OUT/slug;directory.mkdir(exist_ok=True)
    (directory/'index.html').write_text(page(slug,p))
ns='http://www.sitemaps.org/schemas/sitemap/0.9'
ET.register_namespace('',ns)
tree=ET.parse(ROOT/'sitemap.xml'); root=tree.getroot()
for item in list(root):
    loc=item.find('{'+ns+'}loc')
    if loc is not None and loc.text.startswith(BASE+'/chance-darts/'): root.remove(item)
for slug in ['',*PAGES]:
    item=ET.SubElement(root,'{'+ns+'}url'); ET.SubElement(item,'{'+ns+'}loc').text=BASE+route(slug); ET.SubElement(item,'{'+ns+'}lastmod').text=SEO['updated']
ET.indent(tree,space='  ');tree.write(ROOT/'sitemap.xml',encoding='utf-8',xml_declaration=True)
print(f'Built {len(PAGES)+1} static product pages; preserved other sitemap entries.')
