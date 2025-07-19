from rightmove_page_scrape import extract_postcode_and_epc

with open("rightmove_example.html", "r", encoding="utf-8") as f:
    html = f.read()

result = extract_postcode_and_epc(html)
print(result)
