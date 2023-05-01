"""
Main service
"""
import os
import traceback
import requests
import json
from fastapi import BackgroundTasks, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from .AuthUtil import (
    is_authorized,
    generate_okta_token,
    get_user_name_and_email,
)
from types import SimpleNamespace

from app.constant import Constant
from app.db.dynamodb_models import ParentModel
from app.db.dynamodb_utils import create_table

from .loggerFactory import LoggerFactory
from .redisconnection import redis
from .routes import (
    agenda_items_v2,
    key_events,
    products,
    repatha_metrics,
    repatha_metrics,
    pipeline_metrics,
    auth,
    commercial,
    notifications,
)
from app.models.repatha_metrics import (
    Commercial,
)
from app.models.pipeline import (
    Pipeline,
)
from .utils.agenda_items_utils_v2 import (
    calculate_commercial_repatha_status,
    calculate_pipline_status,
)
from .models.agenda_items_v2 import AgendaItem, AgendaItemUpdate, User

env = os.getenv("PA_ENV", "not found")

version = "1.7.15"

tags_metadata = [
    {
        "name": "Agenda Items",
        "description": "Manage agenda items",
    },
    {
        "name": "Pipeline",
        "description": "Retrieve information for Pipeline Key Events and Products",
    },
    {"name": "General", "description": "General utilities"},
]

app = FastAPI(
    title="Sensing PA APIs", version=version, openapi_tags=tags_metadata
)  # , dependencies=[Depends(is_authorized)])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(key_events.router)
app.include_router(products.router)
app.include_router(agenda_items_v2.router)
app.include_router(repatha_metrics.router)
app.include_router(pipeline_metrics.router)
app.include_router(auth.router)
app.include_router(commercial.router)
app.include_router(notifications.router)

redis_ = redis()

logger = LoggerFactory.get_logger(__name__)


@app.get("/", tags=["General"])
def hello():
    """
    Default route to test heart beat of the app
    ---
    responses:
      200:
        Amgen: Sensing Prioritized Agenda API
    """
    logger.debug(f"Logger factory is working")
    return {"Amgen": f"Sensing PA API version: {version} ENV: {env}"}


@app.get("/clear_all_cache", tags=["General"], response_model=bool)
async def clear():
    logger.debug(f"clear_all_cache: clearing cache")
    for key in redis_.scan_iter(f"{Constant.REDIS_KEY_PREFIX}*"):
        redis_.delete(key)
    logger.debug(f"clear_all_cache: cache cleared for {Constant.REDIS_KEY_PREFIX}")

    return True


@app.get("/clear_all_cache_reload", tags=["General"], response_model=bool)
async def clear_reload(background_tasks: BackgroundTasks, token=Depends(is_authorized)):
    logger.debug(f"clear_all_cache: clearing cache")
    for key in redis_.scan_iter(f"{Constant.REDIS_KEY_PREFIX}*"):
        redis_.delete(key)
    logger.debug(f"clear_all_cache: loading cache in bacground")
    background_tasks.add_task(load_data, token=token)

    return True


@app.get("/clear_all_cache_reload_auto", tags=["General"], response_model=bool)
async def clear_reload_auto(background_tasks: BackgroundTasks):
    logger.debug(f"clear_all_cache: clearing cache")
    for key in redis_.scan_iter(f"{Constant.REDIS_KEY_PREFIX}*"):
        redis_.delete(key)
    logger.debug(f"clear_all_cache: loading cache in bacground")
    data = '{"credentials": ""}'
    token = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
    token.credentials = generate_okta_token()
    # load_data(token=token)
    background_tasks.add_task(load_data, token=token)

    return True


def load_data(token):
    # latest key events
    logger.debug(f"load_data: loading commercial")
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
    response = requests.get(
        f"https://prioritized-agenda-api-{env}.nimbus.amgen.com/api/v2/agenda_items/board?is_active=true",
        headers=headers,
    )
    # for Debug
    commId = 0
    pipelineIds = []
    j = response.json()
    for g in j["groups"]:
        for i in g["items"]:
            if i["name"] == "Repatha":
                commId = i["agendaItemId"]
            elif i["archetype"] == "Pipeline":
                pipelineIds.append(i["agendaItemId"])

    user = User()
    user = get_user_name_and_email(token)

    # commercial start
    comm = Commercial()
    comm = repatha_metrics.get_commercial(commId, token)
    agendaItem = agenda_items_v2.get_agenda_item(commId)
    agendaItem.status = comm.status
    logger.debug(f"retrived {agendaItem.name} setting status to {agendaItem.status}")
    logger.debug(f"pre update for  {agendaItem.name}")
    agenda_items_v2.update_agenda_item(agendaItem, user)
    agendaItem.name
    logger.debug(f"set status for {agendaItem.name} to {agendaItem.status}")
    # commercial end

    # pipeline start
    logger.debug(f"load_data: pipeline")
    for i in pipelineIds:
        try:
            pipelineObj = Pipeline()
            pipelineObj = pipeline_metrics.get_pipeline_by_id(i, token)
            logger.debug(
                f"load_data: pipeline calculating status for {pipelineObj.title}"
            )
            status = calculate_pipline_status(pipelineObj)
            agendaItem = agenda_items_v2.get_agenda_item(i)
            agendaItem.status = status
            agenda_items_v2.update_agenda_item(agendaItem, user)
            logger.debug(f"set status for {agendaItem.name} to {agendaItem.status}")
        except:
            logger.debug(f"load_data: failed to load pipline data for agenda item {i}")
            logger.debug(traceback.print_exc())
    # pipeline end

    logger.debug(f"load_data: refresh complete")

    return True


def load_data_v2(token):
    # latest key events
    logger.debug(f"load_data: loading commercial")
    headers = {
        "Authorization": "Bearer " + token.credentials,
        "content-type": "application/json",
    }
    response = requests.get(
        f"https://prioritized-agenda-api-{env}.nimbus.amgen.com/api/v2/agenda_items/board?is_active=true",
        headers=headers,
    )
    # for Debug
    commIds = []
    pipelineIds = []
    j = response.json()
    for g in j["groups"]:
        for i in g["items"]:
            if i["archetype"] == "Commercial":
                commIds.append(i["agendaItemId"])
            elif i["archetype"] == "Pipeline":
                pipelineIds.append(i["agendaItemId"])

    user = User()
    user = get_user_name_and_email(token)

    # commercial start
    for i in commIds:
        commercial.get_commercial(i, token)
    # commercial end

    # pipeline start
    logger.debug(f"load_data: pipeline")
    for i in pipelineIds:
        try:
            pipelineObj = Pipeline()
            pipelineObj = pipeline_metrics.get_pipeline_by_id(i, token)
            logger.debug(
                f"load_data: pipeline calculating status for {pipelineObj.title}"
            )
            status = calculate_pipline_status(pipelineObj)
            agendaItem = agenda_items_v2.get_agenda_item(i)
            agendaItem.status = status
            agenda_items_v2.update_agenda_item(agendaItem, user)
            logger.debug(f"set status for {agendaItem.name} to {agendaItem.status}")
        except:
            logger.debug(f"load_data: failed to load pipline data for agenda item {i}")
            logger.debug(traceback.print_exc())
    # pipeline end

    logger.debug(f"load_data: refresh complete")

    return True


@app.on_event("startup")
async def startup_event():
    logger.debug("Starting up")
    create_table(
        ParentModel,
        delete_if_exists=False,
        read_capacity_units=10,
        write_capacity_units=10,
        populate_table=False,
    )
    logger.debug("Startup complete")
