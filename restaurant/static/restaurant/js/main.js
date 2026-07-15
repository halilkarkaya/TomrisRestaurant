(() => {
  const header = document.querySelector("[data-header]");
  const menuToggle = document.querySelector("[data-menu-toggle]");
  const navigation = document.querySelector("[data-navigation]");
  const navLinks = [...document.querySelectorAll("[data-nav-link]")];
  const sections = [...document.querySelectorAll("[data-section]")];
  const deferredImages = [...document.querySelectorAll("[data-deferred-src]")];
  const skipLink = document.querySelector(".skip-link");
  const mainContent = document.querySelector("#icerik");
  const flagImage = document.querySelector("[data-flag-image]");
  const flagTribute = document.querySelector("[data-flag-intro]");
  const mapContainer = document.querySelector("[data-map-container]");
  const mapFrame = document.querySelector("[data-map-frame]");
  const mapLoadButton = document.querySelector("[data-map-load]");
  const desktopNavigation = window.matchMedia("(min-width: 52.01rem)");

  const hideUnavailableFlagImage = () => flagImage?.classList.add("is-unavailable");

  if (flagImage) {
    flagImage.addEventListener("error", hideUnavailableFlagImage, { once: true });
    if (flagImage.complete && flagImage.naturalWidth === 0) hideUnavailableFlagImage();
  }

  if (flagTribute) {
    let hasSeenFlagIntro = false;

    try {
      hasSeenFlagIntro = window.sessionStorage.getItem("tomris:flag-intro-seen") === "1";
      if (!hasSeenFlagIntro) window.sessionStorage.setItem("tomris:flag-intro-seen", "1");
    } catch {
      hasSeenFlagIntro = false;
    }

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!hasSeenFlagIntro && !prefersReducedMotion) flagTribute.classList.add("is-arriving");
  }

  if (mapContainer && mapFrame && mapLoadButton && mapFrame.dataset.mapSrc) {
    mapLoadButton.hidden = false;
    mapLoadButton.addEventListener(
      "click",
      () => {
        const mapSource = mapFrame.dataset.mapSrc;
        if (!mapSource) return;

        mapLoadButton.disabled = true;
        mapLoadButton.textContent = "Harita yükleniyor…";
        mapContainer.classList.add("is-loading");
        mapFrame.hidden = false;

        mapFrame.addEventListener(
          "load",
          () => {
            mapContainer.classList.remove("is-loading");
            mapContainer.classList.add("is-loaded");
          },
          { once: true }
        );

        mapFrame.src = mapSource;
        delete mapFrame.dataset.mapSrc;
      },
      { once: true }
    );
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

  const loadDeferredImage = (image) => {
    const source = image.dataset.deferredSrc;
    if (!source) return;
    const sourceSet = image.dataset.deferredSrcset;
    if (sourceSet) image.srcset = sourceSet;
    image.src = source;
    delete image.dataset.deferredSrc;
    delete image.dataset.deferredSrcset;
  };

  const startDeferredImageLoading = () => {
    if (!deferredImages.length) return;

    if ("IntersectionObserver" in window) {
      const imageObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            loadDeferredImage(entry.target);
            imageObserver.unobserve(entry.target);
          });
        },
        { rootMargin: "150px 0px" }
      );

      deferredImages.forEach((image) => imageObserver.observe(image));
    } else {
      deferredImages.forEach(loadDeferredImage);
    }
  };

  const scheduleDeferredImageLoading = () => {
    if ("requestIdleCallback" in window) {
      window.requestIdleCallback(startDeferredImageLoading, { timeout: 1500 });
    } else {
      window.setTimeout(startDeferredImageLoading, 400);
    }
  };

  if (deferredImages.length) {
    const opensBelowHero = window.location.hash && window.location.hash !== "#anasayfa";
    if (opensBelowHero) {
      scheduleDeferredImageLoading();
    } else {
      const handleFirstMeaningfulScroll = () => {
        if (window.scrollY <= 8) return;
        window.removeEventListener("scroll", handleFirstMeaningfulScroll);
        scheduleDeferredImageLoading();
      };
      window.addEventListener("scroll", handleFirstMeaningfulScroll, { passive: true });
    }
  }

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
