async function loadResults() {
  const loading = document.getElementById("loading");
  const metrics = document.getElementById("metrics");
  try {
    const [summaryResponse, auditResponse] = await Promise.all([
      fetch("results/summary.json", { cache: "no-store" }),
      fetch("results/gravity_hypothesis.json", { cache: "no-store" })
    ]);
    if (!summaryResponse.ok || !auditResponse.ok) throw new Error("One or more result files are unavailable");
    const [result, audit] = await Promise.all([summaryResponse.json(), auditResponse.json()]);
    const tx = result.transcriptomics;
    const supportedImaging = result.imaging.filter(row => row.welch_fdr < 0.05).length;
    metrics.innerHTML = `
      <article><strong>${tx.genes_with_p_value.toLocaleString()}</strong><span>genes tested in OSD-255</span></article>
      <article><strong>${tx.genes_with_fdr_below_0_05.toLocaleString()}</strong><span>genes at NASA FDR &lt; 0.05</span></article>
      <article><strong>${result.imaging.length}</strong><span>prespecified imaging endpoints</span></article>
      <article><strong>${supportedImaging}</strong><span>imaging endpoints at Welch FDR &lt; 0.05</span></article>`;
    document.getElementById("boundaries").innerHTML = result.claim_boundaries
      .map(item => `<li>${item}</li>`).join("");
    setupSolver(result.imaging);
    renderCrossMissionAudit(audit);
    loading.textContent = "Results loaded from the reproducible workflow.";
    metrics.hidden = false;
  } catch (error) {
    loading.textContent = "No derived results are loaded yet. Run the fetch and analysis commands; the interface will not substitute demonstration values.";
  }
}

function renderCrossMissionAudit(audit) {
  const gravity = audit.gravity_validation;
  const radiation = audit.analog_attribution.find(row => row.time === "7 day" && row.mechanism === "radiation");
  const metrics = document.getElementById("audit-metrics");
  metrics.innerHTML = `
    <article><strong>${gravity.mapped_to_osd758}/${gravity.discovery_panel_genes}</strong><span>RR-9 genes mapped to OSD-758</span></article>
    <article><strong>${formatNumber(gravity.rr9_vs_osd758_uG_spearman_rho, 3)}</strong><span>RR-9 vs OSD-758 uG Spearman ρ (p=${formatNumber(gravity.rr9_vs_osd758_uG_spearman_p, 3)})</span></article>
    <article><strong>${formatNumber(gravity.rr9_vs_osd758_uG_direction_fraction * 100, 1)}%</strong><span>same direction across missions</span></article>
    <article><strong>${gravity.gravity_sensitive_candidates}</strong><span>strict gravity-sensitive candidates</span></article>`;
  document.getElementById("radiation-finding").innerHTML = `<strong>Seven-day radiation-compatible signal:</strong> the OSD-758 residual flight effect and OSD-203 radiation response were concordant in ${radiation.direction_concordant}/${radiation.direction_total} RR-9 genes (${formatNumber(radiation.direction_fraction * 100, 1)}%; Spearman ρ=${formatNumber(radiation.spearman_rho, 3)}). The panel exceeded 10,000 equally sized random-gene panels after correction (empirical FDR=${formatNumber(radiation.panel_enrichment_fdr, 4)}).`;
}

function evidenceClass(row) {
  const welch = row.welch_fdr < 0.05;
  const rank = row.mann_whitney_fdr < 0.05;
  if (welch && rank) return { label: "Concordant evidence", tone: "strong" };
  if (welch || rank) return { label: "Model-sensitive evidence", tone: "mixed" };
  return { label: "Not supported at FDR 0.05", tone: "limited" };
}

function formatNumber(value, digits = 3) {
  return Number(value).toLocaleString(undefined, { maximumFractionDigits: digits });
}

function normalCdf(value) {
  const sign = value < 0 ? -1 : 1;
  const x = Math.abs(value) / Math.sqrt(2);
  const t = 1 / (1 + 0.3275911 * x);
  const erf = sign * (1 - (((((1.061405429 * t - 1.453152027) * t)
    + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x));
  return 0.5 * (1 + erf);
}

function probabilityState(row) {
  const total = row.n_flight + row.n_ground;
  const variance = total / (row.n_flight * row.n_ground)
    + (row.hedges_g ** 2) / (2 * (total - 2));
  const standardError = Math.sqrt(variance);
  return {
    standardError,
    lower: row.hedges_g - 1.96 * standardError,
    upper: row.hedges_g + 1.96 * standardError,
    directionProbability: normalCdf(Math.abs(row.hedges_g) / standardError)
  };
}

function setupSolver(rows) {
  const select = document.getElementById("endpoint-select");
  const output = document.getElementById("solver-output");
  select.innerHTML = rows.map((row, index) =>
    `<option value="${index}">${row.dataset} · ${row.endpoint}</option>`).join("");
  select.disabled = false;

  const render = () => {
    const row = rows[Number(select.value)];
    const status = evidenceClass(row);
    const probability = probabilityState(row);
    const direction = row.difference_flight_minus_ground > 0 ? "higher" : "lower";
    const exclusions = row.unmapped_samples_excluded
      ? `<p class="solver-note">Unmapped samples excluded without guessing a group: ${row.unmapped_samples_excluded}</p>` : "";
    output.innerHTML = `
      <div class="solver-verdict ${status.tone}">
        <span>Evidence classification</span>
        <strong>${status.label}</strong>
        <p>Space Flight is ${direction} than Ground Control by ${formatNumber(Math.abs(row.difference_flight_minus_ground))} ${row.unit}.</p>
      </div>
      <div class="solver-stat"><span>Hedges' g</span><strong>${formatNumber(row.hedges_g)}</strong></div>
      <div class="solver-stat probability-stat"><span>Approx. probability of direction</span><strong>${formatNumber(probability.directionProbability * 100, 1)}%</strong></div>
      <div class="solver-stat"><span>Approx. 95% interval for g</span><strong>${formatNumber(probability.lower)} to ${formatNumber(probability.upper)}</strong></div>
      <div class="solver-stat"><span>Welch FDR</span><strong>${formatNumber(row.welch_fdr, 4)}</strong></div>
      <div class="solver-stat"><span>Mann–Whitney FDR</span><strong>${formatNumber(row.mann_whitney_fdr, 4)}</strong></div>
      <div class="solver-stat"><span>Samples</span><strong>${row.n_flight} flight · ${row.n_ground} ground</strong></div>
      <p class="probability-caveat">Reference posterior: flat prior + Normal approximation to Hedges' g. This probability concerns the sign of the group difference, not disease, mechanism or causality.</p>
      ${exclusions}`;
  };
  select.addEventListener("change", render);
  select.value = "0";
  render();
}

function expectedDecisionValue(p, benefit, loss) {
  return Math.max(0, p * benefit - (1 - p) * loss);
}

function evsiAt(p, benefit, loss, sensitivity, specificity, studyCost) {
  const positive = p * sensitivity + (1 - p) * (1 - specificity);
  const negative = p * (1 - sensitivity) + (1 - p) * specificity;
  const postPositive = positive > 0 ? (p * sensitivity) / positive : 0;
  const postNegative = negative > 0 ? (p * (1 - sensitivity)) / negative : 0;
  const after = positive * expectedDecisionValue(postPositive, benefit, loss)
    + negative * expectedDecisionValue(postNegative, benefit, loss) - studyCost;
  return after - expectedDecisionValue(p, benefit, loss);
}

document.getElementById("voi-form").addEventListener("submit", event => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  const low = Number(data.get("p_low"));
  const high = Number(data.get("p_high"));
  const benefit = Number(data.get("benefit"));
  const loss = Number(data.get("loss"));
  const sensitivity = Number(data.get("sensitivity"));
  const specificity = Number(data.get("specificity"));
  const cost = Number(data.get("study_cost"));
  const output = document.getElementById("voi-output");
  if (low > high) {
    output.textContent = "pL must be less than or equal to pU.";
    return;
  }
  const values = Array.from({ length: 201 }, (_, index) => {
    const p = low + (high - low) * index / 200;
    return evsiAt(p, benefit, loss, sensitivity, specificity, cost);
  });
  const minimum = Math.min(...values);
  const maximum = Math.max(...values);
  const verdict = minimum > 0
    ? "The study has positive net value throughout the uncertainty interval."
    : maximum <= 0
      ? "The study does not have positive net value anywhere in the interval."
      : "The decision is sensitive to the prior probability inside the interval.";
  output.innerHTML = `<strong>Net EVSI interval: ${formatNumber(minimum)} to ${formatNumber(maximum)}</strong><span>${verdict}</span>`;
});

document.getElementById("pl-form").addEventListener("submit", event => {
  event.preventDefault();
  const data = new FormData(event.currentTarget);
  const budget = Number(data.get("budget"));
  const names = ["OSD-758 artificial gravity", "OSD-715 proteomics", "Cross-mission meta-analysis", "Retinal cell-type mapping"];
  const studies = names.map((name, index) => ({
    name,
    cost: Number(data.get(`cost_${index}`)),
    value: Number(data.get(`value_${index}`))
  }));
  let best = { value: 0, cost: 0, selected: [] };
  for (let mask = 0; mask < (1 << studies.length); mask += 1) {
    const selected = studies.filter((_, index) => mask & (1 << index));
    const totalCost = selected.reduce((sum, study) => sum + study.cost, 0);
    const totalValue = selected.reduce((sum, study) => sum + study.value, 0);
    if (totalCost <= budget && (totalValue > best.value || (totalValue === best.value && totalCost < best.cost))) {
      best = { value: totalValue, cost: totalCost, selected };
    }
  }
  const output = document.getElementById("pl-output");
  if (!best.selected.length) {
    output.textContent = "No positive-value combination fits the available budget.";
    return;
  }
  output.innerHTML = `<strong>Selected plan: ${best.selected.map(study => study.name).join("; ")}</strong><span>Total cost ${formatNumber(best.cost)} · declared value ${formatNumber(best.value)}.</span>`;
});

loadResults();
