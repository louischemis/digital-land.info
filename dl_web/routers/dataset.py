import logging
import urllib.parse
import json

from digital_land.view_model import ViewModel
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from ..resources import fetch, get_view_model, specification, templates
from ..utils import create_dict

router = APIRouter()
logger = logging.getLogger(__name__)

# base_url = "http://127.0.0.1/digital-land/"
# base_url = "http://127.0.0.1:8001/digital-land/"
base_url = "http://datasetteawsentityv2-env.eba-gbrdriub.eu-west-2.elasticbeanstalk.com/digital-land/"
datasette_url = "https://datasette.digital-land.info/"


async def get_datasets():
    url = f"{base_url}dataset.json?_shape=object"
    logger.info("get_datasets: %s", url)
    return await fetch(url)


async def get_datasets_with_theme():
    url = f"{datasette_url}digital-land.json?sql=SELECT%0D%0A++DISTINCT+dataset.dataset%2C%0D%0A++dataset.name%2C%0D%0A++dataset.plural%2C%0D%0A++dataset.typology%2C%0D%0A++%28%0D%0A++++CASE%0D%0A++++++WHEN+pipeline.pipeline+IS+NOT+NULL+THEN+1%0D%0A++++++WHEN+pipeline.pipeline+IS+NULL+THEN+0%0D%0A++++END%0D%0A++%29+AS+dataset_active%2C%0D%0A++GROUP_CONCAT%28dataset_theme.theme%2C+%22%3B%22%29+AS+dataset_themes%0D%0AFROM%0D%0A++dataset%0D%0A++LEFT+JOIN+pipeline+ON+dataset.dataset+%3D+pipeline.pipeline%0D%0A++INNER+JOIN+dataset_theme+ON+dataset.dataset+%3D+dataset_theme.dataset%0D%0Agroup+by%0D%0A++dataset.dataset%0D%0Aorder+by%0D%0Adataset.name+ASC"
    logger.info("get_datasets_with_themes: %s", url)
    return await fetch(url)


async def get_dataset(dataset):
    url = f"{base_url}dataset.json?_shape=object&dataset={urllib.parse.quote(dataset)}"
    logger.info("get_dataset: %s", url)
    return await fetch(url)


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    response = await get_datasets_with_theme()
    results = [create_dict(response["columns"], row) for row in response["rows"]]
    datasets = [d for d in results if d['dataset_active']]
    themes = {}
    for d in datasets:
        dataset_themes = d['dataset_themes'].split(";")
        for theme in dataset_themes:
            themes.setdefault(theme, {'dataset': []})
            themes[theme]['dataset'].append(d)


    return templates.TemplateResponse(
        "dataset_index.html", {"request": request, "datasets": datasets, "themes": themes}
    )


@router.get("/{dataset}", response_class=HTMLResponse)
async def get_dataset_index(
    request: Request, dataset: str, view_model: ViewModel = Depends(get_view_model)
):
    try:
        _dataset = await get_dataset(dataset)
        typology = specification.field_typology(
            dataset
        )  # replace this with typology from dataset
        entities = view_model.list_entities(typology, dataset)
        return templates.TemplateResponse(
            "dataset.html",
            {
                "request": request,
                "dataset": _dataset[dataset],
                "entities": entities,
                "key_field": specification.key_field(typology),
            },
        )
    except KeyError as e:
        logger.exception(e)
        return templates.TemplateResponse(
            "dataset-backlog.html",
            {
                "request": request,
                "name": dataset.replace("-", " ").capitalize(),
            },
        )
