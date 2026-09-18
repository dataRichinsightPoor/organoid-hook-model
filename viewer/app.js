"use strict";
let atlas, lab, mode="atlas", currentRows=[], activeData, chartGeometry;
const $=id=>document.getElementById(id);
const fmt=(x,d=3)=>Math.abs(x)>=1000?Number(x).toLocaleString(undefined,{maximumFractionDigits:1}):Number(x).toPrecision(d).replace(/\.?0+$/,"").replace(/\.$/,"");
const doseFmt=x=>Number(x).toLocaleString(undefined,{maximumSignificantDigits:3});
const labels={permeability_fluorescence:"Permeability fluorescence",committed_fraction:"Committed to death",membrane_compromised_cumulative:"Cumulative membrane loss",atp_proxy:"ATP-like signal",caspase_proxy:"Committed-state / caspase proxy",ldh_proxy:"LDH-like reporter",surface_complex_copies:"Surface ternary complex",internalized_complex_copies:"Endosomal ternary complex",payload_copies:"Intracellular payload",delivered_payload_cumulative:"Cumulative productive delivery"};
const descriptions={
 reference:"Default illustrative parameters. Persistent reporter; 150 µm radius; 100,000 initial surface copies per cell.",
 transport:"Radius 250 µm; diffusivity 0.1 µm²/s. Fixed organoid count also increases total cells. NOT spatially converged: this joint geometry/transport stress test is qualitative only.",
 core_low:"Core surface copies are 3% of rim copies. Radial receptor heterogeneity changes the accessible target distribution.",
 fast_repair:"Downstream protein-recovery half-time is 2 h. This is a generic damage-recovery assumption, not receptor turnover.",
 slow_repair:"Downstream protein-recovery half-time is 96 h. Receptor kinetics are unchanged.",
 reporter_loss:"Reporter loss is 0.08 h⁻¹ (8.7 h half-time). This is an optional stress test, NOT a claim about dye stability.",
 poor_release:"Only 0.1% of nominal payload yield becomes productive. Binding and internalization can occur with little effect downstream."
};
function params(){
 let p={...activeData.base_parameters};
 if(mode==="atlas")Object.assign(p,activeData.traffic_presets[$("traffic").value],{copies_per_cell:+$("copies").value,receptor_half_life_h:+$("half").value});
 else Object.assign(p,activeData.cases[$("case").value].overrides);
 return p;
}
function metrics(y){
 const peak=Math.max(...y),i=y.indexOf(peak),depth=peak>0?Math.max(0,1-y.at(-1)/peak):0;
 const meaningful=peak>=.05,interior=i>0&&i<y.length-1;
 return {peak,i,depth,flag:meaningful&&interior&&depth>=.1,
 status:!meaningful?"Low signal; uninformative":interior&&depth>=.1?"Descriptive hook":"No resolved hook in this range"};
}
function download(name,content,type="application/json"){
 const b=new Blob([content],{type}),url=URL.createObjectURL(b),a=document.createElement("a");
 a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function csv(){
 const fields=activeData.fields, rows=[["mode","case","copies_per_cell","traffic","receptor_half_life_h","order","secondary_nm","primary_nm","time_h",...fields]];
 for(const r of currentRows)for(let a=0;a<activeData.doses_nm.length;a++)for(let t=0;t<activeData.times_h.length;t++){
  rows.push([mode,mode==="lab"?$("case").value:"atlas",params().copies_per_cell,mode==="atlas"?$("traffic").value:"custom",params().receptor_half_life_h,r.order,r.secondary,activeData.doses_nm[a],activeData.times_h[t],...r.values[a][t]]);
 }
 download("organoid-hook-displayed.csv",rows.map(r=>r.join(",")).join("\n")+"\n","text/csv");
}
function chart(id,x,series,{log=false,ymax=1,xlabel="",ylabel=""}={}){
 const el=$(id),ctx=el.getContext("2d"),r=el.getBoundingClientRect(),dpr=window.devicePixelRatio||1;
 el.width=Math.round(r.width*dpr);el.height=Math.round(r.height*dpr);ctx.scale(dpr,dpr);
 const style=getComputedStyle(document.documentElement),get=v=>style.getPropertyValue(v).trim();
 const w=r.width,h=r.height,m={l:w<450?47:59,r:16,t:17,b:48},pw=w-m.l-m.r,ph=h-m.t-m.b;
 const transform=v=>log?Math.log10(v):v,xmin=transform(x[0]),xmax=transform(x.at(-1));
 const xp=v=>m.l+(transform(v)-xmin)/(xmax-xmin)*pw,yp=v=>h-m.b-v/ymax*ph;
 ctx.fillStyle=get("--surface");ctx.fillRect(0,0,w,h);ctx.font="12px Satoshi, sans-serif";ctx.textBaseline="middle";
 for(let i=0;i<=4;i++){let v=ymax*i/4,y=yp(v);ctx.strokeStyle=get("--line");ctx.lineWidth=.6;ctx.beginPath();ctx.moveTo(m.l,y);ctx.lineTo(w-m.r,y);ctx.stroke();ctx.fillStyle=get("--muted");ctx.textAlign="right";ctx.fillText(ymax>5?Number(v).toLocaleString(undefined,{maximumSignificantDigits:2}):v.toFixed(2),m.l-8,y);}
 const ticks=log?[.01,.1,1,10,100,1000]:x;
 ctx.textAlign="center";for(const v of ticks)ctx.fillText(doseFmt(v),xp(v),h-m.b+17);
 ctx.fillStyle=get("--muted");ctx.fillText(xlabel,m.l+pw/2,h-10);
 const colors=[get("--series1"),get("--series2"),get("--series3")],dash=[[2,4],[7,4],[]];
 series.forEach((s,j)=>{ctx.strokeStyle=colors[j];ctx.lineWidth=2.4;ctx.setLineDash(dash[j]);ctx.beginPath();s.y.forEach((v,i)=>{i?ctx.lineTo(xp(x[i]),yp(v)):ctx.moveTo(xp(x[i]),yp(v));});ctx.stroke();ctx.setLineDash([]);ctx.fillStyle=colors[j];s.y.forEach((v,i)=>{ctx.beginPath();ctx.arc(xp(x[i]),yp(v),2.5,0,Math.PI*2);ctx.fill();});});
 if(id==="curve")chartGeometry={xp,yp,m,w,h,x,series};
}
function render(){
 if(!atlas||!lab)return;
 activeData=mode==="atlas"?atlas:lab;
 $("atlas-controls").hidden=mode!=="atlas";$("lab-controls").hidden=mode!=="lab";
 $("atlas-mode").classList.toggle("active",mode==="atlas");$("lab-mode").classList.toggle("active",mode==="lab");
 $("atlas-mode").setAttribute("aria-pressed",mode==="atlas");$("lab-mode").setAttribute("aria-pressed",mode==="lab");
 currentRows=activeData.curves.filter(r=>r.order===$("order").value&&(mode==="atlas"?
  r.copies===+$("copies").value&&r.traffic===$("traffic").value&&r.half_life===+$("half").value:r.case===$("case").value));
 if(currentRows.length!==3)throw new Error("Expected exactly three secondary concentration curves.");
 const ti=+$("time").value,field=$("readout").value,fi=activeData.fields.indexOf(field),p=params();
 const y=currentRows.map(r=>r.values.map(v=>v[ti][fi]));
 const isCount=field.includes("copies")||field==="delivered_payload_cumulative";
 const max=Math.max(...y.flat());
 const ymax=isCount?Math.max(1,max*1.08):1;
 $("count").textContent=`${(atlas.simulation_count+lab.simulation_count).toLocaleString()} synthetic simulations · 3 observation times`;
 $("context").textContent=`${mode==="atlas"?"Receptor atlas":activeData.cases[$("case").value].name} · ${activeData.times_h[ti]} h from first addition · accumulation`;
 $("case-description").textContent=descriptions[$("case").value]||"";
 $("plot-title").textContent=labels[field];
 $("y-description").textContent=isCount?"Model-equivalent copies per initial cell; not experimental molecule counts.":field==="permeability_fluorescence"?"Normalized to a modeled, fully permeabilized initial population.":"Normalized model state or generic reporter signal; not a calibrated commercial assay.";
 $("plot-note").textContent="Primary and secondary are conjugate-molecule concentrations, not payload-equivalent concentrations. Points are computed; connecting lines guide the eye.";
 chart("curve",activeData.doses_nm,y.map((v,i)=>({y:v,label:currentRows[i].secondary+" nM secondary"})),{log:true,ymax,xlabel:"Primary antibody concentration (nM)"});
 $("metrics").innerHTML=currentRows.map((r,i)=>{
  const m=metrics(y[i]),eligible=!isCount&&field!=="atp_proxy";
  return `<div class="metric"><div class="label">${r.secondary} nM SECONDARY</div><div class="value">${eligible?(m.depth*100).toFixed(1)+"% decline":doseFmt(m.peak)+" peak"}</div><div class="result">${eligible?m.status:"Inspect the full curve"}</div><div class="label">Peak sampled at ${doseFmt(activeData.doses_nm[m.i])} nM primary${eligible?" · decline from peak to top dose":""}</div></div>`;
 }).join("");
 let di=Math.min(+$("dose").value,activeData.doses_nm.length-1),mid=currentRows[1];
 const idx=name=>activeData.fields.indexOf(name);
 const signals=["committed_fraction","permeability_fluorescence","atp_proxy"].map(f=>({label:labels[f],y:activeData.times_h.map((_,t)=>mid.values[di][t][idx(f)])}));
 chart("timechart",activeData.times_h,signals,{xlabel:"Time from first addition (h)"});
 for(const region of ["core","rim"]){let value=mid.values[di][ti][idx(region+"_committed")];$(region+"-bar").style.width=Math.max(0,Math.min(100,value*100))+"%";$(region+"-value").textContent=(100*value).toFixed(1)+"%";}
 $("interpretation").textContent=mode==="lab"?descriptions[$("case").value]:"Receptor abundance, internalization, and endosomal degradation are separate parameters. Recycling can return intact complexes without producing payload. Increasing surface copies also increases the finite-bath binding sink.";
 $("fixed").innerHTML=Object.entries(p).map(([k,v])=>`<div>${k}: <strong>${v}</strong></div>`).join("");
 $("table-head").innerHTML="<tr><th>Primary (nM)</th>"+currentRows.map(r=>`<th>${r.secondary} nM secondary</th>`).join("")+"</tr>";
 $("table-body").innerHTML=activeData.doses_nm.map((a,i)=>"<tr><td>"+doseFmt(a)+"</td>"+y.map(v=>`<td>${v[i].toPrecision(7)}</td>`).join("")+"</tr>").join("");
 $("curve").setAttribute("aria-label",`${labels[field]} at ${activeData.times_h[ti]} hours, across 13 primary concentrations and three secondary concentrations. Exact data follow in the expandable table.`);
 $("csv").disabled=false;$("png").disabled=false;
}
function reset(){
 mode="atlas";$("copies").value="100000";$("traffic").value="retained";$("half").value="24";$("order").value="simultaneous";$("time").value="2";$("readout").value="permeability_fluorescence";$("case").value="reference";$("dose").value="7";render();
}
for(const id of ["copies","traffic","half","case","order","time","readout","dose"])$(id).addEventListener("change",()=>{try{render()}catch(e){showError(e)}});
$("atlas-mode").onclick=()=>{mode="atlas";render()};$("lab-mode").onclick=()=>{mode="lab";render()};
$("reset").onclick=reset;$("csv").onclick=csv;
$("parameters").onclick=()=>{if(activeData)download("parameters.json",JSON.stringify(params(),null,2)+"\n")};
$("png").onclick=()=>{$("curve").toBlob(b=>{if(!b)return;const a=document.createElement("a"),url=URL.createObjectURL(b);a.href=url;a.download="synthetic-dose-response.png";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)});};
$("theme").onclick=()=>{const dark=document.documentElement.dataset.theme==="dark";document.documentElement.dataset.theme=dark?"light":"dark";$("theme").textContent=dark?"Dark mode":"Light mode";render()};
$("curve").addEventListener("mousemove",e=>{if(!chartGeometry)return;const g=chartGeometry,rect=$("curve").getBoundingClientRect(),x=e.clientX-rect.left;let i=0,best=Infinity;g.x.forEach((a,j)=>{let d=Math.abs(g.xp(a)-x);if(d<best){best=d;i=j}});$("tooltip").hidden=false;$("tooltip").innerHTML=`Primary: ${doseFmt(g.x[i])} nM<br>`+g.series.map(s=>`${s.label}: ${s.y[i].toPrecision(4)}`).join("<br>")});
$("curve").addEventListener("mouseleave",()=>{$("tooltip").hidden=true});
function showError(e){$("error").hidden=false;$("error").textContent="The evidence files could not be loaded or rendered. Please reload, or open the repository to download the data. Details: "+e.message;console.error(e)}
window.addEventListener("resize",()=>{if(atlas)render()});
// Dark is the publication default, independent of the operating-system theme.
Promise.all(["atlas.json","lab.json"].map(url=>fetch(url).then(r=>{if(!r.ok)throw new Error(`${url}: HTTP ${r.status}`);return r.json()}))).then(([a,l])=>{
 atlas=a;lab=l;
 $("case").innerHTML=Object.entries(l.cases).map(([k,v])=>`<option value="${k}">${v.name}</option>`).join("");
 $("dose").innerHTML=a.doses_nm.map((v,i)=>`<option value="${i}">${doseFmt(v)} nM</option>`).join("");
 $("dose").value="7";render();
}).catch(showError);
