import { expect, test } from "@playwright/test";

test("starts and advances a simulated session", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("SIMULATED READER LAB")).toBeVisible();
  await page.getByRole("button", { name: "Step once" }).click();
  await expect(page.getByText("WHY THIS ACTION")).toBeVisible();
  await expect(page.getByText("1 STEPS")).toBeVisible();
});
