# Notion destination and tool adapters

These identifiers are navigation hints established from the owner's inventory.
Fetch the live schema before each writing session; do not assume it never changes.

- Database: https://app.notion.com/p/c0222bcc58d54de68476a797ef5c8b5b
- Database ID: `c0222bcc-58d5-4de6-8476-a797ef5c8b5b`
- Data source: `collection://b44c8a23-0066-47c5-a4cc-a4bb2f1aed21`
- Data source ID: `b44c8a23-0066-47c5-a4cc-a4bb2f1aed21`

## Properties

| Property | Established type | Intake behavior |
| --- | --- | --- |
| Name | title | Specific equipment/kit name; quantity prefix for multiples |
| Location | select | Set exact existing option `Dust Wave` unless overridden |
| Type | multi-select | Select relevant existing options; never invent new schema |
| Acquired? | checkbox | True for the owner's supplied inventory item; not for a wish-list request |
| Cost / Checked Out? | rollup | Do not write |
| Who Checked It Out? / Project / Expenses | relations | Preserve; do not infer |
| Date / Who's bringing it? / Use on the feature? | other | Leave untouched unless requested |

Existing useful Type options include Lighting, Stands, Grip, Camera Support,
Stabilizer, Microphone, Audio, Storage, Production, Battery, Lens, and Camera.
Verify current options. Examples: SSD → Storage; light → Lighting; microphone kit
→ Microphone + Audio; boom mic stand → Stands + Audio; camera tripod → Camera
Support; light stand → Stands + Grip; digital communication kit → Audio + Production.

## Capability mapping

Use whichever connected tools are actually installed. Do not hardcode a tool
namespace or require a particular plugin provider in the shared skill.

| Need | Notion MCP/connector | Direct Notion API equivalent |
| --- | --- | --- |
| Destination | fetch database, then collection/data source schema | Retrieve database and its data source |
| Duplicates | search scoped to collection; inspect candidates | Query target data source, handling pagination |
| Create row | create page with data_source_id parent | Create page with data_source_id parent and native properties |
| Local photo | create-file-upload; send multipart binary file | File Upload API create/send; check uploaded status |
| Attach media | create/update page with returned media source | Native image/pdf block using completed file_upload ID |
| Repair | fetch page, then targeted content/block update | Retrieve children, update affected block |

Connector property shorthands observed in this thread (not raw API JSON):

```json
{
  "Name": "Samsung T7 Portable SSD — 500GB (Gray)",
  "Location": "Dust Wave",
  "Type": ["Storage"],
  "Acquired?": "__YES__"
}
```

Raw API adapters must use native typed property objects, e.g. checkbox `true`,
select `{name: "Dust Wave"}`, multi_select name objects, and a title rich-text
array. Obtain API versions and request schemas from the installed adapter/current
official documentation rather than guessing. Keep credentials in the host's
configured credential store or environment; never commit tokens or signed URLs.

## Markdown and file attachment contract

For the Notion MCP dialect, read `notion://docs/notion-flavored-markdown-spec`
through the Notion fetch/resource capability before authoring content. An example
of the established dialect is:

```xml
<image source="file-upload://COMPLETED_UPLOAD_ID">Short caption.</image>

<pdf source="file-upload://COMPLETED_UPLOAD_ID">Exact model manual.</pdf>
```

Replace placeholders only with completed uploads from the active connection.
These tags are not raw Notion API block JSON and must not be sent as ordinary
text by an adapter that does not support them. Use native media blocks instead.

For a connector-provided upload URL, send exactly the requested multipart field
and headers. Use a safe HTTP client without logging authorization headers. The
upload must report success before attaching. Do not interpolate secrets into
shell commands, reuse uploads created by another integration, or publish images
to an unrelated third-party host to work around access.

## Image repair lesson

In this thread, copying a media reference from the older generic Tripod Dolly
page into the separate Dot Line entry produced an image that did not load.
Re-uploading the local image directly and replacing the new page's media fixed
the attachment path. Treat opaque cross-page references as unsafe to transplant.
Stable media references can be preserved when editing the SAME page; re-fetch
signed URLs when bytes are needed. New pages should receive fresh uploads.
