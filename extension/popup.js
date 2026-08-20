const API = 'https://careerflow-liart.vercel.app/api';
const $ = id => document.getElementById(id);

async function init() {
  const { token, autoCapture = true } = await chrome.storage.local.get(['token', 'autoCapture']);
  $('auth').hidden = !!token;
  $('capture').hidden = !token;
  $('auto').checked = autoCapture;
  if (!token) return;

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id || !/^https?:/.test(tab.url || '')) {
    $('detect-status').textContent = 'OPEN A JOB PAGE TO AUTO-FILL';
    $('job_url').value = tab?.url || '';
    return;
  }

  chrome.tabs.sendMessage(tab.id, { type: 'extract-job' }, (job) => {
    if (chrome.runtime.lastError || !job) {
      $('detect-status').textContent = 'FILL IN THE DETAILS MANUALLY';
      $('job_url').value = tab.url;
      return;
    }
    $('detect-status').textContent = `DETECTED FROM ${(job.source || 'THIS PAGE').toUpperCase()}`;
    $('role').value = job.role === 'Role not detected' ? '' : job.role;
    $('company').value = job.company || '';
    $('location').value = job.location || '';
    $('work_mode').value = job.work_mode || 'Unknown';
    $('employment_type').value = job.employment_type || 'Full-time';
    $('salary').value = job.salary || '';
    $('job_url').value = job.job_url || tab.url;
  });
}

$('login').onclick = async () => {
  const email = $('email').value.trim();
  const password = $('password').value;
  if (!email || !password) return show($('message'), 'Enter your email and password.');
  try {
    const r = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) {
      const detail = Array.isArray(data.detail) ? data.detail.map(item => item.msg || 'Invalid value').join('. ') : data.detail;
      return show($('message'), detail || 'Could not log in.');
    }
    await chrome.storage.local.set({ token: data.access_token });
    show($('message'), '');
    init();
  } catch {
    show($('message'), 'CareerFlow is unreachable. Check your connection and try again.');
  }
};

$('auto').onchange = () => chrome.storage.local.set({ autoCapture: $('auto').checked });

$('save').onclick = async () => {
  const company = $('company').value.trim();
  const role = $('role').value.trim();
  if (company.length < 2 || role.length < 2) return show($('message2'), 'Company and role need at least 2 characters.');
  const job = {
    company,
    role,
    location: $('location').value.trim() || 'Remote',
    work_mode: $('work_mode').value,
    employment_type: $('employment_type').value,
    status: $('status').value,
    salary: $('salary').value.trim() || null,
    job_url: $('job_url').value.trim() || null,
    source: 'Extension',
    priority: 'Normal',
    next_step: null,
    notes: null
  };
  $('save').disabled = true;
  $('save').textContent = 'Saving…';
  const result = await new Promise(resolve => chrome.runtime.sendMessage({ type: 'capture-job', job }, resolve));
  $('save').disabled = false;
  $('save').textContent = 'Save to CareerFlow';
  if (result?.ok) show($('message2'), result.duplicate ? 'Already saved to CareerFlow.' : 'Saved to CareerFlow ✓');
  else if (result?.reason === 'session-expired' || result?.reason === 'not-authenticated') { await chrome.storage.local.remove('token'); init(); }
  else show($('message2'), result?.reason || 'Could not save this job.');
};

$('logout').onclick = async () => {
  await chrome.storage.local.remove('token');
  init();
};

function show(node, message) { node.textContent = message; }

init();
