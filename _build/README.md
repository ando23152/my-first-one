# Site build
build.py generates every page from home_template.html (home page), glossary.py (24 terms), and catalog.json (parts).
When the real domain is connected: set BASE to the domain and INDEX = True in build.py, rebuild, and redeploy so search engines can index the site.

## Online checkout (off until Stripe is set up)
- `shop.py`: cart page, order pages, `assets/prices.json`, and the on/off switch (`CHECKOUT`).
- `import_prices.py`: copies column H of TPF_Website_Prices.xlsx into the catalog.
- `checkout-server/`: the Stripe checkout server. Setup steps are in its README.
