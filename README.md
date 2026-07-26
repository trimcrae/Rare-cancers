# email-outbox

Scratch branch. A scheduled Claude session writes `newsletter-summary.md` here; the weekly newsletter
send (`method-watch.yml`, Fridays 7:00 AM ET) picks it up if it is ≤2 days old. Not part of the site or
main history.

`daily-summary.md` was removed 2026-07-26 together with the daily status email's cron — nothing writes or
reads it any more. It is still in this branch's history if the daily cadence is ever revived.
See `research/modalities/daily-email-system.md` on `main` for the full picture.
