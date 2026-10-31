'use strict';
// True Part Fabrication checkout server.
// Creates Stripe Checkout sessions for priced, fit-confirmed parts.
// Prices come ONLY from prices.json on this server (written by the site build),
// never from the browser. Stays closed (503) until the Stripe keys are set and
// ENABLE_CHECKOUT=true. See README.md.

const http = require('http');
const fs = require('fs');
const path = require('path');

function loadPrices(file) {
  const p = JSON.parse(fs.readFileSync(file || path.join(__dirname, 'prices.json'), 'utf8'));
  if (!p || typeof p.items !== 'object' || !Array.isArray(p.ship)) throw new Error('prices.json is not valid');
  return p;
}

function config(env) {
  const site = (env.SITE_URL || '').replace(/\/+$/, '');
  const extra = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim().replace(/\/+$/, '')).filter(Boolean);
  let origin = '';
  try { origin = site ? new URL(site).origin : ''; } catch (e) { origin = ''; }
  return {
    site,
    origins: [origin, ...extra].filter(Boolean),
    secretKey: env.STRIPE_SECRET_KEY || '',
    webhookSecret: env.STRIPE_WEBHOOK_SECRET || '',
    enabled: String(env.ENABLE_CHECKOUT || '').toLowerCase() === 'true',
    autoTax: String(env.AUTOMATIC_TAX || '').toLowerCase() === 'true',
  };
}

// Turn [{slug, qty}] into priced lines, or throw a message safe to show the customer.
function priceCart(prices, items) {
  if (!Array.isArray(items) || items.length === 0) throw userError('Your cart has no parts that can be bought online.');
  if (items.length > 50) throw userError('Too many different parts in one order. Split it, or send a quote request.');
  const max = prices.maxQty || 25;
  const merged = new Map();
  for (const x of items) {
    const slug = x && typeof x.slug === 'string' ? x.slug : '';
    const qty = Number(x && x.qty);
    const p = prices.items[slug];
    if (!p) throw userError('One of the parts in your cart can no longer be bought online. Refresh your cart and try again.');
    if (!Number.isInteger(qty) || qty < 1 || qty > max) throw userError(`Quantities must be between 1 and ${max}. For more, send a quote request.`);
    merged.set(slug, Math.min(max, (merged.get(slug) || 0) + qty));
  }
  const rank = { small: 0, medium: 1, large: 2 };
  let ship = null;
  const lines = [];
  let subtotal = 0;
  for (const [slug, qty] of merged) {
    const p = prices.items[slug];
    if (!Number.isInteger(p.cents) || p.cents < 50) throw userError('A price in the cart is not set correctly. Please send a quote request instead.');
    lines.push({ slug, name: p.name, ref: p.ref || '', unit: p.cents, qty, total: p.cents * qty });
    subtotal += p.cents * qty;
    const tier = prices.ship.find(s => s.id === p.ship) || prices.ship[prices.ship.length - 1];
    if (!ship || rank[tier.id] > rank[ship.id]) ship = tier;
  }
  return { lines, subtotal, shipping: ship, pickup: prices.pickup || null, total: subtotal + (ship ? ship.cents : 0) };
}

function userError(msg) { const e = new Error(msg); e.user = true; return e; }

function readBody(req, limit) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    req.on('data', c => { size += c.length; if (size > limit) { reject(userError('Request too large.')); req.destroy(); } else chunks.push(c); });
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

function createServer(opts = {}) {
  const env = opts.env || process.env;
  const cfg = config(env);
  const prices = opts.prices || loadPrices(opts.pricesFile);
  let stripe = opts.stripe || null;
  if (!stripe && cfg.secretKey) stripe = require('stripe')(cfg.secretKey);
  const log = opts.log || console.log;
  const hits = new Map(); // simple per-IP rate limit for checkout

  function ready() { return cfg.enabled && !!stripe && !!cfg.site; }

  function send(res, status, obj, origin) {
    const h = { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' };
    if (origin && cfg.origins.includes(origin)) { h['Access-Control-Allow-Origin'] = origin; h['Vary'] = 'Origin'; }
    res.writeHead(status, h);
    res.end(JSON.stringify(obj));
  }

  function limited(ip) {
    const now = Date.now(), w = hits.get(ip) || [];
    const recent = w.filter(t => now - t < 60000);
    recent.push(now);
    hits.set(ip, recent);
    return recent.length > 20;
  }

  return http.createServer(async (req, res) => {
    const origin = req.headers.origin || '';
    const url = new URL(req.url, 'http://x');
    try {
      if (req.method === 'OPTIONS') {
        const h = { 'Access-Control-Allow-Methods': 'POST, GET, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '600' };
        if (cfg.origins.includes(origin)) { h['Access-Control-Allow-Origin'] = origin; h['Vary'] = 'Origin'; }
        res.writeHead(204, h); return res.end();
      }
      if (req.method === 'GET' && (url.pathname === '/api/health' || url.pathname === '/')) {
        return send(res, 200, { ok: true, checkout: ready() ? 'open' : 'closed', parts: Object.keys(prices.items).length }, origin);
      }
      if (req.method === 'POST' && url.pathname === '/api/quote-total') {
        const body = JSON.parse((await readBody(req, 20000)).toString('utf8') || '{}');
        return send(res, 200, priceCart(prices, body.items), origin);
      }
      if (req.method === 'POST' && url.pathname === '/api/checkout') {
        if (origin && cfg.origins.length && !cfg.origins.includes(origin)) return send(res, 403, { error: 'Not allowed.' }, origin);
        if (!ready()) return send(res, 503, { error: "Online checkout isn't open yet. Send your cart as a quote request and we'll reply with a total." }, origin);
        const ip = (req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').split(',')[0].trim();
        if (limited(ip)) return send(res, 429, { error: 'Too many tries. Wait a minute and try again.' }, origin);
        const body = JSON.parse((await readBody(req, 20000)).toString('utf8') || '{}');
        const cart = priceCart(prices, body.items);
        const shipping_options = [{ shipping_rate_data: { type: 'fixed_amount', display_name: 'USPS shipping', fixed_amount: { amount: cart.shipping.cents, currency: 'usd' },
          delivery_estimate: { minimum: { unit: 'business_day', value: 5 }, maximum: { unit: 'business_day', value: 12 } } } }];
        if (cart.pickup) shipping_options.push({ shipping_rate_data: { type: 'fixed_amount', display_name: cart.pickup.label, fixed_amount: { amount: cart.pickup.cents, currency: 'usd' } } });
        const session = await stripe.checkout.sessions.create({
          mode: 'payment',
          line_items: cart.lines.map(l => ({ quantity: l.qty, price_data: { currency: 'usd', unit_amount: l.unit,
            product_data: { name: l.name, description: (l.ref ? l.ref + '. ' : '') + 'Compatible aftermarket part, made to order in Modesto, CA.', metadata: { slug: l.slug } } } })),
          shipping_address_collection: { allowed_countries: ['US'] },
          shipping_options,
          phone_number_collection: { enabled: true },
          billing_address_collection: 'auto',
          automatic_tax: { enabled: cfg.autoTax },
          success_url: cfg.site + '/order/success/?session_id={CHECKOUT_SESSION_ID}',
          cancel_url: cfg.site + '/order/cancelled/',
          metadata: { source: 'website', parts: cart.lines.map(l => l.slug + 'x' + l.qty).join(',').slice(0, 490) },
        });
        return send(res, 200, { url: session.url }, origin);
      }
      if (req.method === 'POST' && url.pathname === '/api/webhook') {
        if (!stripe || !cfg.webhookSecret) return send(res, 503, { error: 'Webhook not configured.' });
        const raw = await readBody(req, 1000000);
        let event;
        try { event = stripe.webhooks.constructEvent(raw, req.headers['stripe-signature'] || '', cfg.webhookSecret); }
        catch (e) { return send(res, 400, { error: 'Bad signature.' }); }
        if (event.type === 'checkout.session.completed') {
          const s = event.data.object;
          log(`ORDER PAID ${s.id} total=${(s.amount_total / 100).toFixed(2)} ${s.currency} parts=${(s.metadata && s.metadata.parts) || ''}`);
        }
        return send(res, 200, { received: true });
      }
      send(res, 404, { error: 'Not found.' }, origin);
    } catch (e) {
      if (e.user) return send(res, 400, { error: e.message }, origin);
      if (e instanceof SyntaxError) return send(res, 400, { error: 'Bad request.' }, origin);
      log('ERROR ' + (e && e.message));
      send(res, 502, { error: 'Checkout could not be started. Try again, or send your cart as a quote request.' }, origin);
    }
  });
}

module.exports = { createServer, priceCart, loadPrices, config };

if (require.main === module) {
  const port = Number(process.env.PORT || 10000);
  const srv = createServer();
  srv.listen(port, () => console.log(`checkout server on :${port}`));
}
