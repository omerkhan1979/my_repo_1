from playwright.sync_api import sync_playwright

with sync_playwright() as playwright:
  browser = playwright.chromium.launch()
  context = browser.newContext()
  page = context.newPage()
  
  # Test: has title
  page.goto('https://playwright.dev/')
  assert 'Playwright' in page.title()
  
  # Test: get started link
  page.goto('https://playwright.dev/')
  page.click('link=Get started')
  assert page.isVisible('heading=Installation')
  
  browser.close()
