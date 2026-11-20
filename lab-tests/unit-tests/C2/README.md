# C2 — README Test_definitions: profil tidak ada → 404 NOT_FOUND (PR fork #7, branch test/tc-c2)
Branch ini MENERAPKAN perubahan README dari commit cdf2a63 (branch docs/readme-non-existent-qos-profile) ke `code/Test_definitions/README.md`.
Menguji: scenario `quality_on_demand_createSession_404.1_non_existent_qos_profile` ada dan menuntut 404/NOT_FOUND; README tidak memuat usulan lama "400 INVALID_ARGUMENT is proposed"; bullet README menyebut 404 NOT_FOUND dan tag yang dirujuk ada di feature; README menyebut createQosAssignment "pending".
`test_baseline_unfixed_main_readme_is_stale` = baseline-unfixed (informational): README main (`git show origin/main:...`) masih usang.
Jalankan: `git fetch --depth 1 origin main` lalu `cd lab-tests/unit-tests/C2 && pytest -q -rA` (butuh pytest, pyyaml).
Hasil: lihat `RESULT.txt` — 5 passed (0 fail, 0 xfail). Baseline di main polos diharapkan gagal di 3 tes README (tidak dijalankan lagi di sini).
