import { test, expect } from "@playwright/test";
import path from "path";
import fs from "fs";

test.describe("Phase 1 E2E Test Suite - Kavish Career OS", () => {
  
  // 1. Application loads
  test("1. application loads and redirects to dashboard", async ({ page }) => {
    await page.goto("/");
    await page.waitForURL("**/dashboard");
    await expect(page).toHaveTitle(/Kavish Career OS/);
    await expect(page.getByRole("heading", { level: 1, name: "Executive Command Center" })).toBeVisible();
  });

  // 2. Dashboard route loads
  test("2. dashboard route loads with live metrics and career gps banner", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { level: 1, name: "Executive Command Center" })).toBeVisible();
    await expect(page.getByText("Urgent Act-Now", { exact: true })).toBeVisible();
    await expect(page.getByText("CAREER GPS")).toBeVisible();
    await expect(page.getByRole("button", { name: "Refresh Metrics" })).toBeVisible();
  });

  // 3. Jobs route loads
  test("3. jobs route loads with opportunity radar and modal trigger", async ({ page }) => {
    await page.goto("/jobs");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { level: 1, name: /Job Radar/ })).toBeVisible();
    const ingestBtn = page.getByRole("button", { name: /Ingest Opportunity|Ingest Job Description/ });
    await expect(ingestBtn.first()).toBeVisible();
  });

  // 4. Recruiters route loads
  test("4. recruiters route loads with CRM interface", async ({ page }) => {
    await page.goto("/recruiters");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { level: 1, name: /Recruiter CRM/ })).toBeVisible();
    await expect(page.getByRole("button", { name: /Add Recruiter Contact|Add Recruiter/ }).first()).toBeVisible();
  });

  // 5. Applications route loads
  test("5. applications route loads with pipeline stages", async ({ page }) => {
    await page.goto("/applications");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { level: 1, name: /Application Pipeline/ })).toBeVisible();
  });

  // 6. Interviews route loads
  test("6. interviews route loads with assistant shell", async ({ page }) => {
    await page.goto("/interviews");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { level: 1, name: /Interview Assistant/ })).toBeVisible();
  });

  // 7. Analytics route loads
  test("7. analytics route loads with conversion telemetry", async ({ page }) => {
    await page.goto("/analytics");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { level: 1, name: /Career Funnel/ })).toBeVisible();
    await expect(page.getByText("Full Funnel Progression")).toBeVisible();
  });

  // 8. Approvals route loads
  test("8. approvals route loads with Level 2 autonomy guard", async ({ page }) => {
    await page.goto("/approvals");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { level: 1, name: /Approval Center/ })).toBeVisible();
    await expect(page.getByText(/LEVEL 2/)).toBeVisible();
  });

  // 9. Settings route loads
  test("9. settings route loads with scoring weight sliders and service status", async ({ page }) => {
    await page.goto("/settings");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { level: 1, name: /Settings & System Configuration/ })).toBeVisible();
    await expect(page.getByText("Configurable Opportunity Scoring Weights")).toBeVisible();
    await expect(page.getByRole("button", { name: "Save Configured Weights" })).toBeVisible();
    await expect(page.getByText("Service Status & Boundary")).toBeVisible();
  });

  // 10. Mobile viewport navigation works
  test("10. mobile viewport navigation works via bottom bar", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    // Target the mobile navigation bar link for Radar
    const mobileRadarLink = page.locator('nav.md\\:hidden a[href="/jobs"]');
    await expect(mobileRadarLink).toBeVisible();
    await mobileRadarLink.click();
    await page.waitForURL("**/jobs");
    await expect(page.getByRole("heading", { level: 1, name: /Job Radar/ })).toBeVisible();

    // Target the mobile navigation bar link for Approvals
    const mobileApprovalsLink = page.locator('nav.md\\:hidden a[href="/approvals"]');
    await expect(mobileApprovalsLink).toBeVisible();
    await mobileApprovalsLink.click();
    await page.waitForURL("**/approvals");
    await expect(page.getByRole("heading", { level: 1, name: /Approval Center/ })).toBeVisible();

    // Target the mobile navigation bar link for Settings
    const mobileSettingsLink = page.locator('nav.md\\:hidden a[href="/settings"]');
    await expect(mobileSettingsLink).toBeVisible();
    await mobileSettingsLink.click();
    await page.waitForURL("**/settings");
    await expect(page.getByRole("heading", { level: 1, name: /Settings/ })).toBeVisible();
  });

  // 11. No horizontal overflow on mobile
  test("11. no horizontal overflow on mobile viewports (320px, 375px, 390px)", async ({ page }) => {
    const mobileWidths = [320, 375, 390];
    const testRoutes = ["/dashboard", "/jobs", "/recruiters", "/approvals", "/settings"];

    for (const width of mobileWidths) {
      await page.setViewportSize({ width, height: 800 });
      for (const route of testRoutes) {
        await page.goto(route);
        await page.waitForLoadState("networkidle");

        const overflow = await page.evaluate(() => {
          return {
            scrollWidth: document.documentElement.scrollWidth,
            innerWidth: window.innerWidth,
          };
        });

        expect(
          overflow.scrollWidth,
          `Horizontal overflow on ${route} at ${width}px: scrollWidth (${overflow.scrollWidth}) > innerWidth (${overflow.innerWidth})`
        ).toBeLessThanOrEqual(overflow.innerWidth);
      }
    }
  });

  // 12. Production build succeeds
  test("12. production build verification test", async () => {
    const buildManifestPath = path.join(__dirname, "../.next/build-manifest.json");
    expect(fs.existsSync(buildManifestPath), "Next.js .next/build-manifest.json must exist from production build").toBeTruthy();
  });

});
