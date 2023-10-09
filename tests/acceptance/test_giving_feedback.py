def test_give_feedback_on_a_dataset(
    server_process, BASE_URL, page, add_base_entities_to_database_yield_reset
):
    page.goto(BASE_URL)

    page.get_by_role("link", name="Datasets", exact=True).click()
    page.get_by_role("link", name="Geography").click()
    page.get_by_role("link", name="Brownfield site").click()
    page.get_by_role("link", name="Give feedback on this dataset").click()

    # ensure that the page has redirected to the google form
    assert "docs.google.com" in page.url
    assert page.get_by_role("heading", name="Give feedback on this dataset")

    # had to add this as it seems to take some time for Google forms to auto populate this field
    page.wait_for_timeout(500)

    # ensure the form has the correct dataset name
    assert (
        page.get_by_role(
            "textbox", name="Which dataset were you looking at?"
        ).input_value()
        == "Brownfield site"
    )
