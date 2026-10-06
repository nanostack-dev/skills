# Discover the engine's dialect and capabilities

Use this reference before writing definitions for an unfamiliar engine or after
its version changes. The graph and verification lessons in the main skill do not
imply that a particular node type, command or execution rule exists.

Read the repository's scripts and test guide first. Then inspect the actual tool's
help, version, schemas and relevant documentation or source. Record the discovered
bindings in the project's own guide, with the version and source of the evidence.
Use small disposable probes for behavior that documentation leaves ambiguous.

| Capability | Establish before relying on it |
| --- | --- |
| Suite selection | Whether names, IDs, tags, files or patterns select flows; match-any versus match-all behavior; zero-match handling; setup dependencies |
| Scope | How identity, tenant/organization and environment are selected and resolved; explicit target reporting; required permissions |
| Definition ownership | Repository versus remote authority; export/import support; published versus draft revisions; how CI chooses the revision |
| Updates | Supported authoring interfaces and schema; merge versus replacement behavior; preservation of unrelated metadata |
| Graph execution | Edge semantics; branch concurrency; failure propagation; cancellation; valid cycles or repetition |
| Cleanup | Always/finally support; waiting for failed branches; output availability after a failed assertion; cancellation fallback and ownership ledger |
| References | Exact output/interpolation syntax; ancestor requirements; missing-value handling; literal-template escaping and repeated expansion |
| Variables | Available scopes, precedence and overlays; secure input mechanisms; generator evaluation time and subflow input binding |
| Assertions | Supported extractors/operators and their types; exact versus substring matching; expected/actual diagnostics; templated assertion values |
| Polling | Native polling or supported harness loop; input visibility; deadlines, intervals and final failure evidence |
| Event observation | Isolated capture support; resource correlation; event matching/consumption; duplicate and forbidden-event checks; observation window |
| Secrets | Encrypted storage where available, permissions, value-read behavior and redaction in every result/export channel |
| Results | Completion API or report, per-node statuses, skipped/unevaluated outcomes, actual selected identities and cleanup results |
| CI | Required gate and runtime, revision/selection, credentials, report retention, cleanup and permitted failure-recovery policy |

For each required capability, distinguish **supported**, **unsupported** and
**unverified**. When a native feature is absent, use an existing authorized harness
or supported API only if it preserves the same outcome and isolation. Otherwise
record the unexecuted boundary. Replacing a command name or inventing a generic
flag does not make an unsupported engine feature available.

Keep examples in the engine's real, validated dialect once those bindings are
known. Only runnable project examples should claim actual syntax; dependency
sketches remain clearly labeled conceptual diagrams.
