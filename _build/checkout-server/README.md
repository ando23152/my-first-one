# True Part Fabrication checkout server

A small Node server that turns the website cart into a Stripe Checkout payment page.
It is **off** until you do the steps below. Until then it answers "checkout isn't open yet"
and the website keeps sending carts as quote requests.

## How it works

1. A customer adds parts to the cart on the website.
2. Only parts with a **price and a confirmed fit** can be bought online. Everything else stays a quote request.
3. "Check out securely" sends the part IDs and quantities to this server. The server looks up the
   prices in its own `prices.json` (it never trusts prices from the browser) and asks Stripe for a checkout page.
4. The customer pays on Stripe's page. Stripe emails the receipt. You see the order in the Stripe dashboard
   and get Stripe's order email.
5. The customer returns to `/order/success/` (or `/order/cancelled/`).

`prices.json` is written by the site build from the catalog, so the website and the server always show and charge the same price.

## Going live (you do these; never share keys in chat)

1. **Create a Stripe account** at stripe.com for True Part Fabrication LLC. Finish identity and bank details.
2. **Set prices**: fill in column H of `TPF_Website_Prices.xlsx`, then `python3 import_prices.py TPF_Website_Prices.xlsx` and rebuild.
3. **Create the server on Render**: New → Web Service → this repo, branch `truepart-site`.
   - Root directory: `_build/checkout-server`
   - Build command: `npm ci`
   - Start command: `npm start`
   - Health check path: `/api/health`
4. **Environment variables** (Render → the service → Environment). Paste these yourself:
   | Name | Value |
   |---|---|
   | `STRIPE_SECRET_KEY` | From Stripe → Developers → API keys (starts with `sk_live_`, or `sk_test_` to try it first) |
   | `STRIPE_WEBHOOK_SECRET` | From step 5 (starts with `whsec_`) |
   | `SITE_URL` | The website address, no trailing slash, e.g. `https://truepartfabrication.com` |
   | `ENABLE_CHECKOUT` | `true` |
   | `AUTOMATIC_TAX` | `true` only after Stripe Tax is set up with your California seller's permit |
   | `ALLOWED_ORIGINS` | Optional: other site addresses allowed to start checkout, comma-separated |
5. **Webhook**: Stripe → Developers → Webhooks → Add endpoint `https://<server address>/api/webhook`,
   event `checkout.session.completed`. Copy its signing secret into `STRIPE_WEBHOOK_SECRET`. Paid orders then show
   in the Render logs as `ORDER PAID …`.
6. **Switch the website on**: in `site_src/shop.py` set `CHECKOUT["enabled"] = True` and
   `CHECKOUT["endpoint"]` to the server address. Rebuild and deploy.
7. **Test** with `sk_test_` keys and Stripe's test card first, then swap in the live key.

## Shipping

Placeholder tiers, in `site_src/shop.py` (`SHIP`): small $4.00, medium $4.75, large $5.50 (the eBay rates).
An order is charged the largest tier among its parts. Local pickup in Modesto is free.

## Endpoints

- `GET /api/health`: `{ ok, checkout: "open" | "closed", parts }`
- `POST /api/quote-total`: `{ items: [{ slug, qty }] }` returns server-side totals (no Stripe call)
- `POST /api/checkout`: same body; returns `{ url }` for the Stripe page, or 503 while closed
- `POST /api/webhook`: Stripe events (signature checked)

## Tests

`npm test` (no keys or network needed).
