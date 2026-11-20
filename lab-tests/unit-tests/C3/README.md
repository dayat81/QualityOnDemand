# C3 — createSession 400.9 (kode error) — QoD fork issue #1
Menguji: OAS `CreateSessionBadRequest400` memuat `INVALID_ARGUMENT` dan `QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE` (+ contoh); feature 400.9 hanya menerima `INVALID_ARGUMENT` (gap, xfail strict); usulan `proposed_400_9.feature` (terima salah satu) valid secara Gherkin dan salinan feature asli yang dipatch satu baris tetap ter-parse.
Jalankan: `cd C3 && ../.venv/bin/pytest -q -rx` (repo QoD: env `QOD_REPO`, default `../../QualityOnDemand`; file feature/OAS di working tree sama dengan main).
Hasil di box: **7 passed, 1 xfailed** (`RESULT.txt`); main polos (`/tmp/qodmain`): sama.
Catatan: step "is one of" bukan step baku CAMARA; proposal masih menunggu preferensi maintainer. Spectral/gherkin-lint upstream tidak dijalankan (tidak terpasang; TODO `npx @stoplight/spectral-cli`, `gherkin-lint` bila diperlukan).
