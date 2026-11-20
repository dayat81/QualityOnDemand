import pathlib
HERE = pathlib.Path(__file__).resolve().parent
UPSTREAM = HERE / "fixtures" / "upstream_954b773_qos-profiles-retrieveQosProfiles.feature"   # camaraproject/QoSProfiles main @954b773
PROPOSED = HERE / "proposed" / "qos-profiles-retrieveQosProfiles.feature"                    # proposed revision (belongs in QoSProfiles, not in this fork)
