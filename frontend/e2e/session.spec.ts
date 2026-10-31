import { expect, test } from "@playwright/test";

test("starts and advances a simulated session", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Simulated reader lab")).toBeVisible();
  await page.getByRole("button", { name: "Step once" }).click();
  await expect(page.getByText("Why this action")).toBeVisible();
  await expect(page.getByText("1 step")).toBeVisible();
});
