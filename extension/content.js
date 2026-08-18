function text(selectors) {
  for (const selector of selectors) { const node = document.querySelector(selector); if (node?.innerText?.trim()) return node.innerText.trim(); }
  return '';
}

function extractJob() {
  const body = document.body?.innerText || '';
  const host = location.hostname.replace(/^www\./, '');
  const title = text(['h1', '[data-testid="job-title"]', '[class*="job-title"]']) || document.title.split('|')[0].trim();
  const company = document.querySelector('meta[property="og:site_name"]')?.content || text(['[data-testid="company-name"]', '[class*="company-name"]']) || host.split('.')[0];
  const salary = (body.match(/(?:₹|\$|€|£)\s?[\d,.]+\s?(?:k|K|LPA|lpa)?(?:\s?[-–]\s?(?:₹|\$|€|£)?\s?[\d,.]+\s?(?:k|K|LPA|lpa)?)?/i) || [''])[0];
  const work_mode = /hybrid/i.test(body) ? 'Hybrid' : /remote/i.test(body) ? 'Remote' : /on[- ]?site/i.test(body) ? 'Onsite' : 'Unknown';
  const employment_type = /internship/i.test(body) ? 'Internship' : /contract/i.test(body) ? 'Contract' : /part[- ]?time/i.test(body) ? 'Part-time' : 'Full-time';
  return {company: company.slice(0, 120), role: title.slice(0, 120), location: (text(['[data-testid="job-location"]', '[class*="location"]']) || 'See job posting').slice(0, 120), salary: salary.slice(0, 80) || null, employment_type, work_mode, job_url: location.href.slice(0, 500), source: host.slice(0, 80), status: 'Applied', priority: 'Normal', next_step: null, notes: 'Captured automatically by CareerFlow.'};
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => { if (message.type === 'extract-job') sendResponse(extractJob()); });

let lastSubmit = 0;
document.addEventListener('submit', (event) => {
  const formText = `${event.target.innerText || ''} ${event.submitter?.innerText || ''}`;
  if (!/apply|submit application|send application/i.test(formText) || Date.now() - lastSubmit < 10000) return;
  lastSubmit = Date.now();
  chrome.runtime.sendMessage({type: 'capture-job', job: {...extractJob(), automatic: true}});
}, true);
