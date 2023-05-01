"""
Auth Config Structure
{
    id: <id-string>,
    <endpoint-path>: {
        "component_names": [<component-name>]
        "sub_component_names": [(<component-name>, <sub-component-name>)]
    }
}
"""

AUTH_CONFIG = {
    # PA EDIT
    "edit": {"component_names": ["edit"]},
    "homePdf": {"component_names": ["homePdf"]},
    "gridReader": {"component_names": ["gridReader"]},
    "gridAdmin": {"component_names": ["gridAdmin"]},
    "commercial": {"component_names": ["commercial"]},
    "pipeline": {"component_names": ["pipeline"]},
    "nonProduct": {"component_names": ["nonProduct"]},
    "processSimplification": {"component_names": ["processSimplification"]},
    "export": {"component_names": ["export"]},
    "changeLog": {"component_names": ["changeLog"]},
    "ceoStaffNav": {"component_names": ["ceoStaffNav"]},
    "funcNav": {"component_names": ["funcNav"]},
}
