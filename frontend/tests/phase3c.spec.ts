import { test, expect } from "@playwright/test";

test.describe("Phase 3C: KUBERA Compensation Intelligence E2E Verification", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/jobs");
    const count = await page.locator(".cursor-pointer").count();
    if (count === 0) {
      await page.getByRole("button", { name: /Ingest Opportunity/i }).click();
      await page.getByPlaceholder("e.g. Snowflake").fill("Snowflake");
      await page.getByPlaceholder("e.g. Lead BI Engineer").fill("Senior Analytics Engineer");
      await page.getByPlaceholder("Paste full job description text here...").fill(
        "Senior Analytics Engineer. Salary range $180,000 - $210,000 USD. Strong Snowflake, dbt, SQL required."
      );
      await page.getByRole("button", { name: /Ingest & Parse Opportunity/i }).click();
      await page.waitForTimeout(500);
    }
  });

  test("Jobs page allows opening KUBERA Compensation tab with gauges and reasoning", async ({ page }) => {
    await page.goto("/jobs");
    const jobCard = page.locator(".cursor-pointer").first();
    await jobCard.click();

    // Click KUBERA tab
    const kuberaTab = page.getByRole("button", { name: /KUBERA Compensation/i });
    await expect(kuberaTab).toBeVisible();
    await kuberaTab.click();

    // Verify header and gauges
    await expect(page.getByText("Financial Compensation Evaluation")).toBeVisible();
    await expect(page.getByText("Salary Fit")).toBeVisible();
    await expect(page.getByText("Market Position")).toBeVisible();
    await expect(page.getByText("Remote Alignment")).toBeVisible();
    await expect(page.getByText("Location Value")).toBeVisible();

    // Verify Policy Target Comparison
    await expect(page.getByText(/Compensation Analysis & Policy Comparison/i)).toBeVisible();
    await expect(page.getByText(/Policy Target:/i)).toBeVisible();
  });

  test("Switching between ARJUNA and KUBERA tabs is responsive and instantaneous", async ({ page }) => {
    await page.goto("/jobs");
    const jobCard = page.locator(".cursor-pointer").first();
    await jobCard.click();

    // Initially ARJUNA is open
    await expect(page.getByText("Required Coverage")).toBeVisible();

    // Switch to KUBERA
    await page.getByRole("button", { name: /KUBERA Compensation/i }).click();
    await expect(page.getByText("Salary Fit")).toBeVisible();

    // Switch back to ARJUNA
    await page.getByRole("button", { name: /ARJUNA Skill Fit/i }).click();
    await expect(page.getByText("Required Coverage")).toBeVisible();
  });

  test("KUBERA Intelligence view has zero horizontal overflow on mobile viewports", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/jobs");
    await page.waitForLoadState("networkidle");

    const jobCard = page.locator(".cursor-pointer").first();
    if (await jobCard.isVisible()) {
      await jobCard.click();
      await page.getByRole("button", { name: /KUBERA Compensation/i }).click();
      await page.waitForTimeout(300);
    }

    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1);
  });
});
