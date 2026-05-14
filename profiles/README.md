# EPAS Starter Profile Bundles

This directory contains machine-readable starter bundles for the EPAS v2.1 profile layer.

Each bundle can be applied with:

```bash
python scripts/configure.py --bundle <bundle-id>
```

Bundle IDs in this starter suite are organized by:

- lifecycle: `prototype`, `demo`, `mvp`, `production`
- data model family: `relational`, `entity-native`

The relational bundles match the current shipped runtime closely.
The entity-native bundles document the SurrealDB-targeted path for teams building entity-and-relationship-native systems.
