/**
 * DocStory — Analytics and attribution (js/analytics.js)
 * Loaded on every page from the shared <head> block (seo.py).
 *
 * - Page views: Vercel Web Analytics (cookieless; on whenever the site runs on Vercel).
 * - Attribution: remembers which ad or link first brought someone here (utm_* tags or the
 *   referring site), so the contribute form can include it with each submission.
 *
 * Nothing here sets cookies or records personal information.
 */
(function () {
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* storage blocked */ } },
  };
  function addScript(src) {
    var s = document.createElement('script');
    s.defer = true; s.src = src;
    document.head.appendChild(s);
  }

  // Vercel Web Analytics (page views)
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
  if (!/^(localhost|127\.0\.0\.1)$/.test(location.hostname)) addScript('/_vercel/insights/script.js');

  // Attribution: first touch is kept; last touch updates whenever someone arrives from outside
  var params = new URLSearchParams(location.search);
  var utm = {};
  ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'].forEach(function (k) {
    var v = params.get(k); if (v) utm[k] = v.slice(0, 100);
  });
  var ref = '';
  try { ref = document.referrer && new URL(document.referrer).hostname !== location.hostname ? new URL(document.referrer).hostname : ''; } catch (e) { /* ignore */ }
  if (Object.keys(utm).length || ref) {
    var touch = Object.assign({ referrer: ref, landing: location.pathname, date: new Date().toISOString().slice(0, 10) }, utm);
    if (!store.get('docstoryFirstTouch')) store.set('docstoryFirstTouch', JSON.stringify(touch));
    store.set('docstoryLastTouch', JSON.stringify(touch));
  }

  // People who came from an ad, or who have opened the contribute pages, never see the reading gate
  var medium = (utm.utm_medium || '').toLowerCase(), source = (utm.utm_source || '').toLowerCase();
  if (/^(paid|cpc|ads?|paid_social|paidsocial)$/.test(medium) || source === 'reddit' || /^\/contribute(\/|$)/.test(location.pathname)) {
    store.set('docstoryContributor', 'true');
  }

  function read(k) { try { return JSON.parse(store.get(k) || 'null'); } catch (e) { return null; } }

  window.DocStoryTrack = {
    /** Where this visitor came from, as one readable line for the submission email. */
    source: function () {
      var t = read('docstoryFirstTouch'), last = read('docstoryLastTouch');
      if (!t) return 'Direct or unknown';
      var line = function (x) {
        return [x.utm_source, x.utm_medium, x.utm_campaign, x.utm_content].filter(Boolean).join(' / ') ||
          (x.referrer ? 'Referral from ' + x.referrer : 'Direct') + '';
      };
      var out = line(t) + ' (first visit ' + t.date + ', landed on ' + t.landing + ')';
      if (last && JSON.stringify(last) !== JSON.stringify(t)) out += '; most recently ' + line(last) + ' on ' + last.date;
      return out;
    },
    isContributor: function () { return store.get('docstoryContributor') === 'true'; },
  };
})();
