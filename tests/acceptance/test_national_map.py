def wait_for_map_layer(page, layer, attempts=10, check_interval=10):
    for i in range(attempts):
        isHidden = page.evaluate(
            f'() => mapControllers.map.map.getLayer("{layer}").isHidden()'
        )
        if isHidden is False:
            return True
        page.wait_for_timeout(check_interval)
    assert False, f"Layer {layer} did not appear on the map"


def test_toggle_layers_on_the_national_map_correctly_shows_entity(
    server_process,
    page,
    context,
    add_base_entities_to_database_yield_reset,
    skip_if_not_supportsGL,
    test_settings,
    BASE_URL,
):
    # as the map xy coords are dependent on the viewport size, we need to set it to make sure the tests are consistent
    page.set_viewport_size({"width": 800, "height": 600})

    page.goto(
        BASE_URL + "/map/#50.88865897214836,-2.260771340418273,11.711391365982688z"
    )
    page.get_by_label("Conservation area").check()
    wait_for_map_layer(page, "conservation-area-source-fill-extrusion")
