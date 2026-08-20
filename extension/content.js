function text(selectors) {
  for (const selector of selectors) {
    const node = document.querySelector(selector);
    if (node?.innerText?.trim()) return node.innerText.trim();
  }
  return '';
}

function siteExtract(host) {
  if (host.includes('linkedin.com')) {
    return {
      role: text(['h1.job-details-jobs-unified-top-card__job-title', '.job-details-jobs-unified-top-card__job-title', 'h1.jobs-unified-top-card__job-title', 'h1.t-24']),
      company: text(['.job-details-jobs-unified-top-card__company-name a', '.job-details-jobs-unified-top-card__company-name', '.jobs-unified-top-card__company-name a', 'a.app-aware-link[href*="/company/"]']),
      location: text(['.job-details-jobs-unified-top-card__primary-description-container span', '.jobs-unified-top-card__bullet', '.job-details-jobs-unified-top-card__tertiary-description-container span']),
      source: 'LinkedIn'
    };
  }
  if (host.includes('indeed.com')) {
    return {
      role: text(['h1.jobsearch-JobInfoHeader-title', 'h1[data-testid="jobsearch-JobInfoHeader-title"]']),
      company: text(['[data-testid="inlineHeader-companyName"]', '.jobsearch-CompanyInfoContainer a', '.jobsearch-InlineCompanyRating div']),
      location: text(['[data-testid="job-location"]', '.jobsearch-JobInfoHeader-subtitle div']),
      source: 'Indeed'
    };
  }
  if (host.includes('glassdoor.com')) {
    return {
      role: text(['[data-test="job-title"]', 'h1']),
      company: text(['[data-test="employer-name"]']),
      location: text(['[data-test="location"]']),
      source: 'Glassdoor'
    };
  }
  return null;
}

function extractJob() {
  const body = document.body?.innerText || '';
  const host = location.hostname.replace(/^www\./, '');
  const site = siteExtract(host) || {};

  let role = site.role || text(['h1', '[data-testid="job-title"]', '[class*="job-title"]']);
  let company = site.company || document.querySelector('meta[property="og:site_name"]')?.content || text(['[data-testid="company-name"]', '[class*="company-name"]']);

  if (!role || !company) {
    // Fallback: parse the page/meta title for common "Role at Company" / "Role - Company" / "Company hiring Role" patterns.
    const raw = (document.querySelector('meta[property="og:title"]')?.content || document.title || '').replace(/\s+/g, ' ').trim();
    let m;
    if (!role && !company && (m = raw.match(/^(.+?)\s+hiring\s+(.+?)(?:\s+in\s+.+)?$/i))) {
      company = company || m[1].trim();
      role = role || m[2].trim();
    } else if (!role && !company && (m = raw.match(/^(.+?)\s+-\s+(.+?)(?:\s+-\s+.+)?$/))) {
      role = role || m[1].trim();
      company = company || m[2].trim();
    } else if (!role && !company && (m = raw.match(/^(.+?)\s+at\s+(.+)$/i))) {
      role = role || m[1].trim();
      company = company || m[2].trim();
    } else if (!role) {
      role = raw.split('|')[0].trim();
    }
  }

  if (!company) company = host.split('.')[0];

  const location_ = site.location || text(['[data-testid="job-location"]', '[class*="location"]']) || 'See job posting';
  const salary = (body.match(/(?:₹|\$|€|£)\s?[\d,.]+\s?(?:k|K|LPA|lpa)?(?:\s?[-–]\s?(?:₹|\$|€|£)?\s?[\d,.]+\s?(?:k|K|LPA|lpa)?)?/i) || [''])[0];
  const work_mode = /hybrid/i.test(body) ? 'Hybrid' : /remote/i.test(body) ? 'Remote' : /on[- ]?site/i.test(body) ? 'Onsite' : 'Unknown';
  const employment_type = /internship/i.test(body) ? 'Internship' : /contract/i.test(body) ? 'Contract' : /part[- ]?time/i.test(body) ? 'Part-time' : 'Full-time';

  return {
    company: company.slice(0, 120),
    role: (role || 'Role not detected').slice(0, 120),
    location: location_.slice(0, 120),
    salary: salary.slice(0, 80) || null,
    employment_type,
    work_mode,
    job_url: location.href.slice(0, 500),
    source: (site.source || host).slice(0, 80),
    status: 'Wishlist',
    priority: 'Normal',
    next_step: null,
    notes: null
  };
}

function toast(message, ok) {
  const el = document.createElement('div');
  el.textContent = message;
  el.style.cssText = `position:fixed;z-index:2147483647;bottom:20px;right:20px;padding:12px 16px;border-radius:8px;font:600 13px Arial,sans-serif;color:#fff;background:${ok ? '#26392e' : '#8a3324'};box-shadow:0 6px 20px rgba(0,0,0,.25);transition:opacity .3s;max-width:280px`;
  document.documentElement.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 3500);
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'extract-job') sendResponse(extractJob());
});

let lastSubmit = 0;
document.addEventListener('submit', (event) => {
  const formText = `${event.target.innerText || ''} ${event.submitter?.innerText || ''}`;
  if (!/apply|submit application|send application/i.test(formText) || Date.now() - lastSubmit < 10000) return;
  lastSubmit = Date.now();
  const job = { ...extractJob(), status: 'Applied', notes: 'Captured automatically by CareerFlow.', automatic: true };
  chrome.runtime.sendMessage({ type: 'capture-job', job }, (result) => {
    if (!result) return;
    if (result.ok) toast(result.duplicate ? 'Already in your CareerFlow pipeline.' : `Saved "${job.role}" to CareerFlow ✓`, true);
    else if (result.reason !== 'disabled' && result.reason !== 'not-authenticated') toast(`CareerFlow: ${result.reason}`, false);
  });
}, true);
