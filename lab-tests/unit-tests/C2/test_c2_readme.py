"""C2 (fixed branch: README changed as in commit cdf2a63): README statement about non-existent QoS profile must match the feature file (tag exists, 404/NOT_FOUND).
Run against the branch docs/readme-non-existent-qos-profile (on plain main, the README tests are EXPECTED TO FAIL)."""
import re, pytest
from conftest import TD, scenario_block, unfixed_text

TAG = "quality_on_demand_createSession_404.1_non_existent_qos_profile"
README = (TD / "README.md").read_text()

def test_feature_scenario_exists_and_is_404_not_found(create_feature):
    blk = scenario_block(create_feature, TAG)
    assert "status code is 404" in blk and '"$.code" is "NOT_FOUND"' in blk

def test_readme_has_no_stale_400_proposal():
    assert "400 INVALID_ARGUMENT is proposed" not in README

def test_readme_states_404_and_references_existing_tag(create_feature):
    m = re.search(r"\*[^\n]*QosProfileName[^\n]*", README)
    assert m, "README bullet about QosProfileName/non-existent profile not found (unfixed main?)"
    line = m.group(0)
    assert "404" in line and "NOT_FOUND" in line
    tags = re.findall(r"`(quality_on_demand_createSession_[^`]+)`", line)
    assert tags, "no scenario tag referenced"
    for t in tags: assert f"@{t}" in create_feature, f"{t} not in feature"

def test_readme_mentions_createQosAssignment_pending():
    assert "createQosAssignment" in README and "pending" in README


def test_baseline_unfixed_main_readme_is_stale():
    """baseline-unfixed (informational): upstream main README still has the old 'proposed 400' bullet."""
    assert "400 INVALID_ARGUMENT is proposed" in unfixed_text("code/Test_definitions/README.md")
