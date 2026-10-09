/**
 * DocStory — Shared Interactivity (js/main.js)
 * Handles: mobile nav drawer, directory search/filter, map pin interactions,
 * email signup (Kit) for "Join Now" buttons and the 3-free-interviews gate
 */

/* ==============================================
   Email signup (Kit)
   Addresses go to the Kit form below and appear under Subscribers in Kit.
   The form uses double opt-in, so Kit emails each subscriber a confirmation link.
=============================================== */
window.DocStorySignup = (function () {
  const KIT_FORM_URL = 'https://app.kit.com/forms/10021243/subscriptions';
  const LS_SIGNED = 'emailSignedUp';
  const LS_EMAIL  = 'signupEmail';
  const EMAIL_RE  = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  // Storage can be blocked (private mode, strict settings); never let that break the page
  const store = {
    get(k)    { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* ignore */ } },
  };

  function isSignedUp() { return store.get(LS_SIGNED) === 'true'; }

  async function subscribe(email) {
    const body = new FormData();
    body.append('email_address', email);
    const res = await fetch(KIT_FORM_URL, { method: 'POST', body, headers: { Accept: 'application/json' } });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || (data.status && data.status !== 'success')) throw new Error('Kit signup failed');
    store.set(LS_SIGNED, 'true');
    store.set(LS_EMAIL, email);
  }

  let modal = null;

  function build() {
    const el = document.createElement('div');
    el.id = 'signup-modal';
    el.className = 'hidden fixed inset-0 z-[100] flex items-end sm:items-center justify-center';
    el.setAttribute('role', 'dialog');
    el.setAttribute('aria-modal', 'true');
    el.setAttribute('aria-labelledby', 'signup-title');
    el.innerHTML = `
      <div data-signup-backdrop class="absolute inset-0 bg-on-background/50 backdrop-blur-sm"></div>
      <div class="relative bg-surface-container-lowest rounded-t-2xl sm:rounded-2xl shadow-2xl w-full sm:max-w-md sm:mx-4 px-lg pt-lg pb-xl">
        <button type="button" data-signup-close aria-label="Close"
          class="hidden absolute top-3 right-3 w-10 h-10 rounded-full flex items-center justify-center text-slate-gray hover:bg-vibrant-iris/10 focus:outline-none focus-visible:ring-2 focus-visible:ring-vibrant-iris">
          <span class="material-symbols-outlined text-[22px]" aria-hidden="true">close</span>
        </button>
        <div class="flex items-center justify-center w-14 h-14 rounded-full bg-vibrant-iris/15 mx-auto mb-md">
          <span data-signup-icon class="material-symbols-outlined text-vibrant-iris text-[28px]" style="font-variation-settings:'FILL' 1" aria-hidden="true">lock</span>
        </div>
        <h2 id="signup-title" class="font-headline-lg text-headline-lg text-primary text-center mb-xs"></h2>
        <p data-signup-text class="font-body-md text-body-md text-slate-gray text-center mb-lg leading-relaxed"></p>
        <form data-signup-form novalidate>
          <label for="signup-email" class="sr-only">Email address</label>
          <input type="email" id="signup-email" name="email" placeholder="your@email.com" autocomplete="email" required
            aria-describedby="signup-error"
            class="w-full border border-primary/20 rounded-lg px-md py-sm font-body-md text-body-md text-primary placeholder:text-slate-gray/60 focus:outline-none focus:ring-2 focus:ring-vibrant-iris focus:border-transparent transition-all bg-white mb-xs">
          <p id="signup-error" role="alert" class="font-body-md text-xs text-[#b42318] mb-sm hidden"></p>
          <button type="submit" data-signup-submit
            class="w-full bg-vibrant-iris text-white py-sm rounded-full font-label-md text-label-md hover:opacity-90 active:scale-[0.98] transition-all shadow-sm disabled:opacity-60 disabled:cursor-wait focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-vibrant-iris">
            Get free access →
          </button>
        </form>
        <p data-signup-fine class="font-body-md text-xs text-slate-gray text-center mt-md">No spam. Unsubscribe anytime.</p>
      </div>`;
    document.body.appendChild(el);
    return el;
  }

  /**
   * open({ gate: true, onSuccess })  — the 3-interview paywall: can't be dismissed
   * open()                           — "Join Now": dismissible with ×, Esc, or backdrop
   */
  function open(opts = {}) {
    let gate = !!opts.gate;
    modal = modal || build();
    const $ = sel => modal.querySelector(sel);
    const form = $('[data-signup-form]'), input = $('#signup-email'), err = $('#signup-error');
    const submit = $('[data-signup-submit]'), closeBtn = $('[data-signup-close]');
    const returnFocus = document.activeElement;

    $('#signup-title').textContent = gate ? "You've read 3 free interviews" : 'Join DocStory';
    $('[data-signup-text]').textContent = gate
      ? 'Sign up for free to keep reading — unlimited access to every DocStory interview.'
      : 'Get unlimited access to every student interview, free.';
    $('[data-signup-icon]').textContent = gate ? 'lock' : 'mail';
    closeBtn.classList.toggle('hidden', gate);
    form.classList.remove('hidden');
    $('[data-signup-fine]').textContent = 'No spam. Unsubscribe anytime.';
    err.classList.add('hidden');
    submit.disabled = false;
    submit.textContent = 'Get free access →';

    function close() {
      modal.classList.add('hidden');
      document.removeEventListener('keydown', onKey);
      if (returnFocus && returnFocus.focus) returnFocus.focus();
    }
    function onKey(e) { if (e.key === 'Escape' && !gate) close(); }
    function showError(msg) { err.textContent = msg; err.classList.remove('hidden'); input.focus(); }

    closeBtn.onclick = close;
    $('[data-signup-backdrop]').onclick = gate ? null : close;
    input.oninput = () => err.classList.add('hidden');
    form.onsubmit = async e => {
      e.preventDefault();
      const email = input.value.trim();
      if (!EMAIL_RE.test(email)) return showError('Please enter a valid email address.');
      submit.disabled = true;
      submit.textContent = 'Signing you up…';
      try {
        await subscribe(email);
      } catch (ex) {
        submit.disabled = false;
        submit.textContent = 'Get free access →';
        return showError("Something went wrong and we couldn't sign you up. Please try again.");
      }
      if (opts.onSuccess) opts.onSuccess(email);
      // Confirmation state: Kit has emailed a link to confirm the subscription
      $('#signup-title').textContent = "You're in!";
      $('[data-signup-text]').textContent = `Check ${email} for a link to confirm your subscription.`;
      $('[data-signup-icon]').textContent = 'mark_email_read';
      form.classList.add('hidden');
      closeBtn.classList.remove('hidden');
      $('[data-signup-backdrop]').onclick = close;
      gate = false;   // now dismissible either way
      closeBtn.focus();
    };

    modal.classList.remove('hidden');
    document.addEventListener('keydown', onKey);
    setTimeout(() => input.focus(), 50);
  }

  // Any element with data-signup opens the signup box
  document.addEventListener('click', e => {
    const trigger = e.target.closest('[data-signup]');
    if (!trigger) return;
    e.preventDefault();
    const drawer = document.getElementById('mobile-nav-drawer');   // close the mobile menu if open
    if (drawer) drawer.classList.add('translate-x-full');
    open();
  });

  return { open, isSignedUp };
})();

document.addEventListener('DOMContentLoaded', () => {

  /* ==============================================
     1. Mobile Navigation Drawer
  =============================================== */
  const toggle  = document.getElementById('mobile-menu-toggle');
  const drawer  = document.getElementById('mobile-nav-drawer');
  const closeBtn = document.getElementById('mobile-menu-close');

  if (toggle && drawer && closeBtn) {
    const open  = () => { drawer.classList.remove('translate-x-full'); };
    const close = () => { drawer.classList.add('translate-x-full'); };

    toggle.addEventListener('click', open);
    closeBtn.addEventListener('click', close);
    drawer.addEventListener('click', e => { if (e.target === drawer) close(); });
  }

  /* ==============================================
     2. Directory: Search + Filter
  =============================================== */
  const searchInput  = document.getElementById('school-search');
  const schoolList   = document.getElementById('school-list');
  const resultsCount = document.getElementById('results-count');
  const btnAll  = document.getElementById('filter-all');
  const btnMD   = document.getElementById('filter-md');
  const btnDO   = document.getElementById('filter-do');

  if (schoolList) {
    const cards = Array.from(schoolList.querySelectorAll('article'));
    let activeFilter = 'all';

    const ACTIVE_CLS   = 'bg-vibrant-iris text-white shadow-sm';
    const INACTIVE_CLS = 'bg-surface-container-high text-slate-gray';

    function setFilterBtn(active, ...rest) {
      active.className = `${ACTIVE_CLS} px-4 py-1.5 rounded-full font-label-md text-xs cursor-pointer whitespace-nowrap transition-all`;
      rest.forEach(b => { if (b) b.className = `${INACTIVE_CLS} px-4 py-1.5 rounded-full font-label-md text-xs cursor-pointer hover:bg-surface-dim whitespace-nowrap transition-all`; });
    }

    function applyFilters() {
      const query = searchInput ? searchInput.value.trim().toLowerCase() : '';
      let count = 0;
      cards.forEach(card => {
        const num  = card.id.replace('card-', '');
        const pin  = document.getElementById(`pin-${num}`);
        const name = (card.dataset.name || '').toLowerCase();
        const type = card.dataset.type || '';
        const show = name.includes(query) && (activeFilter === 'all' || type === activeFilter);
        card.style.display = show ? '' : 'none';
        if (pin) pin.style.display = show ? '' : 'none';
        if (show) count++;
      });
      if (resultsCount) resultsCount.textContent = `Showing ${count} result${count !== 1 ? 's' : ''}.`;
    }

    if (btnAll) btnAll.addEventListener('click', () => { activeFilter = 'all'; setFilterBtn(btnAll, btnMD, btnDO); applyFilters(); });
    if (btnMD)  btnMD.addEventListener('click',  () => { activeFilter = 'md';  setFilterBtn(btnMD, btnAll, btnDO);  applyFilters(); });
    if (btnDO)  btnDO.addEventListener('click',  () => { activeFilter = 'do';  setFilterBtn(btnDO, btnAll, btnMD);  applyFilters(); });
    if (searchInput) searchInput.addEventListener('input', applyFilters);

    /* ==============================================
       3. Map Pins ↔ Card Highlight
    =============================================== */
    cards.forEach(card => {
      const num = card.id.replace('card-', '');
      const pin = document.getElementById(`pin-${num}`);

      // Highlight card on pin click
      if (pin) {
        pin.addEventListener('click', () => {
          cards.forEach(c => c.classList.remove('ring-2', 'ring-vibrant-iris', 'bg-vibrant-iris/5', 'scale-[1.01]'));
          card.classList.add('ring-2', 'ring-vibrant-iris', 'bg-vibrant-iris/5', 'scale-[1.01]');
          card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        });
      }

      // Highlight pin border on card click
      card.addEventListener('click', () => {
        cards.forEach(c => c.classList.remove('ring-2', 'ring-vibrant-iris', 'bg-vibrant-iris/5', 'scale-[1.01]'));
        card.classList.add('ring-2', 'ring-vibrant-iris', 'bg-vibrant-iris/5', 'scale-[1.01]');
        if (pin) {
          const inner = pin.querySelector('.w-14');
          if (inner) {
            inner.classList.add('scale-110');
            setTimeout(() => inner.classList.remove('scale-110'), 350);
          }
        }
      });
    });
  }

  /* ==============================================
     4. Hero School Name Cycling
  =============================================== */
  const schoolNames = [
    "Harvard Medical School",
    "Yale School of Medicine",
    "Johns Hopkins University School of Medicine",
    "Duke University School of Medicine",
    "Mayo Clinic School of Medicine",
    "Northwestern University Feinberg School of Medicine",
    "Weill Cornell Medical College",
    "Baylor College of Medicine",
    "David Geffen School of Medicine at UCLA",
    "UC San Diego School of Medicine",
    "UC Irvine School of Medicine",
    "USC Keck School of Medicine",
    "University of Florida College of Medicine",
    "University of Miami Miller School of Medicine",
    "USF Morsani College of Medicine",
    "Florida State University College of Medicine",
    "Tulane University School of Medicine",
    "Rush Medical College",
    "Creighton University School of Medicine",
    "Medical College of Wisconsin",
    "Drexel University College of Medicine",
    "New York Medical College",
    "Touro College of Osteopathic Medicine",
    "University of Massachusetts Medical School",
    "University of Cincinnati College of Medicine",
    "Indiana University School of Medicine",
    "University of Iowa Carver College of Medicine",
    "University of Alabama at Birmingham School of Medicine",
    "University of Tennessee Health Science Center",
    "Virginia Commonwealth University School of Medicine",
    "Eastern Virginia Medical School",
    "Wayne State School of Medicine",
    "Southern Illinois University School of Medicine",
    "TCU Burnett School of Medicine",
    "Medical College of Georgia at Augusta University",
    "Kentucky College of Osteopathic Medicine",
    "Western University of Health Sciences College of Osteopathic Medicine",
    "California University of Science and Medicine",
    "Chicago Medical School at Rosalind Franklin University",
  ];

  const schoolEl = document.getElementById('school-name-cycle');
  if (schoolEl) {
    let schoolIdx = 0;
    schoolEl.textContent = schoolNames[0] + '.';

    setInterval(() => {
      schoolEl.classList.add('school-exit');
      setTimeout(() => {
        schoolIdx = (schoolIdx + 1) % schoolNames.length;
        schoolEl.textContent = schoolNames[schoolIdx] + '.';
        schoolEl.classList.remove('school-exit');
        schoolEl.classList.add('school-enter');
        void schoolEl.offsetHeight;
        schoolEl.classList.remove('school-enter');
      }, 280);
    }, 3000);
  }

});
