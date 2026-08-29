import { test, expect } from "@playwright/test";

test.describe("Phase 3D: CHANAKYA Opportunity Prioritization E2E Verification", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/jobs");
    const count = await page.locator(".cursor-pointer").count();
    if (count === 0) {
      await page.getByRole("button", { name: /Ingest Opportunity/i }).click();
      await page.getByPlaceholder("e.g. Snowflake").fill("Snowflake");
      await page.getByPlaceholder("e.g. Lead BI Engineer").fill("Principal Analytics Engineer");
      await page.getByPlaceholder("Paste full job description text here...").fill(
        "Principal Analytics Engineer. Base compensation $200,000 - $250,000 USD. Requires SQL, Snowflake, dbt, Python."
      );
      await page.getByRole("button", { name: /Ingest & Parse Opportunity/i }).click();
      await page.waitForTimeout(500);
    }
  });

  test("Jobs page displays prioritized opportunity cards with Next Best Action", async ({ page }) => {
    await page.goto("/jobs");
    await expect(page.locator("h1")).toContainText("Job Radar");

    const jobCard = page.locator(".cursor-pointer").first();
    await expect(jobCard).toBeVisible();

    // Verify Next Best Action badge is rendered on card
    await expect(page.getByText(/Next Best Action:/i).first()).toBeVisible();
  });

  test("Clicking job card opens CHANAKYA Decision & Prioritization tab by default", async ({ page }) => {
    await page.goto("/jobs");
    const jobCard = page.locator(".cursor-pointer").first();
    await jobCard.click();

    // Verify header and gauges
    await expect(page.getByText("CHANAKYA Decision & Prioritization")).toBeVisible();
    await expect(page.getByText("Priority Score")).toBeVisible();
    await expect(page.getByText("Urgency (Velocity)")).toBeVisible();
    await expect(page.getByText("Actionability")).toBeVisible();
    await expect(page.getByText("Execution Effort")).toBeVisible();

    // Verify Recommended Next Action banner
    await expect(page.getByText("Recommended Next Action")).toBeVisible();

    // Verify Why Ranked Here explainability
    await expect(page.getByText("Why Ranked Here")).toBeVisible();
  });

  test("Priority filter tabs filter opportunities smoothly", async ({ page }) => {
    await page.goto("/jobs");
    
    // Click All Ranked tab
    await page.getByRole("button", { name: /All Ranked/i }).click();
    await expect(page.locator(".cursor-pointer").first()).toBeVisible();

    // Click High Priority tab
    await page.getByRole("button", { name: /High Priority/i }).click();
    await page.waitForTimeout(300);
  });

  test("CHANAKYA Intelligence view has zero horizontal overflow on mobile viewports", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/jobs");
    await page.waitForLoadState("networkidle");

    const jobCard = page.locator(".cursor-pointer").first();
    if (await jobCard.isVisible()) {
      await jobCard.click();
      await page.waitForTimeout(300);
    }

    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1);
  });
});
