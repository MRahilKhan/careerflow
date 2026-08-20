const API = 'https://careerflow-liart.vercel.app/api';

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type !== 'capture-job') return;
  capture(message.job).then(sendResponse).catch(error => sendResponse({ ok: false, reason: `CareerFlow is unreachable. (${error.message})` }));
  return true; // keep the message channel open for the async response
});

async function capture(job) {
  if (!job?.job_url || !job?.company || !job?.role) return { ok: false, reason: 'Could not find the company and role on this page.' };
  const { token, autoCapture = true, savedUrls = [] } = await chrome.storage.local.get(['token', 'autoCapture', 'savedUrls']);
  if (!token) return { ok: false, reason: 'not-authenticated' };
  if (!autoCapture && job.automatic) return { ok: false, reason: 'disabled' };
  if (savedUrls.includes(job.job_url)) return { ok: true, duplicate: true };

  const { automatic, ...payload } = job; // strip our internal-only flag before sending to the API
  const response = await fetch(`${API}/applications`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload)
  });

  if (response.status === 401) {
    await chrome.storage.local.remove('token');
    return { ok: false, reason: 'session-expired' };
  }
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = Array.isArray(body.detail) ? body.detail.map(item => item.msg || 'Invalid field').join('. ') : body.detail;
    return { ok: false, reason: detail || `Could not save job (${response.status})` };
  }
  await chrome.storage.local.set({ savedUrls: [...savedUrls.slice(-99), job.job_url] });
  return { ok: true };
}
