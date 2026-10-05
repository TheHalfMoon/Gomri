# P02-G2b Internal Identity

**Parent:** #8  
**Canonical base:** `7996ebb53dddcb74e239fd57581d9646b74157c6`

## G2b-1 scope

This grain migrates Gomrey-owned ephemeral internal identity only:

- blank-slide browser event constant and event name;
- chart runtime global and DOM marker;
- splash component/export/CSS identity and user-visible loading text.

No persisted clipboard or generated-chart protocol is changed in this grain.

## Deliberate binary-artwork exception

`/Presenton_Splash.png` remains the imported donor binary. G2b renames the component and CSS identity around it but does not relabel the image. Replacement requires a real Gomrey artwork asset and belongs to P02-G3.

## Compatibility

These event/runtime identifiers are process-local ephemeral implementation details, so no legacy dual-read layer is introduced. Persisted protocol identifiers are handled separately in G2b-2.

## Qualification

No CI or review PASS is claimed here until the exact candidate is tested and reviewed.

## G2b-2 persisted protocol migration

New clipboard writes use Gomrey MIME, text prefix, local-storage key and payload format. Presenton MIME/prefix/storage/format values remain readable and are normalized to the Gomrey payload format before paste. ClipboardEvent copy also emits a legacy MIME payload for bounded transition compatibility.

New chart HTML/config writes use Gomrey chart globals, canvas markers and configuration extension keys. Renderers accept legacy Presenton globals/attributes/extension keys. The legacy chart-state global aliases the same state object as the canonical Gomrey global during the compatibility window.

This is a read-compatibility migration, not a claim that historical artifacts have been rewritten.
