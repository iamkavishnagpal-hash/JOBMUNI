const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const TARGET_URL = 'http://localhost:3000';
const ARTIFACT_DIR = path.join(__dirname, '../../artifacts_screenshots');

if (!fs.existsSync(ARTIFACT_DIR)) {
  fs.mkdirSync(ARTIFACT_DIR, { recursive: true });
}

(async () => {
  console.log('Starting Playwright E2E Verification across Desktop & Mobile...');
  const browser = await chromium.launch({ headless: true });
  
  // 1. Desktop Test (1920x1080)
  const desktopContext = await browser.newContext({ viewport: { width: 1920, height: 1080 } });
  const desktopPage = await desktopContext.newPage();

  // Test Dashboard
  await desktopPage.goto(`${TARGET_URL}/dashboard`, { waitUntil: 'networkidle' });
  console.log('Desktop Dashboard title:', await desktopPage.title());
  await desktopPage.screenshot({ path: path.join(ARTIFACT_DIR, 'desktop_dashboard.png'), fullPage: true });

  // Test Jobs Page & Manual Ingest
  await desktopPage.goto(`${TARGET_URL}/jobs`, { waitUntil: 'networkidle' });
  await desktopPage.screenshot({ path: path.join(ARTIFACT_DIR, 'desktop_jobs_empty.png') });

  // Test Recruiters Page
  await desktopPage.goto(`${TARGET_URL}/recruiters`, { waitUntil: 'networkidle' });
  await desktopPage.screenshot({ path: path.join(ARTIFACT_DIR, 'desktop_recruiters.png') });

  // Test Approvals Page
  await desktopPage.goto(`${TARGET_URL}/approvals`, { waitUntil: 'networkidle' });
  await desktopPage.screenshot({ path: path.join(ARTIFACT_DIR, 'desktop_approvals.png') });

  // Test Settings Page
  await desktopPage.goto(`${TARGET_URL}/settings`, { waitUntil: 'networkidle' });
  await desktopPage.screenshot({ path: path.join(ARTIFACT_DIR, 'desktop_settings.png') });

  // 2. Mobile Viewport Test (375x667)
  const mobileContext = await browser.newContext({ viewport: { width: 375, height: 667 } });
  const mobilePage = await mobileContext.newPage();

  await mobilePage.goto(`${TARGET_URL}/dashboard`, { waitUntil: 'networkidle' });
  await mobilePage.screenshot({ path: path.join(ARTIFACT_DIR, 'mobile_dashboard.png') });

  await mobilePage.goto(`${TARGET_URL}/approvals`, { waitUntil: 'networkidle' });
  await mobilePage.screenshot({ path: path.join(ARTIFACT_DIR, 'mobile_approvals.png') });

  await mobilePage.goto(`${TARGET_URL}/settings`, { waitUntil: 'networkidle' });
  await mobilePage.screenshot({ path: path.join(ARTIFACT_DIR, 'mobile_settings.png') });

  await browser.close();
  console.log('Playwright E2E verification complete! All screenshots saved.');
})();
