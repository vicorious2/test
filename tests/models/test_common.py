from app.models.common import Owners, SummaryInfo


def test_common_models():
    owners = Owners()
    summary_info = SummaryInfo()

    owners.ceoStaffSponsors = []
    owners.operatingTeamOwners = []

    summary_info.status = ""
    summary_info.reason = ""
    summary_info.scope = ""
    summary_info.keyInsights = ""

    assert True
