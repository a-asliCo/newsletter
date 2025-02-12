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

document.addEventListener("DOMContentLoaded", function () {
    const lastUpdatedElement = document.querySelector(".last-updated");

    if (lastUpdatedElement) {
        // Get the last modified date of the HTML file
        const lastModified = new Date(document.lastModified);
        
        // Format the date (e.g., 07 Feb. 2025)
        const formattedDate = lastModified.toLocaleDateString("en-GB", {
            day: "2-digit",
            month: "short",
            year: "numeric"
        });

        // Update the text content with <span> for styling
        lastUpdatedElement.innerHTML = `Last Updated: <span>${formattedDate}</span>`;
    }
});

document.addEventListener("DOMContentLoaded", function () {
    // Select elements
    const socialLinks = document.querySelectorAll(".socials a");
    const searchBar = document.querySelector(".search-input"); // Assuming there's an input field for search
    const heatmapButton = document.getElementById("heatmap-btn");

    // Load stored counts
    let socialClicks = parseInt(localStorage.getItem("socialClicks")) || 0;
    let searchCount = parseInt(localStorage.getItem("searchCount")) || 0;
    let visitCount = parseInt(localStorage.getItem("visitCount")) || 0;

    // Update display
    document.getElementById("social-clicks").innerText = socialClicks;
    document.getElementById("search-count").innerText = searchCount;
    document.getElementById("visit-count").innerText = visitCount;

    // Track social link clicks
    socialLinks.forEach(link => {
        link.addEventListener("click", function () {
            socialClicks++;
            localStorage.setItem("socialClicks", socialClicks);
            document.getElementById("social-clicks").innerText = socialClicks;
        });
    });

    // Track searches
    if (searchBar) {
        searchBar.addEventListener("keydown", function (event) {
            if (event.key === "Enter" && searchBar.value.trim() !== "") {
                searchCount++;
                localStorage.setItem("searchCount", searchCount);
                document.getElementById("search-count").innerText = searchCount;
            }
        });
    }

    // Track website visits
    visitCount++;
    localStorage.setItem("visitCount", visitCount);
    document.getElementById("visit-count").innerText = visitCount;

    // Show heatmap when button is clicked
    heatmapButton.addEventListener("click", function () {
        alert("🔴 Click Heatmap feature coming soon!");
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("search-input");
    const searchResults = document.getElementById("search-results");
    const allArticles = document.querySelectorAll(".news-feed .columns, .longer-readings .columns");
    let searchCount = parseInt(localStorage.getItem("searchCount")) || 0;

    // Function to filter articles based on search input
    function searchArticles() {
        const query = searchInput.value.toLowerCase().trim();
        searchResults.innerHTML = ""; // Clear previous results

        if (query === "") {
            searchResults.style.display = "none";
            return;
        }

        let foundArticles = 0;

        allArticles.forEach(article => {
            const title = article.querySelector(".title")?.textContent.toLowerCase();
            const subtitle = article.querySelector(".subtitle")?.textContent.toLowerCase();
            const link = article.querySelector("a")?.href;

            if ((title && title.includes(query)) || (subtitle && subtitle.includes(query))) {
                const resultEntry = document.createElement("div");
                resultEntry.classList.add("search-result-item");
                resultEntry.innerHTML = `
                    <h3>${article.querySelector(".title").textContent}</h3>
                    <p>${article.querySelector(".subtitle").textContent}</p>
                    <a href="${link}" target="_blank">Read more</a>
                `;
                searchResults.appendChild(resultEntry);
                foundArticles++;
            }
        });

        if (foundArticles === 0) {
            searchResults.innerHTML = "<p>No matching articles found.</p>";
        }

        searchResults.style.display = "block";

        // Update search count
        searchCount++;
        localStorage.setItem("searchCount", searchCount);
        document.getElementById("search-count").innerText = searchCount;
    }

    searchInput.addEventListener("input", searchArticles);
});
