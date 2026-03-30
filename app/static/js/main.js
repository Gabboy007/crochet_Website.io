const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("visible");
    }
  });
}, { threshold: 0.18 });

document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));

document.querySelectorAll(".tilt-card").forEach((card) => {
  card.addEventListener("mousemove", (e) => {
    if (window.innerWidth <= 768) return;

    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const rotateX = ((y / rect.height) - 0.5) * -8;
    const rotateY = ((x / rect.width) - 0.5) * 8;

    card.style.transform = `perspective(1200px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
  });

  card.addEventListener("mouseleave", () => {
    card.style.transform = "perspective(1200px) rotateX(0deg) rotateY(0deg)";
  });
});

const menuToggle = document.getElementById("menuToggle");
const mobileNav = document.getElementById("mobileNav");

if (menuToggle && mobileNav) {
  menuToggle.addEventListener("click", () => {
    const isOpen = mobileNav.classList.toggle("show");
    menuToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
  });

  mobileNav.querySelectorAll("a").forEach((link) => {
    link.addEventListener("click", () => {
      mobileNav.classList.remove("show");
      menuToggle.setAttribute("aria-expanded", "false");
    });
  });
}

const openFormBtn = document.getElementById("openFormBtn");
const orderModal = document.getElementById("orderModal");
const closeModal = document.getElementById("closeModal");
const closeModalBtn = document.getElementById("closeModalBtn");

function openForm() {
  if (!orderModal) return;
  orderModal.classList.add("active");
  orderModal.setAttribute("aria-hidden", "false");
  document.body.style.overflow = "hidden";
}

function closeForm() {
  if (!orderModal) return;
  orderModal.classList.remove("active");
  orderModal.setAttribute("aria-hidden", "true");
  document.body.style.overflow = "";
}

if (openFormBtn) {
  openFormBtn.addEventListener("click", openForm);
}

if (closeModal) {
  closeModal.addEventListener("click", closeForm);
}

if (closeModalBtn) {
  closeModalBtn.addEventListener("click", closeForm);
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    closeForm();
  }
});

document.querySelectorAll("[data-slideshow]").forEach((slideshow) => {
  const slides = slideshow.querySelectorAll(".slide");
  const prevBtn = slideshow.querySelector("[data-prev]");
  const nextBtn = slideshow.querySelector("[data-next]");

  if (!slides.length || slides.length === 1) return;

  let currentIndex = 0;

  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.toggle("active", i === index);
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      currentIndex = (currentIndex - 1 + slides.length) % slides.length;
      showSlide(currentIndex);
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      currentIndex = (currentIndex + 1) % slides.length;
      showSlide(currentIndex);
    });
  }
});

// PRODUCTS TOGGLE
const toggleProductsBtn = document.getElementById("toggleProducts");
const collectionsSection = document.getElementById("collections");

if (toggleProductsBtn) {
  let productsExpanded = false;

  toggleProductsBtn.addEventListener("click", () => {
    const items = document.querySelectorAll(".hidden-product");
    productsExpanded = !productsExpanded;

    items.forEach((item) => {
      if (productsExpanded) {
        item.classList.add("show-card");
      } else {
        item.classList.remove("show-card");
      }
    });

    toggleProductsBtn.textContent = productsExpanded ? "Show Less" : "See More";

    if (!productsExpanded && collectionsSection) {
      collectionsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
}

// REVIEWS TOGGLE
const toggleReviewsBtn = document.getElementById("toggleReviews");
const reviewsSection = document.getElementById("reviews");

if (toggleReviewsBtn) {
  let reviewsExpanded = false;

  toggleReviewsBtn.addEventListener("click", () => {
    const items = document.querySelectorAll(".hidden-review");
    reviewsExpanded = !reviewsExpanded;

    items.forEach((item) => {
      if (reviewsExpanded) {
        item.classList.add("show-card");
      } else {
        item.classList.remove("show-card");
      }
    });

    toggleReviewsBtn.textContent = reviewsExpanded ? "Show Less" : "See More";

    if (!reviewsExpanded && reviewsSection) {
      reviewsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });
}