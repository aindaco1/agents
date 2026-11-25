# Dust Wave Equipment Intake

Shared procedure skill for Codex and Hermes, distilled from the owner's equipment
intake workflow. This is a procedure, not a new persona; it does not change the
roster, model routing, agent count, or existing memories.

The canonical package lives at `skills/operations/dustwave-equipment-intake/`.
Use the repository publisher rather than hand-copying or replacing live libraries:

```sh
python3 scripts/sync_portable_skills.py --skill dustwave-equipment-intake --plan
# Review the preview, then use its exact plan_hash with the same selection:
python3 scripts/sync_portable_skills.py --skill dustwave-equipment-intake --apply <plan_hash>
python3 scripts/sync_portable_skills.py --skill dustwave-equipment-intake --check
```

Run those commands from the agents checkout, including the iCloud checkout after
pulling/merging the change. A common existing checkout is:
`/Users/aindaco1/Library/Mobile Documents/com~apple~CloudDocs/agents`.
Do not assume that directory is mounted in a cloud session.

The publisher installs the same package under:

- Codex: `~/.agents/skills/dustwave-equipment-intake/`
- Hermes: `~/.hermes/skills/operations/dustwave-equipment-intake/`

If a different runtime/profile uses another skills library, use the publisher's
documented destination flags and inspect the preview. Do not auto-trust a repo,
replace a profile, or bypass an existing publication conflict.

## Invoke

- Codex: `$dustwave-equipment-intake Add this 500GB SSD.`
- Hermes: `/dustwave-equipment-intake Add these three lights.`

Attach original photos and mention quantities or kit membership. Both runtimes
need their own working Notion connection with access to the Equipment database,
image inspection, and an upload-capable HTTP/Notion tool. Tool names are resolved
at runtime. Installing this skill does not configure authentication or guarantee
media-editing availability. If discovery differs in the installed Hermes version,
use its skill selector and select the categorized package.

## Expected behaviors

| Request | Expected result |
| --- | --- |
| Add 3× of a photographed light | One entry with 3× in its title and quantity three |
| Add tripod/head/plate | One kit with supported components and photo captions |
| Add a similar stand | Separate record; don't overwrite a generic older stand |
| No tags/location in body | Set Location/Type properties; omit those body sections |
| Case has three radios and three empty slots | Record three units, never six |
| Model unreadable | Use distinguishing visible features; omit invented model |
| Photograph of a packed reflector | Only estimate packed size if asked |
| Image broken in Notion | Fresh upload, replace affected media, preserve text |
| Photos supplied | Faithful crop/original; no reconstructed labels or hardware |
| User asks for a manual | Verified exact-model PDF, uploaded and embedded |

No live inventory writes are necessary to install or validate this package.
Publication checks establish package compatibility, not proof that a future agent
will follow every instruction or that a particular Notion connection works.

Format references: [Codex skills](https://developers.openai.com/codex/skills/),
[Hermes skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/),
and [Agent Skills specification](https://agentskills.io/specification).
Repository-specific frontmatter and publisher conventions take precedence over
generic installation examples.
