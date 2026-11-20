# C3 — createSession 400.9 (kode error) — QoD fork issue #1 (PR fork #4, branch test/tc-c3)
Branch ini MENGUBAH `code/Test_definitions/quality-on-demand-createSession.feature` (scenario 400.9): `"$.code" is "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE" or "INVALID_ARGUMENT"` (gaya sama seperti 400.5/400.7 di file yang sama) + komentar satu baris.
Menguji (sekarang normal assert, tanpa xfail): OAS memuat kedua kode + contoh; feature hasil perbaikan menerima keduanya dan kodenya ada di OAS; feature ter-parse (gherkin) dengan tag unik; baseline+1 baris == scenario hasil perbaikan. `test_baseline_*` = baseline-unfixed (informational) memakai `git show origin/main:...`.
Jalankan: `git fetch --depth 1 origin main` lalu `cd lab-tests/unit-tests/C3 && pytest -q -rA` (pytest, pyyaml, gherkin-official).
Hasil: lihat `RESULT.txt` — 10 passed. Spectral/gherkin-lint upstream tidak dijalankan (TODO).
Catatan: ini perubahan di FORK; belum ada PR upstream; preferensi maintainer (opsi 1 atau 2) belum diketahui.
