# TC-C5 — Skenario event `QOS_STATUS_CHANGED` `DURATION_EXPIRED` & `NETWORK_TERMINATED`
Issue: https://github.com/dayat81/QualityOnDemand/issues/2 (fork; belum diposting upstream)
Status: DRAFT, belum dieksekusi. Bukti eksisting: `/workspace/fase1-closeout/callback/` (5 kasus, 37 callback, 19 sesi, 0 duplikat).

## Fakta lab
- Sink referensi TLS: `/workspace/qod-adapter-013/tools/sink.py <host> <port> <cert> <key> <out.jsonl>` (di conformance: `127.0.0.1:18443`, `https://127.0.0.1:18443/sink`, log `/tmp/qod-conf/sink.jsonl`); di lab core: `127.0.0.1:8443` dalam netns core (CALLBACKS.md).
- Event type: `org.camaraproject.quality-on-demand.v1.qos-status-changed`, content-type `application/cloudevents+json`, Authorization `Bearer <sinkCredential.accessToken>`.
- Adapter 0.1.3 `lifecycle.auto_delete_s: 360`.
- Hasil lama: c2 DURATION_EXPIRED Δ10.02 s (duration 10 s); c3 NETWORK_TERMINATED via kegagalan southbound (POST 201 lalu callback UNAVAILABLE/NETWORK_TERMINATED, template PCC 5QI 4 UE1 dihapus = fault injection, dipulihkan `provision.sh apply`); c4 NETWORK_TERMINATED via PCF terminate (sesi PDU UE1 dilepas, ±5.6 s setelah restart UE); c1/c5 DELETE_REQUESTED.
- Skrip ulang: TODO — skrip yang menghasilkan c1..c5 tidak ditemukan di folder callback (hanya hasil). Cari di `/workspace/fase1-closeout/tools/cb_test.py` (ada; belum dibaca isinya/argumennya) dan `/workspace/fase1-closeout/provision`.

## Prasyarat
- Stack n5 jalan (n5-lab, n5-gnb, n5-ue1/2, n5-adapter 0.1.3) untuk TC yang memakai core; TC-C5-01..02 bisa dengan mock backend conformance (tanpa RAN).
- Probe UDP UE1→AS:18080 (`udpgen.py`) agar AVAILABLE terkonfirmasi di N3 (seperti c1-c5).

## Kasus uji
### TC-C5-01 — DURATION_EXPIRED
- Langkah: createSession `duration: 10` dengan `sink=https://127.0.0.1:18443/sink`, `sinkCredential{credentialType:"ACCESSTOKEN", accessTokenType:"bearer", accessToken:"<tok>"}`; tunggu 15 s; baca `sink.jsonl`; `GET /sessions/{id}`.
- Expected: tepat 2 event berurutan: (1) `AVAILABLE`, statusInfo absen; (2) `UNAVAILABLE` + `statusInfo=DURATION_EXPIRED`, Δ ≈ duration (toleransi: TODO tetapkan, lab mencatat 10.02 s untuk 10 s). `getSession` setelahnya 200 dengan `UNAVAILABLE` (sampai 360 s auto delete); setelah 360 s → 404.
- Pass/fail: urutan + statusInfo benar, `$.data.sessionId` sama dengan respons create, `$.id` unik, Authorization Bearer cocok.
- Evidence: `callback/…/per-session/*.jsonl`-style log, `curl -i` getSession.

### TC-C5-02 — NETWORK_TERMINATED, kegagalan pembuatan di sisi jaringan setelah 201
- Langkah: fault injection seperti c3 (hapus template PCC 5QI profil dari UE target — lihat `c3-fault-inject.txt`), createSession QOS_L; kembalikan template dengan `provision.sh apply` (`c3-restore-provision.log`) di akhir WAJIB.
- Expected: 201 (qosStatus bisa langsung `UNAVAILABLE`) lalu 1 event `UNAVAILABLE/NETWORK_TERMINATED`.
- Negatif: tidak ada event `AVAILABLE`.
- Evidence: sink log, `c3-restore-provision.log` (drift 0).

### TC-C5-03 — NETWORK_TERMINATED, jaringan menghentikan sesi aktif (PCF terminate)
- Langkah: createSession, tunggu `AVAILABLE`, lalu lepas sesi PDU UE1 (restart `n5-ue1`, mis. `sudo docker restart n5-ue1` — ini menyentuh container lab; jalankan HANYA di jendela lab yang disetujui user) → PCF kirim Npcf notify `/terminate`.
- Expected: `AVAILABLE` → `UNAVAILABLE/NETWORK_TERMINATED` (lab: ±5.6 s setelah restart).
- Evidence: `pcf.win.log`, `smf.win.log` (jendela log), sink log.

### TC-C5-04 — Exactly-once (tidak ada duplikat)
- Langkah: jalankan TC-01..03 + DELETE_REQUESTED (deleteSession pada sesi AVAILABLE, feature `deleteSession_02_event_notification` sudah ada), lalu hitung duplikat per `(sessionId, qosStatus, statusInfo)` dari `sink.jsonl`.
- Expected: duplikat = 0 (format `duplicate-check.txt`: `callbacks N sessions M duplicates 0`).
- Pass/fail: 0 duplikat; setiap `$.id` unik.

### TC-C5-05 — Negatif: sesi UNAVAILABLE dihapus (tidak ada event terminasi tambahan)
- Langkah: setelah TC-01 (UNAVAILABLE/DURATION_EXPIRED), `DELETE /sessions/{id}`.
- Expected: 204 dan TIDAK ada event baru (konsisten dengan QoD #651 / deleteSession scenario UNAVAILABLE).

### TC-C5-06 — Negatif: tanpa `sink` tidak ada callback
- Langkah: createSession duration 10 tanpa sink; tunggu 15 s.
- Expected: tidak ada entri baru di sink; `getSession` tetap `UNAVAILABLE`.

### TC-C5-07 — Regresi: sink gagal/401 tidak mematahkan sesi
- Langkah: sink dengan token yang tidak cocok (atau sink mati). TODO: perilaku retry adapter belum terdokumentasi di sumber yang dibaca; catat.
- Expected: sesi tetap berjalan; kegagalan tercatat di log adapter (TODO nama file log).

## Gherkin kandidat (tambahan upstream; nama final menunggu jawaban maintainer)
```gherkin
  @quality_on_demand_createSession_02_3_event_duration_expired
  Scenario: Event is received when the session duration expires
    Given a valid testing device supported by the service, identified by the token or provided in the request body
    And the request body property "$.duration" is set to a valid duration for the selected QoS profile
    And the request property "$.sink" is set to a URL where events can be monitored
    And the request property "$.sinkCredential.credentialType" is set to "ACCESSTOKEN"
    And the request property "$.sinkCredential.accessToken" is set to a valid access token accepted by the events receiver
    When the request "createSession" is sent
    And the session reaches status "AVAILABLE"
    And the session duration elapses
    Then an event is received at the address of the request property "$.sink"
    And the event header "Authorization" is set to "Bearer " + the value of the request property "$.sinkCredential.accessToken"
    And the event header "Content-Type" is set to "application/cloudevents+json"
    And the event body complies with the OAS schema at "#/components/schemas/EventQosStatusChanged"
    And the event body property "$.type" is set to "org.camaraproject.quality-on-demand.v1.qos-status-changed"
    And the event body property "$.data.sessionId" has the same value as createSession response property "$.sessionId"
    And the event body property "$.data.qosStatus" is "UNAVAILABLE"
    And the event body property "$.data.statusInfo" is "DURATION_EXPIRED"

  @quality_on_demand_createSession_02_4_event_network_terminated
  Scenario: Event is received when the network terminates an AVAILABLE session
    Given an existing QoS session created by operation createSession with provided values for "sink" and "sinkCredential", and with status "AVAILABLE"
    When the network terminates the QoS session (implementation-specific trigger)
    Then an event is received at the address of the "$.sink" provided for createSession
    And the event body property "$.data.qosStatus" is "UNAVAILABLE"
    And the event body property "$.data.statusInfo" is "NETWORK_TERMINATED"
    And exactly one event is received for that sessionId and status
```
Catatan: step "the session duration elapses" / "the network terminates" butuh definisi implementasi-spesifik (pola "Testing assets" di header feature). Step baru di `steps/` harness lab: TODO.

## Blocker / TODO
- Skrip pemicu c1..c5 belum ditemukan → reuse `tools/cb_test.py` (TODO baca). TC-03 menyentuh n5-ue1 (gangguan lab): butuh jendela lab.
- Toleransi timing Δ expiry belum ditetapkan.
