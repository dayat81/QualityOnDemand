# C2 — README Test_definitions: profil tidak ada → 404 NOT_FOUND (branch docs/readme-non-existent-qos-profile)
Menguji: scenario `quality_on_demand_createSession_404.1_non_existent_qos_profile` ada dan menuntut 404/NOT_FOUND; README tidak lagi memuat usulan lama "400 INVALID_ARGUMENT is proposed"; bullet README menyebut 404 NOT_FOUND dan semua tag yang dirujuk ada di feature; README menyebut createQosAssignment "pending".
Jalankan: `cd C2 && ../.venv/bin/pytest -q` (working tree = branch C2) dan `QOD_REPO=/tmp/qodmain ../.venv/bin/pytest -q` (main polos, dibuat `git archive main`).
Hasil di box: branch C2 **4 passed** (`RESULT.txt`); main polos **3 failed, 1 passed** (`RESULT-on-main.txt`) = diharapkan (README belum diperbaiki).
