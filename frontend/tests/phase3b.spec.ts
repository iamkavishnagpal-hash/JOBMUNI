import { test, expect } from "@playwright/test";

test.describe("Phase 3B: ARJUNA JD Alignment E2E Verification", () => {
  test.beforeEach(async ({ page }) => {
    // Ingest a high-fit job if none exist
    await page.goto("/jobs");
    const count = await page.locator(".cursor-pointer").count();
    if (count === 0) {
      await page.getByRole("button", { name: /Ingest Opportunity/i }).click();
      await page.getByPlaceholder("e.g. Snowflake").fill("Snowflake");
      await page.getByPlaceholder("e.g. Lead BI Engineer").fill("Senior Analytics Engineer");
      await page.getByPlaceholder("Paste full job description text here...").fill(
        "We are looking for a Senior Analytics Engineer with strong Snowflake, dbt, and SQL skills. Preferred experience with Looker and Python."
      );
      await page.getByRole("button", { name: /Ingest & Parse Opportunity/i }).click();
      await page.waitForTimeout(500);
    }
  });

  test("Jobs page displays ARJUNA match verdict badges and cards", async ({ page }) => {
    await page.goto("/jobs");
    await expect(page.locator("h1")).toContainText("Job Radar");

    const jobCard = page.locator(".cursor-pointer").first();
    await expect(jobCard).toBeVisible();
    await expect(page.getByText(/View Intelligence/i).first()).toBeVisible();
  });

  test("Clicking job card opens ARJUNA Precision Alignment Modal with gauges and reasoning", async ({ page }) => {
    await page.goto("/jobs");
    const jobCard = page.locator(".cursor-pointer").first();
    await jobCard.click();

    // Click ARJUNA Skill Fit tab
    const arjunaTab = page.getByRole("button", { name: /ARJUNA Skill Fit/i });
    await expect(arjunaTab).toBeVisible();
    await arjunaTab.click();

    // Verify 4 coverage gauges
    await expect(page.getByText("Required Coverage")).toBeVisible();
    await expect(page.getByText("Preferred Coverage")).toBeVisible();
    await expect(page.getByText("Evidence Density")).toBeVisible();
    await expect(page.getByText("Seniority Fit")).toBeVisible();

    // Verify Explainable Rationale within dialog
    const dialog = page.getByRole("dialog");
    await expect(dialog.getByText("Explainable Rationale & Action")).toBeVisible();

    // Verify Matched Skills Section
    await expect(dialog.getByText(/Matched Required Skills/i)).toBeVisible();
  });

  test("ARJUNA Alignment Modal has zero horizontal overflow on mobile viewports", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/jobs");
    await page.waitForLoadState("networkidle");

    const jobCard = page.locator(".cursor-pointer").first();
    if (await jobCard.isVisible()) {
      await jobCard.click();
      await page.getByRole("button", { name: /ARJUNA Skill Fit/i }).click();
      await page.waitForTimeout(300);
    }

    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1);
  });
});
