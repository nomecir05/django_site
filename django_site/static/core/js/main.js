(() => {
  "use strict";

  const body = document.body;
  const menuButton = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("[data-menu]");
  const header = document.querySelector("[data-header]");

  const closeMenu = () => {
    if (!menuButton || !menu) return;
    menuButton.setAttribute("aria-expanded", "false");
    menu.classList.remove("open");
    body.classList.remove("menu-open");
  };

  if (menuButton && menu) {
    menuButton.addEventListener("click", () => {
      const isOpen = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!isOpen));
      menu.classList.toggle("open", !isOpen);
      body.classList.toggle("menu-open", !isOpen);
    });
    menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
    window.addEventListener("resize", () => {
      if (window.innerWidth > 900) closeMenu();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeMenu();
    });
  }

  const setHeaderState = () => {
    if (header) header.classList.toggle("scrolled", window.scrollY > 20);
  };
  setHeaderState();
  window.addEventListener("scroll", setHeaderState, { passive: true });

  const reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries, activeObserver) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            activeObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -30px" }
    );
    reveals.forEach((element) => observer.observe(element));
  } else {
    reveals.forEach((element) => element.classList.add("is-visible"));
  }

  document.querySelectorAll("[data-dismiss]").forEach((button) => {
    button.addEventListener("click", () => button.closest(".flash")?.remove());
  });

  const copyButton = document.querySelector("[data-copy-reference]");
  if (copyButton) {
    copyButton.addEventListener("click", async () => {
      const value = copyButton.dataset.value || "";
      try {
        await navigator.clipboard.writeText(value);
        copyButton.textContent = "Copied";
      } catch (_error) {
        const temporary = document.createElement("textarea");
        temporary.value = value;
        temporary.setAttribute("readonly", "");
        temporary.style.position = "absolute";
        temporary.style.left = "-9999px";
        document.body.appendChild(temporary);
        temporary.select();
        document.execCommand("copy");
        temporary.remove();
        copyButton.textContent = "Copied";
      }
      window.setTimeout(() => { copyButton.textContent = "Copy"; }, 1800);
    });
  }

  const detailsField = document.querySelector("#id_details");
  const characterCount = document.querySelector("[data-char-count]");
  if (detailsField && characterCount) {
    const updateCount = () => {
      characterCount.textContent = `${detailsField.value.length} characters`;
    };
    detailsField.addEventListener("input", updateCount);
    updateCount();
  }

  document.querySelectorAll("img").forEach((image) => {
    image.addEventListener("error", () => {
      image.style.background = "linear-gradient(135deg, #dce3e6, #f4f1ea)";
      image.alt = `${image.alt} (image unavailable)`;
    }, { once: true });
  });
})();
