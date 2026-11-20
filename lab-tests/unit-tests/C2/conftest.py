import os, pathlib, pytest, yaml
def _find_root():
    if os.environ.get("QOD_REPO"): return pathlib.Path(os.environ["QOD_REPO"])
    here = pathlib.Path(__file__).resolve()
    for p in here.parents:                      # inside the repo (lab-tests/unit-tests/<id>) or the local layout
        if (p / "code/Test_definitions").is_dir(): return p
    return here.parents[2] / "QualityOnDemand"
ROOT = _find_root()
TD = ROOT / "code" / "Test_definitions"

@pytest.fixture(scope="session")
def oas():
    return yaml.safe_load((ROOT / "code/API_definitions/quality-on-demand.yaml").read_text())

@pytest.fixture(scope="session")
def create_feature():
    return (TD / "quality-on-demand-createSession.feature").read_text()

def scenario_block(text, tag):
    """Return the lines of the scenario that starts at '@tag' up to the next tag line."""
    lines, out, on = text.splitlines(), [], False
    for l in lines:
        s = l.strip()
        if s == "@" + tag: on = True; continue
        if on and s.startswith("@"): break
        if on: out.append(l)
    assert on, f"scenario tag @{tag} not found"
    return "\n".join(out)


def unfixed_text(relpath, rev="origin/main"):
    """Content of a repo file at the unfixed baseline revision (the fork's main = upstream main 8570290); skips if unavailable."""
    import subprocess
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), "show", f"{rev}:{relpath}"], text=True, stderr=subprocess.DEVNULL)
    except Exception:
        pytest.skip(f"baseline {rev} not available in this checkout (run: git fetch --depth 1 origin main)")
