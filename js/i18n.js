/* =====================================================================
   FULLIN — bilingual toggle (Hebrew ⇄ English)
   ---------------------------------------------------------------------
   • Hebrew stays in the HTML as the source of truth. On first load we
     cache every translatable node's original content, so switching back
     to Hebrew simply restores it — no Hebrew strings are duplicated here.
   • English strings live in the EN dictionary below, keyed by the
     data-i18n* attributes placed on the elements.
   • The chosen language is stored in localStorage and re-applied on every
     page (so the whole site stays in the selected language while browsing).

   Markup contract:
     data-i18n="key"              → element.innerHTML
     data-i18n-placeholder="key"  → placeholder attribute
     data-i18n-alt="key"          → alt attribute
     data-i18n-value="key"        → value attribute (submit buttons)
     data-i18n-wait="key"         → data-wait attribute (Webflow submit)
     data-i18n-aria="key"         → aria-label attribute
     data-i18n-href="key"         → href attribute
     data-i18n-title="key"        → document.title (put on <title>)
   ===================================================================== */
(function () {
  "use strict";

  var STORAGE_KEY = "fullin-lang";

  // ---- English dictionary -------------------------------------------------
  var EN = {
    // <title> per page
    "title.index": "FULLIN - Always charged, no matter where",
    "title.contact": "Contact - FULLIN",
    "title.privacy": "Privacy Policy - FULLIN",
    "title.terms": "Terms of Use - FULLIN",

    // Navbar
    "nav.home": "Home",
    "nav.how": "How it works",
    "nav.price": "Pricing",
    "nav.business": "For business",
    "nav.faq": "FAQ",
    "nav.contact": "Contact",

    // Hero
    "hero.h1": 'The last 1% is a <strong class="bold-text red">liar</strong>',
    "hero.p": "You'll never be stuck with a dead battery again.<br><br>Rent a power bank in seconds from any FULLIN station, and return it at any station across the network.<br><br>No sign-up. No app. Just the power to move.",
    "hero.cta": "Join the revolution",
    "hero.badgeApple": "Download on the App Store",
    "hero.badgeGoogle": "Get it on Google Play",

    // Section 2 — dead battery
    "s2.h1": "A dead battery ruins moments",
    "s2.p": "How many times has your phone died at exactly the most important moment? FULLIN gives you the confidence to always stay connected – no hunting for an outlet, no chargers forgotten at home, and no empty battery ruining your day.",
    "s2.cta": "Join as a business partner",

    // How it works
    "how.title": "How it works",
    "how.1.title": "Scan &amp; start",
    "how.1.body": "Scan the QR code on the station to rent directly, or rent through the FULLIN app.<br>Confirm the deposit with Apple Pay or Google Pay, and the charger releases automatically.",
    "how.2.title": "Charge anywhere",
    "how.2.body": "Take the power bank with you and charge your phone wherever you are.<br>FULLIN chargers support all leading smartphones, including iPhone and Android devices.",
    "how.3.title": "Return at any station",
    "how.3.body": "When you're done, simply return the charger to any FULLIN station in the network.<br>No need to return it to the same station where you started.",

    // Rent instantly
    "rent.eyebrow": "Rent instantly",
    "rent.h1": "Instant charging. No app.",
    "rent.p": "Scan the QR code on any FULLIN station and rent a power bank in seconds.<br><br>Pay instantly with card, Apple Pay or Google Pay.<br><br>No downloads, no sign-ups. Just power when you need it.",
    "rent.cta": "Download the app",

    // App CTA card
    "appcta.h1": "Download the app<br>and get your first hour of charging free 🎁",
    "appcta.subtitle": "Join the FULLIN network — hundreds of stations across the country, rent in one second, no commitment.",
    "appcta.chip1": "⚡ Instant rental",
    "appcta.chip2": "🗺️ Hundreds of stations",
    "appcta.chip3": "🎁 First hour free",

    // About the app
    "about.h1": "About the app",
    "about.p": "Find nearby stations, start a rental instantly, and return the charger at any point across the network.",
    "about.cta": "Download the app",

    // Growing network
    "grow.h1": "The network is growing across Israel",
    "grow.p": "FULLIN stations are spread all across Israel – in bars, cafés, malls and public places.<br><br>Our network keeps growing so you can easily find a charger wherever you are.<br>Rent a charger in seconds, and return it at any FULLIN station.",

    // Pricing
    "price.h1": "Simple, transparent pricing",
    "price.card1.front": "Pay per hour",
    "price.card1.price": "₪12 per hour",
    "price.card1.desc": "Rent a full charger from any FULLIN station and pay only for the time you used.",
    "price.card2.front": "Charger not returned",
    "price.card2.price": "₪200 if not returned",
    "price.card2.desc": "If the charger isn't returned within 48 hours, a maximum charge of ₪200 applies.",
    "price.card3.front": "Daily cap",
    "price.card3.price": "₪50 max per day",
    "price.card3.desc": "Use the charger all day – and never pay more than ₪50 per 24 hours.",
    "price.note": "No subscription. No hidden costs. No obligation to download an app.",

    // For business
    "biz.h1": "Become a partner",
    "biz.p": "Bring a convenient charging experience to your customers and keep them connected the whole time they're with you.<br><br>FULLIN stations improve the customer experience, extend the time spent at your business, and require zero effort from your staff.",
    "biz.feat1": "Extends customer dwell time",
    "biz.feat2": "No staff involvement",
    "biz.feat3": "Improves the customer experience",
    "biz.cta": "Join the FULLIN network",

    // FAQ
    "faq.title": "Need help?",
    "faq.subtitle": "Everything you need to know about FULLIN chargers, stations and rentals.",
    "faq.chat": 'Need help? <strong class="bold-text-3">Chat with us </strong><strong>💬</strong>',
    "faq.q1": "How do I rent a charger?",
    "faq.a1": "Scan the QR code with your phone camera or through the FULLIN app, complete the rental process, and the charger releases automatically.",
    "faq.q2": "Do I need to download the app?",
    "faq.a2": "No. You can rent directly by scanning the QR code. That said, the app helps you find nearby stations and manage your rentals.",
    "faq.q3": "Where can I return the charger?",
    "faq.a3": "You can return the charger at any FULLIN station in the network.",
    "faq.q4": "How much does it cost?",
    "faq.a4": "The price is ₪12 per hour, with a daily cap of ₪50.",
    "faq.q5": "What happens if I don't return the charger?",
    "faq.a5": "If the charger isn't returned within 48 hours, a maximum charge of ₪200 applies.",

    // Footer
    "footer.tagline": "FULLIN – Israel's leading network for renting power banks. Always charged, no matter where.",
    "footer.company": "Company",
    "footer.home": "Home",
    "footer.about": "About",
    "footer.help": "Help",
    "footer.terms": "Terms of Use",
    "footer.privacy": "Privacy Policy",
    "footer.copyright": "© All rights reserved to FULLIN, 2026",

    // Contact page
    "contact.first": "First name",
    "contact.first.ph": "e.g. Israel",
    "contact.last": "Last name",
    "contact.last.ph": "e.g. Israeli",
    "contact.email": "Email address",
    "contact.email.ph": "example@youremail.com",
    "contact.phone": "Phone number",
    "contact.phone.ph": "050-000-0000",
    "contact.message": "Message",
    "contact.message.ph": "Write your message here...",
    "contact.submit": "Send message",
    "contact.wait": "One moment...",
    "contact.whatsappOr": "Or reach us directly on WhatsApp",
    "contact.whatsappBtn": "Message us on WhatsApp",
    "contact.successTitle": "Thank you! We'll get back to you soon",
    "contact.successBody": "We've received your message and will get back to you as soon as possible. Our team is committed to providing the best support, and we thank you for your patience.",
    "contact.error": "Oops! Something went wrong submitting the form. Please try again.",

    // Legal pages
    "legal.updated": "Last updated:",
    "legal.soon": "Content coming soon.",
    "privacy.title": "Privacy Policy",
    "privacy.s1": "1. Introduction",
    "privacy.s2": "2. What information we collect",
    "privacy.s3": "3. Use of information",
    "privacy.s4": "4. Data retention and security",
    "privacy.s5": "5. Your rights",
    "privacy.s6": "6. Contact",
    "privacy.contact": 'For questions about your privacy and data, reach out to us via the <a href="contact-us.html">contact page</a>.',
    "terms.title": "Terms of Use",
    "terms.s1": "1. Introduction",
    "terms.s2": "2. Charger rental",
    "terms.s3": "3. Payment and usage fees",
    "terms.s4": "4. Returning the charger",
    "terms.s5": "5. Liability and cancellations",
    "terms.s6": "6. Privacy",
    "terms.s7": "7. Contact",
    "terms.privacy": 'Please review our <a href="privacy.html">Privacy Policy</a>.',
    "terms.contact": 'For questions or clarifications about these Terms of Use, reach out to us via the <a href="contact-us.html">contact page</a>.'
  };

  // attribute name for each data-i18n-* variant
  var ATTR_MAP = {
    "data-i18n-placeholder": "placeholder",
    "data-i18n-alt": "alt",
    "data-i18n-value": "value",
    "data-i18n-wait": "data-wait",
    "data-i18n-aria": "aria-label",
    "data-i18n-href": "href"
  };

  var origHTML = new WeakMap();      // element -> original Hebrew innerHTML
  var origAttr = new WeakMap();      // element -> { attrName: originalValue }
  var origTitle = null;
  var cached = false;

  function cacheOriginals() {
    if (cached) return;
    cached = true;
    origTitle = document.title;
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      origHTML.set(el, el.innerHTML);
    });
    Object.keys(ATTR_MAP).forEach(function (dataAttr) {
      var attr = ATTR_MAP[dataAttr];
      document.querySelectorAll("[" + dataAttr + "]").forEach(function (el) {
        var store = origAttr.get(el) || {};
        store[attr] = el.getAttribute(attr);
        origAttr.set(el, store);
      });
    });
  }

  function apply(lang) {
    cacheOriginals();
    var en = lang === "en";

    // <html lang/dir> — drives which CSS design layer is active
    document.documentElement.setAttribute("lang", en ? "en" : "he-il");
    document.documentElement.setAttribute("dir", en ? "ltr" : "rtl");

    // innerHTML nodes
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var key = el.getAttribute("data-i18n");
      if (en) {
        if (EN[key] != null) el.innerHTML = EN[key];
      } else {
        el.innerHTML = origHTML.get(el);
      }
    });

    // <title> — element carrying data-i18n-title
    var titleEl = document.querySelector("[data-i18n-title]");
    if (titleEl) {
      var tKey = titleEl.getAttribute("data-i18n-title");
      document.title = en && EN[tKey] != null ? EN[tKey] : origTitle;
    }

    // attributes
    Object.keys(ATTR_MAP).forEach(function (dataAttr) {
      var attr = ATTR_MAP[dataAttr];
      document.querySelectorAll("[" + dataAttr + "]").forEach(function (el) {
        var key = el.getAttribute(dataAttr);
        if (en) {
          if (EN[key] != null) el.setAttribute(attr, EN[key]);
        } else {
          var store = origAttr.get(el);
          if (store && store[attr] != null) el.setAttribute(attr, store[attr]);
        }
      });
    });

    // toggle button label always shows the OTHER language
    document.querySelectorAll("[data-lang-toggle]").forEach(function (btn) {
      btn.innerHTML =
        '<svg class="lang-toggle__globe" viewBox="0 0 24 24" fill="none" ' +
        'stroke="currentColor" stroke-width="2" stroke-linecap="round" ' +
        'stroke-linejoin="round" aria-hidden="true">' +
        '<circle cx="12" cy="12" r="9"></circle>' +
        '<path d="M3 12h18"></path>' +
        '<path d="M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18z"></path></svg>' +
        "<span>" + (en ? "עברית" : "EN") + "</span>";
      btn.setAttribute("aria-label", en ? "עבור לעברית" : "Switch to English");
    });
  }

  function setLang(lang) {
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
    apply(lang);
  }

  function currentLang() {
    try { return localStorage.getItem(STORAGE_KEY) === "en" ? "en" : "he"; }
    catch (e) { return "he"; }
  }

  function init() {
    apply(currentLang());
    document.querySelectorAll("[data-lang-toggle]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        setLang(currentLang() === "en" ? "he" : "en");
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  // expose for debugging / manual calls
  window.FullinI18n = { set: setLang, current: currentLang };
})();
