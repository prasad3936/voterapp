// ====================================================
// DARK MODE TOGGLE
// ====================================================
const darkToggle = document.getElementById("darkToggle");
if (darkToggle) {
  const saved = localStorage.getItem("zp_dark");
  if (saved === "1") {
    document.body.classList.add("dark");
    darkToggle.textContent = "☀️";
  }

  darkToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark");
    const isDark = document.body.classList.contains("dark");
    darkToggle.textContent = isDark ? "☀️" : "🌙";
    localStorage.setItem("zp_dark", isDark ? "1" : "0");
  });
}

// ====================================================
// SMOOTH SCROLL FOR INTERNAL LINKS
// ====================================================
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener("click", (e) => {
    const targetId = link.getAttribute("href").substring(1);
    const target = document.getElementById(targetId);
    if (target) {
      e.preventDefault();
      window.scrollTo({
        top: target.offsetTop - 70,
        behavior: "smooth",
      });
    }
  });
});

// ====================================================
// COUNTER ANIMATION
// ====================================================
const counters = document.querySelectorAll(".metric-value");
let countersStarted = false;

function animateCounters() {
  counters.forEach((counter) => {
    const target = +counter.getAttribute("data-target");
    let current = 0;
    const duration = 1200;
    const step = Math.max(1, Math.floor(target / (duration / 16)));

    function update() {
      current += step;
      if (current >= target) {
        counter.textContent = target.toLocaleString();
      } else {
        counter.textContent = current.toLocaleString();
        requestAnimationFrame(update);
      }
    }
    update();
  });
}

const counterObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting && !countersStarted) {
        countersStarted = true;
        animateCounters();
      }
    });
  },
  { threshold: 0.4 }
);

const metricSection = document.querySelector(".hero-metrics");
if (metricSection) counterObserver.observe(metricSection);

// ====================================================
// SCROLL REVEAL
// ====================================================
const revealEls = document.querySelectorAll(".reveal");
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.2 }
);

revealEls.forEach((el) => revealObserver.observe(el));

// ====================================================
// TESTIMONIAL SLIDER
// ====================================================
const testimonials = [
  {
    text: "Mission ZP app helped our team track every booth in real-time. We could plan visits and follow-ups with full clarity.",
    name: "Sitting ZP Member",
    role: "Rural Constituency",
  },
  {
    text: "Previously we were working in Excel sheets and WhatsApp groups. Now everything is in one app – lists, PDFs and reports.",
    name: "City Corporator",
    role: "Urban Ward",
  },
  {
    text: "Ground karyakartas can search voters by house, family and booth in seconds. It saves hours during campaign rush.",
    name: "Campaign Manager",
    role: "Local Body Elections",
  },
];

let tIndex = 0;
const tText = document.getElementById("testimonialText");
const tName = document.getElementById("testimonialName");
const tRole = document.getElementById("testimonialRole");
const dots = document.querySelectorAll(".dot");

function renderTestimonial(index) {
  const t = testimonials[index];
  if (!tText || !tName || !tRole) return;

  tText.textContent = `“${t.text}”`;
  tName.textContent = t.name;
  tRole.textContent = t.role;

  dots.forEach((d) => d.classList.remove("active"));
  if (dots[index]) dots[index].classList.add("active");
}

dots.forEach((dot) => {
  dot.addEventListener("click", () => {
    tIndex = +dot.dataset.index;
    renderTestimonial(tIndex);
  });
});

if (testimonials.length && tText) {
  renderTestimonial(tIndex);
  setInterval(() => {
    tIndex = (tIndex + 1) % testimonials.length;
    renderTestimonial(tIndex);
  }, 7000);
}

// ====================================================
// FAQ ACCORDION
// ====================================================
const faqItems = document.querySelectorAll(".faq-item");

faqItems.forEach((item) => {
  const btn = item.querySelector(".faq-question");
  const answer = item.querySelector(".faq-answer");
  const icon = item.querySelector(".faq-icon");

  btn.addEventListener("click", () => {
    const isOpen = item.classList.contains("active");

    // close all
    faqItems.forEach((it) => {
      it.classList.remove("active");
      const ans = it.querySelector(".faq-answer");
      const ic = it.querySelector(".faq-icon");
      if (ans) ans.style.maxHeight = null;
      if (ic) ic.textContent = "+";
    });

    if (!isOpen) {
      item.classList.add("active");
      answer.style.maxHeight = answer.scrollHeight + "px";
      icon.textContent = "–";
    }
  });
});

// ====================================================
// ENQUIRY FORM → GOOGLE FORM BACKEND
// ====================================================
let submitted = false;

function showSuccessModal() {
  const modal = document.getElementById("successModal");
  const submitBtn = document.getElementById("submitBtn");
  if (modal && submitBtn) {
    modal.style.display = "flex";
    submitBtn.classList.remove("loading");
    submitBtn.textContent = "Send Enquiry";
  }
  const form = document.getElementById("google-form");
  if (form) form.reset();
  submitted = false;
}

const form = document.getElementById("google-form");
const submitBtn = document.getElementById("submitBtn");
const closeSuccess = document.getElementById("closeSuccess");

if (form && submitBtn) {
  form.addEventListener("submit", function (e) {
    // Basic validation
    let valid = true;
    const fields = form.querySelectorAll("input, textarea");

    fields.forEach((f) => {
      if (!f.value.trim()) {
        valid = false;
        f.classList.add("error");
        setTimeout(() => f.classList.remove("error"), 1500);
      }
    });

    if (!valid) {
      e.preventDefault();
      return;
    }

    // allow submit, mark flag so iframe onload knows it was from us
    submitted = true;
    submitBtn.classList.add("loading");
    submitBtn.textContent = "Sending...";
  });
}

if (closeSuccess) {
  closeSuccess.addEventListener("click", () => {
    const modal = document.getElementById("successModal");
    if (modal) modal.style.display = "none";
  });
}

// Close success modal when clicking outside
window.addEventListener("click", (e) => {
  const modal = document.getElementById("successModal");
  if (e.target === modal) {
    modal.style.display = "none";
  }
});

// ====================================================
// APK DOWNLOAD POPUP
// ====================================================
const apkModal = document.getElementById("apkModal");
const apkBtn = document.getElementById("apkBtn");
const apkBtn2 = document.getElementById("apkBtn2");
const closeApk = document.getElementById("closeApk");

function openApkModal() {
  if (apkModal) apkModal.style.display = "flex";
}

if (apkBtn) {
  apkBtn.addEventListener("click", (e) => {
    e.preventDefault();
    openApkModal();
  });
}

if (apkBtn2) {
  apkBtn2.addEventListener("click", (e) => {
    e.preventDefault();
    openApkModal();
  });
}

if (closeApk && apkModal) {
  closeApk.addEventListener("click", () => {
    apkModal.style.display = "none";
  });
}
// Redirect to Install Guide
const goInstallGuide = document.getElementById("goInstallGuide");

if (goInstallGuide) {
  goInstallGuide.addEventListener("click", () => {
    if (apkModal) apkModal.style.display = "none"; // close popup
  });
}

// Close APK modal when clicking outside
window.addEventListener("click", (e) => {
  if (e.target === apkModal) {
    apkModal.style.display = "none";
  }
});
