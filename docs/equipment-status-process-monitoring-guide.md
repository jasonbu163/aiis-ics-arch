# Device Status, Process Monitoring, and Energy User Guide

[中文](equipment-status-process-monitoring-guide.zh-CN.md) · [Project documentation](README.md) · [r10 operations and background](equipment-status-process-monitoring.md#r10-guide) · [Machine contract v2](../contracts/published/http-api/equipment-observation-v2/README.md)

Energy statistics are served at `/monitor/consumption` with the sole page grant `monitor.energy`. The old `/monitor/energy` URL is retired. A deployment still using `monitor.consumption` requires explicit owner review and grant migration. The page grant adds no API permission, meter scope or management access. Set the private profile’s schema revision to `e9f3b5d7c021` on the adopted target. The checked-in example retains its published revision. [Retirement specification](../plans/ARCH-OBS-002-legacy-observation-retirement/spec.md)

## Registered write sources

Use this flow for a sender that supplies only a registered source key. The private observation profile and enabled, verified MySQL target still apply. This candidate requires revision `e9f3b5d7c021`. Legacy v2 examples below still use the machine credential and device profile. Any migration or service switch on a real environment needs separate approval.

1. Follow sections 2–3 to configure areas, metrics, slots for each target, and the card or curve for that target.
2. Sign in as admin. Under **Device Status → Configuration → Write source registration**, add `sma-demo-1` with an optional name, and enable it. The table can be filtered by key or name. Drag ordinary column boundaries to resize them. **Reset widths** restores this table's defaults.
3. Send a JSON sample to `POST /api/v1/integration/observations` with the actual offset-bearing `observedAt`. Use the same key for both targets. One request writes one target. The request and response examples are available in the contract vectors.
4. Select the source in the equipment or process page. Latest replaces the full snapshot for each task, so include all areas that should remain visible. History appends samples and leaves gaps for metrics absent from each sample. Query one saved item set using `GET /api/v1/integration/observations/latest`.
5. Disabling stops writes while retaining reads. Deleting hides the source from normal selection and the public API. Admin data management still shows retained rows under a label with the deleted status.

[Registered-source contract and examples](../contracts/published/http-api/observation-write-sources-v1/README.md)

## 1. Prepare the environment and access

Use an authorized test environment with the frontend and backend ready and the matching database migration already applied. Ask the environment owner to prepare a dedicated synthetic device (here, `obs-demo-device`) and, for the energy exercise, a dedicated meter `obs-demo-meter`. The latest endpoint replaces the entire snapshot for a device and task, so use test-only equipment and tasks. Check that the example keys are available in your environment because areas, metrics, cards, and curves are global configuration.

Have the environment owner merge the test entries into the private profile outside the repository, keeping existing entries. Check that `target.serverUuid`, `schema`, and `schemaRevision` match the actual backend database target. Use the real target identifiers and a dedicated credential. The UUID and digest in the example are placeholders. [v2 private profile example](../contracts/published/http-api/equipment-observation-v2/example-profile.json)

- In `devices`, register the `equipmentId`, bilingual names, `staleAfterSeconds`, and `futureToleranceSeconds`. In `readScopes`, add that equipment ID to the applicable human roles, including the `admin` who will manage records. Sign in with a user account. The card, curve, and energy pages require `equipment-observation-read`, `monitor-observation-read`, and `energy-consumption-read`, respectively. Configuration and data management require an admin account, and records remain scoped to its permitted devices or meters.
- In `producers`, register and enable the synthetic sender, with `kind` set to `external` for this example. Give the sender a random ASCII machine Bearer through a secure channel. Store only its SHA-256 digest as 64 lowercase hexadecimal characters in `tokenSha256`. Add two `grants` for the same `equipmentId` and `groupKey: heatZone1`, one for `target: latest` and one for `target: history`, each with `zone1Actual` and `zone1Set` in `metricKeys`. Machine authorization is separate from user accounts.
- For energy, register the `meterId` and bilingual names in `meters`, assign the meter to the applicable human roles in `meterReadScopes`, and add the `meterId`, `groupKey: electricity`, and `metricKeys: ["energyInterval"]` to the sender's `energyGrants`.

Have the owner verify `OBSERVATION_ENABLED=true` and `OBSERVATION_PROFILE_FILE` points to the private file, then coordinate a backend reload to pick up the cached configuration. The Web configuration defines areas and displays. Device and meter identities and machine grants come from the profile. If the selectors are empty, check registration and read scopes first. A new environment may also have no cards, curves, meter metrics, or samples yet.

## 2. Create the heating zone, metrics, and slots

As admin, open **Device Status → Configuration**. In each tab, click **Add**, enter the values, and click **Save**.

1. **Area settings**. In **Metric key**, enter the area key `heatZone1` (`groupKey`). For **Category**, select **Temp Process**. Enter **Chinese name** “加热区 1” and **English name** “Heating Zone 1”, set **Sort order** to `10`, and turn on **Enabled**.
2. **Metrics**. Add both rows below. In **Sampling group**, select Heating Zone 1. **Category** comes from that area. Set **Type** to **Number**, **Unit** to `°C` (optional), and **Decimal places** to `1`.

   | Metric key | Chinese name | English name |
   | --- | --- | --- |
   | `zone1Actual` | 实际温度 | Actual temperature |
   | `zone1Set` | 设定温度 | Set temperature |

3. **Slots**. Add each row below. Type the area key `heatZone1` into **Sampling group**, select the corresponding name from the **Metric key** dropdown, and turn on **Enabled** for each row.

   | Target | Sampling group | Slot | Metric key |
   | --- | --- | --- | --- |
   | Latest (`latest`) | `heatZone1` | 1 | `zone1Actual` |
   | Latest (`latest`) | `heatZone1` | 2 | `zone1Set` |
   | History (`history`) | `heatZone1` | 1 | `zone1Actual` |
   | History (`history`) | `heatZone1` | 2 | `zone1Set` |

Choose a configuration category in the upper card. Use **Add**, filters and the table in the lower card. Slots start with all existing bindings, including latest, history and disabled rows. Select a target, sampling group or keyword, then click **Search**. Click **Reset** to show all again. **Reset widths** only restores the current table's column widths.

Each target and area has its own slots 1–100. Once used, slot bindings and physical meaning, including type and unit, are protected. For a latest-only metric, add just the latest slot. Keep using the same keys in reports after editing display names.

## 3. Configure the card and chart

1. Open **Device Status → Configuration → Cards → Add**. In **Metric key**, enter the card key `heatZone1Card` (`cardKey`). Set **Page** to **Temp Process**, enter **Chinese title** “加热区 1 温度” and **English title** “Heating Zone 1 Temperature”, set **Sort order** to `10`, and turn on **Enabled**. Click **Add metric** twice, select Actual temperature and Set temperature, enable both items, and save. A card supports up to 10 enabled items.
2. Open **Process Monitoring → Configuration → Curves → Add**. In **Metric key**, enter the chart key `heatingTemperature` (`curveGroupKey`). Set **Category** to **Temp Process** (temperature), enter **Chinese title** “加热区温度” and **English title** “Heating Zone Temperatures”, set **Sort order** to `10`, and turn on **Enabled**. Click **Add metric** to add and enable both `°C` numeric metrics. Set **Line style** for each, for example **Solid** for actual temperature and **Dashed** for set temperature, then save. Older configurations display as solid. Use numeric metrics of the same category and unit in one chart. Cards, curves, latest writing, and history retention are configured independently. A history plot needs enabled history slots and incoming samples.

## 4. Discover, submit, and view a sample

Use the commands below for your dedicated test equipment. Replace the example address with the approved API base URL, and verify the equipment, task, authorized areas, and metric keys. Ask the environment owner for the machine credential through a secure channel. Enter it at the hidden terminal prompt below. Keep the plaintext out of files, command arguments, and shell history. In a request client, use its Bearer Token field.

```bash
OBS_API='https://observation.example.invalid/api/v1'
printf 'Machine token (hidden): '
read -r -s OBS_MACHINE_TOKEN
printf '\n'

printf 'Authorization: Bearer %s\n' "$OBS_MACHINE_TOKEN" |
  curl --fail-with-body -sS -H @- "$OBS_API/integration/metric-definitions?equipmentId=obs-demo-device"
```

The GET returns only definitions authorized for the machine, including types, units, and whether the two targets are enabled. Once both metrics are enabled for both targets, save the common request body below as `observation.json`. Replace `observedAt` with the actual sampling time, or the time the simulated sample was taken, including its UTC offset. Assign a new `eventId` to a different sample. Keep the task number as a string to preserve leading zeros.

```json
{
  "eventId": "obs-demo-000042-001",
  "data": {
    "equipmentId": "obs-demo-device",
    "taskNo": "000042",
    "observedAt": "2026-11-18T10:00:00+08:00",
    "quality": "good",
    "groups": {
      "heatZone1": { "zone1Actual": 810.2, "zone1Set": 815.0 }
    }
  }
}
```

```bash
printf 'Authorization: Bearer %s\n' "$OBS_MACHINE_TOKEN" |
  curl --fail-with-body -sS -H @- -H 'Content-Type: application/json' \
  --data-binary @observation.json "$OBS_API/integration/equipment/latest-snapshots"

printf 'Authorization: Bearer %s\n' "$OBS_MACHINE_TOKEN" |
  curl --fail-with-body -sS -H @- -H 'Content-Type: application/json' \
  --data-binary @observation.json "$OBS_API/integration/monitor/history-samples"
```

- **Latest.** One complete latest snapshot is kept per device and task. A newer sample replaces all areas, clearing omitted areas or values to missing. The machine needs permission for the entire replacement scope.
- **History.** Set `quality: "good"` explicitly. History appends metrics with enabled history slots. Both targets can use the same event ID and return separate receipts. Check each response for `outcome`, `recordId`, and any `stored` or `skipped` items. For a retry on the same target, keep the producer, `eventId`, and original body.
- **Values.** Send scalar values in their original types and put units in configuration. Omit areas or metrics for missing data. `null` is invalid as a metric value. Numeric `0` and Boolean `false` are valid. See the contract for other optional fields. [Machine contract v2](../contracts/published/http-api/equipment-observation-v2/README.md)

Open **Device Status → Temp Process**, select the test equipment, and choose `000042` from the task dropdown or use **Follow most recent sample**. Click **Search**. The card should show `810.2` for Actual temperature (°C) and `815.0` for Set temperature (°C). Click the clock in a card header to reveal individual sampling times. Missing values display “—”. Booleans retain `true` and `false` as neutral labels. The page refreshes every five seconds by default. **Refresh** repeats the applied query. **Restore defaults** returns to the initial source and follows its latest task. The other card pages are **Production Params**, **Drive Process**, and **Cleaning process**.

Open **Process Monitoring → Temperature Curve**. On first entry, the page finds the latest drawable sample in your authorized sources and loads the eight hours ending at that sample. To look up an older task, enter or select its task number, such as `000042`, and click **Search**. The automatically displayed range does not constrain the lookup. Leave the source on **All authorized sources** or select a specific source. The header shows the result source. A complete Shanghai time range you enter manually takes priority. Clear the range to return to task-based time selection. **Refresh** and **Auto refresh** keep the applied source, task and time after a search. **Restore defaults** follows the latest drawable sample again within your selected source scope. The x-axis uses `observedAt`. If there are no drawable samples, the page explains why and shows no chart. The other curve pages are **Drive monitoring** and **Cleaning monitoring**.

## 5. Add a second area and inspect records

Create another temperature area `heatZone2` with `zone2Actual` (“2 区实际温度” / “Zone 2 actual temperature”) and `zone2Set` (“2 区设定温度” / “Zone 2 set temperature”). Include the zone in each name so you can distinguish the metrics in the dropdowns. Use slots 1 and 2 within that area on each target. Add a second card if needed and add both `°C` metrics to the existing `heatingTemperature` chart. Have the environment owner grant the second area on both targets and load the changes. When sending the next full bundle for the same device and task, include both `heatZone1` and `heatZone2` in `data.groups` to keep the latest values you still want displayed. Search again on Temperature Curve, then use **Select areas** for one or more areas or **Select all areas**.

| Admin entry | Filters, display settings, and edits |
| --- | --- |
| **Device Status → Data management** | Filter latest snapshots by equipment, sampling group (enter `heatZone1`), and task number. Use **Metric columns** to choose display columns and order. Open **Details** to inspect the source values and save a remark. |
| **Process Monitoring → Data management → Process samples** | Filter by equipment, sampling group, task number, and optionally the sampling time range. Use **Metric columns** to choose display columns and order. Open **Details** to inspect sample values and save a remark or set **Abnormal** or **Reviewed**. |
| **Process Monitoring → Data management → Energy samples** | Search by meter and sampling group. Set **Show column** and **Column order** in **Meter metrics**. Inspect values in the sample table and use **Edit** to save a remark or set **Abnormal** or **Reviewed**. |

These controls change display settings and annotations. Raw values have no edit or delete action.

## 6. Configure and submit energy samples

1. Open **Process Monitoring → Configuration → Meter metrics**. The list starts with all meter metrics you can access. Choose a meter or sampling group, or enter a keyword and click **Search**. Click **Reset** to show all again. Click **Add**, select a specific test meter in the form and enter `electricity` as **Sampling group**. Enter `energyInterval` as **Metric key**, `1` as **Slot**, “时段用电量” and “Interval electricity use” as the names, and `electricityConsumption` as **Physical quantity key**. Select **Interval** (`interval`) for **Measurement mode**, enter `kWh` as **Unit** and `1` for **Decimal places**. Turn on **Enabled** and **Show column**. Set **Column order** to `10` if desired, then save. The continuity and maximum sampling interval rules apply to cumulative readings.
2. Use the machine GET to discover authorized, enabled meter definitions. Send the body below as `energy.json` to the independent energy POST. Set the event ID, meter, group, metric, and times for your actual authorized test sample. Interval samples carry a real window with the start before the end. Energy samples are submitted by meter and group without a task number.

   ```json
   {
     "eventId": "obs-demo-energy-001",
     "data": {
       "meterId": "obs-demo-meter",
       "groupKey": "electricity",
       "observedAt": "2026-11-18T10:15:00+08:00",
       "quality": "good",
       "intervalStartAt": "2026-11-18T10:00:00+08:00",
       "intervalEndAt": "2026-11-18T10:15:00+08:00",
       "values": { "energyInterval": 2.5 }
     }
   }
   ```

   ```bash
   printf 'Authorization: Bearer %s\n' "$OBS_MACHINE_TOKEN" |
     curl --fail-with-body -sS -H @- "$OBS_API/integration/energy/metric-definitions?meterId=obs-demo-meter&groupKey=electricity"

   printf 'Authorization: Bearer %s\n' "$OBS_MACHINE_TOKEN" |
     curl --fail-with-body -sS -H @- -H 'Content-Type: application/json' \
     --data-binary @energy.json "$OBS_API/integration/energy/samples"
   ```

3. In **Process Monitoring → Energy Stats**, select the meter, `electricity`, and **Interval electricity use**. Set the report range to the actual full interval sent in the example and click **Search**. Complete coverage gives **Period usage 2.5 kWh**. In **Energy samples**, check the raw record by meter and group. If an interval leaves a gap, overlaps another interval, or crosses the report boundary, review the incomplete-result reason.

**Cumulative** (`cumulative`) usage is the difference between the opening and closing boundary readings. Confirm the unit, continuity, and meter-change rules, and set a maximum sampling interval. Missing boundaries, unknown continuity, a falling counter, or bad quality leave usage incomplete without a zero substitute. **Interval** usage sums good, non-overlapping increments that cover the entire report window. **Instantaneous** (`instantaneous`) values, such as power in kW, are readings or trends and cannot be summed directly as usage. A bundle containing only cumulative or instantaneous metrics omits the interval fields. Avoid adding cumulative and interval totals for the same consumption.

## 7. Troubleshoot and finish

- **No equipment or meter options.** Check the human read permission, profile registrations and scopes, and whether the service has loaded them. If options appear but there is no data, check enabled metrics, cards or curves, the relevant slots, task, and sampling range. Inspect receipts for `stale`, `no_history_metrics`, or skipped items.
- **Request failed.** For `401`, check the machine credential. For `403`, check grants and the full replacement scope. For `422`, check keys, types, timestamp offsets, and history quality. For `409`, check for an event and body conflict. A `503` can indicate a target that is not ready, concurrent contention, or an unknown commit outcome. Check target status and known receipts. When retrying the same event, use its original ID and body under the v2 contract to avoid duplicate writes.
- **Clean up test data.** Keep the target, producer, event IDs, and record IDs. If cleanup is required, have the environment owner confirm ownership, references, and authorization and handle the exact records.

Manual HTTP submission verifies configuration and the machine interface in the chosen environment. SMA product integration, DAA/PLC integration, and production deployment each require separate validation.
