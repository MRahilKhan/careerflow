const API = 'http://localhost:8000';

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== 'capture-job') return;
  capture(message.job).then(sendResponse);
  return true;
});

async function capture(job) {
  const { token, autoCapture = true, savedUrls = [] } = await chrome.storage.local.get(['token', 'autoCapture', 'savedUrls']);
  if (!token) return { ok: false, reason: 'not-authenticated' };
  if (!autoCapture && job.automatic) return { ok: false, reason: 'disabled' };
  if (savedUrls.includes(job.job_url)) return { ok: true, duplicate: true };
  const response = await fetch(`${API}/applications`, {
    method: 'POST', headers: {'Content-Type': 'application/json', Authorization: `Bearer ${token}`}, body: JSON.stringify(job)
  });
  if (response.status === 401) { await chrome.storage.local.remove('token'); return {ok: false, reason: 'session-expired'}; }
  if (!response.ok) return {ok: false, reason: (await response.json()).detail || 'Could not save job'};
  await chrome.storage.local.set({savedUrls: [...savedUrls.slice(-99), job.job_url]});
  return {ok: true};
}
