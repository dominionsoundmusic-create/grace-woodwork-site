
import {createRequire as ___nfyCreateRequire} from "module";
import {fileURLToPath as ___nfyFileURLToPath} from "url";
import {dirname as ___nfyPathDirname} from "path";
let __filename=___nfyFileURLToPath(import.meta.url);
let __dirname=___nfyPathDirname(___nfyFileURLToPath(import.meta.url));
let require=___nfyCreateRequire(import.meta.url);


// netlify/functions/shop-auth.mjs
import { getStore } from "@netlify/blobs";
import { createHash, randomBytes, timingSafeEqual } from "node:crypto";
var PRESET = "grace-shop";
function hash(password, salt) {
  return createHash("sha256").update(salt + "|" + password).digest("hex");
}
function same(a, b) {
  const x = Buffer.from(String(a));
  const y = Buffer.from(String(b));
  return x.length === y.length && timingSafeEqual(x, y);
}
var json = (body, status = 200) => new Response(JSON.stringify(body), {
  status,
  headers: { "Content-Type": "application/json", "Cache-Control": "no-store" }
});
var shop_auth_default = async (req) => {
  if (req.method !== "POST")
    return json({ error: "POST only" }, 405);
  const store = getStore("grace-shop-auth");
  let body;
  try {
    body = await req.json();
  } catch {
    return json({ error: "bad request" }, 400);
  }
  const action = body.action;
  const record = await store.get("password", { type: "json" });
  if (action === "status") {
    return json({ isSet: !!record });
  }
  if (action === "set") {
    if (record)
      return json({ error: "A password is already set. Use change instead." }, 409);
    const pw = String(body.password || "");
    if (pw.length < 4)
      return json({ error: "Pick at least 4 characters." }, 400);
    const salt = randomBytes(16).toString("hex");
    await store.setJSON("password", { salt, hash: hash(pw, salt), set: Date.now() });
    return json({ ok: true, preset: PRESET });
  }
  if (action === "check") {
    if (!record)
      return json({ error: "No password set yet." }, 409);
    const pw = String(body.password || "");
    if (!same(hash(pw, record.salt), record.hash)) {
      await new Promise((r) => setTimeout(r, 600));
      return json({ ok: false }, 401);
    }
    return json({ ok: true, preset: PRESET });
  }
  if (action === "change") {
    if (!record)
      return json({ error: "No password set yet." }, 409);
    const cur = String(body.current || "");
    const next = String(body.next || "");
    if (!same(hash(cur, record.salt), record.hash)) {
      await new Promise((r) => setTimeout(r, 600));
      return json({ ok: false, error: "Current password is wrong." }, 401);
    }
    if (next.length < 4)
      return json({ error: "Pick at least 4 characters." }, 400);
    const salt = randomBytes(16).toString("hex");
    await store.setJSON("password", { salt, hash: hash(next, salt), set: Date.now() });
    return json({ ok: true, preset: PRESET });
  }
  return json({ error: "unknown action" }, 400);
};
export {
  shop_auth_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsibmV0bGlmeS9mdW5jdGlvbnMvc2hvcC1hdXRoLm1qcyJdLAogICJzb3VyY2VzQ29udGVudCI6IFsiaW1wb3J0IHsgZ2V0U3RvcmUgfSBmcm9tICdAbmV0bGlmeS9ibG9icyc7XG5pbXBvcnQgeyBjcmVhdGVIYXNoLCByYW5kb21CeXRlcywgdGltaW5nU2FmZUVxdWFsIH0gZnJvbSAnbm9kZTpjcnlwdG8nO1xuXG4vLyBHcmFjZSdzIHNob3AtdXBsb2FkIHBhc3N3b3JkLiBTdG9yZWQgc2VydmVyLXNpZGUgaW4gTmV0bGlmeSBCbG9icywgbmV2ZXIgaW5cbi8vIHRoZSBwYWdlLiBIZSBzZXRzIGl0IG9uIGZpcnN0IHZpc2l0IGFuZCBjYW4gY2hhbmdlIGl0IGhpbXNlbGYgZnJvbSBhbnkgZGV2aWNlLlxuLy9cbi8vIFRoZSBnYXRlIGlzIHJlYWwgcmF0aGVyIHRoYW4gY29zbWV0aWM6IHRoZSBDbG91ZGluYXJ5IHVwbG9hZCBwcmVzZXQgaXMgTk9UIGluXG4vLyB0aGUgcGFnZSBzb3VyY2UuIFRoaXMgZnVuY3Rpb24gb25seSBoYW5kcyBpdCBiYWNrIG9uY2UgdGhlIHBhc3N3b3JkIGNoZWNrc1xuLy8gb3V0LCBzbyB3aXRob3V0IHRoZSBwYXNzd29yZCB5b3UgY2Fubm90IHVwbG9hZCBhbnl0aGluZy5cblxuY29uc3QgUFJFU0VUID0gJ2dyYWNlLXNob3AnO1xuXG5mdW5jdGlvbiBoYXNoKHBhc3N3b3JkLCBzYWx0KSB7XG4gIHJldHVybiBjcmVhdGVIYXNoKCdzaGEyNTYnKS51cGRhdGUoc2FsdCArICd8JyArIHBhc3N3b3JkKS5kaWdlc3QoJ2hleCcpO1xufVxuXG5mdW5jdGlvbiBzYW1lKGEsIGIpIHtcbiAgY29uc3QgeCA9IEJ1ZmZlci5mcm9tKFN0cmluZyhhKSk7XG4gIGNvbnN0IHkgPSBCdWZmZXIuZnJvbShTdHJpbmcoYikpO1xuICByZXR1cm4geC5sZW5ndGggPT09IHkubGVuZ3RoICYmIHRpbWluZ1NhZmVFcXVhbCh4LCB5KTtcbn1cblxuY29uc3QganNvbiA9IChib2R5LCBzdGF0dXMgPSAyMDApID0+XG4gIG5ldyBSZXNwb25zZShKU09OLnN0cmluZ2lmeShib2R5KSwge1xuICAgIHN0YXR1cyxcbiAgICBoZWFkZXJzOiB7ICdDb250ZW50LVR5cGUnOiAnYXBwbGljYXRpb24vanNvbicsICdDYWNoZS1Db250cm9sJzogJ25vLXN0b3JlJyB9XG4gIH0pO1xuXG5leHBvcnQgZGVmYXVsdCBhc3luYyAocmVxKSA9PiB7XG4gIGlmIChyZXEubWV0aG9kICE9PSAnUE9TVCcpIHJldHVybiBqc29uKHsgZXJyb3I6ICdQT1NUIG9ubHknIH0sIDQwNSk7XG5cbiAgY29uc3Qgc3RvcmUgPSBnZXRTdG9yZSgnZ3JhY2Utc2hvcC1hdXRoJyk7XG4gIGxldCBib2R5O1xuICB0cnkgeyBib2R5ID0gYXdhaXQgcmVxLmpzb24oKTsgfSBjYXRjaCB7IHJldHVybiBqc29uKHsgZXJyb3I6ICdiYWQgcmVxdWVzdCcgfSwgNDAwKTsgfVxuXG4gIGNvbnN0IGFjdGlvbiA9IGJvZHkuYWN0aW9uO1xuICBjb25zdCByZWNvcmQgPSBhd2FpdCBzdG9yZS5nZXQoJ3Bhc3N3b3JkJywgeyB0eXBlOiAnanNvbicgfSk7XG5cbiAgLy8gSXMgYSBwYXNzd29yZCBzZXQgeWV0P1xuICBpZiAoYWN0aW9uID09PSAnc3RhdHVzJykge1xuICAgIHJldHVybiBqc29uKHsgaXNTZXQ6ICEhcmVjb3JkIH0pO1xuICB9XG5cbiAgLy8gRmlyc3QtcnVuOiBjaG9vc2UgYSBwYXNzd29yZC4gT25seSBhbGxvd2VkIHdoaWxlIG5vbmUgZXhpc3RzLlxuICBpZiAoYWN0aW9uID09PSAnc2V0Jykge1xuICAgIGlmIChyZWNvcmQpIHJldHVybiBqc29uKHsgZXJyb3I6ICdBIHBhc3N3b3JkIGlzIGFscmVhZHkgc2V0LiBVc2UgY2hhbmdlIGluc3RlYWQuJyB9LCA0MDkpO1xuICAgIGNvbnN0IHB3ID0gU3RyaW5nKGJvZHkucGFzc3dvcmQgfHwgJycpO1xuICAgIGlmIChwdy5sZW5ndGggPCA0KSByZXR1cm4ganNvbih7IGVycm9yOiAnUGljayBhdCBsZWFzdCA0IGNoYXJhY3RlcnMuJyB9LCA0MDApO1xuICAgIGNvbnN0IHNhbHQgPSByYW5kb21CeXRlcygxNikudG9TdHJpbmcoJ2hleCcpO1xuICAgIGF3YWl0IHN0b3JlLnNldEpTT04oJ3Bhc3N3b3JkJywgeyBzYWx0LCBoYXNoOiBoYXNoKHB3LCBzYWx0KSwgc2V0OiBEYXRlLm5vdygpIH0pO1xuICAgIHJldHVybiBqc29uKHsgb2s6IHRydWUsIHByZXNldDogUFJFU0VUIH0pO1xuICB9XG5cbiAgLy8gTm9ybWFsIHNpZ24taW4uXG4gIGlmIChhY3Rpb24gPT09ICdjaGVjaycpIHtcbiAgICBpZiAoIXJlY29yZCkgcmV0dXJuIGpzb24oeyBlcnJvcjogJ05vIHBhc3N3b3JkIHNldCB5ZXQuJyB9LCA0MDkpO1xuICAgIGNvbnN0IHB3ID0gU3RyaW5nKGJvZHkucGFzc3dvcmQgfHwgJycpO1xuICAgIGlmICghc2FtZShoYXNoKHB3LCByZWNvcmQuc2FsdCksIHJlY29yZC5oYXNoKSkge1xuICAgICAgYXdhaXQgbmV3IFByb21pc2UociA9PiBzZXRUaW1lb3V0KHIsIDYwMCkpOyAvLyBzbG93IGRvd24gZ3Vlc3NpbmdcbiAgICAgIHJldHVybiBqc29uKHsgb2s6IGZhbHNlIH0sIDQwMSk7XG4gICAgfVxuICAgIHJldHVybiBqc29uKHsgb2s6IHRydWUsIHByZXNldDogUFJFU0VUIH0pO1xuICB9XG5cbiAgLy8gQ2hhbmdlIGl0LiBSZXF1aXJlcyB0aGUgY3VycmVudCBvbmUuXG4gIGlmIChhY3Rpb24gPT09ICdjaGFuZ2UnKSB7XG4gICAgaWYgKCFyZWNvcmQpIHJldHVybiBqc29uKHsgZXJyb3I6ICdObyBwYXNzd29yZCBzZXQgeWV0LicgfSwgNDA5KTtcbiAgICBjb25zdCBjdXIgPSBTdHJpbmcoYm9keS5jdXJyZW50IHx8ICcnKTtcbiAgICBjb25zdCBuZXh0ID0gU3RyaW5nKGJvZHkubmV4dCB8fCAnJyk7XG4gICAgaWYgKCFzYW1lKGhhc2goY3VyLCByZWNvcmQuc2FsdCksIHJlY29yZC5oYXNoKSkge1xuICAgICAgYXdhaXQgbmV3IFByb21pc2UociA9PiBzZXRUaW1lb3V0KHIsIDYwMCkpO1xuICAgICAgcmV0dXJuIGpzb24oeyBvazogZmFsc2UsIGVycm9yOiAnQ3VycmVudCBwYXNzd29yZCBpcyB3cm9uZy4nIH0sIDQwMSk7XG4gICAgfVxuICAgIGlmIChuZXh0Lmxlbmd0aCA8IDQpIHJldHVybiBqc29uKHsgZXJyb3I6ICdQaWNrIGF0IGxlYXN0IDQgY2hhcmFjdGVycy4nIH0sIDQwMCk7XG4gICAgY29uc3Qgc2FsdCA9IHJhbmRvbUJ5dGVzKDE2KS50b1N0cmluZygnaGV4Jyk7XG4gICAgYXdhaXQgc3RvcmUuc2V0SlNPTigncGFzc3dvcmQnLCB7IHNhbHQsIGhhc2g6IGhhc2gobmV4dCwgc2FsdCksIHNldDogRGF0ZS5ub3coKSB9KTtcbiAgICByZXR1cm4ganNvbih7IG9rOiB0cnVlLCBwcmVzZXQ6IFBSRVNFVCB9KTtcbiAgfVxuXG4gIHJldHVybiBqc29uKHsgZXJyb3I6ICd1bmtub3duIGFjdGlvbicgfSwgNDAwKTtcbn07XG4iXSwKICAibWFwcGluZ3MiOiAiOzs7Ozs7Ozs7O0FBQUEsU0FBUyxnQkFBZ0I7QUFDekIsU0FBUyxZQUFZLGFBQWEsdUJBQXVCO0FBU3pELElBQU0sU0FBUztBQUVmLFNBQVMsS0FBSyxVQUFVLE1BQU07QUFDNUIsU0FBTyxXQUFXLFFBQVEsRUFBRSxPQUFPLE9BQU8sTUFBTSxRQUFRLEVBQUUsT0FBTyxLQUFLO0FBQ3hFO0FBRUEsU0FBUyxLQUFLLEdBQUcsR0FBRztBQUNsQixRQUFNLElBQUksT0FBTyxLQUFLLE9BQU8sQ0FBQyxDQUFDO0FBQy9CLFFBQU0sSUFBSSxPQUFPLEtBQUssT0FBTyxDQUFDLENBQUM7QUFDL0IsU0FBTyxFQUFFLFdBQVcsRUFBRSxVQUFVLGdCQUFnQixHQUFHLENBQUM7QUFDdEQ7QUFFQSxJQUFNLE9BQU8sQ0FBQyxNQUFNLFNBQVMsUUFDM0IsSUFBSSxT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
