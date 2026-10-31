'use strict';
const test = require('node:test');
const assert = require('node:assert');
const { createServer, priceCart } = require('./server');

const PRICES = { maxQty: 25, pickup: { label: 'Local pickup in Modesto', cents: 0 },
  ship: [{ id: 'small', label: 'Small part', cents: 400 }, { id: 'medium', label: 'Medium part', cents: 475 }, { id: 'large', label: 'Large part', cents: 550 }],
  items: { 'clip-a': { name: 'Clip A', ref: 'Replaces X 1', cents: 900, ship: 'small' }, 'sep-b': { name: 'Separator B', ref: 'Replaces Y 2', cents: 2400, ship: 'large' } } };
const ENV = { SITE_URL: 'https://example.test', ENABLE_CHECKOUT: 'true' };

function start(opts) {
  return new Promise(r => { const s = createServer({ prices: PRICES, log: () => {}, ...opts }); s.listen(0, () => r(s)); });
}
async function call(s, method, p, body, headers = {}) {
  const res = await fetch(`http://127.0.0.1:${s.address().port}${p}`, { method, headers: { 'Content-Type': 'application/json', ...headers }, body: body ? JSON.stringify(body) : undefined });
  return { status: res.status, json: await res.json().catch(() => null), headers: res.headers };
}

test('totals use server prices and the largest shipping tier', () => {
  const t = priceCart(PRICES, [{ slug: 'clip-a', qty: 2 }, { slug: 'sep-b', qty: 1 }, { slug: 'clip-a', qty: 1 }]);
  assert.equal(t.subtotal, 900 * 3 + 2400);
  assert.equal(t.shipping.cents, 550);
  assert.equal(t.total, 900 * 3 + 2400 + 550);
});

test('rejects unknown parts, bad quantities and empty carts', () => {
  assert.throws(() => priceCart(PRICES, [{ slug: 'nope', qty: 1 }]), /no longer be bought/);
  assert.throws(() => priceCart(PRICES, [{ slug: 'clip-a', qty: 0 }]), /between 1 and 25/);
  assert.throws(() => priceCart(PRICES, [{ slug: 'clip-a', qty: 1.5 }]), /between 1 and 25/);
  assert.throws(() => priceCart(PRICES, [{ slug: 'clip-a', qty: 99 }]), /between 1 and 25/);
  assert.throws(() => priceCart(PRICES, []), /no parts/);
});

test('checkout is closed (503) without Stripe keys', async () => {
  const s = await start({ env: { SITE_URL: 'https://example.test' } });
  const r = await call(s, 'POST', '/api/checkout', { items: [{ slug: 'clip-a', qty: 1 }] });
  assert.equal(r.status, 503);
  const h = await call(s, 'GET', '/api/health');
  assert.equal(h.json.checkout, 'closed');
  s.close();
});

test('checkout is closed when keys exist but ENABLE_CHECKOUT is off', async () => {
  const s = await start({ env: { SITE_URL: 'https://example.test' }, stripe: { checkout: { sessions: { create: async () => ({ url: 'x' }) } } } });
  assert.equal((await call(s, 'POST', '/api/checkout', { items: [{ slug: 'clip-a', qty: 1 }] })).status, 503);
  s.close();
});

test('creates a session with server prices; ignores prices sent by the browser', async () => {
  let seen;
  const stripe = { checkout: { sessions: { create: async (p) => { seen = p; return { url: 'https://checkout.stripe.test/s/1' }; } } } };
  const s = await start({ env: ENV, stripe });
  const r = await call(s, 'POST', '/api/checkout', { items: [{ slug: 'sep-b', qty: 2, price: 1 }] }, { Origin: 'https://example.test' });
  assert.equal(r.status, 200);
  assert.equal(r.json.url, 'https://checkout.stripe.test/s/1');
  assert.equal(r.headers.get('access-control-allow-origin'), 'https://example.test');
  assert.equal(seen.line_items[0].price_data.unit_amount, 2400);
  assert.equal(seen.line_items[0].quantity, 2);
  assert.equal(seen.shipping_options[0].shipping_rate_data.fixed_amount.amount, 550);
  assert.equal(seen.shipping_options[1].shipping_rate_data.fixed_amount.amount, 0);
  assert.match(seen.success_url, /^https:\/\/example\.test\/order\/success\/\?session_id=\{CHECKOUT_SESSION_ID\}$/);
  assert.deepEqual(seen.shipping_address_collection.allowed_countries, ['US']);
  s.close();
});

test('blocks other websites and bad input', async () => {
  const stripe = { checkout: { sessions: { create: async () => ({ url: 'u' }) } } };
  const s = await start({ env: ENV, stripe });
  assert.equal((await call(s, 'POST', '/api/checkout', { items: [{ slug: 'clip-a', qty: 1 }] }, { Origin: 'https://evil.test' })).status, 403);
  assert.equal((await call(s, 'POST', '/api/checkout', { items: [{ slug: 'nope', qty: 1 }] })).status, 400);
  const bad = await fetch(`http://127.0.0.1:${s.address().port}/api/checkout`, { method: 'POST', body: '{not json' });
  assert.equal(bad.status, 400);
  s.close();
});

test('webhook rejects a bad signature', async () => {
  const stripe = { webhooks: { constructEvent: () => { throw new Error('bad'); } }, checkout: { sessions: { create: async () => ({}) } } };
  const s = await start({ env: { ...ENV, STRIPE_WEBHOOK_SECRET: 'whsec_test' }, stripe });
  assert.equal((await call(s, 'POST', '/api/webhook', { a: 1 }, { 'stripe-signature': 'x' })).status, 400);
  s.close();
});

test('real prices.json from the build loads', () => {
  const p = require('./server').loadPrices();
  assert.ok(p.items && Array.isArray(p.ship));
});

test('webhook accepts a correctly signed event (real Stripe library, no network)', async () => {
  const Stripe = require('stripe');
  const stripe = Stripe('sk_test_dummy_not_a_real_key');
  const logs = [];
  const s = createServer({ prices: PRICES, env: { ...ENV, STRIPE_WEBHOOK_SECRET: 'whsec_local_test' }, stripe, log: m => logs.push(m) });
  await new Promise(r => s.listen(0, r));
  const payload = JSON.stringify({ id: 'evt_1', type: 'checkout.session.completed', data: { object: { id: 'cs_1', amount_total: 2950, currency: 'usd', metadata: { parts: 'sep-bx1' } } } });
  const header = stripe.webhooks.generateTestHeaderString({ payload, secret: 'whsec_local_test' });
  const res = await fetch(`http://127.0.0.1:${s.address().port}/api/webhook`, { method: 'POST', headers: { 'stripe-signature': header, 'Content-Type': 'application/json' }, body: payload });
  assert.equal(res.status, 200);
  assert.match(logs[0], /ORDER PAID cs_1 total=29\.50/);
  s.close();
});
