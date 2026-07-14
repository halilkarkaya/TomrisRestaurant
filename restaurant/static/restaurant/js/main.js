(() => {
  const header = document.querySelector("[data-header]");
  const menuToggle = document.querySelector("[data-menu-toggle]");
  const navigation = document.querySelector("[data-navigation]");
  const navLinks = [...document.querySelectorAll("[data-nav-link]")];
  const sections = [...document.querySelectorAll("[data-section]")];
  const skipLink = document.querySelector(".skip-link");
  const mainContent = document.querySelector("#icerik");
  const flagImage = document.querySelector("[data-flag-image]");
  const desktopNavigation = window.matchMedia("(min-width: 52.01rem)");

  const hideUnavailableFlagImage = () => flagImage?.classList.add("is-unavailable");

  if (flagImage) {
    flagImage.addEventListener("error", hideUnavailableFlagImage, { once: true });
    if (flagImage.complete && flagImage.naturalWidth === 0) hideUnavailableFlagImage();
  }

  const setHeaderState = () => {
    header?.classList.toggle("is-scrolled", window.scrollY > 24);
  };

  const setMenuState = (open, restoreFocus = false) => {
    if (!menuToggle || !navigation) return;

    menuToggle.setAttribute("aria-expanded", String(open));
    navigation.classList.toggle("is-open", open);
    document.body.classList.toggle("nav-open", open);

    if (!open && restoreFocus) {
      menuToggle.focus();
    }
  };

  const focusHashTarget = (link) => {
    const hash = link?.getAttribute("href");
    if (!hash?.startsWith("#") || hash === "#") return;

    const target = document.querySelector(hash);
    if (!target) return;

    const hadTabIndex = target.hasAttribute("tabindex");
    if (!hadTabIndex) target.setAttribute("tabindex", "-1");

    requestAnimationFrame(() => {
      target.focus({ preventScroll: true });
      if (!hadTabIndex) {
        target.addEventListener("blur", () => target.removeAttribute("tabindex"), { once: true });
      }
    });
  };

  setHeaderState();
  window.addEventListener("scroll", setHeaderState, { passive: true });

  menuToggle?.addEventListener("click", () => {
    const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
    setMenuState(!isOpen);
  });

  navigation?.addEventListener("click", (event) => {
    const link = event.target.closest("a");
    if (!link) return;

    const wasMobileMenu = !desktopNavigation.matches;
    setMenuState(false);
    if (wasMobileMenu) focusHashTarget(link);
  });

  header?.querySelector(".brand")?.addEventListener("click", () => setMenuState(false));

  skipLink?.addEventListener("click", () => {
    requestAnimationFrame(() => mainContent?.focus({ preventScroll: true }));
  });

  document.addEventListener("keydown", (event) => {
    const menuIsOpen = menuToggle?.getAttribute("aria-expanded") === "true";

    if (event.key === "Escape" && menuIsOpen) {
      setMenuState(false, true);
    }

    if (event.key === "Tab" && menuIsOpen && navigation && menuToggle) {
      const focusableItems = [menuToggle, ...navigation.querySelectorAll("a[href]")];
      const firstItem = focusableItems[0];
      const lastItem = focusableItems.at(-1);

      if (event.shiftKey && document.activeElement === firstItem) {
        event.preventDefault();
        lastItem.focus();
      } else if (!event.shiftKey && document.activeElement === lastItem) {
        event.preventDefault();
        firstItem.focus();
      }
    }
  });

  desktopNavigation.addEventListener("change", (event) => {
    if (event.matches) setMenuState(false);
  });

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        const visibleEntry = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (!visibleEntry) return;

        navLinks.forEach((link) => {
          const isCurrent = link.getAttribute("href") === `#${visibleEntry.target.id}`;
          if (isCurrent) link.setAttribute("aria-current", "location");
          else link.removeAttribute("aria-current");
        });
      },
      { rootMargin: "-30% 0px -55%", threshold: [0.05, 0.25, 0.55] }
    );

    sections.forEach((section) => observer.observe(section));
  }

  const year = document.querySelector("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());
})();
