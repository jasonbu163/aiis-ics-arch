# PLC Tools

The PLC tool group converts reviewed engineering inputs into contracts used by
the optional Control Agent. It is an offline preparation toolset. It never
connects to a live PLC and it does not contain site workbooks in the public
baseline.

- `point-mapping/` — point contract conversion.
- `projection-mapping/` — field-to-point review.
- `snapshot-policy/` — raw/latest policy conversion.
- `s7-virtual-plc/` — local simulator support.

Each tool keeps empty `inputs/` and `outputs/` directories. Put private files in
a separate workspace and pass explicit paths when running a conversion.
