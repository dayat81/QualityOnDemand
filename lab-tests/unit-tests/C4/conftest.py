import os, pathlib
ROOT = pathlib.Path(os.environ.get("QOSP_REPO", pathlib.Path(__file__).resolve().parents[2] / "QoSProfiles"))
# NOTE: the QoSProfiles feature file is NOT part of the QualityOnDemand fork; set QOSP_REPO to a clone of camaraproject/QoSProfiles.
FEATURE = ROOT / "code/Test_definitions/qos-profiles-retrieveQosProfiles.feature"
