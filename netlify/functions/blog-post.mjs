import { getStore } from '@netlify/blobs';
import { createHash, timingSafeEqual } from 'node:crypto';
import { postHtml, buildIndex, buildSitemap, titlesFromIndex, undash, esc } from '../blog-render.mjs';

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
  const html = postHtml({ title, body, photo: b.photo || '', dateStr, name, stamp });

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

    let titles = {};
    try {
      const ix = await gh('GET', `/repos/${OWNER}/${REPO}/contents/${BLOG}/index.html`, null, TOKEN);
      titles = titlesFromIndex(Buffer.from(ix.content, 'base64').toString('utf-8'));
    } catch { titles = {}; }
    titles[name] = esc(undash(title));

    let sitemap = '';
    try {
      const sm = await gh('GET', `/repos/${OWNER}/${REPO}/contents/sitemap.xml`, null, TOKEN);
      sitemap = Buffer.from(sm.content, 'base64').toString('utf-8');
    } catch { sitemap = ''; }

    const files = [
      { path, content: html },
      { path: `${BLOG}/index.html`, content: buildIndex(all, titles) },
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
