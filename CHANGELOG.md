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
