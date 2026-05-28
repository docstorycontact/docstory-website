/**
 * DocStory — Shared Interactivity (js/main.js)
 * Handles: mobile nav drawer, directory search/filter, map pin interactions
 */

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
