const state = {
    companies: [],
    selectedSymbol: null,
    compareSymbol: "",
    days: 30,
    chart: null,
};

async function fetchJson(url) {
    const response = await fetch(url);
    if (!response.ok) {
        const detail = await response.text();
        throw new Error(detail || `Request failed: ${response.status}`);
    }
    return response.json();
}

async function init() {
    try {
        state.companies = await fetchJson("/companies");
        if (!state.companies.length) {
            throw new Error("No companies available.");
        }
        state.selectedSymbol = state.companies[0].symbol;
        renderCompanyList();
        renderCompareOptions();
        bindRangeControls();
        bindCompareControls();
        bindZoomControls();
        document.getElementById("company-count").textContent = `${state.companies.length} loaded`;
        await refreshDashboard();
    } catch (error) {
        document.getElementById("selected-company").textContent = "Unable to load data";
        document.getElementById("chart-subtitle").textContent = error.message;
        console.error(error);
    }
}

function renderCompanyList() {
    const list = document.getElementById("company-list");
    list.innerHTML = "";

    state.companies.forEach((company) => {
        const button = document.createElement("button");
        button.className = `company-btn ${company.symbol === state.selectedSymbol ? "active" : ""}`;
        button.innerHTML = `<strong>${company.company_name}</strong><br><span>${company.symbol}</span>`;
        button.addEventListener("click", async () => {
            state.selectedSymbol = company.symbol;
            if (state.compareSymbol === state.selectedSymbol) {
                state.compareSymbol = "";
                document.getElementById("compare-select").value = "";
            }
            renderCompanyList();
            renderCompareOptions();
            await refreshDashboard();
        });
        list.appendChild(button);
    });
}

function renderCompareOptions() {
    const select = document.getElementById("compare-select");
    const current = state.compareSymbol;
    select.innerHTML = `<option value="">No comparison</option>`;

    state.companies
        .filter((company) => company.symbol !== state.selectedSymbol)
        .forEach((company) => {
            const option = document.createElement("option");
            option.value = company.symbol;
            option.textContent = `${company.company_name} (${company.symbol})`;
            if (company.symbol === current) {
                option.selected = true;
            }
            select.appendChild(option);
        });
}

function bindRangeControls() {
    document.querySelectorAll(".range-btn").forEach((button) => {
        button.addEventListener("click", async () => {
            state.days = Number(button.dataset.days);
            document.querySelectorAll(".range-btn").forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");
            await refreshDashboard();
        });
    });
}

function bindCompareControls() {
    document.getElementById("compare-btn").addEventListener("click", async () => {
        state.compareSymbol = document.getElementById("compare-select").value;
        await refreshDashboard();
    });
}

function bindZoomControls() {
    document.getElementById("zoom-in-btn").addEventListener("click", () => {
        if (state.chart) {
            state.chart.zoom(1.2);
        }
    });

    document.getElementById("zoom-out-btn").addEventListener("click", () => {
        if (state.chart) {
            state.chart.zoom(0.8);
        }
    });

    document.getElementById("zoom-reset-btn").addEventListener("click", () => {
        if (state.chart) {
            state.chart.resetZoom();
        }
    });
}

async function refreshDashboard() {
    const [summary, baseSeries] = await Promise.all([
        fetchJson(`/summary/${encodeURIComponent(state.selectedSymbol)}`),
        fetchJson(`/data/${encodeURIComponent(state.selectedSymbol)}?days=${state.days}`),
    ]);

    updateSummary(summary);

    if (state.compareSymbol) {
        const comparison = await fetchJson(
            `/compare?symbol1=${encodeURIComponent(state.selectedSymbol)}&symbol2=${encodeURIComponent(state.compareSymbol)}&days=${state.days}`
        );
        updateChart(comparison.series);
        document.getElementById("chart-subtitle").textContent =
            `${state.days}-day view comparing ${comparison.series[0].symbol} and ${comparison.series[1].symbol}`;
    } else {
        updateChart([{ symbol: baseSeries.symbol, company_name: summary.company_name, points: baseSeries.points }]);
        document.getElementById("chart-subtitle").textContent =
            `${state.days}-day closing-price view for ${summary.company_name}`;
    }
}

function updateSummary(summary) {
    document.getElementById("selected-company").textContent = `${summary.company_name} (${summary.symbol})`;
    document.getElementById("latest-close").textContent = formatCurrency(summary.latest_close);
    document.getElementById("range-52w").textContent = `${formatCurrency(summary.low_52w)} - ${formatCurrency(summary.high_52w)}`;
    document.getElementById("volatility").textContent = formatPercent(summary.latest_volatility_7d);

    const summaryList = document.getElementById("summary-list");
    summaryList.innerHTML = "";

    const entries = [
        ["Average Close", formatCurrency(summary.average_close)],
        ["Latest Daily Return", formatPercent(summary.latest_daily_return)],
        ["Available Days", `${summary.available_days} records`],
        ["52-Week High", formatCurrency(summary.high_52w)],
        ["52-Week Low", formatCurrency(summary.low_52w)],
        ["Volatility Score", formatPercent(summary.latest_volatility_7d)],
    ];

    entries.forEach(([label, value]) => {
        const wrapper = document.createElement("div");
        wrapper.innerHTML = `<dt>${label}</dt><dd>${value}</dd>`;
        summaryList.appendChild(wrapper);
    });
}

function updateChart(seriesCollection) {
    const labels = seriesCollection[0].points.map((point) => point.date);
    const palette = [
        { border: "#0f766e", background: "rgba(15, 118, 110, 0.14)" },
        { border: "#c27803", background: "rgba(194, 120, 3, 0.14)" },
    ];

    const datasets = seriesCollection.map((series, index) => ({
        label: `${series.company_name} (${series.symbol})`,
        data: series.points.map((point) => point.close),
        borderColor: palette[index].border,
        backgroundColor: palette[index].background,
        borderWidth: 3,
        tension: 0.25,
        fill: false,
        pointRadius: 0,
        pointHoverRadius: 4,
    }));

    const context = document.getElementById("price-chart");
    if (state.chart) {
        state.chart.destroy();
    }

    state.chart = new Chart(context, {
        type: "line",
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false,
            },
            plugins: {
                legend: {
                    position: "bottom",
                },
                tooltip: {
                    callbacks: {
                        label: (tooltipItem) => `${tooltipItem.dataset.label}: ${formatCurrency(tooltipItem.parsed.y)}`,
                    },
                },
                zoom: {
                    limits: {
                        x: { minRange: 5 },
                    },
                    pan: {
                        enabled: true,
                        mode: "x",
                    },
                    zoom: {
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true,
                        },
                        mode: "x",
                    },
                },
            },
            scales: {
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45,
                    },
                },
                y: {
                    ticks: {
                        callback: (value) => formatCompactCurrency(value),
                    },
                },
            },
        },
    });
}

function formatCurrency(value) {
    return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 2,
    }).format(value);
}

function formatPercent(value) {
    return `${(value * 100).toFixed(2)}%`;
}

function formatCompactCurrency(value) {
    return `Rs. ${Number(value).toFixed(0)}`;
}

document.addEventListener("DOMContentLoaded", init);
