import os
from fastapi import APIRouter, Depends, HTTPException
import requests
from ..loggerFactory import LoggerFactory


logger = LoggerFactory.get_logger(__name__)


class HttpRequest:
    def http_post(url, data, token):
        headers = {
            "Authorization": "Bearer " + token.credentials,
            "content-type": "application/json",
        }
        response = requests.post(
            url,
            headers=headers,
            json=data,
        )
        if response.status_code != 200:
            logger.debug(f"{url} returned: {response.status_code}")
            return None
        return response.json()

    def http_get(url, token):
        headers = {
            "Authorization": "Bearer " + token.credentials,
            "content-type": "application/json",
        }
        response = requests.get(
            url,
            headers=headers,
        )
        if response.status_code != 200:
            logger.debug(f"{url} returned: {response.status_code}")
            return None

        return response.json()
