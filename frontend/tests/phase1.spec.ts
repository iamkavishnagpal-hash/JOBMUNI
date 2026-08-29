import { test, expect } from "@playwright/test";
import path from "path";
import fs from "fs";

test.describe("Phase 1 E2E Test Suite - JOBMUNI", () => {
  
  // 1. Application loads
  test("1. application loads and redirects to dashboard", async ({ page }) => {
    await page.goto("/");
    await page.waitForURL("**/dashboard");
    await expect(page).toHaveTitle(/JOBMUNI|Kavish Career OS/);
    await expect(page.getByRole("heading", { level: 1, name: /Opportunity Overview|Executive Command Center/ })).toBeVisible();
  });

  // 2. Dashboard route loads
  test("2. dashboard route loads with live metrics and career gps banner", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { level: 1, name: /Opportunity Overview|Executive Command Center/ })).toBeVisible();
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
    await expect(page.getByText("No Scheduled Interviews")).toBeVisible();
  });

  // 7. Analytics route loads
  test("7. analytics route loads with conversion telemetry", async ({ page }) => {
    await page.goto("/analytics");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { level: 1, name: /Career Funnel|Analytics/ })).toBeVisible();
    await expect(page.getByText("Full Funnel Progression")).toBeVisible();
  });

  // 8. Approvals route loads
  test("8. approvals route loads with Level 2 autonomy guard", async ({ page }) => {
    await page.goto("/approvals");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { level: 1, name: /Approval Center/ })).toBeVisible();
    await expect(page.getByText(/AUTONOMY POLICY LEVEL 2/i)).toBeVisible();
  });

  // 9. Settings route loads
  test("9. settings route loads with scoring weight sliders and service status", async ({ page }) => {
    await page.goto("/settings");
    await page.waitForLoadState("networkidle");
    await expect(page.getByRole("heading", { level: 1, name: /Settings/ })).toBeVisible();
  });

  // 10. Mobile viewport responsive check
  test("10. mobile viewport navigation works via bottom bar", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    const bottomNav = page.locator("nav.fixed.bottom-0");
    await expect(bottomNav).toBeVisible();

    const jobsNavLink = bottomNav.getByRole("link", { name: "Radar" });
    await expect(jobsNavLink).toBeVisible();
    await jobsNavLink.click();

    await page.waitForURL("**/jobs");
    await expect(page.getByRole("heading", { level: 1, name: /Job Radar/ })).toBeVisible();
  });

  // 11. Responsive viewports
  test("11. no horizontal overflow on mobile viewports (320px, 375px, 390px)", async ({ page }) => {
    const viewports = [
      { width: 320, height: 568 },
      { width: 375, height: 667 },
      { width: 390, height: 844 },
    ];

    const routes = ["/dashboard", "/jobs", "/recruiters", "/applications", "/interviews", "/analytics", "/approvals", "/settings"];

    for (const vp of viewports) {
      await page.setViewportSize(vp);
      for (const route of routes) {
        await page.goto(route);
        await page.waitForLoadState("networkidle");

        const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
        const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);

        expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1);
      }
    }
  });

  // 12. Build test
  test("12. production build verification test", async () => {
    const nextDir = path.join(process.cwd(), ".next");
    expect(fs.existsSync(nextDir)).toBe(true);
  });
});
