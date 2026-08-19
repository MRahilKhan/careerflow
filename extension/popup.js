const API = 'https://careerflow-one.vercel.app/api';
const $ = id => document.getElementById(id);
let job;

async function init() {
  const {token, autoCapture = true} = await chrome.storage.local.get(['token', 'autoCapture']);
  $('auth').hidden = !!token; $('capture').hidden = !token; $('auto').checked = autoCapture;
  if (token) { const [tab] = await chrome.tabs.query({active: true, currentWindow: true}); chrome.tabs.sendMessage(tab.id, {type: 'extract-job'}, data => { if (chrome.runtime.lastError) return show($('message2'), 'Open a normal job page first.'); job = data; render(); }); }
}
function render() { $('job-title').textContent = job.role || 'Job found'; $('preview').innerHTML = `<b>${job.company}</b><br>${job.location} · ${job.work_mode} · ${job.employment_type}<br>${job.salary || 'Salary not detected'}`; }
function show(node, message) { node.textContent = message; }
 $('login').onclick = async () => { try { const r = await fetch(`${API}/auth/login`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({email:$('email').value, password:$('password').value})}); const data = await r.json(); if (!r.ok) { const detail=Array.isArray(data.detail)?data.detail.map(item=>item.msg||'Invalid value').join('. '):data.detail; return show($('message'), detail || 'Could not connect'); } await chrome.storage.local.set({token:data.access_token}); init(); } catch { show($('message'), 'CareerFlow is unreachable. Check the live deployment and try again.'); } };
$('auto').onchange = () => chrome.storage.local.set({autoCapture: $('auto').checked});
$('save').onclick = async () => { if (!job) return show($('message2'), 'Open a job listing page first.'); const result = await new Promise(resolve => chrome.runtime.sendMessage({type:'capture-job', job}, resolve)); show($('message2'), result?.ok ? (result.duplicate ? 'Already saved.' : 'Saved to CareerFlow ✓') : (result?.reason || 'Could not save this job.')); };
$('logout').onclick = async () => { await chrome.storage.local.remove('token'); init(); };
init();
