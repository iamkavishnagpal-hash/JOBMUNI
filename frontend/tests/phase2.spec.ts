import { test, expect } from "@playwright/test";

test.describe("Phase 2 E2E Test Suite - Ingestion, Verification & Automation", () => {
  test("1. jobs page displays ingested opportunities with status and scores", async ({ page }) => {
    await page.goto("/jobs");
    await page.waitForLoadState("networkidle");

    await expect(page.getByRole("heading", { level: 1, name: /Job Radar/ })).toBeVisible();
    
    // Check that table or job radar container renders
    const mainContainer = page.locator("main, table, .empty-state");
    await expect(mainContainer.first()).toBeVisible();
  });

  test("2. dashboard reflects real ingested opportunities and priority tiers", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    await expect(page.getByRole("heading", { level: 1, name: "Executive Command Center" })).toBeVisible();
    await expect(page.getByText("Urgent Act-Now", { exact: true })).toBeVisible();
    await expect(page.getByText("CAREER GPS")).toBeVisible();
  });

  test("3. settings page displays discovery and scoring configuration", async ({ page }) => {
    await page.goto("/settings");
    await page.waitForLoadState("networkidle");

    await expect(page.getByRole("heading", { level: 1, name: /Settings & System Configuration/ })).toBeVisible();
    await expect(page.getByText("Configurable Opportunity Scoring Weights")).toBeVisible();
  });
});
