const { chromium } = require("playwright");

async function capture() {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  console.log("Navigating to http://localhost:3000/jobs...");
  await page.goto("http://localhost:3000/jobs");
  await page.waitForLoadState("networkidle");

  const jobCard = page.locator(".cursor-pointer").first();
  if (await jobCard.isVisible()) {
    await jobCard.click();
    await page.waitForTimeout(500);
    await page.getByRole("button", { name: /KUBERA Compensation/i }).click();
    await page.waitForTimeout(500);
  }

  const screenshotPath = "C:/Users/kavis/.gemini/antigravity-ide/brain/6ca9ded4-9b3c-423e-9098-88d52a854e00/kubera_compensation_desktop.png";
  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log(`Desktop compensation screenshot saved to: ${screenshotPath}`);

  // Mobile screenshot
  const mobileContext = await browser.newContext({ viewport: { width: 375, height: 812 } });
  const mobilePage = await mobileContext.newPage();
  await mobilePage.goto("http://localhost:3000/jobs");
  await mobilePage.waitForLoadState("networkidle");

  const mobileCard = mobilePage.locator(".cursor-pointer").first();
  if (await mobileCard.isVisible()) {
    await mobileCard.click();
    await mobilePage.waitForTimeout(500);
    await mobilePage.getByRole("button", { name: /KUBERA Compensation/i }).click();
    await mobilePage.waitForTimeout(500);
  }

  const mobileScreenshotPath = "C:/Users/kavis/.gemini/antigravity-ide/brain/6ca9ded4-9b3c-423e-9098-88d52a854e00/kubera_compensation_mobile.png";
  await mobilePage.screenshot({ path: mobileScreenshotPath, fullPage: true });
  console.log(`Mobile compensation screenshot saved to: ${mobileScreenshotPath}`);

  await browser.close();
}

capture().catch((err) => {
  console.error(err);
  process.exit(1);
});
