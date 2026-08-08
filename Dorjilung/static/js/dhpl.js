document.addEventListener('DOMContentLoaded', function () {
  // Flags the page as JS-capable so the scroll-reveal CSS (which hides
  // .dhpl-reveal-anim elements pre-animation) only kicks in when it can
  // also be reversed — keeps content visible if JS fails to load.
  document.body.classList.add('js-ready');

  // Scroll-reveal — each section uses a layout-appropriate entrance
  // (slide left/right, scale, or a staggered pop/slide for grids and
  // table rows), triggered the first time it enters the viewport.
  var revealEls = document.querySelectorAll('.dhpl-reveal-anim');
  if (revealEls.length) {
    if ('IntersectionObserver' in window) {
      var revealObserver = new IntersectionObserver(
        function (entries, observer) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add('is-visible');
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
      );
      revealEls.forEach(function (el) {
        revealObserver.observe(el);
      });
    } else {
      revealEls.forEach(function (el) {
        el.classList.add('is-visible');
      });
    }
  }

  // Progress bar — grows from 0 to its real value once it scrolls into
  // view, instead of just appearing already filled.
  var progressFill = document.querySelector('.dhpl-progress-bar-fill');
  if (progressFill) {
    if ('IntersectionObserver' in window) {
      var progressObserver = new IntersectionObserver(
        function (entries, observer) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.style.width = (entry.target.dataset.progress || '0') + '%';
              observer.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.5 }
      );
      progressObserver.observe(progressFill);
    } else {
      progressFill.style.width = (progressFill.dataset.progress || '0') + '%';
    }
  }

  var toggle = document.querySelector('.dhpl-mobile-toggle');
  var menu = document.getElementById('dhpl-main-nav');

  if (toggle && menu) {
    toggle.addEventListener('click', function () {
      var open = this.getAttribute('aria-expanded') === 'true';
      this.setAttribute('aria-expanded', String(!open));
      menu.classList.toggle('open', !open);
    });
  }

  // Close the mobile menu when a link is clicked
  if (menu) {
    menu.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        if (window.matchMedia('(max-width: 900px)').matches) {
          menu.classList.remove('open');
          if (toggle) toggle.setAttribute('aria-expanded', 'false');
        }
      });
    });
  }

  // Hero image carousel — crossfades between slides on an interval,
  // pauses on hover/focus, and supports dot navigation.
  var hero = document.querySelector('.dhpl-hero');
  var slides = document.querySelectorAll('.dhpl-hero-slide');
  var dots = document.querySelectorAll('.dhpl-hero-dots .dot');
  var caption = document.querySelector('.dhpl-hero-caption');

  if (hero && slides.length > 1) {
    var current = 0;
    var intervalId;
    var DELAY = 2200;

    function showSlide(index) {
      slides[current].classList.remove('active');
      dots[current] && dots[current].classList.remove('active');
      current = (index + slides.length) % slides.length;
      slides[current].classList.add('active');
      dots[current] && dots[current].classList.add('active');
      if (caption) caption.textContent = slides[current].dataset.caption || '';
    }

    function next() {
      showSlide(current + 1);
    }

    function start() {
      intervalId = window.setInterval(next, DELAY);
    }

    function stop() {
      window.clearInterval(intervalId);
    }

    if (caption) caption.textContent = slides[current].dataset.caption || '';

    dots.forEach(function (dot, i) {
      dot.addEventListener('click', function () {
        showSlide(i);
        stop();
        start();
      });
    });

    hero.addEventListener('mouseenter', stop);
    hero.addEventListener('mouseleave', start);
    hero.addEventListener('focusin', stop);
    hero.addEventListener('focusout', start);

    start();
  }

  // Video modal — opens the self-hosted intro video in a lightbox and
  // pauses/rewinds it on close so it doesn't keep playing in the background.
  var videoModal = document.getElementById('dhpl-video-modal');
  var videoPlayer = document.getElementById('dhpl-intro-video');
  var videoTriggers = document.querySelectorAll('[data-video-trigger]');

  if (videoModal && videoPlayer && videoTriggers.length) {
    function openVideoModal() {
      videoModal.classList.add('open');
      videoModal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      videoPlayer.play();
    }

    function closeVideoModal() {
      videoModal.classList.remove('open');
      videoModal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      videoPlayer.pause();
      videoPlayer.currentTime = 0;
    }

    videoTriggers.forEach(function (trigger) {
      trigger.addEventListener('click', openVideoModal);
    });

    videoModal.querySelectorAll('[data-video-close]').forEach(function (el) {
      el.addEventListener('click', closeVideoModal);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && videoModal.classList.contains('open')) {
        closeVideoModal();
      }
    });
  }

  // Info modals — generic blurred-backdrop content cards (Explore
  // Environment / Explore Social). A trigger's data-modal-trigger value
  // is the id of the modal it should open.
  var infoModals = document.querySelectorAll('.dhpl-info-modal');
  if (infoModals.length) {
    var openInfoModal = function (modal) {
      modal.classList.add('open');
      modal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    };
    var closeInfoModal = function (modal) {
      modal.classList.remove('open');
      modal.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
    };

    document.querySelectorAll('[data-modal-trigger]').forEach(function (trigger) {
      trigger.addEventListener('click', function () {
        var modal = document.getElementById(trigger.dataset.modalTrigger);
        if (modal) openInfoModal(modal);
      });
    });

    infoModals.forEach(function (modal) {
      modal.querySelectorAll('[data-modal-close]').forEach(function (el) {
        el.addEventListener('click', function () {
          closeInfoModal(modal);
        });
      });
    });

    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      infoModals.forEach(function (modal) {
        if (modal.classList.contains('open')) closeInfoModal(modal);
      });
    });

    // Deep links — visiting a page with #some-modal-id in the URL (e.g.
    // from the homepage notice board) opens that modal automatically.
    if (window.location.hash) {
      var targetModal = document.getElementById(window.location.hash.slice(1));
      if (targetModal && targetModal.classList.contains('dhpl-info-modal')) {
        openInfoModal(targetModal);
      }
    }
  }

  // Structure: organogram chart show/hide toggle
  var orgToggle = document.querySelector('[data-org-toggle]');
  var orgChart = document.getElementById('dhpl-org-chart');
  if (orgToggle && orgChart) {
    orgToggle.addEventListener('click', function () {
      var expanded = orgToggle.getAttribute('aria-expanded') === 'true';
      orgToggle.setAttribute('aria-expanded', String(!expanded));
      orgChart.hidden = expanded;
      var label = orgToggle.querySelector('[data-org-toggle-label]');
      if (label) label.textContent = expanded ? 'Show Organogram' : 'Hide Organogram';
    });
  }

  // CLD Dashboard: Hide/Show Details toggle for the activity cards grid.
  document.querySelectorAll('.dhpl-cldp-toggle').forEach(function (toggle) {
    var target = document.getElementById(toggle.getAttribute('aria-controls'));
    if (!target) return;
    toggle.addEventListener('click', function () {
      var expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!expanded));
      target.hidden = expanded;
      var label = toggle.querySelector('[data-cldp-toggle-label]');
      if (label) label.textContent = expanded ? 'Show Details' : 'Hide Details';
    });
  });

  // Structure: department accordion — click a department to expand/
  // collapse its member list.
  document.querySelectorAll('[data-dept-toggle]').forEach(function (header) {
    header.addEventListener('click', function () {
      var item = header.closest('.dhpl-dept-item');
      if (!item) return;
      var open = item.classList.contains('open');
      item.classList.toggle('open', !open);
      header.setAttribute('aria-expanded', String(!open));
    });
  });
});
