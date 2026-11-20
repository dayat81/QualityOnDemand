# TC-C4 — QoSProfiles `_06_device_qos_profiles_not_found` vs `C01.07_device_not_supported`
Issue: https://github.com/dayat81/QualityOnDemand/issues/3 (fork; target upstream camaraproject/QoSProfiles, belum diposting)
Status: DRAFT, belum dieksekusi. Tidak butuh RAN/core — hanya adapter + behave.

## Fakta lab
- Fixture `/workspace/qod-adapter-013/tests/conformance/devices.yaml`: IMSI 001019999900009 (ipv4 10.99.0.9) `service:false`; 001019999900010 (10.99.0.10) `profiles:false`.
- Harness `behave/features/steps/qod_steps.py` baris 83-86: C01.07 → `dev(9)` (service:false → 422); `_06` (retrieveQosProfiles) → `dev(10)` (profiles:false → 200 `[]`). Artinya step yang sama kalimatnya ("a device for which the service is not applicable") dipetakan ke dua fixture berbeda: ini bukti ambiguitas yang dilaporkan.
- Endpoint: `POST /qos-profiles/v1/retrieve-qos-profiles` (adapter conformance `127.0.0.1:18080`). Baseline run4: retrieveQosProfiles 21/21 PASS.

## Kasus uji
### TC-C4-01 — Baseline: kedua skenario lolos dengan 2 fixture berbeda
- Langkah: `bash /workspace/fase1-closeout/conformance/run-behave.sh c4-01`
- Expected: `_06` PASS (200 `[]`), `C01.07` PASS (422 SERVICE_NOT_APPLICABLE).
- Evidence: `conformance/results/c4-01/behave.json` (filter tag).

### TC-C4-02 — Bukti ambiguitas: device yang sama tidak bisa memenuhi keduanya
- Langkah (curl, `$TOKEN` TODO, bentuk body device TODO verifikasi):
```
for IP in 10.99.0.9 10.99.0.10; do
 curl -sS -i -X POST http://127.0.0.1:18080/qos-profiles/v1/retrieve-qos-profiles \
  -H "Authorization: Bearer $TOKEN" -H "x-correlator: tc-c4-02" -H "Content-Type: application/json" \
  -d "{\"device\":{\"ipv4Address\":{\"publicAddress\":\"$IP\"}}}"; done
```
- Expected: .9 → 422 `SERVICE_NOT_APPLICABLE`; .10 → 200 `[]`. Tidak ada satu device yang menghasilkan keduanya → implementasi butuh flag per-device (`service` vs `profiles`).
- Pass/fail: "issue terbukti" bila hasil di atas dan tidak ada fixture tunggal yang memenuhi kedua skenario sebagai ditulis.

### TC-C4-03 — Negatif: ubah fixture jadi satu device untuk kedua skenario
- Langkah: salinan harness (di folder kerja) dengan step `_06` juga memakai `dev(9)`.
- Expected: `_06` FAIL (dapat 422, bukan 200 `[]`). Menunjukkan pembacaan literal teks `_06` bentrok dengan C01.07.

### TC-C4-04 — Regresi: device normal tetap mendapat profil
- Langkah: retrieve untuk 10.99.0.1.
- Expected: 200, array tak kosong, tiap item patuh schema `QosProfile`, tidak ada profil restricted (`no restricted QoS Profile is included`). Profil: lihat `config/profiles.yaml`.

### TC-C4-05 — Kasus usulan: device eligible tanpa profil → 200 `[]` (precondition dibahasakan ulang)
- Gherkin kandidat:
```gherkin
  @qos_profiles_retrieveQosProfiles_06_device_qos_profiles_not_found
  Scenario: Eligible device has no QoS profiles associated
    Given a valid device for which the service is applicable, provided in the request body or identified by the access token
    And no QoS Profile is associated to that device
    When the request "retrieveQosProfiles" is sent
    Then the response status code is 200
    And the response body is []
```
- Langkah: jalankan pada salinan feature + fixture 10; Expected PASS. C01.07 tetap dengan fixture 9 → PASS. Kedua lolos tanpa kontradiksi.

### TC-C4-06 — Negatif input: tanpa device & tanpa token 2-legged
- Langkah: body `{}` dengan token 2-legged. Expected: 422 `MISSING_IDENTIFIER` (TODO verifikasi kode di feature `retrieveQosProfiles`; sudah ada di suite 21/21).

## Blocker / TODO
- Token & bentuk body: verifikasi lewat `behave/features/steps/camara.py`. Run-behave.sh memakai port 18080 (bentrok bila adapter lain di port itu).
- Draft evidence adapter D6 (`qod-adapter-012/RESULT.md`) bersifat privat: kutip temuan saja.
