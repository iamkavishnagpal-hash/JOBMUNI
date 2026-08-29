import { test, expect } from "@playwright/test";

test.describe("Phase 3A: SARASWATI Evidence Bank E2E Verification", () => {
  test("Evidence Bank route loads with full metrics and items", async ({ page }) => {
    await page.goto("/evidence-bank");
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h1")).toContainText("Candidate Evidence Bank");

    // Metrics cards
    await expect(page.getByText("Verified Competencies")).toBeVisible();
    await expect(page.getByText("Backed Evidence Records")).toBeVisible();
    await expect(page.getByText("Ground Truth Confidence")).toBeVisible();

    // Default seeded competencies present
    await expect(page.getByText("SQL", { exact: true }).first()).toBeVisible();
    await expect(page.getByText("Snowflake", { exact: true }).first()).toBeVisible();
    await expect(page.getByText("dbt", { exact: true }).first()).toBeVisible();
    await expect(page.getByText("Looker", { exact: true }).first()).toBeVisible();
  });

  test("Category filtering and STAR expansion work smoothly", async ({ page }) => {
    await page.goto("/evidence-bank");
    await page.waitForLoadState("networkidle");

    // Click on Tech Skills tab
    await page.getByRole("button", { name: "Tech Skills" }).click();
    await expect(page.getByText("SQL", { exact: true }).first()).toBeVisible();

    // Expand STAR breakdown for Snowflake or first item
    const viewStarBtn = page.getByRole("button", { name: "View STAR" }).first();
    await expect(viewStarBtn).toBeVisible();
    await viewStarBtn.click();
    await expect(page.getByText("Structured STAR Context")).toBeVisible();
  });

  test("Search filtering works accurately", async ({ page }) => {
    await page.goto("/evidence-bank");
    await page.waitForLoadState("networkidle");
    const searchInput = page.getByPlaceholder("Search skills or metrics...");
    await searchInput.fill("Snowflake");
    await expect(page.getByText(/Enterprise Warehouse Cost|Enterprise Snowflake/).first()).toBeVisible();
  });

  test("Sidebar navigates directly to Evidence Bank on desktop", async ({ page, isMobile }) => {
    test.skip(isMobile, "Desktop sidebar only visible on desktop viewports");
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
    const navLink = page.getByRole("link", { name: /Evidence Bank/i });
    await expect(navLink).toBeVisible();
    await navLink.click();
    await expect(page).toHaveURL(/.*evidence-bank/);
  });

  test("Evidence Bank has zero horizontal overflow on mobile viewports", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 });
    await page.goto("/evidence-bank");
    await page.waitForLoadState("networkidle");

    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    const clientWidth = await page.evaluate(() => document.documentElement.clientWidth);
    expect(scrollWidth).toBeLessThanOrEqual(clientWidth + 1);
  });
});
