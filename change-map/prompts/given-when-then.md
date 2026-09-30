Convert the tests of a code change into Given/When/Then tables for a reviewer who will not read test code.

Input: `{TESTS_DIFF}`, a unified diff of the test files. The change: {ONE_LINE_SUMMARY}. There are {TEST_COUNT} test functions. Read the test bodies to learn the real setup, action and assertions.

Output: write a JSON array to `{OUT}`:

```json
[{"rule": "One pending invitation per email per organization",
  "how": "Checked in the service under the organization row lock",
  "given": "Acme has a pending invitation for ana@acme.io",
  "examples": [
    {"when": "an admin invites ana@acme.io again", "then": "409 ALREADY_PENDING", "ok": false, "test": "TestCreateInvitation_RefusesSecondPendingForSameEmail"},
    {"when": "eight admins invite bob@acme.io at the same instant", "then": "one 201, seven 409", "ok": true, "race": true, "test": "TestCreateInvitation_HoldsOnePendingPerEmailUnderConcurrentCreates"}]}]
```

Rules:

- Group the tests into at most 9 business rules, each stated as a sentence a product person would agree with. {RULE_HINTS}
- Tests that fit no rule go in a last rule, "Everyday reads and writes".
- Every test appears in exactly one row. `test` is the exact function name.
- `given` is the shared starting scene of the rule, with concrete example data: a named organization, emails like ana@acme.io, named roles. Extra setup for one row goes at the start of its `when` ("after the invitation expired, an admin invites ana@acme.io").
- `when` is one action in plain words, 14 words or fewer, from the actor's side.
- `then` is the observable outcome, 10 words or fewer: the HTTP status and short error code when the test asserts one, otherwise the fact asserted.
- `ok` is true for success, false for a refusal. `race: true` only for concurrency tests.
- `how` says where the rule is enforced, 10 words or fewer.
- Plain English, no em dashes. Never invent behaviour a test does not assert.

Before writing, check the row count equals {TEST_COUNT} and no name repeats. Final message: the path, the row count, and any test that was hard to place. Under 80 words.
