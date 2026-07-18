/**
 * Toggle de thème clair / sombre / auto (navbar), vanilla JS.
 * L'application initiale (avant peinture) est faite par le script inline
 * dans <head> de base.html — ce fichier gère seulement le contrôle et sa
 * persistance, et suit les changements de préférence système en mode "auto".
 */
(function () {
    var STORAGE_KEY = "benbb96-theme";
    var root = document.documentElement;
    var media = window.matchMedia("(prefers-color-scheme: dark)");

    function resolve(mode) {
        if (mode === "auto") return media.matches ? "dark" : "light";
        return mode;
    }

    function apply(mode) {
        root.setAttribute("data-theme", resolve(mode));
        root.setAttribute("data-theme-mode", mode);
        try {
            localStorage.setItem(STORAGE_KEY, mode);
        } catch (e) {}
        document.querySelectorAll("[data-theme-toggle] [data-mode]").forEach(function (btn) {
            var active = btn.dataset.mode === mode;
            btn.classList.toggle("is-active", active);
            btn.setAttribute("aria-pressed", String(active));
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        apply(root.getAttribute("data-theme-mode") || "auto");
        document.querySelectorAll("[data-theme-toggle] [data-mode]").forEach(function (btn) {
            btn.addEventListener("click", function () { apply(btn.dataset.mode); });
        });
    });

    media.addEventListener("change", function () {
        if (root.getAttribute("data-theme-mode") === "auto") apply("auto");
    });
})();
