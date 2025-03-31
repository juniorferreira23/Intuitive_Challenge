from scripts import scraper_gov_docs, extract_tables_pdf, scraper_operators_docs, populate_database


if __name__ == "__main__":
    scraper_gov_docs.main()
    extract_tables_pdf.main()
    scraper_operators_docs.main()
    populate_database.main()
