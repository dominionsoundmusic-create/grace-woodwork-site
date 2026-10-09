// Page rendering for blog-post.mjs (Grace's /write.html publisher). Kept outside netlify/functions so
// Netlify does not treat it as a function; esbuild bundles it into blog-post.mjs. The local dry run
// (scripts/test_blog_writers.mjs) imports it too.
import { POST, INDEX, BUSINESS } from './blog-templates.mjs';

const DOMAIN = 'gracewoodworkkilgore.com';
const BLOG = 'blog';
export const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function titleFromSlug(name) {
  const s = name.replace(/\.html$/, '').replace(/-\d{10,}$/, '');
  return s.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

// The page templates are rendered by build.py from the site's own header, footer and styles, so a
// post published from /write.html looks exactly like the rest of the site. Only the %%TOKENS%% are
// filled in here. Keep this in step with render_post/render_index in .github/scripts/grace_blog.py.
const DEFAULT_HERO = '/images/hero-2.jpg';
const fill = (tpl, v) => Object.entries(v).reduce((t, [k, val]) => t.split('%%' + k + '%%').join(val), tpl);
const ld = o => JSON.stringify(o).replace(/<\//g, '<\\/');
export const undash = s => String(s).replace(/(\d)\s*[\u2013\u2014]\s*(\d)/g, '$1 to $2')
  .replace(/\s*[\u2013\u2014]\s*/g, ', ').replace(/,\s*,/g, ',').replace(/,\s*([.?!:;])/g, '$1');
const absUrl = p => (p || DEFAULT_HERO).startsWith('http') ? (p || DEFAULT_HERO) : `https://${DOMAIN}${p || DEFAULT_HERO}`;

function heroHtml(photo, alt) {
  const src = photo || DEFAULT_HERO;
  return `<!--post-photo:${esc(src)}--><img src="${esc(src)}" alt="${esc(alt)}" width="1600" height="900" fetchpriority="high" decoding="async">`;
}

export function postHtml({ title, body, photo, dateStr, name, stamp }) {
  title = undash(title);
  const paras = undash(body).split(/\n{2,}/).map(p => p.trim()).filter(Boolean)
    .map(p => '<p>' + esc(p).replace(/\n/g, '<br>') + '</p>').join('\n');
  const description = undash(String(body).replace(/\s+/g, ' ').trim()).slice(0, 150);
  const url = `https://${DOMAIN}/${BLOG}/${name}`;
  const graph = [BUSINESS,
    { '@type': 'BlogPosting', '@id': url + '#article', headline: title, description, image: absUrl(photo),
      datePublished: new Date(stamp).toISOString().slice(0, 10), author: { '@id': BUSINESS['@id'] },
      publisher: { '@id': BUSINESS['@id'] }, mainEntityOfPage: url, inLanguage: 'en-US' },
    { '@type': 'BreadcrumbList', itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Home', item: `https://${DOMAIN}/` },
      { '@type': 'ListItem', position: 2, name: 'Blog', item: `https://${DOMAIN}/${BLOG}/` },
      { '@type': 'ListItem', position: 3, name: title, item: url }] }];
  return fill(POST, {
    TITLE: esc(title) + ' | Grace Woodwork', DESCRIPTION: esc(description), CANONICAL: url, OG_IMAGE: absUrl(photo),
    JSONLD: ld({ '@context': 'https://schema.org', '@graph': graph }), HERO: heroHtml(photo, title),
    PRELOAD: `<link rel="preload" as="image" href="${esc(photo || DEFAULT_HERO)}" fetchpriority="high">`,
    H1: esc(title), DATE: esc(dateStr), BODY: paras, SOURCES: '<!--post-sources--><!--/post-sources-->'
  });
}

// Real post titles come from the current blog index (one request); a post missing from it falls
// back to a title made from its file name.
export function titlesFromIndex(indexHtml) {
  const map = {};
  for (const m of String(indexHtml || '').matchAll(/<a href="\/blog\/([^"]+\.html)">([^<]*)<\/a>/g)) {
    map[m[1]] = m[2];
  }
  return map;
}

export function buildIndex(files, titles = {}) {
  const items = files.map(n => {
    const ts = parseInt((n.match(/-(\d{10,})\.html$/) || [0, 0])[1], 10);
    const when = ts ? new Date(ts).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' }) : '';
    return `    <li><a href="/${BLOG}/${n}">${titles[n] || esc(titleFromSlug(n))}</a>${when ? `<span class="d">${when}</span>` : ''}</li>`;
  }).join('\n');
  const graph = [BUSINESS, { '@type': 'Blog', '@id': `https://${DOMAIN}/${BLOG}/#blog`, name: 'Grace Woodwork blog',
    url: `https://${DOMAIN}/${BLOG}/`, publisher: { '@id': BUSINESS['@id'] }, inLanguage: 'en-US' }];
  const n = files.length;
  return fill(INDEX, {
    TITLE: 'Blog: Furniture Repair and Woodwork Notes | Grace Woodwork',
    DESCRIPTION: 'Notes from the shop: furniture repair, refinishing and custom woodwork advice from Grace Woodwork in Kilgore, Texas.',
    JSONLD: ld({ '@context': 'https://schema.org', '@graph': graph }),
    HERO: heroHtml('/images/hero-6.jpg', 'Pine shelf units being built in the Grace Woodwork shop'),
    PRELOAD: '<link rel="preload" as="image" href="/images/hero-6.jpg" fetchpriority="high">',
    H1: 'From the shop',
    COUNT_TEXT: `${n} post${n === 1 ? '' : 's'} on restoration, repair and custom work, written in Kilgore, Texas.`,
    ITEMS: items
  });
}

export function buildSitemap(xml, files) {
  const today = new Date().toISOString().slice(0, 10);
  const base = `https://${DOMAIN}/${BLOG}/`;
  let out = xml && xml.includes('<urlset') ? xml
    : `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>`;
  out = out.replace(new RegExp(`\\s*<url>(?:(?!</url>)[\\s\\S])*?<loc>\\s*${base.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}[^<]*</loc>[\\s\\S]*?</url>`, 'g'), '');
  const block = [base, ...files.map(f => base + f)]
    .map(u => `  <url>\n    <loc>${u}</loc>\n    <lastmod>${today}</lastmod>\n    <changefreq>monthly</changefreq>\n  </url>`)
    .join('\n');
  return out.replace('</urlset>', block + '\n</urlset>');
}

