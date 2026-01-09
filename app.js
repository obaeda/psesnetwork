// Simple navigation helper
document.addEventListener("DOMContentLoaded", () => {
  // highlight active link
  const links = document.querySelectorAll("nav a");
  links.forEach(a => {
    if (a.getAttribute("href") === location.pathname.replace("/", "")) {
      a.classList.add("active");
    }
  });
});
