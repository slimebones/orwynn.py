# 3.1.5

- update to newest yon

# 3.1.4

- disallow double underscores for sys and rsys functions

# 3.1.3

- adjust to yon refactors

# 3.1.2

- update deps

# 3.1.1

- use classic "orwynn" name for PyPI

# 3.1.0

- integrate with plugins deeply, disallow sys usage without plugins
- remove Dtos, Flag

# 3.0.1

- env: fix logic

# 3.0.0

Rebuild to simplify core.

- converted systems to functions
- implemented plugin architecture
- moved plugins (mongo, auth, rbac) to separate repos

# 2.4.7

- mongo: fixed decide() being a classmethod, renamed to decide_state_flag()

# 2.4.6

- mongo: adjusted to new queries
- mongo: added AggDocReq
- mongo: restructured MongoStateFlag API

# 2.4.5

- updated rxcat

# 2.4.4

- auth: add dummy register_bus_client

# 2.4.3

- boot: added support of ServerBusCfg

# 2.4.2

- auth: fix target connids set

# 2.4.1

- mongo: fix collection factory pre-init collection fetching

# 2.4.0

- updated rxcat
- mongo: added MongoCfg.default_colection_naming for docs which didn't override
  defaults
- mongo: is_lock_check_skipped is now public flag for Doc's upd and del methods
- mongo: added IS_LINKING_IGNORING_LOCK flag to allow/disallow linking to have
         access to locked objects
- sys: added Sys._ok() helper method to pub OkEvt
- mongo: Doc.get_many() now support search queries with $aggregate field

# 2.3.5

## Fixes

- mongo: fix shared cached fields between Doc child classes

# 2.3.4

## Fixes

- msg: add missing code for FlagEvt

# 2.3.3

## Features

- mongo: add CheckLockDocReq to checkout if some document is locked

# 2.3.2

## Fixes

- mongo: lock sys unlocking problems

# 2.3.1

## Fixes

- mongo: fix collection name retrieval for camel case

# 2.3.0

## Features

- mongo: add LockDocSys

# 2.2.0

## Features

- mongo: add locking

# 2.1.0

## Features

- mongo: add field linkage - a deleted sid is removed from related
         collections
- mongo: add locking

## Fixed

- mongo: fixed archive overwriting strategy

# 2.0.0

- going rx

# 1.4.0

- Removed `base` imports.
- Renamed globally `fn` to `func`.
- Fixed indication digesting on polymorph cdto input.
- Added proper module version.
- (SQL) Added sqlite memory default initialization.
- (SQL) SQLConfig.should_drop_env_spec + SQL.recreate_public_schema_cascade
    for PSQL databases
- (DTO) CDTO.convert now accepts any objects.
- (HTTP) HTTPController.has_method.

# 1.3.4

- Update PyKit.

# 1.3.3

## Features

- FastAPI 0.104 support.

## Refactor

- Moved Utils to PyKit.

# 1.3.2

## Fixed

- Error code handling

# 1.3.1

## Fixed

- Updated antievil to conform with new error codes
- Small yet critical fixes

# 1.3.0

## Features

- `orwynn.yml` is the only configuration filename supported for now. To
  override this, define environ `ORWYNN_RC_PATH`.
- MongoStateFlag

## Fixed

- Memory sqlite database is now used by default, instead of raising an error.

## Refactor

- ROUTE, ENDPOINTS and VERSION of controller classes now are PascalCase.
- ORWYNN_APPRC_PATH -> ORWYNN_RC_PATH.

# 1.2.0

## Features

- DTO models and utils
- Class utils

# 1.1.0

## Features

- Big utils update: many utility objects are added, most notable SHD - aka
  session handler

## Refactor

- Many SQL types are renamed
- Sql and SqlConfig are now SQL and SQLConfig

# 1.0.5

- fix: AnyIO breaking changes by version restriction
- feat: Antievil exception library support

# 1.0.4

- perf(mongo): Better optimized document creation.

# 1.0.3

- (http.log): Conditional request/response logging (set to False by default).
- (mongo): MongoConfig now accepts `url` instead `uri` and this field no more
    set by default.
- Structural refactors.
- Database ports for Orwynn development - see `docs/Development.md`.

# 1.0.2

- Small chore changes.

# 1.0.1

- Small chore changes.

# 1.0.0

- First version of the framework.
