"""C4: _06 (200 []) and C01.07 (422 SERVICE_NOT_APPLICABLE) use the same device precondition but expect different outcomes.
Fixture-based: a reference implementation whose behaviour depends ONLY on what the Gherkin text says about the device.
Tests marked 'gap' are EXPECTED TO FAIL on unfixed main (strict xfail)."""
import itertools, pathlib, re, pytest
from gherkin.parser import Parser
from conftest import FEATURE

HERE = pathlib.Path(__file__).parent

def scenarios(path_or_text):
    text = path_or_text.read_text() if hasattr(path_or_text, "read_text") else path_or_text
    doc = Parser().parse(text)
    out = {}
    for ch in doc["feature"]["children"]:
        sc = ch.get("scenario")
        if not sc: continue
        tag = sc["tags"][0]["name"].lstrip("@") if sc["tags"] else sc["name"]
        out[tag] = [s["text"] for s in sc["steps"]]
    return out

def outcome(steps):
    code = next(int(re.search(r"status code is (\d+)", s).group(1)) for s in steps if "status code is" in s)
    return code, ("[]" if any("body is []" in s for s in steps) else "error" if code >= 400 else "other")

def device_phrase(steps):
    """The condition on the device: the Given/And step that talks about 'service is ... applicable/offered'."""
    return next(s for s in steps if re.search(r"service is (not )?(applicable|offered)", s) and "device" in s)

def device_is_not_applicable(steps):
    return bool(re.search(r"for which the service is not (applicable|offered)", device_phrase(steps)))

S06 = "qos_profiles_retrieveQosProfiles_06_device_qos_profiles_not_found"
S07 = "qos_profiles_retrieveQosProfiles_C01.07_device_not_supported"

@pytest.fixture(scope="module")
def main_sc(): return scenarios(FEATURE)

def test_both_scenarios_exist(main_sc):
    assert S06 in main_sc and S07 in main_sc

def test_expected_outcomes_differ(main_sc):
    assert outcome(main_sc[S06]) == (200, "[]")
    assert outcome(main_sc[S07]) == (422, "error")

def test_device_precondition_is_the_same_on_main(main_sc):
    """Documents the issue: both preconditions classify the device as 'service not applicable'."""
    assert device_is_not_applicable(main_sc[S06]) and device_is_not_applicable(main_sc[S07])

def test_no_reference_implementation_satisfies_both_literally(main_sc):
    """Any server whose response is a function of the single classification 'service not applicable' returns one outcome for it."""
    states = {device_is_not_applicable(main_sc[S06]), device_is_not_applicable(main_sc[S07])}
    assert states == {True}                              # only one device state is described
    wanted = {True: {outcome(main_sc[S06]), outcome(main_sc[S07])}}
    # every possible deterministic server: state -> one outcome
    ok = [o for o in {outcome(main_sc[S06]), outcome(main_sc[S07])}
          if all(o in v for v in wanted.values()) and len(wanted[True]) == 1]
    assert ok == []                                      # none: the two expectations are disjoint

@pytest.mark.xfail(strict=True, reason="gap: on main the two device preconditions are distinguishable only by a per-device switch not in the text")
def test_gap_preconditions_are_distinguishable_on_main(main_sc):
    assert device_phrase(main_sc[S06]) != device_phrase(main_sc[S07])
    assert device_is_not_applicable(main_sc[S06]) != device_is_not_applicable(main_sc[S07])

def test_proposed_feature_resolves_conflict():
    p = scenarios(HERE / "proposed_06_C01_07.feature")
    assert outcome(p[S06]) == (200, "[]") and outcome(p[S07]) == (422, "error")
    assert device_is_not_applicable(p[S06]) is False and device_is_not_applicable(p[S07]) is True
    assert any("no QoS Profile is associated" in s for s in p[S06])

class RefServer:
    """Lab-style reference (adapter fixtures: device.service=False -> 422, device.profiles=False -> 200 [])."""
    def __init__(self, service=True, profiles=True): self.service, self.profiles = service, profiles
    def retrieve(self):
        if not self.service: return 422, "error"
        return (200, "[]") if not self.profiles else (200, "non-empty")

def test_ref_server_satisfies_proposed_with_two_flags():
    p = scenarios(HERE / "proposed_06_C01_07.feature")
    assert RefServer(service=True, profiles=False).retrieve() == outcome(p[S06])
    assert RefServer(service=False).retrieve() == outcome(p[S07])

def test_regression_normal_device_gets_profiles():
    assert RefServer().retrieve() == (200, "non-empty")

def test_negative_single_flag_server_cannot_satisfy_proposed():
    p = scenarios(HERE / "proposed_06_C01_07.feature")
    for flag in itertools.product([True, False], repeat=1):
        srv = RefServer(service=flag[0], profiles=flag[0])   # one switch only
        got = srv.retrieve()
        assert not (got == outcome(p[S06]) and got == outcome(p[S07]))
