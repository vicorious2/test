from typing import Optional

from cachetools import TTLCache
from cachetools.func import ttl_cache

from .auth_query import (
    generate_aggregate_graphql_query,
    generate_item_graphql_query,
)

from ..AuthUtil import AuthUtil, get_user_name, get_authz_details
from .helpers import get_query_subcomponent_parent_key


TTL_SECONDS = 120


def are_all_values_true(permissions: dict):
    for value in permissions.values():
        if isinstance(value, dict):
            if not are_all_values_true(value):
                return False
        elif isinstance(value, bool):
            if not value:
                return False
    return True


auth_util = AuthUtil()


class AuthManager:
    def __init__(self, auth_config):
        self.config = auth_config
        """
        All permissions cache stores
        
        {
            <access-token>: {
                "prioritizedAgenda": <boolean>,
                "prioritizedAuthorization": {
                    <component-name>: <boolean>
                    <sub-component-parent-key>: {
                        <sub-component-name>: <boolean>
                    }
                }
            }
        }
        """
        self.__all_permissions_cache = TTLCache(maxsize=128, ttl=TTL_SECONDS)

    def get_all_permissions(self, access_token: str) -> dict:
        if self.__all_permissions_cache.get(access_token, None):
            return self.__all_permissions_cache.get(access_token)
        user_name = get_user_name(access_token)
        # make GraphQL auth call to fetch all permissions
        query_payload = generate_aggregate_graphql_query(self.config, user_name)
        api_payload = {"query": query_payload}

        res = get_authz_details(access_token, api_payload)
        auth_details = res.get("data", {}).get("sensingAuthorization", {})
        print(auth_details)
        # cache response
        if auth_details:
            self.__all_permissions_cache.update([(access_token, auth_details)])
        return auth_details

    @ttl_cache(ttl=TTL_SECONDS)
    def __fetch_endpoint_permissions(
        self, access_token: str, endpoint_path: str
    ) -> dict:
        user_name = get_user_name(access_token)
        # make GraphQL auth call to fetch all permissions
        query_payload = generate_item_graphql_query(
            self.config, user_name, endpoint_path
        )
        if query_payload == None:
            return {}
        api_payload = {"query": query_payload}
        res = get_authz_details(access_token, api_payload)
        auth_details = res.get("data", {}).get("sensingAuthorization", {})
        return auth_details

    def get_endpoint_permissions(
        self, access_token: str, endpoint_path: str
    ) -> Optional[dict]:
        # If endpoint is not configured, there are no permissions
        if endpoint_path not in self.config:
            return None

        # Check permissions from aggregate cache if they exist
        if self.__all_permissions_cache.get(access_token, None):
            # fetch config details
            config = self.config.get(endpoint_path)
            permissions = self.__all_permissions_cache.get(access_token, {})
            components = config.get("component_names", [])
            subcomponents = config.get("sub_component_names", [])
            # If components are not configured, we default to no authorization
            if len(components) == 0:
                return None

            endpoint_permissions = {}
            # Add overall supply value
            endpoint_permissions["prioritizedAgenda"] = permissions.get(
                "prioritizedAgenda", False
            )

            # Add specific components
            for component in components:
                workstream_container = endpoint_permissions.get(
                    "prioritizedAuthorization", {}
                )
                component_authorized = permissions.get(
                    "prioritizedAuthorization", {}
                ).get(component, False)
                component_permission = {component: component_authorized}
                workstream_container.update(component_permission)
                endpoint_permissions.update(
                    {"prioritizedAuthorization": workstream_container}
                )

            # Get sub-components specific sub-components
            components_with_sub_components = set([t[0] for t in subcomponents])
            for component in components_with_sub_components:
                parent_key = get_query_subcomponent_parent_key(component)
                workstream_container = endpoint_permissions.get(
                    "prioritizedAuthorization", {}
                )
                subcomponent_permissions = permissions.get(
                    "prioritizedAuthorization", {}
                ).get(parent_key, {})
                workstream_container.update({parent_key: subcomponent_permissions})
                endpoint_permissions.update(
                    {"prioritizedAuthorization": workstream_container}
                )

            return endpoint_permissions

        # Aggregate cache does not have permissions, so we will fetch permissions for the specific endpoint
        endpoint_permissions = self.__fetch_endpoint_permissions(
            access_token, endpoint_path
        )
        return endpoint_permissions

    def is_completely_authorized(self, access_token: str, endpoint_path: str):
        # If endpoint is not configured, we default to no authorization
        if endpoint_path not in self.config:
            return False

        endpoint_permissions = self.get_endpoint_permissions(
            access_token, endpoint_path
        )

        return are_all_values_true(endpoint_permissions)
