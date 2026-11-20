# TC-C2 — README Test_definitions: profil QoS tidak ada → 404 NOT_FOUND (singkat)
Branch: `docs/readme-non-existent-qos-profile` (commit cdf2a63, pushed ke dayat81/QualityOnDemand; PR upstream belum dibuka). Perubahan: `code/Test_definitions/README.md` baris 10 (wording saja). Patch: `/workspace/oai-camara-contrib/out/0001-docs-update-Test_definitions-README-for-non-existent.patch`.

### TC-C2-01 — Verifikasi diff dokumentasi (tanpa lab)
- Langkah: `git -C /workspace/oai-camara-contrib/QualityOnDemand show cdf2a63 --stat` dan `git diff main..docs/readme-non-existent-qos-profile`.
- Expected: hanya 1 file, 1 baris berubah; tanpa trailer `Signed-off-by`/`Co-authored-by`; author `dayat81 <11910705+dayat81@users.noreply.github.com>`.
- Pass/fail: sesuai.

### TC-C2-02 — Kebenaran klaim: nama scenario ada di feature
- Langkah: `grep -n "createSession_404.1_non_existent_qos_profile" code/Test_definitions/quality-on-demand-createSession.feature` (ada di baris ~493) dan `grep -n "638" README.md`.
- Expected: tag ada; referensi `#638` konsisten dengan wording "pending" untuk createQosAssignment (TODO: cek status #638 saat ini sebelum PR).

### TC-C2-03 — Lab: createSession profil valid-schema tapi tidak ada → 404 NOT_FOUND
- Langkah: `bash /workspace/fase1-closeout/conformance/run-behave.sh c2-03`, scenario `@quality_on_demand_createSession_404.1_non_existent_qos_profile`.
- Expected: PASS (run4 baseline PASS). Curl: createSession dengan `qosProfile` mis. `QOS_DOES_NOT_EXIST` (patuh `QosProfileName`; TODO pastikan pola regex) → 404, `code` `NOT_FOUND`.

### TC-C2-04 — Negatif: profil tidak patuh schema tetap 400 INVALID_ARGUMENT
- Expected: `qosProfile` dengan karakter terlarang (mis. spasi/`!`) → 400 `INVALID_ARGUMENT` (feature 400.x "not compliant with QosProfileName"). Membedakan dengan 404.
