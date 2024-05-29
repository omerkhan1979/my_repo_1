from playwright.sync_api import sync_playwright

def run(playwright):
    #browser = playwright.chromium.launch()
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    test_example(page)
    browser.close()

def test_example(page):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.google.com/")
    page.get_by_label("Search", exact=True).click()
    page.get_by_label("Search", exact=True).fill("playwright")
    page.get_by_text("playwright", exact=True).click()
    page.goto("https://www.google.com/search?q=playwright&sca_esv=d312657b286d9ff2&source=hp&ei=HzVOZs6DAt_d2roPuoWcuAE&iflsig=AL9hbdgAAAAAZk5DL_H8Ef2wJneN9W8L5q3DHU2boQfd&oq=playwright&gs_lp=Egdnd3Mtd2l6GgIYAiIKcGxheXdyaWdodCoCCAAyCxAAGIAEGLEDGIMBMhEQLhiABBixAxiDARjHARivATILEAAYgAQYsQMYgwEyCBAAGIAEGLEDMgsQABiABBixAxiDATILEAAYgAQYsQMYgwEyCBAAGIAEGLEDMgUQABiABDILEAAYgAQYsQMYgwEyCxAAGIAEGLEDGIMBSI0jUL8CWKgNcAF4AJABAJgBigGgAZ0HqgEDNi40uAEByAEA-AEBmAILoALSB6gCCsICEBAAGAMY5QIY6gIYjAMYjwHCAg4QABiABBixAxiDARiKBcICDhAuGIAEGLEDGIMBGIoFwgIREC4YgAQYsQMY0QMYgwEYxwHCAgUQLhiABMICDhAuGIAEGLEDGNEDGMcBwgIOEC4YgAQYsQMYgwEY1ALCAg4QABiABBixAxiLAxjuBMICFxAuGIAEGKADGLEDGNMDGOUEGKgDGIsDwgIIEAAYgAQYiwPCAg4QABiABBixAxiDARiLA8ICCxAAGIAEGJIDGIoFwgIIEAAYgAQYyQPCAgsQABiABBixAxiLA8ICCxAuGIAEGLEDGOUEwgIIEC4YgAQYsQOYAwmSBwM3LjSgB8Vo&sclient=gws-wiz#cobssid=s")
    page.get_by_role("link", name="Playwright: Fast and reliable").click()
    page.get_by_role("link", name="Get started").click()
    page.get_by_role("link", name="Write tests using web first").click()
    page.get_by_role("link", name="Run single test, multiple").click()
    page.get_by_role("link", name="How to run tests from the").click()


with sync_playwright() as playwright:
    run(playwright)