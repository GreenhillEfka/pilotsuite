# Security model

## Alpha guarantees

- mutation code paths are hard-disabled, not merely hidden by the UI;
- no host network, Docker socket, privileged capability, or Home Assistant config mount;
- Home Assistant access uses the short-lived `SUPERVISOR_TOKEN` from the runtime environment;
- the token is never persisted, returned by the API, or logged;
- the UI is exposed through Home Assistant Ingress and restricted to administrators;
- persistent output is limited to `/data`;
- audit records are append-only from the application perspective;
- logs redact keys containing `token`, `secret`, `password`, or `authorization`.

## Future mutation requirements

A release may enable a write only after all of the following exist:

1. typed action allowlist;
2. explicit policy decision and bounded scope;
3. named inverse or an explicit irreversible classification;
4. pre-change backup where the action requires it;
5. postconditions with a bounded verification timeout;
6. automatic rollback for reversible failure;
7. immutable audit events for every transition;
8. UI-visible approval, autonomy window, and revocation;
9. integration tests against a disposable Home Assistant instance.

No LLM response can satisfy or bypass these requirements.

## Reporting

Do not open public issues containing household entity IDs, locations, logs with credentials, or private repository content. Redact sensitive data before sharing diagnostics.

