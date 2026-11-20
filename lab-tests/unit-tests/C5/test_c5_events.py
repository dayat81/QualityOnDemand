"""C5: OAS defines DURATION_EXPIRED / NETWORK_TERMINATED statusInfo but no feature scenario checks them.
Tests marked 'gap' are EXPECTED TO FAIL on unfixed main (strict xfail)."""
import pathlib, re, pytest, jsonschema, glob
from gherkin.parser import Parser
from conftest import TD

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

def test_current_features_cover_only_delete_requested():
    covered = {s for s in ("DURATION_EXPIRED", "NETWORK_TERMINATED", "DELETE_REQUESTED") if f'"$.data.statusInfo" is "{s}"' in ALL}
    assert covered == {"DELETE_REQUESTED"}, f"documents current state: {covered}"

@pytest.mark.xfail(strict=True, reason="gap: no scenario for DURATION_EXPIRED on main")
def test_gap_duration_expired_scenario_exists():
    assert '"$.data.statusInfo" is "DURATION_EXPIRED"' in ALL

@pytest.mark.xfail(strict=True, reason="gap: no scenario for NETWORK_TERMINATED on main")
def test_gap_network_terminated_scenario_exists():
    assert '"$.data.statusInfo" is "NETWORK_TERMINATED"' in ALL

def test_proposed_feature_parses_and_covers_gap():
    t = (HERE / "proposed_events.feature").read_text()
    Parser().parse(t)
    assert '"$.data.statusInfo" is "DURATION_EXPIRED"' in t and '"$.data.statusInfo" is "NETWORK_TERMINATED"' in t

def test_proposed_tags_do_not_collide_with_existing():
    new = re.findall(r"@(\S+)", (HERE / "proposed_events.feature").read_text())
    old = set(re.findall(r"@(\S+)", ALL))
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
