"""C5: OAS defines DURATION_EXPIRED / NETWORK_TERMINATED statusInfo but main had no feature scenario checking them.
This branch adds scenarios 02_4 / 02_5 to the real createSession feature; tests assert the fixed branch.
test_baseline_* are informational checks of the unfixed main (git origin/main)."""
import pathlib, re, pytest, jsonschema, glob
from gherkin.parser import Parser
from conftest import TD, unfixed_text

HERE = pathlib.Path(__file__).parent
ALL = "\n".join(p.read_text() for p in sorted(TD.glob("*.feature")))

def test_oas_statusinfo_enum(oas):
    assert oas["components"]["schemas"]["StatusInfo"]["enum"] == ["DURATION_EXPIRED", "NETWORK_TERMINATED", "DELETE_REQUESTED"]

def test_event_schema_requires_sessionid_and_qosstatus(oas):
    d = oas["components"]["schemas"]["EventQosStatusChanged"]["allOf"][1]["properties"]["data"]
    assert set(d["required"]) == {"sessionId", "qosStatus"} and "statusInfo" in d["properties"]

def test_examples_exist_for_both_events(oas):
    txt = str(oas)
    assert "DURATION_EXPIRED" in txt and "NETWORK_TERMINATED" in txt

CF = "code/Test_definitions/quality-on-demand-createSession.feature"
TAG4 = "quality_on_demand_createSession_02_4_event_duration_expired"
TAG5 = "quality_on_demand_createSession_02_5_event_network_terminated"

def test_baseline_unfixed_main_covers_only_delete_requested():
    """baseline-unfixed (informational): on main only DELETE_REQUESTED had an event scenario."""
    txt = "\n".join(unfixed_text("code/Test_definitions/" + p.name) for p in sorted(TD.glob("*.feature")))
    covered = {s for s in ("DURATION_EXPIRED", "NETWORK_TERMINATED", "DELETE_REQUESTED") if f'"$.data.statusInfo" is "{s}"' in txt}
    assert covered == {"DELETE_REQUESTED"}

def test_fixed_all_statusinfo_values_covered_by_features():
    covered = {s for s in ("DURATION_EXPIRED", "NETWORK_TERMINATED", "DELETE_REQUESTED") if f'"$.data.statusInfo" is "{s}"' in ALL}
    assert covered == {"DURATION_EXPIRED", "NETWORK_TERMINATED", "DELETE_REQUESTED"}

def test_fixed_duration_expired_scenario_in_real_feature(create_feature):
    from conftest import scenario_block
    blk = scenario_block(create_feature, TAG4)
    assert '"$.data.qosStatus" is "UNAVAILABLE"' in blk and '"$.data.statusInfo" is "DURATION_EXPIRED"' in blk

def test_fixed_network_terminated_scenario_in_real_feature(create_feature):
    from conftest import scenario_block
    blk = scenario_block(create_feature, TAG5)
    assert '"$.data.statusInfo" is "NETWORK_TERMINATED"' in blk and "EventQosStatusChanged" in blk

def test_fixed_real_feature_parses_and_tags_unique(create_feature):
    Parser().parse(create_feature)
    tags = re.findall(r"^\s*@(\S+)", create_feature, re.M)
    assert len(tags) == len(set(tags)), "duplicate tags"
    assert TAG4 in tags and TAG5 in tags

def test_fixed_new_scenarios_do_not_touch_existing_ones(create_feature):
    base = unfixed_text(CF)
    for t in re.findall(r"^\s*@(\S+)", base, re.M):
        assert f"@{t}" in create_feature, t
    assert create_feature.count("Scenario") == base.count("Scenario") + 2

def test_proposed_feature_parses_and_covers_gap():
    t = (HERE / "proposed_events.feature").read_text()
    Parser().parse(t)
    assert '"$.data.statusInfo" is "DURATION_EXPIRED"' in t and '"$.data.statusInfo" is "NETWORK_TERMINATED"' in t

def test_proposed_tags_do_not_collide_with_baseline_main():
    new = re.findall(r"@(\S+)", (HERE / "proposed_events.feature").read_text())
    old = set(re.findall(r"@(\S+)", unfixed_text(CF)))
    assert new and not (set(new) & old), set(new) & old

def test_proposed_tags_follow_naming_pattern():
    for t in re.findall(r"@(\S+)", (HERE / "proposed_events.feature").read_text()):
        assert re.fullmatch(r"quality_on_demand_createSession_\d{2}_\d_[a-z_]+", t), t

# Sample CloudEvents (shape as produced by the lab adapter, see /workspace/fase1-closeout/callback) validated vs the OAS schema
def _event(status_info):
    return {"id": "9e4d3509-df85-480e-a0d2-fd45b28cbe27", "source": "https://adapter.example/quality-on-demand/v1",
            "type": "org.camaraproject.quality-on-demand.v1.qos-status-changed", "specversion": "1.0",
            "time": "2026-11-20T03:24:05Z", "datacontenttype": "application/json",
            "data": {"sessionId": "47f0191c-4b9a-4b0f-8e71-7c9f1714c6ee", "qosStatus": "UNAVAILABLE", "statusInfo": status_info}}

@pytest.mark.parametrize("si", ["DURATION_EXPIRED", "NETWORK_TERMINATED", "DELETE_REQUESTED"])
def test_sample_event_validates_against_data_schema(oas, si):
    data_schema = oas["components"]["schemas"]["EventQosStatusChanged"]["allOf"][1]["properties"]["data"]
    schemas = oas["components"]["schemas"]
    def resolve(n):
        if isinstance(n, dict):
            if "$ref" in n and n["$ref"].startswith("#/components/schemas/"):
                return resolve(schemas[n["$ref"].split("/")[-1]])
            return {k: resolve(v) for k, v in n.items()}
        if isinstance(n, list): return [resolve(i) for i in n]
        return n
    jsonschema.validate(_event(si)["data"], resolve(data_schema))

def test_negative_unknown_statusinfo_rejected(oas):
    schemas = oas["components"]["schemas"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate("SOMETHING_ELSE", {"type": "string", "enum": schemas["StatusInfo"]["enum"]})
