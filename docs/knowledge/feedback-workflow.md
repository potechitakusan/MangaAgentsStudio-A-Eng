# Recording Feedback on Request

Updated: 2026-09-26. This production workflow applies to projects created from the project template.

## When to begin recording

Organize findings in `docs/feedback/` only when the user requests a feedback record, for example, "Please save this feedback." There is no need to ask whether to record feedback. Without a request, do not create new feedback records, maintain candidate findings, or report "no new findings." If ongoing recording is requested, follow its specified scope and duration.

Progress, decisions about revisions, PNG review, PSD validation, and the conditions needed to resume generation are normal production records. Keep them as needed; do not duplicate them under the label of feedback.

## What to record when requested

Use `docs/feedback/TEMPLATE.md` and record only the requested scope.

- The issue, change attempted, conditions held constant, and comparison baseline.
- Relative input/output paths, model and workflow identifiers, and key settings.
- Observations, number of attempts, failures, applicable conditions, and counterexamples.
- Status: untested, observed, conditionally reproduced, candidate for shared guidance, or rejected.
- The smallest proposed change to shared knowledge and its supporting evidence.

Do not treat a proposal as demonstrated without reader evaluation. Do not turn one project's preferences into universal rules, or include credentials, unpublished assets, or unorganized logs.

## Incorporating findings into shared knowledge

Creating a record and transmitting it externally are separate actions. Within the requested sharing or incorporation scope, check the evidence and reproduction conditions, then accept, defer, or reject the finding. Incorporate only the necessary knowledge rather than copying the whole project. Do not automatically update existing projects.

When generalizing across models, put input preparation, recording, and evaluation decisions in shared documents; put observed symptoms, operations, and failure examples in documents specific to each model and version. Keep existing service documentation authoritative for connections and fees; do not duplicate the entire workflow per model. Record actual inputs separately from planned candidates, attempt counts and exclusions, and conditions changed at the same time. Do not recast an observation from one model as a verified fact about another.

Distributed documents must retain an evidence summary, material ID, organization date, date read, and scope of applicability. If original materials are not included, do not create nonexistent links; keep their mapping to the provider in the kit's private working records. State when local material has no public URL. Do not mark incorporation as revalidated if its images were not reviewed again.
