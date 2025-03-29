// Smooth fade-in animation
document.addEventListener("DOMContentLoaded", () => {
    document.querySelector(".fade-in").classList.add("visible");
});

// Button click alert
document.querySelectorAll(".btn-animate").forEach(btn => {
    btn.addEventListener("click", () => alert("Feature Coming Soon!"));
});
