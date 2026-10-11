
    document.addEventListener('alpine:init', () => {
      Alpine.data('salesPage', () => ({
        paused: window.matchMedia('(prefers-reduced-motion: reduce)').matches,
        init() {
          document.documentElement.classList.add('enhanced');
          const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
          preference.addEventListener('change', event => { this.paused = event.matches; });
        },
        closeMenu(event) {
          const menu = this.$refs.mobileMenu;
          if (!menu || !menu.open) return;
          menu.open = false;
          if (event && event.type === 'keydown') menu.querySelector('summary').focus();
        }
      }));
      Alpine.data('reveal', () => ({
        watch() {
          if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) {
            this.$el.classList.add('is-visible'); return;
          }
          const observer = new IntersectionObserver(entries => {
            if (entries.some(entry => entry.isIntersecting)) {
              this.$el.classList.add('is-visible'); observer.disconnect();
            }
          }, { threshold: .12 });
          observer.observe(this.$el);
        }
      }));
    });
  