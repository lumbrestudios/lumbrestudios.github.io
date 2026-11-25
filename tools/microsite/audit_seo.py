#!/usr/bin/env python3
"""Non-browser SEO validation and transparent byte budgets; never a CWV test."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,subprocess,hashlib,gzip,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
BASE='https://lumbrestudios.app'; PRE='website-owner-approved-pre-seo-2026-11-25'
SEO=json.loads((ROOT/'tools/microsite/seo.json').read_text())
class Doc(HTMLParser):
 def __init__(self,text):
  super().__init__();self.meta={};self.links=[];self.images=[];self.canonical=[];self.jsons=[];self.in_json=False;self.buf='';self.main=False;self.headings=[];self.heading=None;self.body=False;self.tokens=[];self.source=None;self.lang=None;self.title='';self.in_title=False;self.feed(text)
 def handle_starttag(self,t,attrs):
  a=dict(attrs)
  if t=='body':self.body=True
  if self.body and t not in ['picture','source']:
   norm={k:v for k,v in a.items() if not(t=='img' and k=='sizes')};self.tokens.append(('start',t,sorted(norm.items())))
  if t=='html':self.lang=a.get('lang')
  if t=='title':self.in_title=True
  if t=='main':self.main=True
  if self.main and t in ['h1','h2','h3']:self.heading=[int(t[1]),''];self.headings.append(self.heading)
  if t=='br' and self.heading:self.heading[1]+=' '
  if t=='a':self.links.append(a)
  if t=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content')
  if t=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
  if t=='source':self.source=a.get('srcset')
  if t=='img' and a.get('src'):self.images.append(dict(a,modern=self.source));self.source=None
  if t=='script' and a.get('type')=='application/ld+json':self.in_json=True;self.buf=''
 def handle_endtag(self,t):
  if self.body and t not in ['picture','source']:self.tokens.append(('end',t))
  if t=='body':self.body=False
  if t=='title':self.in_title=False
  if t=='main':self.main=False
  if t in ['h1','h2','h3']:self.heading=None
  if t=='script' and self.in_json:self.jsons.append(json.loads(self.buf));self.in_json=False
 def handle_data(self,d):
  if self.body:self.tokens.append(('text',d))
  if self.heading:self.heading[1]+=d
  if self.in_title:self.title+=d
  if self.in_json:self.buf+=d
errors=[];checks=0
def check(ok,msg):
 global checks
 checks+=1
 if not ok:errors.append(msg)
def old(path):return subprocess.check_output(['git','show',PRE+':'+str(path.relative_to(ROOT))],cwd=ROOT)
def bytesize(path):return (ROOT/path.lstrip('/')).stat().st_size
def chosen(im,viewport,dpr):
 if im.get('modern'):return im['modern'].split()[0]
 if not im.get('srcset'):return im['src']
 size=None
 for term in im['sizes'].split(','):
  term=term.strip();m=re.match(r'\(max-width: (\d+)px\) (.+)',term)
  if m and viewport>int(m[1]):continue
  term=m[2] if m else term
  expression=term.replace('calc','').replace('100vw',str(viewport)).replace('px','')
  # Only generated numeric sizes, no arbitrary source execution.
  assert re.fullmatch(r'[\d .()+*/-]+',expression),expression
  size=eval(expression,{'__builtins__':{}});break
 choices=sorted((int(x.strip().split()[1][:-1]),x.strip().split()[0]) for x in im['srcset'].split(','))
 return next((p for w,p in choices if w>=size*dpr),choices[-1][1])
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
sm={e.find('s:loc',ns).text:e.findtext('s:lastmod',None,ns) for e in ET.parse(ROOT/'sitemap.xml').findall('s:url',ns)}
rows=[];allrefs=set();allids=set();titles=set();descs=set();socials=set()
for slug,config in SEO['pages'].items():
 route='/chance-darts/'+(slug+'/' if slug else '');url=BASE+route;f=ROOT/route.lstrip('/')/'index.html';raw=f.read_bytes();d=Doc(raw.decode());before=Doc(old(f).decode())
 check(d.tokens==before.tokens,route+' approved body content/structure changed beyond sizes and picture wrappers')
 check(d.lang=='en-GB',route+' language')
 check(d.canonical==[url],route+' canonical')
 check(d.title==config['title'] and d.title not in titles,route+' unique title');titles.add(d.title)
 desc=d.meta.get('description');check(desc==config['description'] and desc not in descs,route+' unique description');descs.add(desc)
 check(d.meta.get('og:title')==d.title and d.meta.get('twitter:title')==d.title,route+' social titles')
 check(d.meta.get('og:description')==desc and d.meta.get('twitter:description')==desc,route+' social descriptions')
 check(d.meta.get('og:url')==url,route+' social URL')
 im=config['image'];check(d.meta.get('og:image')==BASE+im['path']==d.meta.get('twitter:image'),route+' social image')
 check(im['path'] not in socials,route+' unique social image');socials.add(im['path'])
 actual=subprocess.check_output(['magick','identify','-format','%w %h',str(ROOT/im['path'].lstrip('/'))],text=True)
 check(actual==str(im['width'])+' '+str(im['height']),route+' social dimensions')
 check(bool(d.meta.get('og:image:alt')) and d.meta.get('og:image:alt')==d.meta.get('twitter:image:alt'),route+' social alt')
 check('noindex' not in str(d.meta).lower(),route+' production noindex')
 check('localhost' not in raw.decode() and '127.0.0.1' not in raw.decode(),route+' development URL')
 check(sum(h[0]==1 for h in d.headings)==1,route+' main H1')
 for i,h in enumerate(d.headings):check(i==0 or h[0]<=d.headings[i-1][0]+1,route+' main heading level skip')
 check(sm.get(url)==SEO['updated'],route+' sitemap lastmod')
 check(any(a.get('data-store') is not None or 'data-store' in a for a in d.links),route+' store conversion')
 graph=d.jsons[0]['@graph'];types=[x['@type'] for x in graph]
 check(all(t in types for t in ['Organization','WebSite','WebPage','BreadcrumbList']),route+' core schema')
 for x in graph:
  check(x.get('@id','').startswith(BASE+'/'),route+' stable schema ID');allids.add(x['@id'])
  check('review' not in x and 'aggregateRating' not in x,route+' no fabricated reviews')
  if x['@type']=='BreadcrumbList':
   crumbs=x['itemListElement'];check(len(crumbs)>=2 and [a['position'] for a in crumbs]==list(range(1,len(crumbs)+1)),route+' breadcrumbs positions')
   check(all(a['name'] and a['item'].startswith(BASE+'/') for a in crumbs),route+' breadcrumb values')
  if x['@type']=='SoftwareApplication':
   check(x['offers']['price']=='0' and x['offers']['priceCurrency']=='GBP' and x['downloadUrl'].startswith('https://apps.apple.com/gb/'),route+' verified free download offer')
 def refs(o):
  if isinstance(o,dict):
   if set(o)=={'@id'}:allrefs.add(o['@id'])
   for v in o.values():refs(v)
  elif isinstance(o,list):
   for v in o:refs(v)
 refs(graph)
 for image in d.images:
  check('alt' in image and image.get('width') and image.get('height'),route+' image accessibility')
  if image.get('fetchpriority')=='high':check(image.get('loading')!='lazy',route+' hero discoverable')
 related=re.search(r'<section class="related">(.*?)</section>',raw.decode(),re.S)
 context=Doc(related.group(1)).links if related else [a for a in d.links if a.get('class') in ['feature-row','text-link','button outline']]
 performance={}
 for name,vp,dpr in [('mobile',390,2),('desktop',1440,1)]:
  paths=set(chosen(i,vp,dpr) for i in d.images);early=set(chosen(i,vp,dpr) for i in d.images if i.get('loading')!='lazy')
  performance[name]={'viewport_css_px':vp,'dpr':dpr,'method':'Static resource-selection estimate, not browser requests/timings; browser may choose other candidates.','all_embedded_image_bytes':sum(bytesize(p) for p in paths),'eager_image_bytes':sum(bytesize(p) for p in early),'selected_images':sorted(paths),'eager_images':sorted(early),'lcp_ms':None,'inp_ms':None,'cls':None}
 rows.append({'page':slug or 'overview','production_url':url,'primary_intent':config['intent'],'target_phrases':config['phrases'],'title':d.title,'meta_description':desc,'h1':next(h[1] for h in d.headings if h[0]==1),'headings':d.headings,'canonical':url,'structured_data':types,'schema_ids':[x['@id'] for x in graph],'rich_results':'Breadcrumb property requirements checked locally; Google tool/rendering unverified.'+(' Software App rich result requirements not met: no genuine visible rating/review; none fabricated.' if 'SoftwareApplication' in types else ''),'og_image':BASE+im['path'],'og_image_alt':im['alt'],'og_image_dimensions':str(im['width'])+'×'+str(im['height']),'social_note':config['social_note'],'sitemap_inclusion':True,'lastmod':sm[url],'internal_link_coverage':{'directory_targets':len({a.get('href') for a in d.links if a.get('href','').startswith('/chance-darts/') and a.get('href','').endswith('/')}),'contextual_targets':sorted({a['href'] for a in context if a.get('href')})},'image_accessibility':'All static images have alt and dimensions; decorative logos have empty alt. Hero image eager; suitable lower images lazy. Full-resolution viewer links preserved.','html_bytes':len(raw),'html_gzip_bytes':len(gzip.compress(raw,mtime=0)),'performance':performance,'indexability_readiness':'Static production markup ready; preview deliberately noindex. New public feature URLs remain pending deployment.','limitations':['Browser mobile/desktop/interaction validation unavailable.','No Lighthouse, field CWV or search-index coverage data.','Live canonical selection, indexation and social preview rendering require post-deployment checks.']})
check(allrefs.issubset(allids),'Schema references resolve across site')
for rel in ['chance-darts/chance-darts.css','chance-darts/chance-darts.js','tools/microsite/content.py','tools/microsite/release.json']:
 f=ROOT/rel;check(f.read_bytes()==old(f),'Approved asset/copy changed: '+rel)
watch=json.loads((ROOT/'tools/microsite/watch-images.json').read_text())
for im in watch:
 f=ROOT/'assets/screenshots/chance-darts/watch'/im['file'];check(f.read_bytes()==old(f),'Original Watch PNG changed '+im['file'])
original=ET.fromstring(old(ROOT/'sitemap.xml'))
for e in original.findall('s:url',ns):
 u=e.find('s:loc',ns).text
 if '/chance-darts/' not in u:
  current=next(x for x in ET.parse(ROOT/'sitemap.xml').findall('s:url',ns) if x.find('s:loc',ns).text==u)
  check(ET.tostring(e)==ET.tostring(current),'Unrelated sitemap entry changed '+u)
result={'status':'FAIL' if errors else 'PASS','checks':checks,'errors':errors,'preserved_approved_body':True if not errors else 'See checks','pages':rows,'shared_resources':{}}
for rel in ['chance-darts/chance-darts.css','chance-darts/chance-darts.js']:
 data=(ROOT/rel).read_bytes();result['shared_resources'][rel]={'bytes':len(data),'gzip_bytes':len(gzip.compress(data,mtime=0)),'brotli_bytes':len(subprocess.check_output(['brotli','-c'],input=data)),'sha256':hashlib.sha256(data).hexdigest()}
result['measurement_limits']='No browser execution or throttling. Byte counts and compression are measured locally; responsive resource selection is estimated. Compression is potential, not an assertion about production response encoding. No Core Web Vitals certification.'
print(json.dumps(result,indent=2,ensure_ascii=False))
raise SystemExit(bool(errors))
