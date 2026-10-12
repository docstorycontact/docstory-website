/**
 * DocStory — Contributor interview form (js/contribute.js)
 * Four steps: about you → choose questions → answer → review & send.
 * Submissions go to Web3Forms, which emails them to DocStory. Each email includes the
 * contributor's .edu address as reply-to, a reference number, the payment decision, and a
 * ready-to-publish interview file (content/interviews/<school>/<name>.md).
 */
(function () {
'use strict';

const D = window.DocStoryContribute;
const C = D.config;
const MIN_PICK = 8, MAX_PICK = 10, MIN_WORDS = 40;
const RANGE = MIN_PICK + '–' + MAX_PICK;
const W3F_URL = 'https://api.web3forms.com/submit';
const HCAPTCHA_SITEKEY = '50b2fe65-b00b-4b9e-ad62-3ba471098be2';   // Web3Forms' shared free-plan key
const EDU_RE = /^[^\s@]+@[^\s@]+\.edu$/i;

/* [id, digit used by the question bank, label, sub-label, MD credit, DO credit, "a/an ..." phrase] */
const YEARS = [
  ['m1', '1', 'First year',  'Foundations',            'MS1', 'OMS1',   'a first-year student'],
  ['m2', '2', 'Second year', 'Boards on the horizon',  'MS2', 'OMS2',  'a second-year student'],
  ['m3', '3', 'Third year',  'Clerkships',             'MS3', 'OMS3', 'a third-year student'],
  ['m4', '4', 'Fourth year', 'Sub-Is and the Match',   'MS4', 'OMS4',  'a fourth-year student'],
];
const CATS = [
  ['pre', 'Pre-clinical'],
  ['clin', 'Clinical'],
  ['res', 'Research'],
  ['glob', 'Global health'],
  ['adv', 'Advocacy'],
  ['life', 'Lifestyle'],
  ['match', 'Boards, advising & the Match'],
  ['big', 'Big picture'],
];
/* [id, label, description, how it reads after "who wants to focus on"] */
const FOCI = [
  ['general', 'A bit of everything', 'Good default if you’re not sure', ''],
  ['pre', 'Pre-clinical', 'Classes, grading, the first two years', 'the pre-clinical years'],
  ['clin', 'Clinical', 'Rotations, hospitals, teams', 'clinical training'],
  ['res', 'Research', 'Mentors, time, publishing', 'research'],
  ['glob', 'Global health', 'Underserved care, work abroad', 'global health'],
  ['adv', 'Advocacy', 'Service, outreach, community', 'advocacy and service'],
  ['life', 'Lifestyle', 'Culture, cost, wellbeing', 'lifestyle'],
  ['match', 'Boards, advising & the Match', 'Step prep, advising, residency', 'boards, advising and the Match'],
];
/* Topic ids before the October 2026 rework, so saved drafts and old recruiting links still work */
const OLD_FOCUS = { academics: 'pre', clinical: 'clin', research: 'res', service: 'adv', global: 'glob', career: 'match' };

/* ---------- Question bank (reworked October 2026) ----------
   [id, topic, years it's offered to, years it's a core suggestion for, question]
   Years: 1 = first year … 4 = fourth year */
const Q = [
  ['a1','pre','1234','12','Walk us through a typical week in the pre-clinical curriculum. Roughly how much is lecture, small group, lab, and self-study?'],
  ['a2','pre','1234','12','How are the preclinical years graded (pass/fail, tiers, internal ranking, etc.)? Do you think this has a major impact on the student culture at your school?'],
  ['a3','pre','1234','','Is lecture attendance required? What do most of your classmates actually do (attend, stream, study from outside resources, etc.)?'],
  ['a4','pre','1234','1','What was the adjustment to the first semester like, and what would you tell an incoming student to do differently? Did your school do anything specific to help you through the first semester and where did you feel on your own?'],
  ['a7','pre','1234','','Which course, block, or professor has been the best part of the curriculum, and why?'],
  ['a8','pre','1234','','Which part of the curriculum do you think has room for improvement, and what specifically is not working?'],
  ['c8','pre','1234','2','What experiences have you had before clerkships (preceptorships, student-run clinics, standardized patients, simulation) to give you at least some exposure to clinical work prior to third year? What experiences provided by your medical school do you think are most helpful in making this transition successful?'],
  ['c9','pre','1234','1','How is clinical skills teaching organized, and how confident do you feel taking a history and doing a physical exam right now?'],

  ['c1','clin','34','34','Briefly describe the main hospitals and clinics you work at and what sort of patient population you see at each. Has one of these clinical sites or clinics been particularly rewarding or influential for you? We want to know about experiences that might be unique to your medical school.'],
  ['c14','clin','34','34','Walk us through a recent day on your current or most recent rotation.'],
  ['c2','clin','34','34','During clinical rotations, were you happy with how directly involved you were in patient care and your value on the team? What did you think about the balance between autonomy and guidance/teaching during your rotations? This is going to differ for every rotation and team you are a part of, so feel free to give examples you feel are representative.'],
  ['c4','clin','34','','Which rotation was your strongest and which was your weakest, and what made the difference?'],
  ['c5','clin','34','','Have there been particular challenges with the logistics of clinical rotations that you wish were different? For example, distance between sites, number of sites to be covered, challenge getting select rotations you want, etc.'],
  ['c6','clin','34','3','How would you describe the culture of feedback during rotations? Were you happy with how/when feedback was given and did you find that it was generally constructive feedback?'],
  ['a11','clin','34','34','Looking back, how well did the pre-clinical years prepare you for the wards? Did you feel by the time clerkships came about, you had an adequate foundation of knowledge to start building clinical skills? Do you feel that foundation of knowledge was a result of structured course work or self-study?'],
  ['c15','clin','34','34','While residents, attendings, and fellows you work with are going to differ from rotation to rotation, can you describe an experience that you think is representative of the housestaff culture at the clinical sites you are at?'],

  ['r1','res','1234','123','Was it challenging to find a research mentor and do you think a medical student that arrives with no research experience would be able to find a research mentor if they desired? Describe how you or a classmate actually got connected with one.'],
  ['r2','res','1234','','Beyond finding a mentor, you also need the time to be able to conduct research projects you are a part of. Is it feasible for medical students to participate in research during pre-clinical and clinical years? Does the program do something to facilitate this participation?'],
  ['r4','res','1234','','What research are you a part of and what is your specific role in it?'],
  ['r11','res','234','','Have you presented or published your work? What support did the school give you, such as funding, conference travel, or help with abstracts?'],

  ['g1','glob','1234','','Have you participated in global health opportunities? If so, describe what the opportunity was and how it was valuable as a personal experience and as a part of your medical education.'],
  ['g10','glob','1234','','For an applicant who wants a career in global health, what makes this school a good or a poor choice?'],
  ['g11','glob','1234','','Are there chances to work with underserved populations? If so, describe the population you work with, the experience itself, and how it contributes to your medical training.'],
  ['g12','glob','1234','','If you were interested in global health but haven\'t done anything abroad, what got in the way: cost, timing, or how the curriculum is set up?'],

  ['s1','adv','1234','12','What community service or outreach are you involved in? What does the work look like and how has it been meaningful to you? If you are not involved in any, is there work that other medical students are doing at your school that you think is particularly meaningful?'],
  ['s5','adv','1234','','If you\'ve done a track or elective in equity, advocacy, or policy, what did it involve, and was it worth the time?'],
  ['s6','adv','1234','','Have students organized around an issue on campus or in the community? What happened?'],
  ['s10','adv','1234','','Does the community within which your medical school is located have a significant impact on the clinical work that you are doing? Is the patient population unique in a way that gives medical students significantly more exposure to a particular type of medicine that may not be the case at other schools?'],

  ['l1','life','1234','1234','How would you describe your class: collaborative, competitive, diverse, close? Give an example that shows it.'],
  ['l2','life','1234','12','What area do you live in? Do you think this area makes it easy to do things to decompress when you have down time? Give examples of things you or other students might do in the area for fun.'],
  ['a10','life','1234','','How responsive is the administration to student feedback? Give an example of something that is currently being discussed, was recently changed, or did not change after students spoke up.'],
  ['l11','life','1234','13','When school got hard, what helped you cope, and did the school\'s own support make a difference?'],
  ['l12','life','1234','2','Roughly what does a month cost you here (rent, food, getting around), and how far does the financial aid budget really stretch?'],

  ['a6','match','234','2','How well did the curriculum prepare you for Step 1 or Level 1? To expand, did you feel the designed curriculum was a major contributor to your success on the exams, or was this mainly a result of dedicated study on your own? How much dedicated study time did you get, and did you feel it was enough?'],
  ['k1','match','1234','4','How does specialty and career advising work? Who advised you, and how useful was it?'],
  ['k12','match','1234','4','Broadly speaking, how do you feel about the success of students at your medical school in the match? While there is always going to be variation in the match rate across specialties, did you feel there were specialties that were difficult to match into from your medical school? Or residency programs/institutions that were difficult to match to from your medical school?'],
  ['k13','match','4','4','Are you happy with the extent to which your school supported you in your efforts to match at the program of your choice (in terms of letters of recommendation, phone calls to program leadership, providing general guidance, etc.)?'],
  ['k14','match','1234','','Are there specialties at your school that are particularly strong and therefore typically garner a lot of interest amongst students?'],

  ['x1','big','1234','','What do you think is a shortcoming of your school or an area that could be improved? Be specific.'],
  ['x2','big','1234','1234','Who thrives here, and who would be happier somewhere else?'],
  ['x3','big','1234','1234','Why did you choose this school over your other options, and would you make the same choice today?'],
  ['x4','big','1234','1234','Have there been moments or experiences you\'ve had that made you glad you chose this medical school/reaffirmed your choice? Have there been some moments that made you question it?'],
  ['x5','big','1234','','What has been different from what you expected based on interview day or the school\'s materials, for better or worse?'],
  ['x6','big','1234','','What is one thing about this school that deserves more credit than it gets?'],
];

const byId = {}; Q.forEach(q => { byId[q[0]] = q; });
const catLabel = {}; CATS.forEach(c => { catLabel[c[0]] = c[1]; });
const fociRow = {}; FOCI.forEach(f => { fociRow[f[0]] = f; });

/* ---------- State (draft saved in this browser) ---------- */
const KEY = 'docstory-contribute-v1';
const blank = () => ({ step: 1, school: '', schoolOther: '', degree: '', year: '', focus: '', credit: 'named', name: '',
  gradYear: '', email: '', undergrad: '', hometown: '', consent: false, terms: false, picks: [], own: '', answers: {}, qi: 0 });
let S = blank();
let submitted = null;   // { ref, text } after a successful submission

(function load() {
  try {
    const d = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (d) Object.keys(S).forEach(k => { if (d[k] !== undefined) S[k] = d[k]; });
  } catch (e) { /* storage blocked or corrupt: start fresh */ }
  if (OLD_FOCUS[S.focus]) S.focus = OLD_FOCUS[S.focus];
  if (!Array.isArray(S.picks)) S.picks = [];
  S.picks = S.picks.filter(id => id === 'own' || byId[id]);
  if (!S.answers || typeof S.answers !== 'object') S.answers = {};
})();
let saveT;
function save() {
  clearTimeout(saveT);
  saveT = setTimeout(() => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* ignore */ } }, 250);
}

const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const words = s => (String(s || '').trim().match(/\S+/g) || []).length;
const yearRow = () => YEARS.find(y => y[0] === S.year) || null;

/* ---------- School helpers ---------- */
const isOther = () => S.school === 'other';
const schoolName = () => isOther() ? S.schoolOther.trim() : ((D.bySlug[S.school] || {}).name || '');
const schoolType = () => isOther() ? S.degree : ((D.bySlug[S.school] || {}).type || '');
function stageLabel() {
  const row = yearRow(); if (!row) return '';
  return schoolType() === 'do' ? row[5] : row[4];
}
function creditName() {
  if (S.credit === 'anon') return 'Anonymous';
  return S.credit === 'first' ? S.name.trim().split(/\s+/)[0] : S.name.trim();
}
const creditLine = () => creditName() + (stageLabel() ? ' · ' + stageLabel() : '');

/* ---------- Questions a student sees ---------- */
const pool = d => Q.filter(q => q[2].indexOf(d) > -1);
function suggested(d, focus) {
  const p = pool(d);
  const core = p.filter(q => q[3].indexOf(d) > -1);
  if (focus === 'general') return core;
  const out = p.filter(q => q[1] === focus);
  p.filter(q => q[1] === 'big').slice(0, 3).forEach(q => { if (out.indexOf(q) < 0) out.push(q); });
  core.forEach(q => { if (out.length < 12 && out.indexOf(q) < 0) out.push(q); });
  return out;
}
function orderedPicks() {
  const ids = Q.map(q => q[0]).filter(id => S.picks.indexOf(id) > -1);
  if (S.picks.indexOf('own') > -1 && S.own.trim()) ids.push('own');
  return ids;
}
const pickOk = () => S.picks.length >= MIN_PICK && S.picks.length <= MAX_PICK;
const qText = id => id === 'own' ? S.own.trim() : byId[id][4];
const qCat = id => id === 'own' ? 'Your question' : catLabel[byId[id][1]];

/* ---------- Payment display ---------- */
function spotsLeft(count) {
  const n = Math.max(0, C.paidCap - count);
  return 'This school has ' + n + ' paid spot' + (n === 1 ? '' : 's') + ' left.';
}
function payInfo() {
  if (!S.school || (isOther() && !S.schoolOther.trim())) return null;
  const st = D.payStatus(S.school);
  const name = schoolName();
  if (st.reason === 'off') return null;
  if (st.paid) {
    return { paid: true, html: '<span class="material-symbols-outlined" aria-hidden="true">check_circle</span><span>Interviews from <b>' + esc(name) +
      '</b> are eligible for <b>' + D.money(C.payAmount) + '</b>, paid once your interview is verified and published.' +
      (st.reason === 'new' ? ' We’ll confirm eligibility for schools we don’t cover yet when we review.'
        : ' ' + spotsLeft(st.count) + ' Paid spots go to the first interviews we accept.') + '</span>' };
  }
  return { paid: false, html: '<span class="material-symbols-outlined" aria-hidden="true">info</span><span>We already have ' + st.count + ' interviews from <b>' + esc(name) +
    '</b>, so new ones from this school aren’t paid right now. You’re still very welcome to contribute: another perspective helps applicants.</span>' };
}
/* The notice fades in rather than changing letter by letter. While someone types an
   unlisted school's name it stays hidden, then appears once they pause (delay in ms). */
let payTimer = null, payShown = '';
function showNotice(info) {
  const n = $('payNotice');
  if (!info) { n.hidden = true; payShown = ''; return; }
  if (info.html === payShown && !n.hidden) return;          // unchanged: don't replay the fade
  payShown = info.html;
  n.className = 'notice ' + (info.paid ? 'paid' : 'cap');
  n.innerHTML = info.html;
  n.hidden = false;
  void n.offsetWidth;                                       // restart the animation
  n.classList.add('fade-in');
}
function renderPay(delay = 0) {
  const info = payInfo(), n = $('payNotice'), b = $('paybadge');
  clearTimeout(payTimer);
  if (delay) { n.hidden = true; payShown = ''; payTimer = setTimeout(() => showNotice(info), delay); }
  else showNotice(info);
  // Long label on wide screens, short one on phones so the progress bar stays one line
  const badge = (long, short) => '<span class="long">' + long + '</span><span class="short" aria-hidden="true">' + short + '</span>';
  if (!info) { b.hidden = !C.payEnabled; b.className = 'paybadge'; b.innerHTML = badge(D.money(C.payAmount) + ' per published interview', D.money(C.payAmount)); return; }
  b.hidden = false;
  b.className = 'paybadge' + (info.paid ? '' : ' off');
  b.innerHTML = info.paid ? badge(D.money(C.payAmount) + ' once published', D.money(C.payAmount)) : badge('Unpaid for this school', 'Unpaid');
}

/* ---------- Step 1 ---------- */
function buildStep1() {
  $('intro').textContent = 'Pick ' + MIN_PICK + ' to ' + MAX_PICK + ' questions that fit your year, then answer them in your own words. Plan for 30 to 45 minutes. Your draft saves in this browser, so you can stop and come back.';
  $('school').innerHTML = '<option value="">Select your school</option>' +
    '<option value="other">Other (school not listed)</option>' +
    '<optgroup label="Schools on DocStory">' +
    D.schools.map(s => '<option value="' + s.slug + '">' + esc(s.name) + '</option>').join('') +
    '</optgroup>';
  $('years').innerHTML = YEARS.map(y =>
    '<label class="opt"><input type="radio" name="year" id="year-' + y[0] + '" value="' + y[0] + '"><b>' + y[2] + '</b><span>' + y[3] + '</span></label>').join('');
  $('foci').innerHTML = FOCI.map(f =>
    '<label class="opt"><input type="radio" name="focus" id="focus-' + f[0] + '" value="' + f[0] + '"><b>' + f[1] + '</b><span>' + f[2] + '</span></label>').join('');
  const now = new Date().getFullYear();
  let o = '<option value="">Select</option>';
  for (let y = now; y <= now + 5; y++) o += '<option value="' + y + '">Class of ' + y + '</option>';
  $('gradYear').innerHTML = o;

  $('school').value = S.school; if ($('school').value !== S.school) S.school = '';
  ['schoolOther', 'name', 'email', 'undergrad', 'hometown'].forEach(k => { $(k).value = S[k]; });
  $('gradYear').value = S.gradYear; if ($('gradYear').value !== S.gradYear) S.gradYear = '';
  if (S.degree && $('degree-' + S.degree)) $('degree-' + S.degree).checked = true;
  if (S.year && $('year-' + S.year)) $('year-' + S.year).checked = true;
  if (S.focus && $('focus-' + S.focus)) $('focus-' + S.focus).checked = true;
  if ($('credit-' + S.credit)) $('credit-' + S.credit).checked = true;
  refreshStep1();
}
function refreshStep1(payDelay = 0) {
  $('schoolOtherWrap').hidden = !isOther();
  const stage = stageLabel() || 'MS3';
  const sample = { named: 'Jordan Lee · ', first: 'Jordan · ', anon: 'Anonymous · ' };
  Object.keys(sample).forEach(k => { const el = document.querySelector('#credit-' + k + ' ~ span'); if (el) el.textContent = sample[k] + stage; });
  const p = $('publishAs');
  if (S.name.trim() && S.year) p.innerHTML = 'Published as: <b>' + esc(creditLine()) + '</b>' + (schoolName() ? ' at ' + esc(schoolName()) : '');
  else p.textContent = 'Add your name and year to preview how your credit will read.';
  renderPay(payDelay);
}
function readStep1() {
  S.school = $('school').value;
  S.schoolOther = $('schoolOther').value.trim();
  const dg = document.querySelector('input[name=degree]:checked'); S.degree = dg ? dg.value : '';
  ['name', 'email', 'undergrad', 'hometown'].forEach(k => { S[k] = $(k).value.trim(); });
  S.gradYear = $('gradYear').value;
  const f = document.querySelector('input[name=focus]:checked'); S.focus = f ? f.value : '';
  const c = document.querySelector('input[name=credit]:checked'); S.credit = c ? c.value : 'named';
  const y = document.querySelector('input[name=year]:checked'); const newYear = y ? y.value : '';
  if (newYear !== S.year) {
    S.year = newYear;
    const row = yearRow();
    if (row) S.picks = S.picks.filter(id => id === 'own' || byId[id][2].indexOf(row[1]) > -1);
  }
}
function step1Problem() {
  if (!S.school) return ['Choose your medical school.', 'school'];
  if (isOther() && !S.schoolOther) return ['Add the name of your school.', 'schoolOther'];
  if (isOther() && !S.degree) return ['Choose MD or DO.', 'degree-md'];
  if (!S.year) return ['Choose your year in medical school.', 'year-m1'];
  if (!S.focus) return ['Choose what you want to talk about most.', 'focus-general'];
  if (!S.name || S.name.split(/\s+/).length < 2) return ['Add your full name (first and last). It’s only published if you choose full-name credit.', 'name'];
  if (!S.gradYear) return ['Select your expected graduation year.', 'gradYear'];
  if (!EDU_RE.test(S.email)) return ['Use your school email address ending in .edu. We verify it before publishing.', 'email'];
  return null;
}

/* ---------- Step 2 ---------- */
function qItem(q) {
  const on = S.picks.indexOf(q[0]) > -1;
  return '<li><label class="q' + (on ? ' on' : '') + '" for="q-' + q[0] + '"><input type="checkbox" id="q-' + q[0] + '" value="' + q[0] + '"' + (on ? ' checked' : '') + '>' +
    '<span>' + q[4] + '</span><span class="chip">' + catLabel[q[1]] + '</span></label></li>';
}
function buildStep2() {
  const row = yearRow(), d = row[1];
  const sug = suggested(d, S.focus);
  const rest = pool(d).filter(q => sug.indexOf(q) < 0);
  $('s2head').textContent = 'Suggested questions for ' + row[6] + (S.focus === 'general' ? '' : ' focused on ' + fociRow[S.focus][3]);
  $('s2sub').textContent = 'Select any ' + RANGE + ' questions from these suggestions or from the other topics below.';
  let h = '<ul class="qs">' + sug.map(qItem).join('') + '</ul>';
  h += '<div class="group"><h3>Other topics</h3><div class="group" style="gap:8px">';
  CATS.forEach(c => {
    const qs = rest.filter(q => q[1] === c[0]);
    if (!qs.length) return;
    h += '<details class="more"><summary><span>' + c[1] + '</span><span class="count" data-cat="' + c[0] + '" data-n="' + qs.length + '"></span></summary><ul class="qs">' + qs.map(qItem).join('') + '</ul></details>';
  });
  h += '</div></div>';
  const ownOn = S.picks.indexOf('own') > -1 && S.own.trim();
  h += '<div class="group"><h3>Add your own question</h3><div class="ownrow"><input type="checkbox" id="q-own" value="own" aria-label="Include my own question"' + (ownOn ? ' checked' : '') + '>' +
       '<input type="text" id="own-text" maxlength="220" placeholder="A question applicants should be asking about your school" aria-label="Your own question" value="' + esc(S.own) + '"></div></div>';
  $('qlist').innerHTML = h;
  tally();
}
function tally() {
  const n = S.picks.length, full = n >= MAX_PICK;
  $('tallyN').textContent = n + ' selected';
  $('tallyH').textContent = n < MIN_PICK ? 'Select at least ' + (MIN_PICK - n) + ' more.' : (full ? 'That’s the maximum. Uncheck one to swap.' : 'You can continue, or add up to ' + (MAX_PICK - n) + ' more.');
  $('go3').disabled = !pickOk();
  $('qlist').classList.toggle('full', full);
  $('qlist').querySelectorAll('input[type=checkbox]').forEach(el => { el.disabled = full && !el.checked; });
  $('qlist').querySelectorAll('[data-cat]').forEach(el => {
    const k = el.closest('details').querySelectorAll('input:checked').length;
    el.textContent = (k ? k + ' selected · ' : '') + el.getAttribute('data-n') + ' questions';
  });
}
$('qlist').addEventListener('change', e => {
  const el = e.target; if (el.type !== 'checkbox') return;
  const id = el.value;
  if (el.checked) {
    if (S.picks.length >= MAX_PICK) { el.checked = false; return; }
    if (id === 'own' && !$('own-text').value.trim()) { el.checked = false; $('own-text').focus(); return; }
    if (S.picks.indexOf(id) < 0) S.picks.push(id);
  } else {
    S.picks = S.picks.filter(x => x !== id);
  }
  const lab = el.closest('.q'); if (lab) lab.classList.toggle('on', el.checked);
  tally(); save();
});
$('qlist').addEventListener('input', e => {
  if (e.target.id !== 'own-text') return;
  S.own = e.target.value;
  if (!S.own.trim() && S.picks.indexOf('own') > -1) { S.picks = S.picks.filter(x => x !== 'own'); $('q-own').checked = false; tally(); }
  save();
});

/* ---------- Step 3 ---------- */
function wcText(n) {
  if (n === 0) return 'Aim for 100 to 200 words. Minimum ' + MIN_WORDS + '.';
  if (n < MIN_WORDS) return n + ' words. ' + (MIN_WORDS - n) + ' more to reach the minimum.';
  return n + ' words';
}
function buildStep3() {
  const ids = orderedPicks();
  $('alist').innerHTML = ids.map((id, i) => {
    const a = S.answers[id] || '', n = words(a);
    return '<div class="acard" id="card-' + id + '"><div class="acard-top"><span class="chip">Question ' + (i + 1) + ' of ' + ids.length + '</span><span class="chip">' + esc(qCat(id)) + '</span></div>' +
      '<label class="qtext" for="ans-' + id + '">' + esc(qText(id)) + '</label>' +
      '<textarea class="in" id="ans-' + id + '" data-id="' + id + '" rows="6">' + esc(a) + '</textarea>' +
      '<span class="wc' + (n >= MIN_WORDS ? ' ok' : (n ? ' short' : '')) + '" id="wc-' + id + '">' + wcText(n) + '</span></div>';
  }).join('');
}
function grow(t) { t.style.height = 'auto'; t.style.height = Math.max(160, t.scrollHeight + 2) + 'px'; }

/* On phones, step 3 shows one question at a time with a progress bar; wider screens list them all */
const phone = window.matchMedia('(max-width: 640px)');
const paged = () => phone.matches && orderedPicks().length > 1;
const answeredCount = ids => ids.filter(id => words(S.answers[id]) >= MIN_WORDS).length;
function showQuestion(i, focus) {
  const ids = orderedPicks(); if (!ids.length) return;
  const on = paged(), qi = Math.max(0, Math.min(i || 0, ids.length - 1)), last = qi === ids.length - 1;
  S.qi = qi;
  $('s3').classList.toggle('paged', on);
  $('qprog').hidden = !on;
  document.querySelector('#s3 .tips').hidden = on && qi > 0;
  ids.forEach((id, k) => { $('card-' + id).hidden = on && k !== qi; });
  $('changeQs').hidden = on && qi > 0;
  $('qprev').hidden = !on || qi === 0;
  $('qnext').hidden = !on || last;
  $('go4').hidden = on && !last;
  if (!on) return;
  $('qprogLabel').textContent = 'Question ' + (qi + 1) + ' of ' + ids.length;
  $('qprogDone').textContent = answeredCount(ids) + ' of ' + ids.length + ' answered';
  $('qprogFill').style.width = ((qi + 1) / ids.length * 100) + '%';
  $('qprogBar').setAttribute('aria-valuemax', ids.length);
  $('qprogBar').setAttribute('aria-valuenow', qi + 1);
  const t = $('ans-' + ids[qi]); grow(t);
  if (focus) t.focus({ preventScroll: true });
}
function stepQuestion(delta) {
  showQuestion(S.qi + delta, true); save();
  $('s3').scrollIntoView({ block: 'start' });
}
$('qprev').addEventListener('click', () => stepQuestion(-1));
$('qnext').addEventListener('click', () => stepQuestion(1));
phone.addEventListener('change', () => { if (S.step === 3) showQuestion(S.qi); });
$('alist').addEventListener('input', e => {
  const t = e.target; if (t.tagName !== 'TEXTAREA') return;
  const id = t.getAttribute('data-id'); S.answers[id] = t.value;
  const n = words(t.value), w = $('wc-' + id);
  w.textContent = wcText(n); w.className = 'wc' + (n >= MIN_WORDS ? ' ok' : (n ? ' short' : ''));
  if (n >= MIN_WORDS) $('card-' + id).classList.remove('bad');
  if (paged()) $('qprogDone').textContent = answeredCount(orderedPicks()) + ' of ' + orderedPicks().length + ' answered';
  grow(t); save();
});
const shortAnswers = () => orderedPicks().filter(id => words(S.answers[id]) < MIN_WORDS);

/* ---------- Step 4 ---------- */
function buildStep4() {
  const ids = orderedPicks(), total = ids.reduce((s, id) => s + words(S.answers[id]), 0);
  $('sum').innerHTML = [['School', schoolName()], ['Published as', creditLine()], ['Verification email', S.email], ['Length', ids.length + ' answers · ' + total + ' words']]
    .map(r => '<div><dt>' + r[0] + '</dt><dd>' + esc(r[1]) + '</dd></div>').join('');
  const info = payInfo(), pr = $('payReview');
  pr.hidden = !info;
  if (info) {
    pr.className = 'notice ' + (info.paid ? 'paid' : 'cap');
    pr.innerHTML = info.paid
      ? '<span class="material-symbols-outlined" aria-hidden="true">payments</span><span>You’ll receive <b>' + D.money(C.payAmount) + '</b> within ' + C.payDays + ' days of your interview being published. You’ll choose ' + esc(C.payMethods) + ' when you reply to our verification email.</span>'
      : info.html;
  }
  $('rlist').innerHTML = ids.map((id, i) =>
    '<div class="acard"><div class="acard-top"><span class="chip">Question ' + (i + 1) + '</span><span class="chip">' + esc(qCat(id)) + '</span></div>' +
    '<p class="qtext">' + esc(qText(id)) + '</p><p class="ans">' + esc(S.answers[id] || '') + '</p></div>').join('');
  $('consent').checked = !!S.consent;
  $('terms').checked = !!S.terms;
  loadCaptcha();
}
$('consent').addEventListener('change', () => { S.consent = $('consent').checked; save(); });
$('terms').addEventListener('change', () => { S.terms = $('terms').checked; save(); });

/* hCaptcha spam check, loaded only when someone reaches the last step */
let captchaId = null, captchaState = 'idle';   // idle | loading | ready | failed
function loadCaptcha() {
  if (!C.web3formsKey || captchaState !== 'idle') return;
  captchaState = 'loading';
  window.dsCaptchaReady = () => {
    try { captchaId = window.hcaptcha.render('captcha', { sitekey: HCAPTCHA_SITEKEY }); captchaState = 'ready'; }
    catch (e) { captchaState = 'failed'; }
  };
  const s = document.createElement('script');
  s.src = 'https://js.hcaptcha.com/1/api.js?render=explicit&onload=dsCaptchaReady';
  s.async = true;
  s.onerror = () => { captchaState = 'failed'; };
  document.head.appendChild(s);
}

/* ---------- Building the submission ---------- */
function makeRef() {
  const A = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';   // no 0/O or 1/I/L, so it reads clearly in email
  const r = new Uint32Array(4); crypto.getRandomValues(r);
  const d = new Date(), pad = n => String(n).padStart(2, '0');
  return 'DS-' + String(d.getFullYear()).slice(2) + pad(d.getMonth() + 1) + pad(d.getDate()) + '-' + Array.from(r, x => A[x % A.length]).join('');
}
const slugify = s => String(s).toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const yq = s => '"' + String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"';

function interviewMarkdown(ref, today) {
  const ids = orderedPicks();
  const lines = ['---', 'name: ' + yq(creditName()), 'school: ' + yq(schoolName()),
    'school_slug: ' + yq(isOther() ? slugify(schoolName()) : S.school), 'year: ' + yq(stageLabel())];
  if (S.undergrad) lines.push('undergraduate: ' + yq(S.undergrad));
  if (S.hometown) lines.push('hometown: ' + yq(S.hometown));
  lines.push('date: ' + yq(today), 'contributor_ref: ' + yq(ref), '---', '',
    '# ' + creditName() + ', ' + stageLabel() + ' — ' + schoolName(), '');
  ids.forEach(id => { lines.push('**Q: ' + qText(id) + '**', '', (S.answers[id] || '').trim(), ''); });
  return lines.join('\n').trim() + '\n';
}
function plainText(ref) {
  const ids = orderedPicks();
  const out = ['DocStory interview · ' + ref, schoolName() + ' · ' + stageLabel(), 'Published as: ' + creditLine(), ''];
  ids.forEach((id, i) => { out.push('Q' + (i + 1) + '. ' + qText(id), (S.answers[id] || '').trim(), ''); });
  return out.join('\n').trim();
}
function suggestedPath() {
  const slug = isOther() ? slugify(schoolName()) : S.school;
  // Full name keeps file names unique; it never appears on the page unless credited
  const who = S.credit === 'anon' ? 'anonymous-' + stageLabel().toLowerCase() : slugify(S.name);
  return 'content/interviews/' + slug + '/' + who + '.md';
}

async function submit() {
  if (!$('consent').checked || !$('terms').checked) return showErr('e4', 'Tick both boxes above to send your interview.');
  if (!C.web3formsKey) {
    console.warn('DocStory: set web3formsKey in js/contribute-config.js to enable submissions.');
    return showErr('e4', 'Submissions are temporarily unavailable. Your draft is saved, so please try again later.');
  }
  let token = '';
  if (captchaState === 'ready') {
    token = window.hcaptcha.getResponse(captchaId);
    if (!token) return showErr('e4', 'Please complete the “I am human” check above.');
  }
  showErr('e4', '');

  const ref = makeRef(), now = new Date();
  const today = now.getFullYear() + '-' + String(now.getMonth() + 1).padStart(2, '0') + '-' + String(now.getDate()).padStart(2, '0');
  const st = D.payStatus(S.school);
  const payLine = st.reason === 'off' ? 'Payment program off'
    : st.paid ? 'ELIGIBLE · ' + D.money(C.payAmount) + (st.reason === 'new' ? ' · school not yet on DocStory (confirm)' : ' · ' + st.count + ' published from this school (cap ' + C.paidCap + ')')
    : 'NOT ELIGIBLE · ' + st.count + ' published from this school (cap ' + C.paidCap + ')';
  const ids = orderedPicks();
  const fd = new FormData();
  fd.append('access_key', C.web3formsKey);
  fd.append('subject', 'Interview ' + ref + ' · ' + schoolName() + ' · ' + stageLabel() + ' · ' + (st.paid ? 'Paid ' + D.money(C.payAmount) : 'Unpaid'));
  fd.append('from_name', 'DocStory Contribute');
  fd.append('email', S.email);                       // reply-to: replying starts verification
  fd.append('Reference', ref);
  fd.append('Payment', payLine);
  fd.append('School', schoolName() + (isOther() ? ' (not listed · ' + S.degree.toUpperCase() + ')' : ''));
  fd.append('Year', stageLabel() + ' · Class of ' + S.gradYear);
  fd.append('Full name (private)', S.name);
  fd.append('School email (verify)', S.email);
  fd.append('Publish credit as', creditLine());
  fd.append('Focus', fociRow[S.focus][1]);
  if (S.undergrad) fd.append('Undergraduate', S.undergrad);
  if (S.hometown) fd.append('Hometown', S.hometown);
  fd.append('Submitted', today);
  fd.append('Came from', window.DocStoryTrack ? window.DocStoryTrack.source() : 'Unknown');
  fd.append('Answers', ids.length + ' answers · ' + ids.reduce((s, id) => s + words(S.answers[id]), 0) + ' words');
  fd.append('Consent', 'Own experience, no patient information, may be published and edited · Agreed to Contributor Terms');
  fd.append('Interview', plainText(ref));
  fd.append('Interview file path', suggestedPath());
  fd.append('Interview file (markdown)', interviewMarkdown(ref, today));
  if (token) fd.append('h-captcha-response', token);
  fd.append('botcheck', '');

  const btn = $('submit');
  btn.disabled = true;
  btn.innerHTML = '<span class="spin" aria-hidden="true"></span> Sending…';
  try {
    const res = await fetch(W3F_URL, { method: 'POST', body: fd, headers: { Accept: 'application/json' } });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || data.success === false) throw new Error(data.message || ('HTTP ' + res.status));
  } catch (err) {
    console.warn('DocStory submission failed:', err);
    btn.disabled = false; btn.textContent = 'Submit interview';
    if (captchaState === 'ready') window.hcaptcha.reset(captchaId);
    return showErr('e4', 'We couldn’t send your interview. Your draft is saved. Check your connection and try again' +
      (C.contactEmail ? ', or email ' + C.contactEmail + ' if it keeps failing.' : '.'));
  }

  submitted = { ref, text: plainText(ref), paid: st.paid };
  try { localStorage.removeItem(KEY); } catch (e) { /* ignore */ }
  showDone();
}
$('submit').addEventListener('click', submit);

/* ---------- Done ---------- */
function showDone() {
  $('refOut').textContent = submitted.ref;
  $('out').value = submitted.text;
  const paid = submitted.paid && C.payEnabled;
  $('doneStep3').textContent = paid ? 'Published and paid' : 'Published';
  $('doneStep3Text').textContent = paid
    ? 'Once you approve, your interview goes live and we send ' + D.money(C.payAmount) + ' by ' + C.payMethods + ' within ' + C.payDays + ' days.'
    : 'Once you approve, your interview goes live on DocStory and we email you the link.';
  for (let i = 1; i <= 5; i++) $('s' + i).hidden = i !== 5;
  document.querySelector('.rail').hidden = true;
  window.scrollTo(0, 0);
}
$('copy').addEventListener('click', () => {
  const out = $('out'), msg = $('copyMsg');
  const fallback = () => { out.focus(); out.select(); msg.textContent = 'Text selected. Press Ctrl or Cmd + C to copy.'; };
  try { navigator.clipboard.writeText(out.value).then(() => { msg.textContent = 'Copied.'; }, fallback); } catch (e) { fallback(); }
});

/* ---------- Navigation ---------- */
function showErr(id, msg) { const e = $(id); e.textContent = msg; e.hidden = !msg; }
function reach() {
  if (step1Problem()) return 1;
  if (!pickOk()) return 2;
  if (shortAnswers().length) return 3;
  return 4;
}
function go(n) {
  if (n === 2) buildStep2();
  if (n === 3) buildStep3();
  if (n === 4) buildStep4();
  for (let i = 1; i <= 5; i++) $('s' + i).hidden = i !== n;
  S.step = n; save();
  const max = reach();
  $('steps').querySelectorAll('button').forEach(b => {
    const k = +b.getAttribute('data-go');
    b.className = k === n ? 'cur' : (k < n ? 'done' : '');
    b.disabled = k > max && k !== n;
    if (k === n) b.setAttribute('aria-current', 'step'); else b.removeAttribute('aria-current');
  });
  if (n === 3) { $('alist').querySelectorAll('textarea').forEach(grow); showQuestion(S.qi); }
  window.scrollTo(0, 0);
}
function tryGo(n) {
  if (S.step === 1) readStep1();
  if (n > 1) {
    const p = step1Problem();
    if (p) { if (S.step !== 1) go(1); showErr('e1', p[0]); const el = $(p[1]); if (el) el.focus(); return; }
    showErr('e1', '');
  }
  if (n > 2 && !pickOk()) { go(2); return; }
  if (n > 3) {
    const bad = shortAnswers();
    if (bad.length) {
      if (S.step !== 3) go(3);
      bad.forEach(id => $('card-' + id).classList.add('bad'));
      if (paged()) showQuestion(orderedPicks().indexOf(bad[0]));
      showErr('e3', bad.length === 1
        ? '1 answer is under ' + MIN_WORDS + ' words. ' + (paged() ? 'It’s shown above.' : 'It’s outlined above.')
        : bad.length + ' answers are under ' + MIN_WORDS + ' words. ' + (paged() ? 'Here’s the first one.' : 'They’re outlined above.'));
      $('ans-' + bad[0]).focus(); return;
    }
    showErr('e3', '');
  }
  go(n);
}
document.addEventListener('click', e => {
  const b = e.target.closest('[data-go]'); if (!b || b.disabled) return;
  tryGo(+b.getAttribute('data-go'));
});
$('f1').addEventListener('submit', e => { e.preventDefault(); tryGo(2); });
function step1Changed(e) { readStep1(); refreshStep1(e && e.target.id === 'schoolOther' ? 700 : 0); if (!$('e1').hidden && !step1Problem()) showErr('e1', ''); save(); }
$('f1').addEventListener('input', step1Changed);
$('f1').addEventListener('change', step1Changed);
$('go3').addEventListener('click', () => tryGo(3));
$('go4').addEventListener('click', () => tryGo(4));

/* ---------- In-app browsers ----------
   Links tapped inside apps like Reddit open in the app's own browser, which may throw away the saved
   draft when someone switches apps. Suggest opening the page in a regular browser before writing. */
(function appNote() {
  try { if (sessionStorage.getItem('appnoteSeen') === '1') return; } catch (e) { /* ignore */ }
  const ua = navigator.userAgent || '';
  const app = /Reddit/i.test(ua) ? 'Reddit' : /Instagram/i.test(ua) ? 'Instagram' : /FBAN|FBAV|FB_IAB/.test(ua) ? 'Facebook'
    : /LinkedInApp/i.test(ua) ? 'LinkedIn' : /Snapchat/i.test(ua) ? 'Snapchat' : /TikTok|musical_ly|BytedanceWebview/i.test(ua) ? 'TikTok' : '';
  let canSave = true;
  try { localStorage.setItem('ds-storage-test', '1'); localStorage.removeItem('ds-storage-test'); } catch (e) { canSave = false; }
  if (!app && canSave) return;
  $('appnoteText').textContent = !canSave
    ? 'This browser isn’t letting us save your draft. Open this page in Safari or Chrome before you start writing so you don’t lose your work.'
    : 'You’re in the ' + app + ' app’s browser, which may not keep your draft if you switch away. To be safe, tap the ⋯ menu and choose “Open in browser” before you start writing.';
  $('appnote').hidden = false;
  $('appnoteClose').addEventListener('click', () => {
    $('appnote').hidden = true;
    try { sessionStorage.setItem('appnoteSeen', '1'); } catch (e) { /* ignore */ }
  });
})();

/* ---------- Start ---------- */
(function preset() {
  // Recruiting links can preselect fields: /contribute/interview/?school=rush-medical-college&year=m3&focus=clin
  const p = new URLSearchParams(location.search);
  const sc = (p.get('school') || '').toLowerCase(), y = (p.get('year') || '').toLowerCase();
  let f = (p.get('focus') || '').toLowerCase(); f = OLD_FOCUS[f] || f;
  if (!S.school && D.bySlug[sc]) S.school = sc;
  if (!S.year && YEARS.some(v => v[0] === y)) S.year = y;
  if (!S.focus && fociRow[f]) S.focus = f;
})();
D.fill();
buildStep1();
go(Math.max(1, Math.min(S.step || 1, reach(), 4)));
})();
