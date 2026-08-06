/* =====================================================================
   ANCHOR'S EDGE, shared course deck engine
   Every course page defines window.COURSE (config data only) and this
   file wires the deck, reveals, and every interaction from it.
   Vanilla JS, no dependencies.
   ===================================================================== */
(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var isTouch = window.matchMedia('(hover: none)').matches;
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var C = window.COURSE || {};

  /* ---------- Nav: scroll state, mobile toggle ---------- */
  var nav = $('.nav');
  var toggle = $('.nav__toggle');
  var links = $('.nav__links');
  window.addEventListener('scroll', function () {
    nav.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });
  if (toggle) {
    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    $$('.nav__links a').forEach(function (a) {
      a.addEventListener('click', function () {
        links.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  /* ---------- Reveal on scroll ---------- */
  var revEls = $$('[data-reveal]');
  if ('IntersectionObserver' in window && !reduce) {
    var revObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); revObs.unobserve(e.target); }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
    revEls.forEach(function (el) { revObs.observe(el); });
    requestAnimationFrame(function () {
      revEls.forEach(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top < window.innerHeight && r.left < window.innerWidth && r.right > 0) {
          el.classList.add('in'); revObs.unobserve(el);
        }
      });
    });
  } else {
    revEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ---------- Manifesto word-by-word reveal ---------- */
  $$('.manifesto p').forEach(function (p) {
    var words = p.textContent.trim().split(/\s+/);
    p.innerHTML = words.map(function (w) { return '<span class="w">' + w + '</span>'; }).join(' ');
  });
  if ('IntersectionObserver' in window && !reduce) {
    var wObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var ws = $$('.w', e.target);
        ws.forEach(function (w, i) { setTimeout(function () { w.classList.add('lit'); }, i * 55); });
        wObs.unobserve(e.target);
      });
    }, { threshold: 0.5 });
    $$('.manifesto').forEach(function (m) { wObs.observe(m); });
  }

  /* ---------- Welcome slide: QR code ---------- */
  var qrBox = $('#qrBox');
  if (qrBox && typeof qrcode === 'function') {
    var qrCard = $('#qrCard');
    var qrTarget = (qrCard && qrCard.getAttribute('data-url')) ||
      (location.protocol === 'file:' ? '' : location.origin + location.pathname);
    var qrUrlEl = $('#qrUrl');
    if (qrTarget) {
      try {
        var qr = qrcode(0, 'M');
        qr.addData(qrTarget);
        qr.make();
        qrBox.innerHTML = qr.createSvgTag({ scalable: true, margin: 2 });
        if (qrUrlEl) qrUrlEl.textContent = qrTarget.replace(/^https?:\/\//, '').replace(/\/$/, '');
      } catch (err) {
        qrBox.parentElement.style.display = 'none';
      }
    } else {
      if (qrUrlEl) qrUrlEl.textContent = 'QR appears when the site is hosted';
      qrBox.innerHTML = '<div style="width:100%;aspect-ratio:1;display:grid;place-items:center;border:1px dashed #E4E4E4;color:#777;font-family:Inter,Arial,sans-serif;font-size:.8rem;padding:1rem;text-align:center">Deploy to generate the QR code</div>';
    }
  }

  /* ---------- Hero ambient particles ---------- */
  var canvas = $('.hero__canvas');
  if (canvas && !reduce && !isTouch) {
    var ctx = canvas.getContext('2d');
    var W, H, parts = [];
    var size = function () {
      W = canvas.width = canvas.offsetWidth * (window.devicePixelRatio > 1 ? 2 : 1);
      H = canvas.height = canvas.offsetHeight * (window.devicePixelRatio > 1 ? 2 : 1);
    };
    size(); window.addEventListener('resize', size);
    for (var i = 0; i < 46; i++) {
      parts.push({ x: Math.random(), y: Math.random(), r: Math.random() * 1.6 + 0.4,
        vy: (Math.random() * 0.00018 + 0.00006), vx: (Math.random() - 0.5) * 0.00008,
        a: Math.random() * 0.5 + 0.2 });
    }
    (function draw() {
      ctx.clearRect(0, 0, W, H);
      for (var j = 0; j < parts.length; j++) {
        var p = parts[j];
        p.y -= p.vy; p.x += p.vx;
        if (p.y < -0.05) { p.y = 1.05; p.x = Math.random(); }
        ctx.beginPath();
        ctx.arc(p.x * W, p.y * H, p.r * (window.devicePixelRatio > 1 ? 2 : 1), 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(207,174,112,' + p.a + ')';
        ctx.fill();
      }
      requestAnimationFrame(draw);
    })();
  } else if (canvas) { canvas.style.display = 'none'; }

  /* ---------- Goal meter: animates baseline to target on view ---------- */
  $$('[data-meter]').forEach(function (m) {
    var span = $('span', m);
    if (!span) return;
    var target = parseFloat(m.getAttribute('data-meter')) || 0;
    var fire = function () { span.style.width = target + '%'; };
    if ('IntersectionObserver' in window && !reduce) {
      var mObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) { setTimeout(fire, 350); mObs.unobserve(e.target); }
        });
      }, { threshold: 0.4 });
      mObs.observe(m);
    } else fire();
  });

  /* ---------- Inline knowledge checks (static markup) ---------- */
  $$('[data-quiz]').forEach(function (root) {
    $$('.quiz__options', root).forEach(function (group) {
      var answered = false;
      var fb = group.parentElement.querySelector('.quiz__feedback');
      $$('.opt', group).forEach(function (opt) {
        opt.addEventListener('click', function () {
          if (answered) return; answered = true;
          var correct = opt.getAttribute('data-correct') === '1';
          $$('.opt', group).forEach(function (o) {
            o.setAttribute('disabled', 'true');
            if (o.getAttribute('data-correct') === '1') o.classList.add('correct');
          });
          if (!correct) opt.classList.add('wrong');
          if (fb) {
            fb.classList.add('show');
            fb.textContent = (correct ? '✓ Correct. ' : '✗ Not quite. ') + (opt.getAttribute('data-why') || '');
            fb.style.color = correct ? 'var(--vu-oak)' : '#c76b5a';
          }
        });
      });
    });
  });

  /* ---------- Scenario trainers (config-driven, N rounds) ---------- */
  function makeTrainer(cfg) {
    var root = document.getElementById(cfg.rootId);
    if (!root) return;
    var idx = 0, score = 0, locked = false;
    var qEl = $('.quiz__q', root), optEl = $('.quiz__options', root),
        fbEl = $('.quiz__feedback', root), progEl = $('.quiz__progress', root),
        nextBtn = $('.quiz__nav .btn', root), resEl = $('.trainer__result', root),
        navEl = $('.quiz__nav', root);
    function render() {
      locked = false;
      var S = cfg.items[idx];
      progEl.textContent = (cfg.progressWord || 'Round') + ' ' + (idx + 1) + ' of ' + cfg.items.length;
      qEl.textContent = S.q;
      fbEl.textContent = '';
      nextBtn.style.visibility = 'hidden';
      nextBtn.textContent = idx === cfg.items.length - 1 ? 'See result' : 'Next';
      optEl.innerHTML = '';
      var labels = S.opts || cfg.labels;
      labels.forEach(function (label, i) {
        var b = document.createElement('button');
        b.className = 'opt';
        b.innerHTML = '<span class="mark">' + String.fromCharCode(65 + i) + '</span><span>' + label + '</span>';
        b.addEventListener('click', function () {
          if (locked) return; locked = true;
          var right = i === S.answer;
          if (right) score++;
          $$('.opt', optEl).forEach(function (o, oi) {
            o.setAttribute('disabled', 'true');
            if (oi === S.answer) o.classList.add('correct');
          });
          if (!right) b.classList.add('wrong');
          fbEl.textContent = (right ? '✓ ' : '✗ ') + S.why;
          fbEl.style.color = right ? 'var(--vu-oak)' : '#c76b5a';
          nextBtn.style.visibility = 'visible';
        });
        optEl.appendChild(b);
      });
    }
    nextBtn.addEventListener('click', function () {
      idx++;
      if (idx >= cfg.items.length) {
        navEl.style.display = 'none';
        qEl.textContent = ''; optEl.innerHTML = ''; progEl.textContent = ''; fbEl.textContent = '';
        resEl.hidden = false;
        resEl.innerHTML = '<div class="quiz__score gold-text">' + score + ' / ' + cfg.items.length + '</div>' +
          '<p style="margin-top:.75rem;color:var(--ink-soft,#555)">' +
          (score >= cfg.passAt ? cfg.passMsg : cfg.failMsg) +
          '</p><button class="btn btn--ghost" data-retry style="margin-top:1rem">Run it again</button>';
        $('[data-retry]', resEl).addEventListener('click', function () {
          idx = 0; score = 0; resEl.hidden = true;
          navEl.style.display = '';
          render();
        });
      } else render();
    });
    render();
  }
  (C.trainers || []).forEach(makeTrainer);

  /* ---------- Choice labs (config-driven builder) ---------- */
  function makeLab(cfg) {
    var lab = document.getElementById(cfg.rootId);
    if (!lab) return;
    var picks = cfg.slots.map(function () { return null; });
    var slotsEl = $('.lab__slots', lab), runBtn = $('.lab__runrow .btn', lab),
        statusEl = $('.lab__runrow .quiz__progress', lab), outEl = $('.lab__outcome', lab);
    var maxPts = cfg.slots.length * 3;
    cfg.slots.forEach(function (slot, si) {
      var d = document.createElement('div');
      d.className = 'slot';
      d.innerHTML = '<h3>' + (si + 1) + ' · ' + slot.key + '</h3>';
      slot.opts.forEach(function (o, oi) {
        var b = document.createElement('button');
        b.className = 'opt'; b.setAttribute('aria-pressed', 'false');
        b.innerHTML = '<span class="mark">' + String.fromCharCode(65 + oi) + '</span><span>' + o.t + '</span>';
        b.addEventListener('click', function () {
          picks[si] = oi;
          $$('.opt', d).forEach(function (x, xi) { x.setAttribute('aria-pressed', String(xi === oi)); });
          var ready = picks.every(function (p) { return p !== null; });
          runBtn.disabled = !ready;
          statusEl.textContent = ready ? 'Ready, run it' :
            'Choose ' + picks.filter(function (p) { return p === null; }).length + ' more';
          outEl.hidden = true;
        });
        d.appendChild(b);
      });
      slotsEl.appendChild(d);
    });
    runBtn.addEventListener('click', function () {
      var score = picks.reduce(function (t, p, i) { return t + cfg.slots[i].opts[p].pts; }, 0);
      var pct = Math.round((score / maxPts) * 100);
      var tier = pct >= 90 ? 'strong' : pct >= 65 ? 'mid' : 'weak';
      var coach = picks.map(function (p, i) {
        return '<div><b>' + cfg.slots[i].key + ':</b> ' + cfg.slots[i].opts[p].coach + '</div>';
      }).join('');
      outEl.innerHTML = '<span class="tag">' + cfg.outcomeTag + ' · ' + score + ' / ' + maxPts + '</span>' +
        '<div class="lab__meter"><span style="width:0"></span></div>' +
        '<p style="margin:0;color:#fff;font-weight:500">' + cfg.heads[tier] + '</p>' +
        '<div class="sample">' + cfg.reactions[tier] + '</div>' +
        '<div class="lab__coach">' + coach + '</div>' +
        (tier !== 'strong' ? '<p class="why" style="margin-top:1rem"><b>Try again:</b> upgrade your weakest choice and rerun it.</p>'
                           : '<p class="why" style="margin-top:1rem"><b>Carry it forward:</b> the capstone points this at your real team.</p>');
      outEl.hidden = false;
      requestAnimationFrame(function () {
        var bar = $('.lab__meter span', outEl);
        if (bar) requestAnimationFrame(function () { bar.style.width = pct + '%'; });
      });
      outEl.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'nearest' });
    });
  }
  (C.labs || []).forEach(makeLab);

  /* ---------- Capstone commitment card ---------- */
  if (C.capstone) {
    var cap = C.capstone;
    var planEl = $('#capstone');
    if (planEl) {
      var pick = { practice: null, when: null };
      var whoIn = $('#capWho'), buildBtn = $('#capBuild'), statusEl2 = $('#capStatus'), outEl2 = $('#capOut');
      var practiceById = {};
      cap.practices.forEach(function (p) { practiceById[p.id] = p; });
      var whenById = {};
      cap.whens.forEach(function (w) { whenById[w.id] = w; });
      function planReady() {
        var ok = whoIn.value.trim().length >= 8 && pick.practice && pick.when;
        buildBtn.disabled = !ok;
        statusEl2.textContent = ok ? 'Ready, build it' : 'Fill in all three parts';
        return ok;
      }
      whoIn.addEventListener('input', planReady);
      [['#capPractice', 'practice'], ['#capWhen', 'when']].forEach(function (cfg2) {
        var group = $(cfg2[0]);
        $$('.opt', group).forEach(function (b) {
          b.addEventListener('click', function () {
            pick[cfg2[1]] = b.getAttribute('data-id');
            $$('.opt', group).forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
            outEl2.hidden = true;
            planReady();
          });
        });
      });
      buildBtn.addEventListener('click', function () {
        if (!planReady()) return;
        var who = whoIn.value.trim();
        var p = practiceById[pick.practice];
        var w = whenById[pick.when];
        var rows = '' +
          '<div class="row"><b>' + cap.whoRow + '</b><span>' + who.replace(/</g, '&lt;') + '</span></div>' +
          '<div class="row"><b>The move</b><span>' + p.name + '. ' + p.move + '</span></div>' +
          '<div class="row"><b>The window</b><span>' + w.out + '</span></div>' +
          '<div class="row"><b>The goal it serves</b><span>' + cap.goalRow + '</span></div>' +
          '<div class="row"><b>The evidence</b><span>' + cap.evidenceRow + '</span></div>';
        outEl2.innerHTML = '<span class="tag">' + cap.cardTitle + '</span>' +
          '<div class="plan__out-grid">' + rows + '</div>' +
          '<div class="lab__runrow" style="margin-top:1.25rem">' +
          '<button class="btn" id="capCopy">Copy my card</button>' +
          '<span class="quiz__progress" id="capCopied" style="color:rgba(255,255,255,.6)">Put it on your calendar now</span></div>';
        outEl2.hidden = false;
        $('#capCopy').addEventListener('click', function () {
          var text = cap.cardTitle.toUpperCase() + ' (' + cap.copyTag + ')\n' +
            cap.whoRow + ': ' + who + '\n' +
            'The move: ' + p.name + '. ' + p.move + '\n' +
            'The window: ' + w.out + '\n' +
            'The goal it serves: ' + cap.goalRow + '\n' +
            'The evidence: ' + cap.evidenceRow;
          (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(function () {
            $('#capCopied').textContent = 'Copied. Paste it somewhere you will see this week.';
          }, function () {
            $('#capCopied').textContent = 'Select the card text above and copy it manually.';
          });
        });
        outEl2.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'nearest' });
      });
    }
  }

  /* ---------- Scored recap quiz ---------- */
  if (C.recap && C.recap.length) {
    var recap = $('#recap');
    if (recap) {
      var QUESTIONS = C.recap;
      var rIdx = 0, rScore = 0, rLocked = false;
      var rqEl = $('#recapQ'), roptEl = $('#recapOptions'), rfbEl = $('#recapFeedback'),
          rprogEl = $('#recapProgress'), rnextBtn = $('#recapNext'),
          rpanelEl = $('#recapPanel'), rresultEl = $('#recapResult');
      var renderR = function () {
        rLocked = false;
        var Q = QUESTIONS[rIdx];
        rqEl.textContent = Q.q;
        rprogEl.textContent = 'Question ' + (rIdx + 1) + ' of ' + QUESTIONS.length;
        rfbEl.textContent = ''; rfbEl.classList.remove('show');
        rnextBtn.style.visibility = 'hidden';
        rnextBtn.textContent = rIdx === QUESTIONS.length - 1 ? 'See score' : 'Next question';
        roptEl.innerHTML = '';
        Q.opts.forEach(function (text, i) {
          var b = document.createElement('button');
          b.className = 'opt';
          b.innerHTML = '<span class="mark">' + String.fromCharCode(65 + i) + '</span><span>' + text + '</span>';
          b.addEventListener('click', function () {
            if (rLocked) return; rLocked = true;
            var right = i === Q.correct;
            if (right) rScore++;
            $$('.opt', roptEl).forEach(function (o, oi) {
              o.setAttribute('disabled', 'true');
              if (oi === Q.correct) o.classList.add('correct');
            });
            if (!right) b.classList.add('wrong');
            rfbEl.classList.add('show');
            rfbEl.textContent = (right ? '✓ Correct. ' : '✗ ') + Q.why;
            rfbEl.style.color = right ? 'var(--vu-oak)' : '#c76b5a';
            rnextBtn.style.visibility = 'visible';
          });
          roptEl.appendChild(b);
        });
      };
      rnextBtn.addEventListener('click', function () {
        rIdx++;
        if (rIdx >= QUESTIONS.length) {
          rpanelEl.hidden = true;
          rresultEl.hidden = false;
          var pct = Math.round((rScore / QUESTIONS.length) * 100);
          var msg = pct >= 75 ? (C.recapMsgs && C.recapMsgs.high) || 'Loaded. The capstone makes it real.' :
                    pct >= 50 ? (C.recapMsgs && C.recapMsgs.mid) || 'Solid. Revisit the section you missed.' :
                                (C.recapMsgs && C.recapMsgs.low) || 'Worth another pass through the deck.';
          rresultEl.innerHTML = '<span class="eyebrow">Your result</span>' +
            '<div class="quiz__score gold-text">' + rScore + ' / ' + QUESTIONS.length + '</div>' +
            '<p class="lead" style="margin-top:1rem">' + msg + '</p>' +
            '<button class="btn btn--dark" id="recapRetry" style="margin-top:1.5rem">Try again</button>';
          $('#recapRetry').addEventListener('click', function () {
            rIdx = 0; rScore = 0; rresultEl.hidden = true; rpanelEl.hidden = false; renderR();
          });
        } else renderR();
      });
      renderR();
    }
  }

  /* ---------- Deck navigation: dots, arrows, keyboard, progress ---------- */
  var slides = $$('.slide');
  var dotWrap = $('#dots');
  var bar = $('#progressBar');
  var counter = $('#deckCount');
  var current = 0;

  if (dotWrap) {
    slides.forEach(function (s, i) {
      var b = document.createElement('button');
      b.type = 'button';
      var label = s.getAttribute('data-title') || ('Section ' + (i + 1));
      b.setAttribute('aria-label', 'Go to: ' + label);
      b.addEventListener('click', function () { goTo(i); });
      dotWrap.appendChild(b);
    });
  }
  var dots = dotWrap ? $$('button', dotWrap) : [];

  function goTo(i) {
    i = Math.max(0, Math.min(slides.length - 1, i));
    slides[i].scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', inline: 'start', block: 'nearest' });
  }
  var barTitle = $('#barTitle');
  function setActive(i) {
    current = i;
    dots.forEach(function (d, di) { d.setAttribute('aria-current', String(di === i)); });
    if (counter) counter.textContent = (i + 1) + ' / ' + slides.length;
    if (barTitle) barTitle.textContent = slides[i].getAttribute('data-title') || '';
    checkHint();
    $$('.nav__links a').forEach(function (a) {
      var href = a.getAttribute('href');
      a.setAttribute('aria-current', String(href === '#' + slides[i].id));
    });
  }
  if ('IntersectionObserver' in window) {
    var sObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { setActive(slides.indexOf(e.target)); }
      });
    }, { threshold: 0.5 });
    slides.forEach(function (s) { sObs.observe(s); });
  }

  var deckEl = $('.deck');
  if (deckEl) {
    deckEl.addEventListener('scroll', function () {
      var w = deckEl.scrollWidth - deckEl.clientWidth;
      if (bar) bar.style.width = (w > 0 ? (deckEl.scrollLeft / w) * 100 : 0) + '%';
      nav.classList.toggle('scrolled', deckEl.scrollLeft > 40);
    }, { passive: true });
  }

  var hint = $('#scrollHint');
  function checkHint() {
    if (!hint || !slides[current]) return;
    var s = slides[current];
    var need = s.scrollHeight - s.clientHeight > 56;
    var atEnd = s.scrollTop + s.clientHeight >= s.scrollHeight - 24;
    hint.classList.toggle('show', need && !atEnd);
  }
  if (hint) {
    hint.addEventListener('click', function () {
      var s = slides[current];
      s.scrollBy({ top: s.clientHeight * 0.7, behavior: reduce ? 'auto' : 'smooth' });
    });
    slides.forEach(function (s) { s.addEventListener('scroll', checkHint, { passive: true }); });
    window.addEventListener('resize', checkHint);
    setTimeout(checkHint, 400);
  }
  setActive(0);

  $$('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href').slice(1);
      if (!id) return;
      var target = document.getElementById(id);
      if (!target) return;
      var slide = target.closest ? (target.closest('.slide') || target) : target;
      if (slides.indexOf(slide) > -1) {
        e.preventDefault();
        goTo(slides.indexOf(slide));
      } else if (id === 'top') {
        e.preventDefault();
        goTo(0);
      }
    });
  });

  document.addEventListener('keydown', function (e) {
    if (['INPUT', 'TEXTAREA', 'SELECT'].indexOf(document.activeElement.tagName) > -1) return;
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || (e.key === ' ' && !e.shiftKey)) {
      e.preventDefault(); goTo(current + 1);
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp' || (e.key === ' ' && e.shiftKey)) {
      e.preventDefault(); goTo(current - 1);
    } else if (e.key === 'Home') { e.preventDefault(); goTo(0); }
    else if (e.key === 'End') { e.preventDefault(); goTo(slides.length - 1); }
  });

  $$('a[href]').forEach(function (a) {
    var href = a.getAttribute('href');
    if (href && href.charAt(0) !== '#') {
      a.setAttribute('target', '_blank');
      a.setAttribute('rel', 'noopener');
    }
  });

  var prevB = $('#deckPrev'), nextB = $('#deckNext');
  if (prevB) prevB.addEventListener('click', function () { goTo(current - 1); });
  if (nextB) nextB.addEventListener('click', function () { goTo(current + 1); });

  var yEl = $('#year'); if (yEl) yEl.textContent = new Date().getFullYear();
})();
