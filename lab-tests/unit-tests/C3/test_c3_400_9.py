"""C3: createSession 400.9 invalid_duration expects INVALID_ARGUMENT, while the OAS also documents
QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE. Tests marked 'gap' are EXPECTED TO FAIL on unfixed main."""
import pathlib, pytest
from gherkin.parser import Parser
from conftest import scenario_block

TAG = "quality_on_demand_createSession_400.9_invalid_duration"
HERE = pathlib.Path(__file__).parent

def codes400(oas):
    sch = oas["components"]["responses"]["CreateSessionBadRequest400"]["content"]["application/json"]["schema"]["allOf"][1]
    return sch["properties"]["code"]["enum"]

def test_oas_lists_specific_duration_code(oas):
    assert "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE" in codes400(oas)

def test_oas_still_allows_invalid_argument(oas):
    assert "INVALID_ARGUMENT" in codes400(oas)

def test_oas_has_duration_out_of_range_example(oas):
    ex = oas["components"]["responses"]["CreateSessionBadRequest400"]["content"]["application/json"]["examples"]
    assert ex["DurationOutOfRangeForQoSProfile"]["value"]["code"] == "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE"

def test_feature_400_9_pins_single_code(create_feature):
    """Documents the issue: the scenario pins exactly INVALID_ARGUMENT."""
    blk = scenario_block(create_feature, TAG)
    assert '"$.code" is "INVALID_ARGUMENT"' in blk

@pytest.mark.xfail(strict=True, reason="gap: feature does not accept the specific code documented in the OAS (fixed by the proposal)")
def test_gap_feature_accepts_specific_code(create_feature):
    blk = scenario_block(create_feature, TAG)
    assert "DURATION_OUT_OF_RANGE" in blk

def test_proposed_scenario_parses_and_accepts_both():
    text = (HERE / "proposed_400_9.feature").read_text()
    Parser().parse(text)  # Gherkin syntax
    blk = scenario_block(text, TAG)
    assert "INVALID_ARGUMENT" in blk and "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE" in blk

def test_proposed_codes_are_subset_of_oas(oas):
    for c in ("INVALID_ARGUMENT", "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE"):
        assert c in codes400(oas)

def test_patched_copy_of_real_feature_parses(create_feature):
    """Apply the proposed one-line change to a copy of the real feature and lint it with the Gherkin parser."""
    old = '    And the response property "$.code" is "INVALID_ARGUMENT"\n'
    new = '    And the response property "$.code" is one of "INVALID_ARGUMENT" or "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE"\n'
    head, _, rest = create_feature.partition("@" + TAG)
    assert old in rest
    patched = head + "@" + TAG + rest.replace(old, new, 1)
    Parser().parse(patched)
    assert patched != create_feature
