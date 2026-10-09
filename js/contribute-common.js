/**
 * DocStory — Contributor program helpers (js/contribute-common.js)
 * Needs js/contribute-config.js and js/contribute-data.js loaded first.
 */
window.DocStoryContribute = (function () {
  const C = window.DOCSTORY_CONTRIBUTE || {};
  const SCHOOLS = window.DOCSTORY_SCHOOLS || [];
  const bySlug = {};
  SCHOOLS.forEach(s => { bySlug[s.slug] = s; });

  const money = n => '$' + Number(n).toLocaleString('en-US');

  /** Payment status for a school slug ('other' = a school DocStory doesn't cover yet). */
  function payStatus(slug) {
    if (!C.payEnabled) return { paid: false, reason: 'off' };
    if (slug === 'other') return { paid: true, reason: 'new' };
    const s = bySlug[slug];
    if (!s) return { paid: false, reason: 'unknown' };
    return s.interviews >= C.paidCap
      ? { paid: false, reason: 'cap', count: s.interviews }
      : { paid: true, reason: 'open', count: s.interviews };
  }

  const paidSchoolCount = () => SCHOOLS.filter(s => s.interviews < C.paidCap).length;

  /**
   * Fill program values into the page:
   *   data-c="amount|cap|methods|reviewDays|replyDays|payDays|contact|paidSchools|totalSchools"
   *   data-if-paid  — element hidden when payment is switched off
   *   data-if-unpaid — element shown only when payment is switched off
   */
  function fill(root = document) {
    const values = {
      amount: money(C.payAmount),
      cap: String(C.paidCap),
      methods: C.payMethods,
      reviewDays: String(C.reviewDays),
      replyDays: String(C.replyDays),
      payDays: String(C.payDays),
      contact: C.contactEmail || 'a DocStory email address',
      paidSchools: String(paidSchoolCount()),
      totalSchools: String(SCHOOLS.length),
    };
    root.querySelectorAll('[data-c]').forEach(el => {
      const v = values[el.getAttribute('data-c')];
      if (v !== undefined) el.textContent = v;
    });
    root.querySelectorAll('[data-if-paid]').forEach(el => { el.hidden = !C.payEnabled; });
    root.querySelectorAll('[data-if-unpaid]').forEach(el => { el.hidden = !!C.payEnabled; });
  }

  return { config: C, schools: SCHOOLS, bySlug, payStatus, paidSchoolCount, money, fill };
})();
