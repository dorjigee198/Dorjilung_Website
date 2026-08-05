document.addEventListener('DOMContentLoaded', function () {
  // Category filter — instant client-side show/hide, no page reload.
  var filterButtons = document.querySelectorAll('.dhpl-gallery-filter-btn');
  var galleryItems = document.querySelectorAll('.dhpl-gallery-item');

  filterButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      filterButtons.forEach(function (b) {
        b.classList.remove('active');
      });
      btn.classList.add('active');

      var filter = btn.dataset.filter;
      galleryItems.forEach(function (item) {
        var show = filter === 'all' || item.dataset.category === filter;
        item.style.display = show ? '' : 'none';
      });
    });
  });

  // Lightbox — click a thumbnail to view it full-size.
  var lightbox = document.getElementById('dhpl-gallery-lightbox');
  var lightboxImg = document.getElementById('dhpl-lightbox-img');
  var lightboxCaption = document.getElementById('dhpl-lightbox-caption');

  if (lightbox && lightboxImg) {
    function openLightbox(src, caption) {
      lightboxImg.src = src;
      lightboxCaption.textContent = caption || '';
      lightboxCaption.style.display = caption ? '' : 'none';
      lightbox.classList.add('open');
      lightbox.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
      lightbox.classList.remove('open');
      lightbox.setAttribute('aria-hidden', 'true');
      lightboxImg.src = '';
      document.body.style.overflow = '';
    }

    galleryItems.forEach(function (item) {
      item.addEventListener('click', function () {
        openLightbox(item.dataset.full, item.dataset.caption);
      });
    });

    lightbox.querySelectorAll('[data-lightbox-close]').forEach(function (el) {
      el.addEventListener('click', closeLightbox);
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && lightbox.classList.contains('open')) {
        closeLightbox();
      }
    });
  }
});
