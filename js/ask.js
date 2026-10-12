/**
 * DocStory — Reader questions (js/ask.js)
 * Loaded only on interview pages whose student opted in to follow-up questions.
 *
 * The question goes to DocStory's inbox through Web3Forms (the same service as the contribute form).
 * DocStory forwards it to the student by hand; the student's email is never on the page.
 * The box hides itself after the student's graduation date (data-until), even before a rebuild.
 */
(function () {
  var box = document.getElementById('ask');
  if (!box) return;
  var C = window.DOCSTORY_CONTRIBUTE || {};
  var W3F_URL = 'https://api.web3forms.com/submit';
  var HCAPTCHA_SITEKEY = '50b2fe65-b00b-4b9e-ad62-3ba471098be2';   // Web3Forms' shared free-plan key
  var EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  var MIN_CHARS = 20, MAX_CHARS = 1000;

  // Past the student's graduation date: take the box away
  var until = box.getAttribute('data-until');
  var today = new Date(); today.setHours(0, 0, 0, 0);
  if (!until || new Date(until + 'T00:00:00') <= today || !C.web3formsKey) { box.remove(); return; }

  var $ = function (id) { return document.getElementById(id); };
  var form = $('askForm'), q = $('askQ'), count = $('askCount'), err = $('askErr'), send = $('askSend');
  var student = box.getAttribute('data-student'), school = box.getAttribute('data-school'), ref = box.getAttribute('data-ref');
  var anon = /^anonymous/i.test(student);
  var who = anon ? 'the student' : student.split(/\s+/)[0];

  q.addEventListener('input', function () {
    var n = q.value.length;
    count.textContent = n ? n + ' / ' + MAX_CHARS : 'Up to 1,000 characters';
  });

  // hCaptcha loads only once someone starts using the form, not on every page view
  var captchaId = null, captchaState = 'idle';
  function loadCaptcha() {
    if (captchaState !== 'idle') return;
    captchaState = 'loading';
    window.dsAskCaptchaReady = function () {
      try { captchaId = window.hcaptcha.render('askCaptcha', { sitekey: HCAPTCHA_SITEKEY }); captchaState = 'ready'; }
      catch (e) { captchaState = 'failed'; }
    };
    var s = document.createElement('script');
    s.src = 'https://js.hcaptcha.com/1/api.js?render=explicit&onload=dsAskCaptchaReady';
    s.async = true;
    s.onerror = function () { captchaState = 'failed'; };
    document.head.appendChild(s);
  }
  form.addEventListener('focusin', loadCaptcha);

  function showErr(msg, focusId) {
    err.textContent = msg; err.hidden = !msg;
    if (msg && focusId) $(focusId).focus();
  }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var email = $('askEmail').value.trim(), name = $('askName').value.trim(), question = q.value.trim();
    if (!EMAIL_RE.test(email)) return showErr('Add your email so ' + who + ' can reply.', 'askEmail');
    if (question.length < MIN_CHARS) return showErr('Add a little more to your question so ' + who + ' knows what you’d like to hear about.', 'askQ');
    if (!$('askOk').checked) return showErr('Tick the box to let us share your email with ' + who + '.', 'askOk');
    var token = '';
    if (captchaState === 'ready') {
      token = window.hcaptcha.getResponse(captchaId);
      if (!token) return showErr('Please complete the “I am human” check.');
    }
    showErr('');

    var fd = new FormData();
    fd.append('access_key', C.web3formsKey);
    fd.append('subject', 'Reader question · ' + ref + ' · ' + student + ' · ' + school);
    fd.append('from_name', 'DocStory Reader Questions');
    fd.append('email', email);                                   // reply-to: the reader
    fd.append('Contributor reference', ref || 'unknown');
    fd.append('Student (as credited)', student);
    fd.append('School', school);
    fd.append('Interview', location.origin + location.pathname);
    fd.append('Reader name', name || '(not given)');
    fd.append('Reader email', email);
    fd.append('Question', question);
    fd.append('Came from', window.DocStoryTrack ? window.DocStoryTrack.source() : 'Unknown');
    fd.append('Consent', 'Reader agreed to share their email with the student so they can reply');
    if (token) fd.append('h-captcha-response', token);
    fd.append('botcheck', '');

    send.disabled = true; send.textContent = 'Sending…';
    fetch(W3F_URL, { method: 'POST', body: fd, headers: { Accept: 'application/json' } })
      .then(function (res) {
        return res.json().catch(function () { return {}; }).then(function (data) {
          if (!res.ok || data.success === false) throw new Error(data.message || ('HTTP ' + res.status));
        });
      })
      .then(function () {
        form.hidden = true;
        $('askDone').textContent = 'Thanks, your question is on its way. We’ll pass it to ' + who + '. If they answer, the reply will come to ' + email +
          ', either from them or from ' + (C.contactEmail || 'DocStory') + '.';
        $('askDone').hidden = false;
      })
      .catch(function (e2) {
        console.warn('DocStory question failed:', e2);
        send.disabled = false; send.textContent = 'Send question';
        if (captchaState === 'ready') window.hcaptcha.reset(captchaId);
        showErr('We couldn’t send your question. Check your connection and try again' +
          (C.contactEmail ? ', or email ' + C.contactEmail + '.' : '.'));
      });
  });
})();
