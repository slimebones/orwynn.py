# CHANGELOG

## UNRELEASED

### Features

- `orwynn.yml` is the only configuration filename supported for now. To
  override this, define environ `ORWYNN_RC_PATH`.

### Fixed

- Memory sqlite database is now used by default, instead of raising an error.

### Refactor

- ROUTE, ENDPOINTS and VERSION of controller classes now are PascalCase.
- ORWYNN_APPRC_PATH -> ORWYNN_RC_PATH.

## 1.2.0

### Features

- DTO models and utils
- Class utils

## 1.1.0

### Features

- Big utils update: many utility objects are added, most notable SHD - aka
  session handler

### Refactor

- Many SQL types are renamed
- Sql and SqlConfig are now SQL and SQLConfig

## 1.0.5

- fix: AnyIO breaking changes by version restriction
- feat: Antievil exception library support

## 1.0.4

- perf(mongo): Better optimized document creation.

## 1.0.3

- (http.log): Conditional request/response logging (set to False by default).
- (mongo): MongoConfig now accepts `url` instead `uri` and this field no more
    set by default.
- Structural refactors.
- Database ports for Orwynn development - see `docs/Development.md`.

## 1.0.2

- Small chore changes.

## 1.0.1

- Small chore changes.

## 1.0.0

- First version of the framework.
