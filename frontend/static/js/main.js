// =============================================================================
// EconoSight — Main JavaScript
// =============================================================================

const API_BASE = "";
const SUPABASE_URL = "https://sgqsaugbjyjuogxrzgpx.supabase.co";
const SUPABASE_KEY = "sb_publishable_sVpovWUtg7UtNSaIHkEqxQ_SK5zi8zf";

// =============================================================================
// Auth helpers
// =============================================================================

function getToken()   { return localStorage.getItem("es_token"); }
function getUser()    { try { return JSON.parse(localStorage.getItem("es_user")); } catch { return null; } }
function isLoggedIn() { return !!getToken(); }

function logout() {
    localStorage.removeItem("es_token");
    localStorage.removeItem("es_user");
    window.location.href = "/";
}

function updateNav() {
    const user = getUser();
    const loginLinks  = document.querySelectorAll(".nav-login");
    const logoutLinks = document.querySelectorAll(".nav-logout");
    const userNames   = document.querySelectorAll(".nav-username");

    if (user) {
        loginLinks.forEach(el  => el.style.display = "none");
        logoutLinks.forEach(el => el.style.display = "inline-block");
        userNames.forEach(el   => el.textContent = user.email?.split("@")[0] || "Account");
    } else {
        loginLinks.forEach(el  => el.style.display = "inline-block");
        logoutLinks.forEach(el => el.style.display = "none");
    }
}

// =============================================================================
// API calls
// =============================================================================

async function apiFetch(path, options = {}) {
    const token = getToken();
    const headers = { "Content-Type": "application/json", ...options.headers };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const r = await fetch(API_BASE + path, { ...options, headers });
    if (!r.ok) {
        const err = await r.json().catch(() => ({ detail: "Request failed" }));
        throw new Error(err.detail || "Request failed");
    }
    return r.json();
}

// =============================================================================
// Alert helper
// =============================================================================

function showAlert(id, message, type = "info") {
    const el = document.getElementById(id);
    if (!el) return;
    el.className = `alert alert-${type} show`;
    el.textContent = message;
    setTimeout(() => el.classList.remove("show"), 6000);
}

// =============================================================================
// Copy to clipboard
// =============================================================================

function copyText(text, btn) {
    navigator.clipboard.writeText(text).then(() => {
        const original = btn.textContent;
        btn.textContent = "Copied!";
        setTimeout(() => btn.textContent = original, 2000);
    });
}

// =============================================================================
// Chart helper — renders a Plotly chart from data
// =============================================================================

function renderLineChart(containerId, data, title, yLabel) {
    const countries = [...new Set(data.map(d => d.country_name))];
    const traces = countries.map(country => {
        const rows = data.filter(d => d.country_name === country)
                         .sort((a, b) => a.year - b.year);
        return {
            x: rows.map(r => r.year),
            y: rows.map(r => r.value),
            name: country,
            type: "scatter",
            mode: "lines+markers",
            line: { width: 2 }
        };
    });

    Plotly.newPlot(containerId, traces, {
        title:  { text: title, font: { color: "#1a2535", size: 15 } },
        xaxis:  { title: "Year", gridcolor: "#eeeeee" },
        yaxis:  { title: yLabel, gridcolor: "#eeeeee" },
        plot_bgcolor:  "#ffffff",
        paper_bgcolor: "#ffffff",
        font:   { color: "#1a2535" },
        legend: { orientation: "h", y: -0.2 },
        margin: { t: 50, b: 60, l: 60, r: 20 }
    }, { responsive: true });
}

function renderBarChart(containerId, labels, values, title, color = "#0096ff") {
    Plotly.newPlot(containerId, [{
        x: labels, y: values, type: "bar",
        marker: { color: color }
    }], {
        title:  { text: title, font: { color: "#1a2535", size: 15 } },
        xaxis:  { gridcolor: "#eeeeee" },
        yaxis:  { gridcolor: "#eeeeee" },
        plot_bgcolor:  "#ffffff",
        paper_bgcolor: "#ffffff",
        font:   { color: "#1a2535" },
        margin: { t: 50, b: 60, l: 60, r: 20 }
    }, { responsive: true });
}

function renderDonutChart(containerId, labels, values, title) {
    Plotly.newPlot(containerId, [{
        labels, values, type: "pie", hole: 0.45,
        marker: { colors: ["#0d1b2a","#1565c0","#00c9a7","#0096ff","#e94560","#243b55","#8899aa","#3d4f61"] }
    }], {
        title:  { text: title, font: { color: "#1a2535", size: 15 } },
        paper_bgcolor: "#ffffff",
        font:   { color: "#1a2535" },
        margin: { t: 50, b: 20, l: 20, r: 20 }
    }, { responsive: true });
}

// =============================================================================
// Number formatter
// =============================================================================

function formatValue(val, indicator) {
    if (val === null || val === undefined) return "N/A";
    if (indicator && indicator.includes("Population")) {
        if (val >= 1e9) return (val / 1e9).toFixed(2) + "B";
        if (val >= 1e6) return (val / 1e6).toFixed(1) + "M";
        return val.toLocaleString();
    }
    if (indicator && indicator.includes("USD")) {
        if (val >= 1e12) return "$" + (val / 1e12).toFixed(2) + "T";
        if (val >= 1e9)  return "$" + (val / 1e9).toFixed(2) + "B";
        return "$" + val.toLocaleString();
    }
    return parseFloat(val).toFixed(2) + (indicator?.includes("%") ? "%" : "");
}

// Init nav on every page
document.addEventListener("DOMContentLoaded", updateNav);
