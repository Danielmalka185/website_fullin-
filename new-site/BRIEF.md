# FULLIN — New site brief (shared by all agents)

Static site: plain HTML + CSS + vanilla JS. **No build step, no frameworks, no npm.** Must open by double-clicking `index.html` and run on any static host. Works on phone and desktop, RTL (he, ar) and LTR (en, ru).

## Who / what
FULLIN rents power banks from self-service charging stations in cafés, bars, restaurants, beaches, hotels, malls and events across Israel. Scan QR -> pay (Apple Pay / Google Pay / card) -> take a power bank -> return at ANY station. App on iOS/Android, 4 languages (he/en/ar/ru). Tagline: "Power To Move". Hebrew hero joke to keep: "ה-1% האחרון הוא שקרן" (the last 1% is a liar).

Two audiences, equal weight: **consumers** (rent) and **business owners** (host a station). Business pitch: zero cost, zero installation, zero staff effort, revenue share, guests stay longer.

## Hard facts (use EXACTLY, never invent)
- Price: **first hour free ONLY for people who download the app** (owner-confirmed). Renting WITHOUT the app (QR scan on the station) = **12 NIS/hour from the very first minute, no free hour**. Never promise a free hour to everyone. After the app's free hour: 12 NIS/hour. Daily cap **60 NIS per day** (owner correction, was 50); second day another 60 cap (up to 120 for two days). If not returned: **maximum total charge 200 NIS** (no '+100' increment is stated any more). **OWNER TO CONFIRM the day-2 / not-returned chain.** No subscription, no hidden fees. **Deposit / credit-frame guarantee (owner correction, authoritative, supersedes earlier notes): ₪200 on BOTH the payment page (PayPlus; real screen says the charge is 12 NIS/hour only and the amount is a credit-frame guarantee, not a charge) AND the card terminal at the station (station screen: 'כרטיס אשראי בעמדה — 200 שקלים נועדו לפיקדון בלבד! ויחזרו לאחר השימוש בהתאם לחברת האשראי'). It is NOT a charge; released after use per the card company (never promise a number of days); only ₪12/hour is actually charged. The not-returned rule (₪200 max total charge) is a separate rule, do not confuse. assets/pay/pay-page-v4.webp has the guarantee caption RE-TYPED to ₪200 (not a real screenshot); owner should send a real updated screenshot.**
- Payment: Apple Pay, Google Pay, credit card. App optional for renting via QR (no free hour without the app); app gives the free first hour, helps find stations and track rentals.
- Power bank: 3 built-in cables (Lightning / USB-C / Micro USB), works with iPhone and Android.
- Stations: 6-slot (small, countertop), 24-slot (medium, 21.5" screen), 48-slot (large, 43" ad screen).
- Real references the owners approved to show by NAME/logo: Lager & Ale, Vert, Frishman beach, Troya, Tea Wei, ICON Fitness, Kanyon HaAmakim (Afula), and events Genesis festival, Infected festival.
- Links: iOS https://apps.apple.com/il/app/fullin/id6757767367?l=he  ·  Android https://play.google.com/store/apps/details?id=com.fullin.app  ·  WhatsApp https://wa.me/972542780713  ·  pages privacy.html, terms.html (copy from old site into new-site root later)

## NEVER write
- Any number of stations/units ("מאות עמדות" is FALSE). Say "wide deployment across Israel" / "פריסה רחבה ברחבי הארץ" only. No rental counts, revenue figures, or profit promises. No profit calculator.
- "Leading network in Israel", "tens of businesses", statistics without source.
- Revenue-share percentages (varies per deal). Say "revenue share" only.
- Claims that hospitals/specific venues have stations. AI scene images must be labeled illustration ("הדמיה") when shown.
- Do NOT use `assets/field/crowd-booth-FACES.webp` (identifiable faces, no consent confirmed). Not in HTML, not in CSS.
- Do not name partner Israel Post in copy.

## Visual direction: dark, futuristic, "sexy"
Palette (CSS vars in `css/tokens.css`): bg `#07090b`, surface `#0e1215`, surface-2 `#141a1f`, text `#f2f5f3`, muted `#8b9a93`, brand green `#2FC353` (glow `rgba(47,195,83,.45)`), accent yellow `#E8F23A` (the power bank cables), line `rgba(255,255,255,.08)`.
Feel: Apple/Linear-grade polish. Big confident type, generous space, glass cards (backdrop-filter, 1px borders), green glow, subtle noise/grid, scroll-reveal, parallax stations, battery/percentage animation (1% -> 100%). Marquee of client logos. Smooth, never janky: 60fps, transform/opacity only.
Fonts: Heebo (he/ar fallback) + Space Grotesk (latin) via Google Fonts; `font-display: swap`.
Motion must respect `prefers-reduced-motion`.

## Technical contract
Folder `new-site/`:
```
index.html            page shell (owned by core agent; section markup owned per-section, see markers)
css/tokens.css base.css hero.css sections.css   (core owns tokens+base+hero; sections agent owns sections.css)
js/i18n.js main.js sections.js                  (core owns i18n+main; sections agent owns sections.js)
content/copy.json     all copy for he/en/ar/ru (copywriter owns)
assets/...            already optimized webp/svg/mp4. Do not modify. Read the file list.
```
- i18n: every visible string is `data-i18n="key"` (text) / `data-i18n-attr="alt:key"` etc. Keys are dotted: `hero.title`, `pricing.free.title`. `i18n.js` loads `content/copy.json` (inline fetch with a fallback: embed he copy in a `<script type="application/json" id="copy-he">` so file:// works), sets `<html lang dir>`, remembers choice in localStorage (try/catch), language switcher in nav. Default he.
- Use logical CSS properties (margin-inline-start, inset-inline-end, text-align:start) so RTL/LTR both work.
- Sections in order, ids: `#top`(hero) `#how` `#price` `#network` `#business` `#proof` `#faq` `#contact`. Mobile-first; breakpoints 640 / 960 / 1280. Tap targets >= 44px. No horizontal scroll at 360px.
- Accessibility: semantic landmarks, alt text via i18n, focus rings, contrast AA, `aria-expanded` on FAQ and mobile menu.
- Performance: images `loading="lazy"` + width/height, hero video muted loop playsinline preload=metadata with poster, no external JS libs. Lighthouse perf >= 90 mobile target.
- SEO: title/description/og tags (og:image `assets/og.jpg` to be created by core), JSON-LD Organization.
- Lead form: fields name, business name, business type (select), phone, city; submit builds a WhatsApp message to https://wa.me/972542780713?text=... (no backend). Validate inline.

## Section content intent
1. **Hero** — dark, 6/24 station cutouts + phone/powerbank floating over green glow, nightclub/bar ambience video or image behind, live battery counter that climbs and "stalls" at 99% then punchline; CTAs: download app / host a station.
2. **How it works** — 3 steps (scan & pay; charge anywhere; return at any station), sticky/animated.
3. **Pricing** — stepped timeline card: 1st hour free (app users only; no-app renters pay 12/hr from minute one) -> 12 NIS/hr -> 60/day cap -> day 2 another 60 cap (up to 120) -> not returned: max total charge 200. Clear, honest, no fine-print feel.
4. **Network** — "wide deployment across Israel" stylised map/graphic of Israel with soft pulsing dots (NO counts), station family (6/24/48) cards with real cutouts.
5. **Business** — what the owner gets (0 cost, 0 install, 0 effort, revenue share, guests stay longer) + venue-type tabs/cards: café/bar, restaurant, beach, hotel, mall, events — use AI scene images labeled "הדמיה".
6. **Proof** — client logo marquee (Lager & Ale, Vert, Frishman, Troya, Tea Wei, ICON, Kanyon HaAmakim; use logos in assets/logos where present, styled text wordmarks otherwise) + real festival field photos (no faces) in a bento grid.
7. **FAQ** — accordion.
8. **Contact** — lead form + WhatsApp button + app badges. Footer with links.
