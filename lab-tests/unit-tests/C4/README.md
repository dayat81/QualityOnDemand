# C4 — QoSProfiles `_06` vs `C01.07` — QoD fork issue #3 (PR fork #6, branch test/tc-c4)
PERBAIKAN YANG SEBENARNYA ADA DI camaraproject/QoSProfiles, bukan di fork QoD ini. Karena itu PR ini hanya memuat:
- `fixtures/upstream_954b773_qos-profiles-retrieveQosProfiles.feature` — salinan feature upstream (QoSProfiles main @954b773), dipakai sebagai baseline.
- `proposed/qos-profiles-retrieveQosProfiles.feature` (+ `proposed/_06.diff`) — usulan: `_06` memakai "service is applicable" + "no QoS Profile is associated"; `C01.07` tidak diubah.
Tes menegaskan terhadap file USULAN (lulus): prekondisi `_06` dan `C01.07` dapat dibedakan dari teks; hanya `_06` yang berubah; file ter-parse; server referensi 2-flag (fixture adapter lab `service`/`profiles`) memenuhi usulan, server 1-flag tidak.
`test_baseline_*` = baseline-unfixed (informational): dokumentasi bahwa file upstream MASIH ambigu (prekondisi sama, hasil beda; tak ada server deterministik yang memenuhi keduanya secara literal).
Jalankan: `cd lab-tests/unit-tests/C4 && pytest -q -rA` (pytest, gherkin-official; tidak butuh clone QoSProfiles).
Hasil: lihat `RESULT.txt` — 12 passed.
