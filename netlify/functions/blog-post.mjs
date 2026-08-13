import { getStore } from '@netlify/blobs';
import { createHash, timingSafeEqual } from 'node:crypto';

// Lets Grace (or his wife) publish a blog post from the browser.
// Behind the same password as the shop upload page. The post is committed to
// the repo as a real HTML file so Google indexes it properly, and the blog
// index and sitemap are rebuilt in the SAME commit — one deploy, not three.

const OWNER = 'dominionsoundmusic-create';
const REPO = 'grace-woodwork-site';
const DOMAIN = 'gracewoodworkkilgore.com';
const BLOG = 'blog';

const json = (b, s = 200) => new Response(JSON.stringify(b), {
  status: s, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }
});

function hash(pw, salt) { return createHash('sha256').update(salt + '|' + pw).digest('hex'); }
function same(a, b) {
  const x = Buffer.from(String(a)), y = Buffer.from(String(b));
  return x.length === y.length && timingSafeEqual(x, y);
}
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const slugify = s => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60) || 'post';

const gh = async (method, path, body, token) => {
  const r = await fetch('https://api.github.com' + path, {
    method,
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'Content-Type': 'application/json',
      'User-Agent': 'grace-blog'
    },
    body: body ? JSON.stringify(body) : undefined
  });
  if (!r.ok) throw new Error(method + ' ' + path + ' -> ' + r.status + ' ' + (await r.text()).slice(0, 180));
  return r.json();
};

function titleFromSlug(name) {
  const s = name.replace(/\.html$/, '').replace(/-\d{10,}$/, '');
  return s.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function postHtml({ title, body, photo, dateStr }) {
  const paras = String(body).split(/\n{2,}/).map(p => p.trim()).filter(Boolean)
    .map(p => '<p>' + esc(p).replace(/\n/g, '<br>') + '</p>').join('\n      ');
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${esc(title)} | Grace Woodwork</title>
<meta name="description" content="${esc(String(body).replace(/\s+/g, ' ').slice(0, 150))}">
<link rel="canonical" href="https://${DOMAIN}/${BLOG}/__SLUG__">
<link rel="icon" href="/favicon.ico" sizes="any">
<style>
:root{--forest:#13261E;--ink:#0B1812;--pine:#EDF0EA;--brass:#C79045;--paper:#F5F8F3}
*{box-sizing:border-box}
body{margin:0;background:var(--pine);color:var(--forest);line-height:1.75;
     font-family:'Karla',system-ui,-apple-system,Arial,sans-serif;font-size:1.05rem}
header{background:var(--forest);padding:16px 24px}
header a{color:var(--brass);text-decoration:none;font-weight:700;font-size:1.1rem}
.wrap{max-width:74ch;margin:0 auto;padding:48px 24px 80px}
h1{font-family:Georgia,'Zilla Slab',serif;font-size:clamp(1.9rem,4vw,2.7rem);line-height:1.18;margin:0 0 10px}
.date{font-family:'Roboto Mono',monospace;font-size:.76rem;letter-spacing:.14em;text-transform:uppercase;color:#8F621E;margin-bottom:30px}
img.lead{width:100%;border-radius:4px;margin:0 0 30px}
p{margin:0 0 20px}
footer{border-top:1px solid rgba(19,38,30,.14);margin-top:46px;padding-top:24px;font-size:.95rem}
footer a{color:var(--forest)}
.cta{display:inline-block;margin-top:14px;background:var(--brass);color:var(--ink);
     text-decoration:none;padding:13px 26px;border-radius:3px;font-weight:700}
</style>
</head>
<body>
<header><a href="/">Grace Woodwork</a></header>
<article class="wrap">
  <h1>${esc(title)}</h1>
  <div class="date">${esc(dateStr)}</div>
  ${photo ? `<img class="lead" src="${esc(photo)}" alt="${esc(title)}">` : ''}
      ${paras}
  <footer>
    <p>Grace Woodwork restores and builds furniture in Kilgore, Texas.</p>
    <a class="cta" href="/#quote">Send a photo, get a quote</a><br>
    <p style="margin-top:18px"><a href="/${BLOG}/">← All posts</a></p>
  </footer>
</article>
</body>
</html>`;
}

function buildIndex(files) {
  const items = files.map(n => {
    const ts = parseInt((n.match(/-(\d{10,})\.html$/) || [0, 0])[1], 10);
    const when = ts ? new Date(ts).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) : '';
    return `    <li><a href="/${BLOG}/${n}">${titleFromSlug(n)}</a>${when ? `<span class="d">${when}</span>` : ''}</li>`;
  }).join('\n');
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Blog | Grace Woodwork</title>
<meta name="description" content="Notes from the shop — furniture restoration and custom woodwork in Kilgore, Texas.">
<link rel="canonical" href="https://${DOMAIN}/${BLOG}/">
<link rel="icon" href="/favicon.ico" sizes="any">
<style>
body{margin:0;background:#EDF0EA;color:#13261E;line-height:1.7;font-family:'Karla',system-ui,Arial,sans-serif}
header{background:#13261E;padding:16px 24px}
header a{color:#C79045;text-decoration:none;font-weight:700;font-size:1.1rem}
.wrap{max-width:800px;margin:0 auto;padding:46px 24px 80px}
h1{font-family:Georgia,serif;font-size:2rem;margin:0 0 6px}
.sub{color:#4a5a50;margin:0 0 28px}
ul{list-style:none;padding:0}
li{padding:16px 0;border-bottom:1px solid rgba(19,38,30,.12);display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
li a{color:#13261E;text-decoration:none;font-weight:600}
li a:hover{color:#8F621E}
.d{color:#7c8a80;font-size:.86rem;white-space:nowrap}
</style>
</head>
<body>
<header><a href="/">Grace Woodwork</a></header>
<div class="wrap">
  <h1>From the shop</h1>
  <p class="sub">${files.length} post${files.length === 1 ? '' : 's'} on restoration, repair and custom work.</p>
  <ul>
${items}
  </ul>
</div>
</body>
</html>`;
}

function buildSitemap(xml, files) {
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

export default async (req) => {
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);
  const TOKEN = process.env.GITHUB_TOKEN;
  if (!TOKEN) return json({ error: 'Publishing is not configured yet — GITHUB_TOKEN is missing.' }, 500);

  let b; try { b = await req.json(); } catch { return json({ error: 'bad request' }, 400); }

  const rec = await getStore('grace-shop-auth').get('password', { type: 'json' });
  if (!rec) return json({ error: 'No password set yet.' }, 409);
  if (!same(hash(String(b.password || ''), rec.salt), rec.hash)) {
    await new Promise(r => setTimeout(r, 600));
    return json({ ok: false, error: 'Wrong password.' }, 401);
  }

  const title = String(b.title || '').trim();
  const body = String(b.body || '').trim();
  if (title.length < 3) return json({ error: 'Give the post a title.' }, 400);
  if (body.length < 20) return json({ error: 'Write a bit more before publishing.' }, 400);

  const stamp = Date.now();
  const name = `${slugify(title)}-${stamp}.html`;
  const path = `${BLOG}/${name}`;
  const dateStr = new Date(stamp).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  const html = postHtml({ title, body, photo: b.photo || '', dateStr }).replace('__SLUG__', name);

  try {
    const ref = await gh('GET', `/repos/${OWNER}/${REPO}/git/ref/heads/main`, null, TOKEN);
    const head = ref.object.sha;
    const baseTree = (await gh('GET', `/repos/${OWNER}/${REPO}/git/commits/${head}`, null, TOKEN)).tree.sha;

    let existing = [];
    try {
      const list = await gh('GET', `/repos/${OWNER}/${REPO}/contents/${BLOG}`, null, TOKEN);
      existing = list.filter(f => f.name.endsWith('.html') && f.name !== 'index.html').map(f => f.name);
    } catch { existing = []; }
    const all = [name, ...existing.filter(n => n !== name)]
      .sort((a, z) => parseInt((z.match(/-(\d{10,})\.html$/) || [0, 0])[1], 10) - parseInt((a.match(/-(\d{10,})\.html$/) || [0, 0])[1], 10));

    let sitemap = '';
    try {
      const sm = await gh('GET', `/repos/${OWNER}/${REPO}/contents/sitemap.xml`, null, TOKEN);
      sitemap = Buffer.from(sm.content, 'base64').toString('utf-8');
    } catch { sitemap = ''; }

    const files = [
      { path, content: html },
      { path: `${BLOG}/index.html`, content: buildIndex(all) },
      { path: 'sitemap.xml', content: buildSitemap(sitemap, all) }
    ];
    const tree = [];
    for (const f of files) {
      const blob = await gh('POST', `/repos/${OWNER}/${REPO}/git/blobs`,
        { content: Buffer.from(f.content).toString('base64'), encoding: 'base64' }, TOKEN);
      tree.push({ path: f.path, mode: '100644', type: 'blob', sha: blob.sha });
    }
    const newTree = await gh('POST', `/repos/${OWNER}/${REPO}/git/trees`, { base_tree: baseTree, tree }, TOKEN);
    const commit = await gh('POST', `/repos/${OWNER}/${REPO}/git/commits`,
      { message: 'New post: ' + title, tree: newTree.sha, parents: [head] }, TOKEN);
    await gh('PATCH', `/repos/${OWNER}/${REPO}/git/refs/heads/main`, { sha: commit.sha }, TOKEN);

    return json({ ok: true, url: `https://${DOMAIN}/${BLOG}/${name}` });
  } catch (e) {
    return json({ error: 'Could not publish: ' + e.message }, 500);
  }
};
