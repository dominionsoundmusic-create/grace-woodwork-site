import { getStore } from '@netlify/blobs';
import { createHash, randomBytes, timingSafeEqual } from 'node:crypto';

// Grace's shop-upload password. Stored server-side in Netlify Blobs, never in
// the page. He sets it on first visit and can change it himself from any device.
//
// The gate is real rather than cosmetic: the Cloudinary upload preset is NOT in
// the page source. This function only hands it back once the password checks
// out, so without the password you cannot upload anything.

const PRESET = 'grace-shop';

function hash(password, salt) {
  return createHash('sha256').update(salt + '|' + password).digest('hex');
}

function same(a, b) {
  const x = Buffer.from(String(a));
  const y = Buffer.from(String(b));
  return x.length === y.length && timingSafeEqual(x, y);
}

const json = (body, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' }
  });

export default async (req) => {
  if (req.method !== 'POST') return json({ error: 'POST only' }, 405);

  const store = getStore('grace-shop-auth');
  let body;
  try { body = await req.json(); } catch { return json({ error: 'bad request' }, 400); }

  const action = body.action;
  const record = await store.get('password', { type: 'json' });

  // Is a password set yet?
  if (action === 'status') {
    return json({ isSet: !!record });
  }

  // First-run: choose a password. Only allowed while none exists.
  if (action === 'set') {
    if (record) return json({ error: 'A password is already set. Use change instead.' }, 409);
    const pw = String(body.password || '');
    if (pw.length < 4) return json({ error: 'Pick at least 4 characters.' }, 400);
    const salt = randomBytes(16).toString('hex');
    await store.setJSON('password', { salt, hash: hash(pw, salt), set: Date.now() });
    return json({ ok: true, preset: PRESET });
  }

  // Normal sign-in.
  if (action === 'check') {
    if (!record) return json({ error: 'No password set yet.' }, 409);
    const pw = String(body.password || '');
    if (!same(hash(pw, record.salt), record.hash)) {
      await new Promise(r => setTimeout(r, 600)); // slow down guessing
      return json({ ok: false }, 401);
    }
    return json({ ok: true, preset: PRESET });
  }

  // Change it. Requires the current one.
  if (action === 'change') {
    if (!record) return json({ error: 'No password set yet.' }, 409);
    const cur = String(body.current || '');
    const next = String(body.next || '');
    if (!same(hash(cur, record.salt), record.hash)) {
      await new Promise(r => setTimeout(r, 600));
      return json({ ok: false, error: 'Current password is wrong.' }, 401);
    }
    if (next.length < 4) return json({ error: 'Pick at least 4 characters.' }, 400);
    const salt = randomBytes(16).toString('hex');
    await store.setJSON('password', { salt, hash: hash(next, salt), set: Date.now() });
    return json({ ok: true, preset: PRESET });
  }

  return json({ error: 'unknown action' }, 400);
};
