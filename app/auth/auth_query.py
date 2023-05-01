from functools import lru_cache
from typing import Dict, Optional

from cachetools import LRUCache

from .helpers import get_query_subcomponent_parent_key


def __get_base_auth_query(user_name: str) -> str:
    return f"""
        query {{
            sensingAuthorization(username: "{user_name}", workstreams: ["prioritized_agenda"], skipWorkstreamLevelAuth: false) {{
                prioritizedAgenda
            }}
        }}
    """.replace(
        " ", ""
    ).strip()


def __group_subcomponents_by_component(subcomponents: set) -> dict:
    """
    Generate dictionary of components as keys with list of sub-components as values

    @param subcomponents: {(<component-name>, <sub-component-name>)}

    Returns dictionary with following structure: { <component-name>: [<sub-component-name>] }
    """
    grouped_subcomponents = {}
    for component, subcomponent in subcomponents:
        if component in grouped_subcomponents:
            grouped_subcomponents[component].append(subcomponent)
        else:
            grouped_subcomponents[component] = [subcomponent]
    return grouped_subcomponents


def __generate_subcomponents_query_items(subcomponents: set) -> str:
    grouped_subcomponents = __group_subcomponents_by_component(subcomponents)
    query_item = ""
    for component, associated_subcomponents in grouped_subcomponents.items():
        parent_key = get_query_subcomponent_parent_key(component)
        subcomponent_items = "\n".join(associated_subcomponents)
        query_item = f"""
            {query_item}
            {parent_key} {{
                {subcomponent_items}
            }}
        """
    return query_item.replace(" ", "").strip()


config_cache = LRUCache(1)


def __parse_auth_config(auth_config: dict) -> tuple:
    if "id" in auth_config and config_cache.get(auth_config["id"], None):
        return config_cache.get(auth_config.get("id"))

    auth_components = set()
    auth_subcomponents = set()
    for item_config in auth_config.values():
        if isinstance(item_config, Dict):
            endpoint_components = item_config.get("component_names", [])
            endpoint_subcomponents = item_config.get("sub_component_names", [])
            auth_components.update(endpoint_components)
            auth_subcomponents.update(endpoint_subcomponents)

    auth_components = frozenset(auth_components)
    auth_subcomponents = frozenset(auth_subcomponents)

    if "id" in auth_config:
        config_cache.update(
            [(auth_config.get("id"), (auth_components, auth_subcomponents))]
        )
    return (auth_components, auth_subcomponents)


@lru_cache(1)
def __generate_graphql_component_body(
    components: frozenset, subcomponents: frozenset
) -> str:
    component_query_items = "\n".join(components)
    subcomponent_query_items = __generate_subcomponents_query_items(subcomponents)
    return f"{component_query_items}\n{subcomponent_query_items}"


def generate_aggregate_graphql_query(auth_config: dict, user_name: str) -> str:
    """
    Generates the GraphQL query for all configured items

    Returns a string representing the GraphQL query
    """
    # Create set of components and sub-components to query
    (auth_components, auth_subcomponents) = __parse_auth_config(auth_config)

    # Return base GraphQL auth call if no components have been defined
    if len(auth_components) == 0:
        return __get_base_auth_query(user_name)

    # Create GraphQL query using defined components and sub-components, if specified
    component_body = __generate_graphql_component_body(
        auth_components, auth_subcomponents
    )
    return f"""\
        query {{
            sensingAuthorization(username: "{user_name}", workstreams: ["prioritized_agenda"], skipWorkstreamLevelAuth: false) {{
                prioritizedAgenda
                prioritizedAuthorization {{
                    {component_body}
                }}
            }}
        }}
    """.replace(
        " ", ""
    ).strip()


def generate_item_graphql_query(
    auth_config: dict, user_name: str, config_key: str
) -> Optional[str]:
    """
    Generates the GraphQL query for a given item that is configured

    Returns a GraphQL query string with configured components and sub-components, if key exists in the config
    """

    components = auth_config.get(config_key, {}).get("component_names", [])
    subcomponents = auth_config.get(config_key, {}).get("sub_component_names", [])

    if len(components) == 0:
        return None

    component_query_items = "\n".join(components)
    subcomponent_query_items = __generate_subcomponents_query_items(set(subcomponents))

    return f"""\
        query {{
            sensingAuthorization(username: "{user_name}", workstreams: ["prioritized_agenda"], skipWorkstreamLevelAuth: false) {{
                prioritizedAgenda
                prioritizedAuthorization {{
                    {component_query_items}
                    {subcomponent_query_items}
                }}
            }}
        }}
    """.replace(
        " ", ""
    ).strip()
