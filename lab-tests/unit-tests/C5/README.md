# C5 — scenario event DURATION_EXPIRED / NETWORK_TERMINATED — QoD fork issue #2
Menguji: enum `StatusInfo`, schema `EventQosStatusChanged`, contoh OAS; fitur main hanya mencakup `DELETE_REQUESTED` (2 xfail strict = gap); `proposed_events.feature` valid Gherkin, tag tidak bentrok dan sesuai pola penamaan (`02_4`, `02_5` karena `02_3` sudah ada); contoh CloudEvent (bentuk dari lab adapter) lolos validasi schema data; negatif: statusInfo tak dikenal ditolak.
Jalankan: `cd C5 && ../.venv/bin/pytest -q -rx`.
Hasil di box: **11 passed, 2 xfailed**. Step "the session duration elapses" / "the network terminates..." belum didefinisikan di tooling manapun (TODO, implementasi-spesifik). Pengiriman event nyata diuji di lab (TC-C5), bukan di sini.
