# TC-C3 — QoD createSession 400.9 `invalid_duration` (kode error)
Issue: https://github.com/dayat81/QualityOnDemand/issues/1 (fork; target upstream camaraproject/QualityOnDemand, belum diposting)
Status dokumen: DRAFT, belum dieksekusi. Semua langkah lab-only, tidak menyentuh container berjalan.

## Konteks & fakta yang dipakai
- Feature: `code/Test_definitions/quality-on-demand-createSession.feature` baris 334-343 menuntut `$.code` = `INVALID_ARGUMENT`; OAS `CreateSessionBadRequest400` juga mendefinisikan `QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE`.
- Lab: adapter 0.1.3 (`/workspace/qod-adapter-013`), config `lifecycle.duration_error_code` (default `INVALID_ARGUMENT`; konfigurasi conformance: `tests/conformance/adapter.yaml`). Profil: `config/profiles.yaml` (min 1 s, max 3600 s).
- Harness: `/workspace/fase1-closeout/conformance/run-behave.sh <tag>` (behave, feature resmi tidak diubah; sha256 dicek via `behave/features.sha256`). Step 400.9 di `behave/features/steps/qod_steps.py:119` mengisi `duration=99999`. Baseline run4: 127/127 PASS (dengan `INVALID_ARGUMENT`).
- Adapter di conformance listen `127.0.0.1:18080`, base path `/quality-on-demand/v1`.

## Prasyarat umum
- QoD adapter 0.1.3 + mock backend (harness conformance) — tidak perlu RAN/core. Port 18080 harus bebas (run-behave.sh mematikan proses `port 18080` — jangan jalankan saat adapter produksi lab memakai port itu: TODO cek port adapter `n5-adapter` agar tidak bentrok).
- Token valid: dibuat oleh harness (TODO: nama helper token di `tools/camclient.py`/`camara.py`, belum diverifikasi untuk curl manual).

## Kasus uji
### TC-C3-01 — Baseline: kode default `INVALID_ARGUMENT` lolos feature r4.3
- Tujuan: konfirmasi perilaku saat ini lolos.
- Prasyarat: adapter 0.1.3, `duration_error_code: INVALID_ARGUMENT`; feature r4.3 asli.
- Langkah: `bash /workspace/fase1-closeout/conformance/run-behave.sh c3-01`
- Expected: scenario `@quality_on_demand_createSession_400.9_invalid_duration` PASS; `features-sha256-check.txt` OK.
- Pass/fail: PASS bila scenario 400.9 passed dan sha256 OK.
- Evidence: `conformance/results/c3-01/{behave.json,plain.txt,summary.md,features-sha256-check.txt}`.

### TC-C3-02 — Reproduksi issue: kode spesifik `DURATION_OUT_OF_RANGE` gagal feature r4.3
- Tujuan: tunjukkan implementasi yang mengembalikan kode spesifik yang didokumentasikan OAS gagal di test.
- Prasyarat: salinan config (BUKAN edit file asli) dengan `lifecycle.duration_error_code: QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE`. TODO: run-behave.sh hardcode `QOD_CONFIG=$A/tests/conformance/adapter.yaml`; buat salinan skrip `run-behave-c3.sh` di folder kerja dengan QOD_CONFIG ke salinan config (jangan ubah skrip/config asli).
- Langkah: jalankan salinan skrip dengan tag `c3-02`.
- Expected: 400.9 FAIL pada step `$.code is "INVALID_ARGUMENT"` (actual `QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE`); skenario lain tetap PASS (126/127).
- Pass/fail: "issue terbukti" bila hanya 400.9 yang gagal dengan pesan itu.
- Evidence: `results/c3-02/{plain.txt,behave.json}` (potong bagian assertion error).

### TC-C3-03 — Respons mentah createSession duration di luar rentang (curl)
- Tujuan: tangkap body error nyata untuk lampiran issue.
- Langkah (adapter hidup, `$TOKEN` TODO):
```
curl -sS -i -X POST http://127.0.0.1:18080/quality-on-demand/v1/sessions \
  -H "Authorization: Bearer $TOKEN" -H "x-correlator: tc-c3-03" -H "Content-Type: application/json" \
  -d '{"device":{"ipv4Address":{"publicAddress":"10.99.0.1"}},"applicationServer":{"ipv4Address":"198.51.100.10"},"qosProfile":"QOS_E","duration":99999}'
```
  (bentuk body device: TODO verifikasi terhadap `camara.py` body default; yang pasti: qosProfile QOS_E, duration 99999.)
- Expected: HTTP 400; `status` 400; `code` sesuai config (TC-C3-01: `INVALID_ARGUMENT`; TC-C3-02: `QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE`); header `x-correlator` = `tc-c3-03`; `Content-Type: application/json`; `message` ramah.
- Evidence: `test-cases/evidence/c3-03-{default,specific}.txt`.

### TC-C3-04 — Batas bawah (negatif): duration di bawah min profil
- Langkah: sama dengan -03 tetapi `duration: 0` (min profil 1 s) lalu `-1`.
- Expected: 400 dengan kode yang sama dengan config aktif. `0`/`-1` mungkin ditolak schema (`INVALID_ARGUMENT` karena `minimum`) — catat kode apa pun; TODO tentukan apakah ini schema-level (selalu INVALID_ARGUMENT) atau profile-level.
- Pass/fail: informasional; hasil jadi masukan apakah usulan "terima salah satu" cukup.

### TC-C3-05 — Batas valid (regresi): duration = maxDuration tidak ditolak
- Langkah: `duration: 3600` dan `duration: 1` untuk QOS_E.
- Expected: 201; sesi dihapus setelahnya (`DELETE /sessions/{id}` → 204).
- Pass/fail: PASS bila 201 (menjamin perubahan kode error tidak menggeser batas).

### TC-C3-06 — Simulasi usulan opsi 2 ("salah satu dari") pada feature salinan
- Tujuan: validasi bahwa perubahan Gherkin yang kita usulkan lolos untuk kedua konfigurasi.
- Langkah: salin feature ke folder kerja (jangan ubah `behave/features` asli karena sha256-pinned), ganti baris 342 dengan
```gherkin
    And the response property "$.code" is one of ["INVALID_ARGUMENT", "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE"]
```
  TODO: step "is one of" belum ada di `steps/*.py` — tulis step baru (di salinan) atau gunakan pola yang dipakai README untuk kasus port-range/accessTokenType (cek kalimat Gherkin aslinya di feature: `grep -n "both could be accepted\|one of" `).
- Expected: scenario PASS pada config default DAN config spesifik.
- Pass/fail: PASS bila kedua konfigurasi hijau.

### TC-C3-07 — Opsi 1 (kode spesifik saja) pada salinan feature
- Langkah: salinan feature dengan `"$.code" is "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE"`.
- Expected: PASS pada config spesifik; FAIL pada config default → menunjukkan opsi 1 mematahkan implementasi lama (argumen untuk memilih opsi 2).

## Skenario Gherkin kandidat (untuk PR upstream, bergantung pilihan maintainer)
```gherkin
  @quality_on_demand_createSession_400.9_invalid_duration
  Scenario: Error response when duration is not valid for selected qos profile
    Given the request body property "duration" is set to an invalid duration for the selected qosProfile
    When the request "createSession" is sent
    Then the response status code is 400
    And the response header "x-correlator" has same value as the request header "x-correlator"
    And the response header "Content-Type" is "application/json"
    And the response property "$.status" is 400
    And the response property "$.code" is "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE"   # opsi 1
    # opsi 2: And the response property "$.code" is one of ["INVALID_ARGUMENT", "QUALITY_ON_DEMAND.DURATION_OUT_OF_RANGE"]
    And the response property "$.message" contains a user friendly text
```

## Blocker / TODO
- Token/body curl manual belum diverifikasi; paling aman jalankan lewat behave.
- Step "one of" perlu dibuat. Tidak bergantung build apa pun (adapter sudah ada), siap jalan setelah port 18080 dipastikan bebas.
