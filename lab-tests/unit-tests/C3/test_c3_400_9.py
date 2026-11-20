"""C3: createSession 400.9 invalid_duration expected only INVALID_ARGUMENT, while the OAS also documents
QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE. This branch changes the real feature to accept both; tests assert the fixed branch.
test_baseline_* are informational checks of the unfixed main (git origin/main)."""
import pathlib, pytest
from gherkin.parser import Parser
from conftest import scenario_block, unfixed_text

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

def test_baseline_unfixed_main_pins_single_code():
    """baseline-unfixed (informational): upstream main pins exactly INVALID_ARGUMENT."""
    blk = scenario_block(unfixed_text("code/Test_definitions/quality-on-demand-createSession.feature"), TAG)
    assert '"$.code" is "INVALID_ARGUMENT"' in blk and "DURATION_OUT_OF_RANGE" not in blk

def test_fixed_feature_accepts_specific_and_generic_code(create_feature):
    blk = scenario_block(create_feature, TAG)
    assert '"$.code" is "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE" or "INVALID_ARGUMENT"' in blk

def test_fixed_feature_parses_and_tag_unique(create_feature):
    Parser().parse(create_feature)
    assert create_feature.count("@" + TAG) == 1

def test_fixed_feature_codes_are_in_oas(create_feature, oas):
    import re
    blk = scenario_block(create_feature, TAG)
    codes = re.search(r'"\$\.code" is (.*)', blk).group(1)
    for c in re.findall(r'"([A-Z_.]+)"', codes):
        assert c in codes400(oas), c

def test_proposed_scenario_parses_and_accepts_both():
    text = (HERE / "proposed_400_9.feature").read_text()
    Parser().parse(text)  # Gherkin syntax
    blk = scenario_block(text, TAG)
    assert "INVALID_ARGUMENT" in blk and "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE" in blk

def test_proposed_codes_are_subset_of_oas(oas):
    for c in ("INVALID_ARGUMENT", "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE"):
        assert c in codes400(oas)

def test_baseline_plus_one_line_equals_fixed_scenario(create_feature):
    """Apply the proposed one-line change to a copy of the real feature and lint it with the Gherkin parser."""
    base = unfixed_text("code/Test_definitions/quality-on-demand-createSession.feature")
    old = '    And the response property "$.code" is "INVALID_ARGUMENT"\n'
    new = '    And the response property "$.code" is "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE" or "INVALID_ARGUMENT"\n'
    head, _, rest = base.partition("@" + TAG)
    patched = head + "@" + TAG + rest.replace(old, new, 1)
    Parser().parse(patched)
    assert scenario_block(patched, TAG) == scenario_block(create_feature, TAG).replace('    # The OAS lists both codes: the specific one is preferred, the generic one is also accepted\n', '')
