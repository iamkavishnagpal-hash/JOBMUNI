const { chromium } = require("playwright");

async function capture() {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  console.log("Navigating to http://localhost:3000/evidence-bank...");
  await page.goto("http://localhost:3000/evidence-bank");
  await page.waitForLoadState("networkidle");

  // Expand the first STAR item
  const starBtn = page.getByRole("button", { name: "View STAR" }).first();
  if (await starBtn.isVisible()) {
    await starBtn.click();
    await page.waitForTimeout(300);
  }

  const screenshotPath = "C:/Users/kavis/.gemini/antigravity-ide/brain/6ca9ded4-9b3c-423e-9098-88d52a854e00/evidence_bank_desktop.png";
  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log(`Desktop screenshot saved to: ${screenshotPath}`);

  // Mobile screenshot
  const mobileContext = await browser.newContext({ viewport: { width: 375, height: 812 } });
  const mobilePage = await mobileContext.newPage();
  await mobilePage.goto("http://localhost:3000/evidence-bank");
  await mobilePage.waitForLoadState("networkidle");

  const mobileScreenshotPath = "C:/Users/kavis/.gemini/antigravity-ide/brain/6ca9ded4-9b3c-423e-9098-88d52a854e00/evidence_bank_mobile.png";
  await mobilePage.screenshot({ path: mobileScreenshotPath, fullPage: true });
  console.log(`Mobile screenshot saved to: ${mobileScreenshotPath}`);

  await browser.close();
}

capture().catch((err) => {
  console.error(err);
  process.exit(1);
});
