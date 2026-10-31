"""Copy the website prices from TPF_Website_Prices.xlsx (column H) into the catalog.

Usage:  python3 import_prices.py [path/to/TPF_Website_Prices.xlsx] [--dry-run]

- A number in column H sets that part's price. A blank cell removes the price.
- Parts with a price AND a confirmed fit become buyable online (once checkout is switched on).
  Parts with a price but no confirmed fit show "From $" and stay on the quote request.
- After importing, run build.py and deploy. The build also refreshes the checkout
  server's price list, so the server and the website always charge the same amount.
"""
import json, sys, os
import openpyxl

CATALOG = "/home/claude/site/catalog.json"

def norm(v):
    return " ".join(str(v or "").split()).lower()

def main(argv):
    dry = "--dry-run" in argv
    args = [a for a in argv if not a.startswith("--")]
    xlsx = args[0] if args else "/home/claude/TPF_Website_Prices.xlsx"
    cat = json.load(open(CATALOG))
    index = {(norm(it["b"]), norm(it["oem"] or it.get("for", "")), norm(it["n"])): it for it in cat["items"]}
    ws = openpyxl.load_workbook(xlsx, data_only=True).active
    header_row = next(r for r in range(1, 15) if norm(ws.cell(r, 1).value) == "brand")
    set_n = cleared = 0
    unmatched, bad, not_fit = [], [], []
    for r in range(header_row + 1, ws.max_row + 1):
        b, ref, n, price = ws.cell(r, 1).value, ws.cell(r, 2).value, ws.cell(r, 3).value, ws.cell(r, 8).value
        if not (b or n):
            continue
        r_ = norm(ref)
        r_ = r_[4:] if r_.startswith("for ") else r_
        it = index.get((norm(b), r_, norm(n)))
        if not it:
            unmatched.append(f"row {r}: {b} {ref} {n}")
            continue
        if price in (None, ""):
            if it.pop("price", None) is not None:
                cleared += 1
            continue
        try:
            p = round(float(str(price).replace("$", "").replace(",", "").strip()), 2)
            if not (0.5 <= p <= 5000):
                raise ValueError
        except ValueError:
            bad.append(f"row {r}: {n}: {price!r}")
            continue
        it["price"] = p
        set_n += 1
        if not it.get("f"):
            not_fit.append(n)
    print(f"Prices set: {set_n}   cleared: {cleared}")
    buy = sum(1 for it in cat["items"] if it.get("price") and it.get("f"))
    print(f"Buyable online (price + confirmed fit): {buy}")
    if not_fit:
        print(f"{len(not_fit)} priced parts have no confirmed fit; they show 'From $' and stay quote-only.")
    for label, rows in (("Rows not matched to a catalog part", unmatched), ("Prices that aren't valid numbers", bad)):
        if rows:
            print(label + ":")
            for x in rows:
                print("  " + x)
    if dry:
        print("Dry run: catalog not changed.")
        return 1 if bad else 0
    tmp = CATALOG + ".tmp"
    json.dump(cat, open(tmp, "w"), ensure_ascii=False, indent=1)
    os.replace(tmp, CATALOG)
    print("Catalog updated. Now run: python3 build.py")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
