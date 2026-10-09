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
  ['m1', '1', 'First year',  'Foundations',            'MS1', 'OMS-I',   'a first-year student'],
  ['m2', '2', 'Second year', 'Boards on the horizon',  'MS2', 'OMS-II',  'a second-year student'],
  ['m3', '3', 'Third year',  'Clerkships',             'MS3', 'OMS-III', 'a third-year student'],
  ['m4', '4', 'Fourth year', 'Sub-Is and the Match',   'MS4', 'OMS-IV',  'a fourth-year student'],
];
const CATS = [
  ['academics', 'Curriculum & academics'],
  ['clinical', 'Clinical training'],
  ['research', 'Research'],
  ['service', 'Community service & advocacy'],
  ['global', 'Global health'],
  ['life', 'Student life & support'],
  ['career', 'Advising, boards & the Match'],
  ['candid', 'Straight talk'],
];
/* [id, label, description, how it reads after "who wants to focus on"] */
const FOCI = [
  ['general', 'A bit of everything', 'Good default if you’re not sure', ''],
  ['academics', 'Curriculum & academics', 'Teaching, grading, exams', 'curriculum and academics'],
  ['clinical', 'Clinical training', 'Rotations, sites, hands-on work', 'clinical training'],
  ['research', 'Research', 'Mentors, funding, publishing', 'research'],
  ['service', 'Community service & advocacy', 'Free clinics, outreach, equity', 'community service and advocacy'],
  ['global', 'Global health', 'Electives abroad, partner sites', 'global health'],
  ['life', 'Student life & support', 'Culture, cost, wellbeing', 'student life and support'],
  ['career', 'Advising, boards & the Match', 'Step prep, advising, residency', 'advising, boards and the Match'],
];

/* ---------- Question bank (to be refined) ----------
   [id, topic, years it's offered to, years it's a core suggestion for, question]
   Years: 1 = first year … 4 = fourth year */
const Q = [
  ['a1','academics','12','12','Walk us through a typical week in the preclinical curriculum. How much is lecture, small group, lab, and self-study?'],
  ['a2','academics','1234','1234','How are the preclinical years graded (pass/fail, tiers, internal ranking), and how does that shape the way classmates treat each other?'],
  ['a3','academics','12','','Is lecture attendance required? What do most of your classmates actually do: attend, stream, or study from outside resources?'],
  ['a4','academics','1','1','What was the adjustment to the first semester like, and what would you tell an incoming student to do differently?'],
  ['a5','academics','12','','How is anatomy taught (dissection, prosection, virtual), and how well did it work for you?'],
  ['a6','academics','234','2','How well did the curriculum prepare you for Step 1 or Level 1? How much dedicated study time did you get, and was it enough?'],
  ['a7','academics','1234','','Which course, block, or professor has been the best part of the curriculum, and why?'],
  ['a8','academics','1234','','Which part of the curriculum would you redesign, and what specifically is not working?'],
  ['a9','academics','12','','How early do students see patients, and what does that early exposure actually involve?'],
  ['a10','academics','234','','How responsive is the administration to student feedback? Give an example of something that changed, or did not, after students spoke up.'],
  ['a11','academics','34','3','Looking back, how well did the preclinical years prepare you for the wards? Where did you feel ahead or behind?'],
  ['a12','academics','1234','','What support exists for students who are struggling academically (tutoring, learning specialists, remediation), and do people use it?'],

  ['c1','clinical','34','34','Where do students rotate? Describe the main hospitals and clinics and the patients you see at each.'],
  ['c2','clinical','34','34','How much hands-on responsibility do students get on clerkships? Give an example of something you did yourself rather than watched.'],
  ['c3','clinical','34','','How are clerkships graded, and how fair does it feel? How much rides on evaluations versus shelf exams?'],
  ['c4','clinical','34','','Which rotation was your strongest and which was your weakest, and what made the difference?'],
  ['c5','clinical','34','','How are rotation sites and schedules assigned? Did you get what you wanted, and how much travel or relocation was involved?'],
  ['c6','clinical','34','','How do residents and attendings treat students? Is teaching built in, or do you have to seek it out?'],
  ['c7','clinical','4','','How did the school support sub-internships and away rotations? Was it easy to get the electives your specialty required?'],
  ['c8','clinical','12','12','What clinical experience have you had before clerkships (preceptorships, student-run clinics, standardized patients, simulation)?'],
  ['c9','clinical','12','','How is clinical skills teaching organized, and how confident do you feel taking a history and doing a physical exam right now?'],
  ['c10','clinical','12','','What have older students told you about clerkships here? What are you looking forward to, and what worries you?'],
  ['c11','clinical','34','','Do students compete with residents, fellows, or other learners for patients and procedures? How does that play out day to day?'],
  ['c12','clinical','34','','How many hours does a typical clerkship week run, and how much time is left to study?'],
  ['c13','clinical','234','','How does the school handle the transition into clerkships (bootcamp, orientation, shadowing)? Did you, or do you expect to, feel ready on day one?'],

  ['r1','research','1234','1234','How easy is it to find a research mentor? Describe how you or a classmate actually got connected with one.'],
  ['r2','research','1234','','Is research required, optional, or built into the curriculum? How much protected time do students get?'],
  ['r3','research','12','','What does the summer after first year look like? Are there funded research programs, and how competitive are they?'],
  ['r4','research','1234','','What project have you worked on, and what did you personally do on it?'],
  ['r5','research','234','','How realistic is it to publish or present as a student here? What support exists for abstracts, posters, and conference travel?'],
  ['r6','research','1234','','Which departments or centers are strongest for student research, and which are hard to break into?'],
  ['r7','research','34','','Do many students take a research year or pursue a dual degree? How does the school support that, and what does it do to cost?'],
  ['r8','research','34','','How much did research matter for the specialties your classmates applied to, and did the school make it easy to build that record?'],
  ['r9','research','1234','','For someone arriving with no research background, what is the realistic path to getting started here?'],
  ['r10','research','1234','','Is there funding for student research (stipends, grants, travel awards)? How did you or classmates get it?'],

  ['s1','service','1234','1234','What community service or outreach are students involved in? Describe the one you know best and what the work looks like.'],
  ['s2','service','1234','','Is there a student-run free clinic? What do students at your level do there, and how hard is it to get a spot?'],
  ['s3','service','1234','','Who lives in the community around the school, and how does the school’s relationship with them show up in your training?'],
  ['s4','service','1234','','Is service required, tracked, or purely voluntary? Does the culture value it or treat it as a box to check?'],
  ['s5','service','1234','','Are there tracks, concentrations, or electives in health equity, advocacy, or policy? What do they involve?'],
  ['s6','service','1234','','Have students organized around an issue on campus or in the community? What happened?'],
  ['s7','service','34','','How did caring for underserved patients on rotations compare with how the school describes its mission?'],
  ['s8','service','12','','How much time do you realistically have for service alongside coursework, and what have you had to give up?'],
  ['s9','service','1234','','Which student organization does the most meaningful work, in your view, and why?'],

  ['g1','global','1234','','What global health opportunities are open to students (electives abroad, partner sites, tracks, certificates)?'],
  ['g2','global','1234','','Have you or a classmate done a rotation or project abroad? Where, for how long, and what was the work?'],
  ['g3','global','1234','','Who pays for global health experiences? Describe the funding that exists and what students cover themselves.'],
  ['g4','global','12','','When is the earliest a student can go abroad, and how do you apply?'],
  ['g5','global','34','','How do international electives fit into fourth year alongside sub-internships and interviews?'],
  ['g6','global','1234','','Does the school have long-standing partner sites, or do students arrange their own placements?'],
  ['g7','global','1234','','Is there local work with refugee, immigrant, or border communities? What do students do?'],
  ['g8','global','1234','','Which faculty do global health work that students can join, and how approachable are they?'],
  ['g9','global','1234','','How does the school prepare students for work abroad (ethics, language, safety), and was it adequate?'],
  ['g10','global','1234','','For an applicant who wants a career in global health, what makes this school a good or a poor choice?'],

  ['l1','life','1234','1234','How would you describe your class: collaborative, competitive, cliquey, close? Give an example that shows it.'],
  ['l2','life','1234','1234','What does a normal week look like outside of school? Where do you live, how do you get around, and what do you do for fun?'],
  ['l3','life','1234','','What is the cost of living like, and how do students manage housing and money on loans?'],
  ['l4','life','1234','','How does the school handle student wellbeing and mental health? Is help easy to get, and do people use it?'],
  ['l5','life','1234','','How diverse are your class and the faculty, and how supported do students from underrepresented backgrounds feel?'],
  ['l6','life','1234','','How accessible are deans and faculty? Is there someone in the administration you would go to with a problem?'],
  ['l7','life','1234','','What is it like here for students with partners, kids, or other obligations outside school?'],
  ['l8','life','1','1','What surprised you most in the first few months that you did not hear on interview day?'],
  ['l9','life','1234','','How is financial aid? Were scholarships and aid packages what you expected, and how helpful is the office?'],
  ['l10','life','1234','','What are the campus and facilities like (study space, library, gym, parking, safety)?'],

  ['k1','career','34','34','How does specialty and career advising work? Who advised you, and how useful was it?'],
  ['k2','career','4','4','How did the school support you through residency applications (letters, the MSPE, mock interviews, application review)?'],
  ['k3','career','4','','Does the school’s name, location, or home programs help or limit students in the Match? What have you seen?'],
  ['k4','career','34','','Is there a home residency program in the specialty you are interested in, and how has that mattered?'],
  ['k5','career','12','','How does the school help you explore specialties early (shadowing, interest groups, mentorship)?'],
  ['k6','career','234','','How does the school prepare students for Step 2 CK or Level 2, and how do students do?'],
  ['k9','career','4','','How open is the school about Match outcomes, including students who did not match?'],
  ['k10','career','1234','','How easy is it to find mentors, and are alumni involved with current students?'],
  ['k11','career','34','','How flexible is fourth year? What did you, or will you, do with elective time?'],

  ['x1','candid','1234','1234','What is the biggest downside of this school? Be specific.'],
  ['x2','candid','1234','1234','Who thrives here, and who would be happier somewhere else?'],
  ['x3','candid','1234','1234','Why did you choose this school, and would you choose it again?'],
  ['x4','candid','1234','1234','What do you know now that you wish you had known before you committed?'],
  ['x5','candid','1234','','What does the school advertise that does not match the day-to-day reality?'],
  ['x6','candid','1234','','What is one thing about this school that deserves more credit than it gets?'],
];

const byId = {}; Q.forEach(q => { byId[q[0]] = q; });
const catLabel = {}; CATS.forEach(c => { catLabel[c[0]] = c[1]; });
const fociRow = {}; FOCI.forEach(f => { fociRow[f[0]] = f; });

/* ---------- State (draft saved in this browser) ---------- */
const KEY = 'docstory-contribute-v1';
const blank = () => ({ step: 1, school: '', schoolOther: '', degree: '', year: '', focus: '', credit: 'named', name: '',
  gradYear: '', email: '', undergrad: '', hometown: '', consent: false, terms: false, picks: [], own: '', answers: {} });
let S = blank();
let submitted = null;   // { ref, text } after a successful submission

(function load() {
  try {
    const d = JSON.parse(localStorage.getItem(KEY) || 'null');
    if (d) Object.keys(S).forEach(k => { if (d[k] !== undefined) S[k] = d[k]; });
  } catch (e) { /* storage blocked or corrupt: start fresh */ }
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
  p.filter(q => q[1] === 'candid').slice(0, 3).forEach(q => { if (out.indexOf(q) < 0) out.push(q); });
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
function payInfo() {
  if (!S.school || (isOther() && !S.schoolOther.trim())) return null;
  const st = D.payStatus(S.school);
  const name = schoolName();
  if (st.reason === 'off') return null;
  if (st.paid) {
    return { paid: true, html: '<span class="material-symbols-outlined" aria-hidden="true">check_circle</span><span>Interviews from <b>' + esc(name) +
      '</b> are eligible for <b>' + D.money(C.payAmount) + '</b>, paid once your interview is verified and published.' +
      (st.reason === 'new' ? ' We’ll confirm eligibility for schools we don’t cover yet when we review.' : '') + '</span>' };
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
$('alist').addEventListener('input', e => {
  const t = e.target; if (t.tagName !== 'TEXTAREA') return;
  const id = t.getAttribute('data-id'); S.answers[id] = t.value;
  const n = words(t.value), w = $('wc-' + id);
  w.textContent = wcText(n); w.className = 'wc' + (n >= MIN_WORDS ? ' ok' : (n ? ' short' : ''));
  if (n >= MIN_WORDS) $('card-' + id).classList.remove('bad');
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
  if (n === 3) $('alist').querySelectorAll('textarea').forEach(grow);
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
      showErr('e3', bad.length === 1
        ? '1 answer is under ' + MIN_WORDS + ' words. It’s outlined above.'
        : bad.length + ' answers are under ' + MIN_WORDS + ' words. They’re outlined above.');
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

/* ---------- Start ---------- */
(function preset() {
  // Recruiting links can preselect fields: /contribute/interview/?school=rush-medical-college&year=m3&focus=clinical
  const p = new URLSearchParams(location.search);
  const sc = (p.get('school') || '').toLowerCase(), y = (p.get('year') || '').toLowerCase(), f = (p.get('focus') || '').toLowerCase();
  if (!S.school && D.bySlug[sc]) S.school = sc;
  if (!S.year && YEARS.some(v => v[0] === y)) S.year = y;
  if (!S.focus && fociRow[f]) S.focus = f;
})();
D.fill();
buildStep1();
go(Math.max(1, Math.min(S.step || 1, reach(), 4)));
})();
