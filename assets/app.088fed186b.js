(() => {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  const fmt = (value) => {
    if (!Number.isFinite(value) || value < 0) return "0:00";
    const whole = Math.floor(value);
    return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, "0")}`;
  };

  // Header surface on scroll
  const topbar = document.getElementById("topbar");
  const onScroll = () => {
    if (!topbar) return;
    topbar.classList.toggle("is-scrolled", window.scrollY > 8);
  };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  async function writeClipboard(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch (_) {}
    try {
      const area = document.createElement("textarea");
      area.value = text;
      area.setAttribute("readonly", "");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      const ok = document.execCommand("copy");
      area.remove();
      return ok;
    } catch (_) {
      return false;
    }
  }

  function showToast(message) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.textContent = message;
    toast.hidden = false;
    window.clearTimeout(showToast._t);
    showToast._t = window.setTimeout(() => {
      toast.hidden = true;
    }, 1800);
  }

  function confirmCopy(button, labelFallback) {
    const label = button.querySelector("span");
    const previous = label ? label.textContent : "";
    button.classList.add("is-copied");
    if (label) label.textContent = "Copied";
    window.setTimeout(() => {
      button.classList.remove("is-copied");
      if (label) label.textContent = previous || labelFallback;
    }, 1600);
  }

  document.querySelectorAll("[data-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      const ok = await writeClipboard(button.dataset.copy || "");
      if (!ok) return showToast("Copy failed");
      confirmCopy(button, "Copy");
      showToast("Copied");
    });
  });

  document.querySelectorAll("[data-copy-target]").forEach((button) => {
    button.addEventListener("click", async () => {
      const target = document.getElementById(button.dataset.copyTarget);
      if (!target) return;
      const ok = await writeClipboard(target.textContent.trim());
      if (!ok) return showToast("Copy failed");
      confirmCopy(button, "Copy");
      showToast("Copied");
    });
  });

  const copyLink = document.getElementById("copyLink");
  if (copyLink) {
    copyLink.addEventListener("click", async () => {
      const ok = await writeClipboard(window.location.href);
      if (!ok) return showToast("Copy failed");
      confirmCopy(copyLink, "Copy link");
      showToast("Link copied");
    });
  }

  const shareBtn = document.getElementById("shareTop");
  if (shareBtn) {
    shareBtn.addEventListener("click", async () => {
      const data = {
        title: "The harness is not the model — The Working Copy",
        text: "A read-only audit for the layer between your editor and your model provider.",
        url: window.location.href,
      };
      if (navigator.share) {
        try {
          await navigator.share(data);
          return;
        } catch (_) {}
      }
      const ok = await writeClipboard(data.url);
      showToast(ok ? "Link copied" : "Share unavailable");
    });
  }

  // Compact audio edition
  const audio = document.getElementById("articleAudio");
  const panel = document.querySelector("[data-audio-panel]");
  const expand = document.querySelector("[data-audio-expand]");
  const toggle = document.querySelector("[data-audio-toggle]");
  const seek = document.querySelector("[data-audio-seek]");
  const fill = document.querySelector("[data-audio-fill]");
  const clock = document.querySelector("[data-audio-clock]");

  if (audio && panel && toggle) {
    const paint = () => {
      const total = Number.isFinite(audio.duration) && audio.duration > 0 ? audio.duration : 0;
      const pct = total ? Math.min(100, (audio.currentTime / total) * 100) : 0;
      if (fill) fill.style.width = `${pct}%`;
      if (clock) {
        clock.textContent = total
          ? audio.currentTime > 0
            ? `${fmt(audio.currentTime)} / ${fmt(total)}`
            : fmt(total)
          : "Audio edition";
      }
      if (seek) {
        seek.setAttribute("aria-valuenow", String(Math.round(pct)));
        seek.setAttribute("aria-valuetext", `${fmt(audio.currentTime)} of ${fmt(total)}`);
      }
    };

    const setPlaying = (playing) => {
      toggle.dataset.playing = playing ? "true" : "false";
      toggle.setAttribute("aria-label", playing ? "Pause the audio edition" : "Play the audio edition");
      toggle.setAttribute("aria-pressed", String(playing));
    };

    audio.addEventListener("loadedmetadata", paint);
    audio.addEventListener("durationchange", paint);
    audio.addEventListener("timeupdate", paint);
    audio.addEventListener("play", () => setPlaying(true));
    audio.addEventListener("pause", () => setPlaying(false));
    audio.addEventListener("ended", () => setPlaying(false));
    audio.addEventListener("error", () => {
      if (clock) clock.textContent = "Audio unavailable";
      showToast("Audio edition unavailable");
    });

    toggle.addEventListener("click", () => {
      if (audio.paused) {
        audio.play().catch(() => {
          if (clock) clock.textContent = "Audio unavailable";
          showToast("Audio edition unavailable");
        });
      } else {
        audio.pause();
      }
    });

    const setOpen = (open) => {
      panel.classList.toggle("is-open", open);
      if (expand) expand.setAttribute("aria-expanded", String(open));
    };

    if (expand) {
      expand.addEventListener("click", () => {
        setOpen(!panel.classList.contains("is-open"));
      });
    }

    document.querySelectorAll("[data-open-audio]").forEach((button) => {
      button.addEventListener("click", (event) => {
        event.preventDefault();
        setOpen(true);
        panel.scrollIntoView({
          behavior: reduceMotion.matches ? "auto" : "smooth",
          block: "center",
        });
        if (expand) expand.focus({ preventScroll: true });
      });
    });

    const skip = (seconds) => {
      if (!Number.isFinite(audio.duration)) return;
      audio.currentTime = Math.min(
        audio.duration,
        Math.max(0, audio.currentTime + seconds),
      );
      paint();
    };

    const back = document.querySelector("[data-audio-back]");
    const forward = document.querySelector("[data-audio-forward]");
    const stop = document.querySelector("[data-audio-stop]");
    if (back) back.addEventListener("click", () => skip(-10));
    if (forward) forward.addEventListener("click", () => skip(10));
    if (stop) {
      stop.addEventListener("click", () => {
        audio.pause();
        audio.currentTime = 0;
        paint();
      });
    }

    if (seek) {
      const seekTo = (clientX) => {
        if (!Number.isFinite(audio.duration) || audio.duration <= 0) return;
        const rect = seek.getBoundingClientRect();
        const pct = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
        audio.currentTime = pct * audio.duration;
        paint();
      };
      seek.addEventListener("click", (event) => seekTo(event.clientX));
      seek.addEventListener("keydown", (event) => {
        if (!Number.isFinite(audio.duration) || audio.duration <= 0) return;
        const step = 5;
        if (event.key === "ArrowRight") {
          audio.currentTime = Math.min(audio.duration, audio.currentTime + step);
        } else if (event.key === "ArrowLeft") {
          audio.currentTime = Math.max(0, audio.currentTime - step);
        } else if (event.key === "Home") {
          audio.currentTime = 0;
        } else if (event.key === "End") {
          audio.currentTime = audio.duration;
        } else if (event.key === " " || event.key === "Enter") {
          toggle.click();
        } else {
          return;
        }
        event.preventDefault();
        paint();
      });
    }

    paint();
  }

  // PWA shell
  if (
    "serviceWorker" in navigator &&
    (window.location.protocol === "https:" ||
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1")
  ) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js").catch(() => {});
    });
  }
})();
