# Team registration

`POST /api/register/team` accepts `multipart/form-data` and requires an
`Idempotency-Key` header (16-128 ASCII letters, numbers, `.`, `_`, `:`, or
`-`). A completed retry with the same key replays the original JSON response;
reusing a key with different data returns `409 DUPLICATE_SUBMISSION`.

Required text fields are `team_name`, `church_name`, `captain_name`,
`captain_phone`, `captain_email`, `vice_name`, `vice_phone`, and
`vice_email`. Optional `captain_whatsapp` and `vice_whatsapp` values must be
ten digits when non-empty. Player names are submitted as
`player_0_name` through `player_16_name`; indexes must be sequential and the
count must be 13-17.

`payment_receipt` is required and must be a genuine PNG, JPEG/JPG, or PDF.
The MIME type and extension must agree and the file must not exceed 5 MiB.
The server generates the Cloudinary object key; the client filename is never
used as a path. Obsolete files (`pastor_letter`, `group_photo`, and player
document fields) are not processed. Unknown fields are ignored.

Successful submissions are stored with `registration_status: "pending"` and
return:

```json
{
  "success": true,
  "data": {
    "registration_status": "pending",
    "team_id": "ICCT-001",
    "team_name": "Example Team"
  },
  "message": "Registration submitted successfully"
}
```

Each configured church can have one registered team. Availability is exposed
at `GET /api/churches/availability`; a full church has `team_count: 1` and
`locked: true`. Configure the authoritative list with the comma-separated
`CHURCH_LIST` environment variable.

Common errors use the JSON shape
`{"success": false, "error_code": "...", "message": "...", "details": {}}`.
Validation errors return `400`, capacity and idempotency conflicts return
`409`, oversized receipts return `413` where supported, and upload failures
return `503`. Email delivery is attempted only after the database commit and
does not invalidate a successful pending registration.
