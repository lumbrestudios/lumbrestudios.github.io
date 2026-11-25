#!/usr/bin/env python3
"""Dependency-free checks against generated files, links, metadata and baseline."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import json, subprocess, xml.etree.ElementTree as ET, hashlib, sys
ROOT=Path(__file__).resolve().parents[2]
BASE='14d6f7ae1923dcfe4b337bd1108debd716b2be76'
class Document(HTMLParser):
 def __init__(self,text):
  super().__init__(convert_charrefs=True);self.ids=[];self.links=[];self.assets=[];self.meta={};self.h1=0;self.title='';self.in_title=False;self.jsons=[];self.in_json=False;self.current_json='';self.images=[];self.canonicals=[];self.scripts=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id'in a:self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if tag=='title':self.in_title=True
  if tag=='a' and 'href'in a:self.links.append(a['href'])
  if tag=='meta':self.meta[a.get('name',a.get('property'))]=a.get('content')
  if tag=='link':
   if a.get('rel')=='canonical':self.canonicals.append(a.get('href'))
   elif a.get('href','').startswith('/'):self.assets.append(a['href'])
  if tag=='img' and 'src' in a:
   self.images.append(a);self.assets.append(a['src'])
   self.assets.extend(s.strip().split(' ')[0] for s in a.get('srcset','').split(',') if s.strip())
  if tag=='script':
   if 'src'in a:self.assets.append(a['src']);self.scripts.append(a['src'])
   self.in_json=a.get('type')=='application/ld+json';self.current_json=''
 def handle_endtag(self,tag):
  if tag=='title':self.in_title=False
  if tag=='script' and self.in_json:self.jsons.append(json.loads(self.current_json));self.in_json=False
 def handle_data(self,data):
  if self.in_title:self.title+=data
  if self.in_json:self.current_json+=data
errors=[];checks=0

def check(ok,message):
 global checks
 checks+=1
 if not ok:errors.append(message)
files=sorted((ROOT/'chance-darts').rglob('index.html'))
check(len(files)==15,'Exactly 15 product pages required')
docs={p:Document(p.read_text()) for p in files}; titles=set(); descriptions=set();assets=set();externals=set()
for file,d in docs.items():
 rel='/'+str(file.relative_to(ROOT)).removesuffix('index.html');label=rel
 check(d.h1==1,label+' requires one h1')
 check(len(d.ids)==len(set(d.ids)),label+' duplicate IDs')
 check(d.title not in titles,label+' duplicate title');titles.add(d.title)
 desc=d.meta.get('description');check(bool(desc),label+' missing description');check(desc not in descriptions,label+' duplicate description');descriptions.add(desc)
 check(d.canonicals==['https://lumbrestudios.app'+rel],label+' incorrect canonical')
 for k in ['og:title','og:description','og:url','og:image','og:image:alt','twitter:card']:
  check(bool(d.meta.get(k)),label+' missing '+k)
 check(d.meta.get('og:url')==d.canonicals[0],label+' OG URL differs')
 check(len(d.jsons)==1,label+' missing structured data')
 for record in d.jsons[0]:
  check(record.get('@context')=='https://schema.org',label+' invalid schema context')
  check(record.get('@type') in ['WebPage','BreadcrumbList','MobileApplication'],label+' unexpected schema type')
  check('aggregateRating' not in record and 'review' not in record,label+' unsupported reviews')
 for img in d.images:
  check('alt'in img,label+' missing alt');check('width'in img and 'height'in img,label+' missing image dimensions')
 for asset in d.assets:
  check((ROOT/asset.lstrip('/')).is_file(),label+' missing asset '+asset);assets.add(asset)
 check(d.scripts==['/chance-darts/chance-darts.js'],label+' unexpected script dependency')
 for href in d.links:
  parsed=urlparse(href)
  if parsed.scheme in ['http','https','mailto']:
   externals.add(href);continue
  path=(ROOT/parsed.path.lstrip('/')) if parsed.path.startswith('/') else file.parent/parsed.path
  if path.is_dir():path=path/'index.html'
  check(path.exists(),label+' broken link '+href)
  if parsed.fragment and path.is_file() and path.suffix=='.html':
   target=docs.get(path) or Document(path.read_text());check(unquote(parsed.fragment) in target.ids,label+' broken anchor '+href)
 check('/chance-darts-privacy.html' in d.links,label+' privacy missing')
 check('/support.html'in d.links,label+' support missing')
 for other in files:
  target='/'+str(other.relative_to(ROOT)).removesuffix('index.html')
  check(target in d.links,label+' no crawlable navigation to '+target)
# All existing tracked non-product files remain byte-identical except sitemap.
tracked=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE],cwd=ROOT,text=True).splitlines(); preserved=0
for name in tracked:
 if name.startswith('chance-darts/') or name=='sitemap.xml':continue
 old=subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)
 check((ROOT/name).is_file() and (ROOT/name).read_bytes()==old,'Protected website file changed: '+name);preserved+=1
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
oldxml=subprocess.check_output(['git','show',BASE+':sitemap.xml'],cwd=ROOT)
oldurls={x.text for x in ET.fromstring(oldxml).findall('s:url/s:loc',ns)}
newurls=[x.text for x in ET.parse(ROOT/'sitemap.xml').findall('s:url/s:loc',ns)]
check(len(newurls)==len(set(newurls)),'Duplicate sitemap URLs');check(oldurls.issubset(set(newurls)),'Old sitemap URLs removed')
for f in files:check('https://lumbrestudios.app/'+str(f.relative_to(ROOT)).removesuffix('index.html') in newurls,'Missing sitemap page')
css=(ROOT/'chance-darts/chance-darts.css').read_text();js=(ROOT/'chance-darts/chance-darts.js').read_text()
check('prefers-reduced-motion'in css,'Reduced motion missing');check(':focus-visible'in css,'Focus outline missing')
check(not any(term in js for term in ['fetch(', 'localStorage','sessionStorage','document.cookie','XMLHttpRequest']),'Unexpected tracking or network storage code')
subprocess.run(['node','--check',str(ROOT/'chance-darts/chance-darts.js')],check=True)
result={'status':'FAIL' if errors else 'PASS','checks':checks,'product_pages':len(files),'preserved_files':preserved,'unique_assets':len(assets),'sitemap_urls':len(newurls),'css_bytes':len(css.encode()),'js_bytes':len(js.encode()),'errors':errors,'external_links':sorted(externals),'limits':['Browser visual, keyboard, responsive overflow and interactive runtime QA unverified: embedded browser unavailable; Safari computer-use access not approved.','Structured-data JSON and asserted fields checked locally; no Google Rich Results certification.']}
print(json.dumps(result,indent=2))
sys.exit(bool(errors))
