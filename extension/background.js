const API = 'https://careerflow-one.vercel.app/api';

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== 'capture-job') return;
  capture(message.job).then(sendResponse).catch(error => sendResponse({ok: false, reason: `CareerFlow is unreachable. Check the live deployment. (${error.message})`}));
  return true;
});

async function capture(job) {
  if (!job?.job_url || !job?.company || !job?.role) return {ok: false, reason: 'Could not find the company and role on this page.'};
  const { token, autoCapture = true, savedUrls = [] } = await chrome.storage.local.get(['token', 'autoCapture', 'savedUrls']);
  if (!token) return { ok: false, reason: 'not-authenticated' };
  if (!autoCapture && job.automatic) return { ok: false, reason: 'disabled' };
  if (savedUrls.includes(job.job_url)) return { ok: true, duplicate: true };
  const response = await fetch(`${API}/applications`, {
    method: 'POST', headers: {'Content-Type': 'application/json', Authorization: `Bearer ${token}`}, body: JSON.stringify(job)
  });
  if (response.status === 401) { await chrome.storage.local.remove('token'); return {ok: false, reason: 'session-expired'}; }
  if (!response.ok) { const payload = await response.json().catch(() => ({})); const detail = Array.isArray(payload.detail) ? payload.detail.map(item => item.msg || 'Invalid field').join('. ') : payload.detail; return {ok: false, reason: detail || `Could not save job (${response.status})`}; }
  await chrome.storage.local.set({savedUrls: [...savedUrls.slice(-99), job.job_url]});
  return {ok: true};
}
