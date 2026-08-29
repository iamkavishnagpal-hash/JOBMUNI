const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const TARGET_URL = 'http://localhost:3000';
const QA_DIR = path.join(__dirname, '../../artifacts_screenshots/qa_viewports');

if (!fs.existsSync(QA_DIR)) {
  fs.mkdirSync(QA_DIR, { recursive: true });
}

const VIEWPORTS = [
  { name: '320x800', width: 320, height: 800, isMobile: true },
  { name: '375x812', width: 375, height: 812, isMobile: true },
  { name: '390x844', width: 390, height: 844, isMobile: true },
  { name: '768x1024', width: 768, height: 1024, isMobile: false },
  { name: '1440x900', width: 1440, height: 900, isMobile: false },
  { name: '1920x1080', width: 1920, height: 1080, isMobile: false },
];

const PAGES = [
  { route: '/dashboard', label: 'dashboard' },
  { route: '/jobs', label: 'jobs' },
  { route: '/recruiters', label: 'recruiters' },
  { route: '/applications', label: 'applications' },
  { route: '/interviews', label: 'interviews' },
  { route: '/analytics', label: 'analytics' },
  { route: '/approvals', label: 'approvals' },
  { route: '/settings', label: 'settings' },
];

(async () => {
  console.log('=== STARTING EXTENSIVE MULTI-VIEWPORT VISUAL & FUNCTIONAL QA PASS ===');
  const browser = await chromium.launch({ headless: true });
  
  const report = {
    viewportsTested: [],
    overflowIssues: [],
    consoleErrors: [],
    navigationFailures: [],
  };

  for (const vp of VIEWPORTS) {
    console.log(`\n--- Testing Viewport: ${vp.name} (${vp.width}x${vp.height}) ---`);
    const context = await browser.newContext({
      viewport: { width: vp.width, height: vp.height },
    });
    const page = await context.newPage();

    // Listen for console errors
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        const text = msg.text();
        console.error(`[Console Error @ ${vp.name}]:`, text);
        report.consoleErrors.push({ viewport: vp.name, url: page.url(), message: text });
      }
    });

    page.on('pageerror', (err) => {
      console.error(`[Page Error @ ${vp.name}]:`, err.message);
      report.consoleErrors.push({ viewport: vp.name, url: page.url(), message: err.message });
    });

    for (const pg of PAGES) {
      const url = `${TARGET_URL}${pg.route}`;
      const response = await page.goto(url, { waitUntil: 'networkidle' });
      const status = response ? response.status() : 0;

      if (status !== 200) {
        console.error(`FAILED: ${pg.route} returned status ${status}`);
        report.navigationFailures.push({ viewport: vp.name, route: pg.route, status });
      }

      // Check horizontal overflow
      const overflow = await page.evaluate(() => {
        const docWidth = document.documentElement.scrollWidth;
        const windowWidth = window.innerWidth;
        return { docWidth, windowWidth, hasOverflow: docWidth > windowWidth };
      });

      if (overflow.hasOverflow) {
        console.warn(`[OVERFLOW WARNING] @ ${vp.name} on ${pg.route}: docWidth=${overflow.docWidth} > windowWidth=${overflow.windowWidth}`);
        report.overflowIssues.push({
          viewport: vp.name,
          route: pg.route,
          docWidth: overflow.docWidth,
          windowWidth: overflow.windowWidth,
        });
      }

      // Save screenshot
      const screenshotPath = path.join(QA_DIR, `${vp.name}_${pg.label}.png`);
      await page.screenshot({ path: screenshotPath });
    }

    // Interactive Test: Modal in /jobs
    await page.goto(`${TARGET_URL}/jobs`, { waitUntil: 'networkidle' });
    const ingestBtn = await page.$('button:has-text("Ingest Opportunity"), button:has-text("Ingest Job Description")');
    if (ingestBtn) {
      await ingestBtn.click();
      await page.waitForTimeout(300);
      await page.screenshot({ path: path.join(QA_DIR, `${vp.name}_jobs_modal.png`) });
      // Close modal
      const cancelBtn = await page.$('button:has-text("Cancel")');
      if (cancelBtn) await cancelBtn.click();
    }

    // Interactive Test: Settings slider adjustment and save
    await page.goto(`${TARGET_URL}/settings`, { waitUntil: 'networkidle' });
    const saveBtn = await page.$('button:has-text("Save Configured Weights")');
    if (saveBtn) {
      await saveBtn.click();
      await page.waitForTimeout(500);
      await page.screenshot({ path: path.join(QA_DIR, `${vp.name}_settings_saved.png`) });
    }

    report.viewportsTested.push(vp.name);
    await context.close();
  }

  await browser.close();

  console.log('\n=== QA AUDIT COMPLETE ===');
  console.log('Viewports Tested:', report.viewportsTested);
  console.log('Overflow Issues Found:', report.overflowIssues.length);
  console.log('Console Errors:', report.consoleErrors.length);
  console.log('Navigation Failures:', report.navigationFailures.length);

  fs.writeFileSync(
    path.join(QA_DIR, 'qa_report.json'),
    JSON.stringify(report, null, 2)
  );
})();
