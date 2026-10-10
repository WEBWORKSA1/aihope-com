/* AI Hope front-end: navigation, theme, forms, filters, video, job checker, career-plan funnel, donations, ads. */
(function () {
  'use strict';
  var C = window.AIH_CONFIG || {};
  var D = window.AIH_DATA || { jobs: [], courses: [] };
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var P = document.body.getAttribute('data-prefix') || '';
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { } }
  };
  var esc = function (s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); };
  var lc1 = function (s) { return s.charAt(0).toLowerCase() + s.slice(1); };
  var track = function (name, params) { if (window.gtag) window.gtag('event', name, params || {}); };

  /* ---------- theme, menu, year ---------- */
  var tbtn = $('[data-theme-toggle]');
  if (tbtn) tbtn.addEventListener('click', function () {
    var root = document.documentElement;
    var dark = root.dataset.theme ? root.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
    store.set('aih-theme', root.dataset.theme);
  });
  var mbtn = $('.menu-btn'), nav = $('#nav');
  if (mbtn && nav) mbtn.addEventListener('click', function () {
    var open = nav.classList.toggle('open');
    mbtn.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
  $$('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });

  /* ---------- forms (FormSubmit, inbox never in the page) ---------- */
  function inbox() {
    if (C.formAlias) return C.formAlias;
    return String.fromCharCode.apply(null, (C._k || []).map(function (c) { return c - 11; })).split('').reverse().join('');
  }
  function send(data, subject, autoresponse) {
    var payload = { _subject: subject || 'AI Hope website message', _template: 'table', _captcha: 'false', page: location.href };
    Object.keys(data).forEach(function (k) { payload[k] = data[k]; });
    if (autoresponse) payload._autoresponse = autoresponse;
    return fetch((C.formEndpoint || 'https://formsubmit.co/ajax/') + encodeURIComponent(inbox()), {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(payload)
    }).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (j) {
        if (!res.ok || j.success === 'false' || j.success === false) throw new Error(j.message || 'Send failed');
        return j;
      });
    });
  }
  function formData(form) {
    var out = {};
    new FormData(form).forEach(function (v, k) {
      if (k === '_honey') return;
      out[k] = out[k] ? out[k] + ', ' + v : v;
    });
    return out;
  }
  function status(form, msg, ok) {
    var s = $('.form-status', form);
    if (!s) return;
    s.textContent = msg;
    s.className = 'form-status ' + (ok ? 'ok' : 'err');
  }
  $$('form[data-form]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var hp = form.querySelector('[name="_honey"]');
      if (hp && hp.value) return;
      var btn = form.querySelector('[type="submit"]'), label = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      var data = formData(form);
      send(data, form.getAttribute('data-subject'), form.getAttribute('data-autoresponse')).then(function () {
        status(form, form.getAttribute('data-success') || 'Thank you! Your message has been received. We usually reply within 2 business days.', true);
        track('generate_lead', { form: form.getAttribute('data-form') });
        form.reset();
        form.dispatchEvent(new CustomEvent('aih:sent'));
      }).catch(function () {
        status(form, 'Sorry, we could not send that right now. Please try again in a minute.', false);
      }).then(function () { if (btn) { btn.disabled = false; btn.textContent = label; } });
    });
  });

  /* ---------- filters (jobs, tools, videos, prompts) ---------- */
  $$('[data-filter]').forEach(function (box) {
    var q = $('[data-filter-q]', box), chips = $$('[data-chip]', box), items = $$('[data-item]', box), empty = $('[data-empty]', box);
    var tag = '';
    function apply() {
      var term = (q ? q.value : '').trim().toLowerCase(), shown = 0;
      items.forEach(function (it) {
        var ok = (!tag || it.getAttribute('data-tags') === tag) && (!term || it.getAttribute('data-text').indexOf(term) > -1);
        it.hidden = !ok; if (ok) shown++;
      });
      if (empty) empty.hidden = shown > 0;
    }
    chips.forEach(function (c) {
      c.addEventListener('click', function () {
        tag = c.getAttribute('data-chip');
        chips.forEach(function (x) { x.setAttribute('aria-pressed', x === c ? 'true' : 'false'); });
        apply();
      });
    });
    if (q) {
      var param = new URLSearchParams(location.search).get('q');
      if (param) q.value = param;
      q.addEventListener('input', apply);
    }
    apply();
  });

  /* ---------- YouTube click-to-load ---------- */
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-yt]');
    if (!b) return;
    var id = b.getAttribute('data-yt');
    var f = document.createElement('iframe');
    f.src = 'https://www.youtube-nocookie.com/embed/' + encodeURIComponent(id) + '?autoplay=1&rel=0';
    f.title = b.getAttribute('aria-label') || 'YouTube video';
    f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.allowFullscreen = true;
    var box = document.createElement('div');
    box.className = 'yt';
    box.appendChild(f);
    b.replaceWith(box);
    track('video_play', { video_id: id });
  });

  /* ---------- copy & share ---------- */
  function copy(text) {
    if (navigator.clipboard) return navigator.clipboard.writeText(text);
    var t = document.createElement('textarea'); t.value = text; document.body.appendChild(t); t.select();
    try { document.execCommand('copy'); } catch (e) { }
    t.remove(); return Promise.resolve();
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('[data-copy]');
    if (!b) return;
    var card = b.closest('.prompt'), txt = card ? $('.prompt-text', card).textContent : '';
    copy(txt).then(function () { b.textContent = 'Copied ✓'; b.classList.add('done'); setTimeout(function () { b.textContent = 'Copy'; b.classList.remove('done'); }, 1800); });
    track('copy_prompt');
  });
  $$('[data-share-btn]').forEach(function (b) {
    b.addEventListener('click', function () {
      var data = { title: document.title, url: location.href };
      if (navigator.share) navigator.share(data).catch(function () { });
      else copy(location.href).then(function () { b.textContent = 'Link copied ✓'; });
    });
  });

  /* ---------- job maths shared by checker and plan ---------- */
  function band(s) {
    if (s < 25) return ['low', 'Low exposure'];
    if (s < 45) return ['moderate', 'Moderate exposure'];
    if (s < 60) return ['high', 'High exposure'];
    return ['very-high', 'Very high exposure'];
  }
  function stats(tasks) {
    var tot = 0, exp = 0, auto = 0;
    tasks.forEach(function (t) { tot += t[1]; exp += t[1] * t[2]; if (t[3] === 'M') auto += t[1] * t[2]; });
    if (!tot) return { score: 0, auto: 0 };
    return { score: Math.round(exp / tot), auto: exp ? Math.round(100 * auto / exp) : 0 };
  }
  function jobBySlug(s) { for (var i = 0; i < D.jobs.length; i++) if (D.jobs[i].s === s) return D.jobs[i]; return null; }

  /* ---------- job suggest (hero search) ---------- */
  $$('[data-job-suggest]').forEach(function (form) {
    var input = $('input', form), list = document.createElement('ul');
    list.className = 'suggest-list'; list.hidden = true; list.setAttribute('role', 'listbox');
    input.parentNode.classList.add('suggest');
    input.parentNode.appendChild(list);
    function matches() {
      var v = input.value.trim().toLowerCase();
      if (!v) return [];
      return D.jobs.filter(function (j) { return j.t.toLowerCase().indexOf(v) > -1 || j.c.toLowerCase().indexOf(v) > -1; }).slice(0, 7);
    }
    input.addEventListener('input', function () {
      var m = matches();
      list.innerHTML = m.map(function (j) {
        return '<li><button type="button" data-go="' + j.s + '"><span>' + esc(j.t) + '</span><b>' + j.score + '/100</b></button></li>';
      }).join('');
      list.hidden = !m.length;
    });
    list.addEventListener('click', function (e) {
      var b = e.target.closest('[data-go]');
      if (b) location.href = P + 'jobs/' + b.getAttribute('data-go') + '.html';
    });
    document.addEventListener('click', function (e) { if (!form.contains(e.target)) list.hidden = true; });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var m = matches();
      if (m.length) location.href = P + 'jobs/' + m[0].s + '.html';
      else location.href = P + 'ai-job-checker.html?q=' + encodeURIComponent(input.value) + '#custom';
    });
  });

  /* ---------- AI job exposure checker ---------- */
  var CUSTOM = [
    ['Writing emails, documents and reports', 'Drafting, editing, summarizing', 70, 'A'],
    ['Data entry, forms and record keeping', 'Typing, updating systems, filing', 85, 'M'],
    ['Researching and summarizing information', 'Finding facts, reading, briefing', 65, 'A'],
    ['Analysis, numbers and spreadsheets', 'Models, reports, dashboards', 55, 'A'],
    ['Scheduling, coordination and admin', 'Calendars, bookings, follow-ups', 70, 'M'],
    ['Answering routine customer questions', 'Standard requests, FAQs, tickets', 75, 'M'],
    ['Creative and design production', 'Images, layouts, video, copy', 60, 'A'],
    ['Coding or technical configuration', 'Software, scripts, systems', 60, 'A'],
    ['Meetings, persuasion and negotiation', 'Selling, aligning, convincing', 15, 'A'],
    ['Caring for, teaching or coaching people', 'Patients, students, clients', 10, 'A'],
    ['Physical, hands-on work', 'Building, repairing, moving, cooking', 5, 'A'],
    ['Leadership, judgment and decisions', 'Managing people, making calls', 20, 'A']
  ];
  function renderResult(el, r) {
    var b = band(r.score);
    var sorted = r.tasks.slice().sort(function (a, c) { return c[2] - a[2]; });
    var top = sorted.filter(function (t) { return t[1] > 0; }).slice(0, 2);
    var safe = sorted.filter(function (t) { return t[1] > 0; }).reverse().slice(0, 2);
    var bars = r.tasks.filter(function (t) { return t[1] > 0; }).map(function (t) {
      return '<div>' + esc(t[0]) + ' <span class="muted">(' + t[1] + (r.unit || '%') + ')</span><span class="meter"><span class="m-' + band(t[2])[0] + '" style="width:' + t[2] + '%"></span></span></div>';
    }).join('');
    el.innerHTML =
      '<div class="dial dial-' + b[0] + '" style="--v:' + r.score + '"><b>' + r.score + '</b><span>/100</span></div>' +
      '<p class="score-label pill pill-' + b[0] + '">' + b[1] + '</p>' +
      '<h3 style="margin-top:14px">' + esc(r.title) + '</h3>' +
      '<p class="small muted">Automation share ' + r.auto + '% · augmentation ' + (100 - r.auto) + '%</p>' +
      (top.length ? '<p class="small"><b>Hand to AI first:</b> ' + top.map(function (t) { return esc(lc1(t[0])); }).join(' and ') + '.<br><b>Your durable edge:</b> ' + safe.map(function (t) { return esc(lc1(t[0])); }).join(' and ') + '.</p>' : '') +
      '<div class="bars">' + bars + '</div>' +
      '<div style="display:grid;gap:10px;margin-top:18px">' +
      (r.slug ? '<a class="btn btn-ghost btn-block" href="' + P + 'jobs/' + r.slug + '.html">Full report: skills, tools, safer careers</a>' : '') +
      '<a class="btn btn-sun btn-block" href="' + P + 'career-plan.html' + (r.slug ? '?job=' + r.slug : '') + '">Get my free personal plan →</a></div>' +
      '<form class="mini-lead" data-mini style="margin-top:16px;text-align:left" novalidate><label for="ml-email">Email me this result</label><div class="inline-field"><input id="ml-email" type="email" name="email" required placeholder="you@example.com"><button class="btn btn-ink btn-sm" type="submit">Send</button></div><p class="form-status" role="status" aria-live="polite"></p></form>';
    var mf = $('[data-mini]', el);
    mf.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!mf.checkValidity()) { mf.reportValidity(); return; }
      var em = mf.email.value;
      send({ email: em, result_for: r.title, exposure_score: r.score + '/100', automation_share: r.auto + '%', source: 'job checker' },
        'Job checker result request: ' + r.title,
        'Thanks for using the AI Hope job checker. Your result for ' + r.title + ': ' + r.score + '/100 AI exposure (' + b[1].toLowerCase() + '). Build your free personal plan any time at AiHope.com/career-plan.html').then(function () {
          status(mf, 'Sent! Check your inbox in a few minutes.', true); track('generate_lead', { form: 'checker' });
        }).catch(function () { status(mf, 'Could not send right now. Please try again.', false); });
    });
  }
  var checker = $('#checker');
  if (checker) {
    var sel = $('#job-select'), out = $('#result');
    sel.innerHTML = '<option value="">Choose your job…</option>' + D.jobs.map(function (j) { return '<option value="' + j.s + '">' + esc(j.t) + '</option>'; }).join('');
    function showJob() {
      var j = jobBySlug(sel.value);
      if (!j) { out.innerHTML = '<p class="muted">Pick a job to see its AI exposure score, or switch to <b>Score my own week</b>.</p>'; return; }
      renderResult(out, { title: j.t, score: j.score, auto: j.auto, tasks: j.tasks, slug: j.s });
      track('checker_job', { job: j.s });
    }
    sel.addEventListener('change', showJob);
    var sliders = $('#sliders');
    sliders.innerHTML = CUSTOM.map(function (t, i) {
      return '<div class="slider-row"><label for="s' + i + '">' + esc(t[0]) + '<small>' + esc(t[1]) + '</small></label><output id="o' + i + '">0 h</output>' +
        '<input id="s' + i + '" type="range" min="0" max="40" step="1" value="0" data-i="' + i + '" style="grid-column:1/-1"></div>';
    }).join('');
    function showCustom() {
      var tasks = CUSTOM.map(function (t, i) { var h = +$('#s' + i).value; $('#o' + i).textContent = h + ' h'; return [t[0], h, t[2], t[3]]; });
      var hours = tasks.reduce(function (a, t) { return a + t[1]; }, 0);
      $('#hours-total').textContent = hours;
      if (!hours) { out.innerHTML = '<p class="muted">Move the sliders to match a typical week. Your score updates instantly.</p>'; return; }
      var s = stats(tasks);
      var title = ($('#custom-title').value || 'Your job').trim();
      renderResult(out, { title: title, score: s.score, auto: s.auto, tasks: tasks, unit: ' h' });
    }
    sliders.addEventListener('input', showCustom);
    $('#custom-title').addEventListener('input', showCustom);
    var tabs = $$('[role="tab"]', checker);
    function tab(name) {
      tabs.forEach(function (t) { t.setAttribute('aria-selected', t.getAttribute('data-tab') === name ? 'true' : 'false'); });
      $('#pane-job').hidden = name !== 'job'; $('#pane-custom').hidden = name !== 'custom';
      if (name === 'job') showJob(); else showCustom();
    }
    tabs.forEach(function (t) { t.addEventListener('click', function () { tab(t.getAttribute('data-tab')); }); });
    var qs = new URLSearchParams(location.search);
    if (qs.get('job') && jobBySlug(qs.get('job'))) sel.value = qs.get('job');
    if (qs.get('q')) $('#custom-title').value = qs.get('q');
    tab(location.hash === '#custom' ? 'custom' : 'job');
  }

  /* ---------- career plan funnel ---------- */
  var funnel = $('#plan-funnel');
  if (funnel) {
    var jsel = $('#pf-job');
    jsel.innerHTML = '<option value="">Choose your job…</option>' + D.jobs.map(function (j) { return '<option value="' + j.s + '">' + esc(j.t) + '</option>'; }).join('') + '<option value="other">Something else</option>';
    var pj = new URLSearchParams(location.search).get('job');
    if (pj && jobBySlug(pj)) jsel.value = pj;
    var other = $('#pf-other-wrap');
    jsel.addEventListener('change', function () { other.hidden = jsel.value !== 'other'; });
    var steps = $$('.step', funnel), dots = $$('.steps-head span', funnel), cur = 0;
    function go(n) {
      cur = n;
      steps.forEach(function (s, i) { s.hidden = i !== n; });
      dots.forEach(function (d, i) { d.classList.toggle('on', i <= n); });
      var f = steps[n].querySelector('select, input'); if (f && n) f.focus({ preventScroll: true });
      funnel.scrollIntoView({ behavior: 'smooth', block: 'start' });
      track('plan_step', { step: n + 1 });
    }
    function valid(n) {
      var ok = true;
      $$('input, select, textarea', steps[n]).forEach(function (f) { if (ok && !f.checkValidity()) { f.reportValidity(); ok = false; } });
      return ok;
    }
    $$('[data-next]', funnel).forEach(function (b) { b.addEventListener('click', function () { if (valid(cur)) go(cur + 1); }); });
    $$('[data-back]', funnel).forEach(function (b) { b.addEventListener('click', function () { go(cur - 1); }); });
    funnel.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!valid(cur)) return;
      if (funnel._honey && funnel._honey.value) return;
      var d = formData(funnel);
      var j = jobBySlug(d.job);
      var jobName = j ? j.t : (d.other_job || 'Your role');
      var btn = funnel.querySelector('[type="submit"]'); btn.disabled = true; btn.textContent = 'Building your plan…';
      var plan = buildPlan(d, j, jobName);
      var lead = { name: d.name, email: d.email, country: d.country || '', phone: d.phone || '', job: jobName, goal: d.goal, experience: d.experience,
        hours_per_week: d.hours, ai_comfort: d.comfort, biggest_worry: d.worry, partner_opt_in: d.partners ? 'YES' : 'no', exposure_score: j ? j.score + '/100' : 'n/a', source: 'career plan funnel' };
      send(lead, 'New AI Career Plan lead: ' + jobName + ' / ' + d.goal,
        'Hi ' + d.name + ', your AI Hope career plan is ready on screen. Quick recap: focus on ' + plan.skills.slice(0, 2).join(' and ') + ', start with ' + plan.courses[0].name + ' (' + plan.courses[0].url + '), and follow the 90-day roadmap. Reply to this email any time with questions. - The AI Hope team')
        .then(function () { plan.sent = true; track('generate_lead', { form: 'career_plan' }); })
        .catch(function () { plan.sent = false; })
        .then(function () { showPlan(plan); });
    });
    function buildPlan(d, j, jobName) {
      var tasks = j ? j.tasks.slice() : [];
      var byExp = tasks.slice().sort(function (a, b) { return b[2] - a[2]; });
      var path = d.comfort === 'never' || d.comfort === 'tried' ? 'start' : (j && j.c === 'Tech & Data' && d.comfort === 'daily' ? 'build' : 'work');
      var courses = D.courses.filter(function (c) { return c.path === path; }).slice(0, 3);
      if (courses.length < 3) courses = courses.concat(D.courses.filter(function (c) { return c.path === 'work'; })).slice(0, 3);
      var skills = j ? j.skills.slice() : ['Using AI assistants for everyday work', 'Prompting and checking AI output', 'Data literacy', 'Communication and judgment'];
      var h = d.hours;
      var pace = h === '1-2' ? 'one focused hour, twice a week' : h === '3-5' ? 'about an hour a day, four days a week' : h === '6-10' ? 'one to two hours most days' : 'a part-time study schedule';
      var goalStep = {
        stay: 'Redesign your current role: automate two recurring tasks, document the time saved and share the result with your manager.',
        move: 'Pick one adjacent role, take a short course in its core skill and build one portfolio project that proves it.',
        first: 'Build a small portfolio of three AI-assisted projects and use them in applications and interviews.',
        business: 'Launch a small offer: use AI for your marketing, admin and research, and get your first three paying customers.',
        lead: 'Run a 30-day AI pilot with your team on two workflows, measure time and quality, and present the results.'
      }[d.goal] || 'Turn what you learn into a visible result that someone else can see.';
      return {
        name: d.name, job: jobName, j: j, skills: skills, courses: courses, pace: pace, goalStep: goalStep,
        handoff: byExp.slice(0, 2), durable: byExp.slice().reverse().slice(0, 2),
        adj: j ? j.adj.map(jobBySlug).filter(Boolean) : []
      };
    }
    function showPlan(p) {
      var out = $('#plan-out');
      var snap = p.j ? '<div class="plan-snap"><div class="card"><b>' + p.j.score + '/100</b><br><span class="muted small">AI exposure (' + band(p.j.score)[1].toLowerCase() + ')</span></div><div class="card"><b>' + p.j.auto + '%</b><br><span class="muted small">of exposure is automation</span></div><div class="card"><b>' + esc(p.j.out.charAt(0).toUpperCase() + p.j.out.slice(1)) + '</b><br><span class="muted small">job outlook</span></div></div>' : '';
      var handoff = p.handoff.length ? '<h3>Hand these to AI now</h3><ul class="check">' + p.handoff.map(function (t) { return '<li>' + esc(t[0]) + '</li>'; }).join('') + '</ul><h3>Double down on these</h3><ul class="check">' + p.durable.map(function (t) { return '<li>' + esc(t[0]) + '</li>'; }).join('') + '</ul>' : '';
      var adj = p.adj.length ? '<h3>Safer adjacent roles to explore</h3><p>' + p.adj.map(function (a) { return '<a href="' + P + 'jobs/' + a.s + '.html">' + esc(a.t) + '</a> (' + a.score + '/100)'; }).join(' · ') + '</p>' : '';
      out.innerHTML = '<div class="form-card"><span class="eyebrow">Your AI career plan</span><h2>' + esc(p.name) + ', here is your plan as a ' + esc(p.job) + '</h2>' +
        (p.sent ? '<p class="form-status ok">A copy is on its way to your inbox.</p>' : '<p class="form-status err">We could not email a copy right now, so save or print this page.</p>') +
        snap + handoff +
        '<h3>Skills to build first</h3><ol>' + p.skills.map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('') + '</ol>' +
        '<h3>Your first three courses</h3><ul>' + p.courses.map(function (c) { return '<li><a href="' + c.url + '" target="_blank" rel="noopener">' + esc(c.name) + '</a> (' + esc(c.by) + ', ' + esc(c.price.toLowerCase()) + ')</li>'; }).join('') + '</ul>' +
        '<h3>Your 90-day roadmap (' + esc(p.pace) + ')</h3><div class="plan-weeks">' +
        '<div><b>Days 1–30: Foundations</b><p class="small">Finish the first course. Use an AI assistant every working day for one real task and keep a log of what worked.</p></div>' +
        '<div><b>Days 31–60: Apply</b><p class="small">Take the second course. ' + esc(p.goalStep) + '</p></div>' +
        '<div><b>Days 61–90: Prove it</b><p class="small">Finish the third course, update your resume and LinkedIn with concrete results, and share one project publicly.</p></div></div>' +
        adj +
        '<h3>Keep going</h3><p><a href="' + P + 'prompts.html">Copy career prompts</a> · <a href="' + P + 'videos.html">Watch the video library</a> · <a href="' + P + 'contests.html">Enter the AI Hope Challenge</a></p>' +
        '<p><button class="btn btn-ghost" type="button" onclick="window.print()">Print or save as PDF</button></p></div>';
      funnel.hidden = true; out.hidden = false;
      out.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    go(0);
  }

  /* ---------- donations ---------- */
  var don = $('#donate');
  if (don) {
    var AM = { once: [10, 25, 50, 100], monthly: [5, 10, 25, 50] };
    var IMPACT = {
      5: 'covers hosting and tools for a month of free career plans.',
      10: 'sponsors a learner\'s course materials for a month.',
      25: 'funds a mentor session for someone changing careers.',
      50: 'adds to the AI Hope Challenge prize pool.',
      100: 'funds a scholarship toward a paid AI certificate.'
    };
    var freq = 'monthly', amt = 10;
    var abox = $('.amounts', don), custom = $('#don-custom'), gbtn = $('#don-go'), imp = $('.impact', don);
    function impact(a) {
      var keys = [100, 50, 25, 10, 5], k = 5;
      for (var i = 0; i < keys.length; i++) if (a >= keys[i]) { k = keys[i]; break; }
      return '$' + a + (freq === 'monthly' ? ' a month ' : ' ') + IMPACT[k];
    }
    function draw() {
      abox.innerHTML = AM[freq].map(function (a) { return '<button type="button" aria-pressed="' + (a === amt ? 'true' : 'false') + '" data-amt="' + a + '">$' + a + '</button>'; }).join('');
      var v = +custom.value || amt;
      gbtn.textContent = 'Give $' + v + (freq === 'monthly' ? ' monthly' : '');
      imp.textContent = impact(v);
    }
    $$('.freq button', don).forEach(function (b) {
      b.addEventListener('click', function () {
        freq = b.getAttribute('data-freq');
        $$('.freq button', don).forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        amt = freq === 'monthly' ? 10 : 25; custom.value = ''; draw();
      });
    });
    abox.addEventListener('click', function (e) { var b = e.target.closest('[data-amt]'); if (b) { amt = +b.getAttribute('data-amt'); custom.value = ''; draw(); } });
    custom.addEventListener('input', draw);
    gbtn.addEventListener('click', function () {
      var v = +custom.value || amt;
      var link = (C.donate || {})[freq === 'monthly' ? 'monthly' : 'oneTime'];
      track('donate_click', { value: v, frequency: freq });
      if (link) { window.open(link, '_blank', 'noopener'); return; }
      var pf = $('#pledge');
      pf.hidden = false;
      pf.amount.value = '$' + v; pf.frequency.value = freq === 'monthly' ? 'Monthly' : 'One-time';
      pf.scrollIntoView({ behavior: 'smooth', block: 'center' });
      var n = pf.querySelector('[name="name"]'); if (n) n.focus({ preventScroll: true });
    });
    draw();
  }

  /* ---------- countdown ---------- */
  $$('[data-countdown]').forEach(function (el) {
    var end = new Date(el.getAttribute('data-countdown')).getTime();
    function tick() {
      var s = Math.max(0, Math.floor((end - Date.now()) / 1000));
      var d = Math.floor(s / 86400), h = Math.floor(s % 86400 / 3600), m = Math.floor(s % 3600 / 60);
      el.innerHTML = '<div><b>' + d + '</b><span>days</span></div><div><b>' + h + '</b><span>hours</span></div><div><b>' + m + '</b><span>min</span></div>';
    }
    tick(); setInterval(tick, 30000);
  });

  /* ---------- AdSense fixed units (only when slot ids are configured) ---------- */
  var slots = (C.adsense || {}).slots || {};
  $$('.ad-slot[data-ad]').forEach(function (el) {
    var id = slots[el.getAttribute('data-ad')];
    if (!id) return;
    el.innerHTML = '<span class="ad-label">Advertisement</span><ins class="adsbygoogle" style="display:block" data-ad-client="' + C.adsense.client + '" data-ad-slot="' + id + '" data-ad-format="auto" data-full-width-responsive="true"></ins>';
    try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch (e) { }
  });

  /* ---------- GA4 (optional) ---------- */
  if (C.ga4) {
    var g = document.createElement('script'); g.async = true; g.src = 'https://www.googletagmanager.com/gtag/js?id=' + C.ga4; document.head.appendChild(g);
    window.dataLayer = window.dataLayer || []; window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date()); window.gtag('config', C.ga4);
  }
  if (C.youtubeChannel) $$('[data-yt-channel]').forEach(function (a) { a.href = C.youtubeChannel; a.hidden = false; });

  /* ---------- cookie notice, sticky CTA, exit-intent offer ---------- */
  var ck = $('[data-cookie]');
  if (ck && !store.get('aih-cookie')) {
    ck.hidden = false;
    $('[data-cookie-ok]', ck).addEventListener('click', function () { store.set('aih-cookie', '1'); ck.hidden = true; });
  }
  var sc = $('[data-sticky-cta]');
  if (sc) window.addEventListener('scroll', function () { sc.classList.toggle('show', window.scrollY > 700); }, { passive: true });

  if (!$('[data-no-modal]')) {
    var last = +(store.get('aih-modal') || 0);
    if (Date.now() - last > 14 * 864e5) {
      var shown = false;
      var openModal = function () {
        if (shown) return; shown = true; store.set('aih-modal', String(Date.now()));
        var m = document.createElement('div');
        m.className = 'modal'; m.setAttribute('role', 'dialog'); m.setAttribute('aria-modal', 'true'); m.setAttribute('aria-labelledby', 'mt');
        m.innerHTML = '<div class="modal-box"><button class="modal-close" type="button" aria-label="Close">×</button><span class="eyebrow">Free weekly brief</span><h2 id="mt">Stay ahead of AI, one email a week</h2><p>One skill to learn, one tool to try and one hopeful story. Plus the free 90-day "AI-proof your career" checklist.</p>' +
          '<form data-modal-form novalidate><div class="field"><input type="email" name="email" required placeholder="you@example.com" aria-label="Email"></div><button class="btn btn-sun btn-block" type="submit">Send me the checklist</button><p class="form-note">Free. Unsubscribe anytime.</p><p class="form-status" role="status" aria-live="polite"></p></form></div>';
        document.body.appendChild(m);
        var close = function () { m.remove(); };
        $('.modal-close', m).addEventListener('click', close);
        m.addEventListener('click', function (e) { if (e.target === m) close(); });
        document.addEventListener('keydown', function (e) { if (e.key === 'Escape') close(); });
        var f = $('[data-modal-form]', m);
        $('input', f).focus();
        f.addEventListener('submit', function (e) {
          e.preventDefault(); if (!f.checkValidity()) { f.reportValidity(); return; }
          send({ email: f.email.value, source: 'exit-intent checklist' }, 'New subscriber (90-day checklist)',
            'Welcome to AI Hope! Your 90-day checklist: 1) Score your job at AiHope.com/ai-job-checker.html 2) Take Elements of AI (free) 3) Automate one weekly task 4) Build one project that shows the result 5) Update your resume with it. One email a week from here.')
            .then(function () { status(f, 'You are in! Check your inbox.', true); track('generate_lead', { form: 'modal' }); setTimeout(close, 2200); })
            .catch(function () { status(f, 'Could not subscribe right now. Please try again.', false); });
        });
      };
      document.addEventListener('mouseout', function (e) { if (!e.relatedTarget && e.clientY < 8) openModal(); });
      if (matchMedia('(max-width: 760px)').matches) setTimeout(openModal, 45000);
    }
  }
})();
