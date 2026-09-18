"use strict";
(() => {
  const byId = id => document.getElementById(id);
  const number = (value, digits=0) => Number(value).toLocaleString("en-US", {minimumFractionDigits:digits, maximumFractionDigits:digits});
  const percent = value => value > 0 && value < .0001 ? (value*100).toPrecision(3)+"%" : number(value*100,2)+"%";
  const fraction = value => value > 0 && value < .0001 ? value.toExponential(3) : number(value,5);
  let evidence, hour=24;
  const selected = () => evidence.rows.find(row => row.case === byId("trace-case").value && row.time_h === hour);
  function render() {
    const r = selected();
    if (!r) throw new Error("The selected trajectory snapshot is missing.");
    const payloadNet = r.delivery_per_initial_cell_per_h-r.payload_loss_per_initial_cell_per_h;
    byId("trace-times").querySelectorAll("button").forEach(button => button.setAttribute("aria-pressed",String(Number(button.dataset.hour)===hour)));
    const stages = [
      ["Surface assembly",number(r.surface_complex_copies),"ternary complexes / initial cell",
       `${number(r.surface_receptors_per_initial_cell)} total receptors remain on the surface. Initial surface copies were 100,000.`],
      ["Endosomal inventory",number(r.internalized_complex_copies),"ternary complexes / initial cell",
       "The currently internalized inventory, not cumulative uptake. Recycling competes with processing."],
      ["Productive payload",number(r.payload_copies),"current equivalents / initial cell",
       `${number(r.delivered_payload_cumulative)} equivalents delivered cumulatively. Current payload also undergoes loss.`],
      ["Recoverable damage",number(r.damage,3),"mean damage Q · 0 to 1",
       "Damage competes with recovery. The nonlinear reactions are solved in each shell before averaging."],
      ["Death commitment",percent(r.committed_fraction),"of the initial population",
       `${percent(r.E_fraction)} are committed but not yet membrane-permeable. Mean delay to permeability is 6 h.`],
      ["Fluorescence",fraction(r.permeability_fluorescence),"normalized permeability signal",
       `${percent(r.D_fraction)} are reporter-accessible by cell count. Optical weighting makes the signal slightly different.`]
    ];
    byId("trace-output").innerHTML = `<p class="trace-snapshot">${hour} h snapshot · A ${number(r.primary_nm,r.primary_nm<10?3:0)} nM / S ${number(r.secondary_nm)} nM</p>
      <ol class="trace-stages">${stages.map(([title,value,unit,note],i)=>`<li><div class="trace-step">0${i+1} / ${title}</div><div class="trace-value">${value}</div><div class="trace-unit">${unit}</div><p>${note}</p></li>`).join("")}</ol>
      <div class="trace-rate"><h3>Payload bookkeeping at ${hour} h</h3>
        <p class="trace-arithmetic">dP̄/dt = delivery − loss ≈ ${number(r.delivery_per_initial_cell_per_h,2)} − ${number(r.payload_loss_per_initial_cell_per_h,2)} ≈ <strong>${number(payloadNet,2)}</strong> equivalents / initial cell / h</p>
        <p class="small muted">Delivery = 0.20 × (ln 2 / 12 h) × endosomal complex copies. Loss = (ln 2 / 12 h) × current payload. P̄ is the initial-cell-weighted mean; this linear balance can be averaged exactly. Displayed values are rounded after calculation.</p>
      </div>`;
  }
  function fail(error) {
    byId("trace-error").hidden=false;
    byId("trace-error").textContent="The worked-example data could not be loaded. Reload, or use the static equations and downloadable CSV below. "+error.message;
    byId("trace-output").innerHTML="";
    byId("trace-output").setAttribute("aria-busy","false");
    byId("trace-case").disabled=true;
    byId("trace-times").disabled=true;
  }
  byId("trace-case").addEventListener("change",()=>{try{render()}catch(error){fail(error)}});
  byId("trace-times").querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>{
    hour=Number(button.dataset.hour);try{render()}catch(error){fail(error)}
  }));
  fetch("trace/trace.json").then(response=>{
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }).then(data=>{
    if (!Array.isArray(data.rows) || data.rows.length !== 18 || data.metadata?.model_version !== "0.1.0") throw new Error("Unexpected evidence schema.");
    const cases=["sampled_peak","primary_excess","more_secondary"];
    for (const scenario of cases) for (const t of [0,6,12,24,48,72]) {
      const matches=data.rows.filter(row=>row.case===scenario&&row.time_h===t);
      if(matches.length!==1 || Object.entries(matches[0]).some(([key,value])=>key!=="case" && (typeof value!=="number" || !Number.isFinite(value)))) throw new Error("Incomplete or nonnumeric trajectory.");
    }
    evidence=data;
    const columns=cases.map(scenario=>data.rows.find(row=>row.case===scenario&&row.time_h===72));
    const fields=[
      ["Surface ternary complexes","surface_complex_copies",number],
      ["Endosomal ternary complexes","internalized_complex_copies",number],
      ["Current payload equivalents","payload_copies",number],
      ["Cumulative payload delivery","delivered_payload_cumulative",number],
      ["Mean damage Q","damage",value=>number(value,3)],
      ["Death commitment","committed_fraction",percent],
      ["Normalized fluorescence","permeability_fluorescence",fraction]
    ];
    byId("trace-comparison").innerHTML=fields.map(([label,field,format])=>`<tr><th scope="row">${label}</th>${columns.map(row=>`<td>${format(row[field])}</td>`).join("")}</tr>`).join("");
    render();
    byId("trace-case").disabled=false;
    byId("trace-times").disabled=false;
    byId("trace-output").setAttribute("aria-busy","false");
  }).catch(fail);
})();
