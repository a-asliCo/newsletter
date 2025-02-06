document.addEventListener("DOMContentLoaded", function () {
  const bottomHover = document.querySelector(".bottom-hover");

  if (!bottomHover) {
    console.error("❌ Error: .bottom-hover element not found.");
    return; // Exit if the element doesn't exist
  }

  bottomHover.addEventListener("click", function () {
      if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
          console.log("✅ Already at the bottom of the page.");
          return; // Prevent scrolling past the end
      }

      window.scrollBy({
          top: window.innerHeight, // Scroll down by full viewport height
          behavior: "smooth"
      });
  });

  bottomHover.addEventListener("mouseenter", function () {
      console.log("🖱️ Cursor entered the bottom-hover area.");
  });

  bottomHover.addEventListener("mouseleave", function () {
      console.log("👋 Cursor left the bottom-hover area.");
  });
});
