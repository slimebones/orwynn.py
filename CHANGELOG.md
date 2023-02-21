# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [0.4.0a0](https://github.com/ryzhovalex/orwynn/releases/tag/0.4.0a0) - 2023-02-21

<small>[Compare with 0.3.7](https://github.com/ryzhovalex/orwynn/compare/0.3.7...0.4.0a0)</small>

### Features

- New import system structure ([40a070d](https://github.com/ryzhovalex/orwynn/commit/40a070db3cb7dda406965f0b83c42c85a4328dee) by ryzhovalex).
- Add global routes for websocket protocol ([2562d87](https://github.com/ryzhovalex/orwynn/commit/2562d87f8d021a703097d48a3bb9e155543dfce2) by ryzhovalex).
- Add global routes adding for Client ([4b6acab](https://github.com/ryzhovalex/orwynn/commit/4b6acab3bd41ef36eddab91a5be24c488c409865) by ryzhovalex).
- Add headers binding for Client ([7c9996f](https://github.com/ryzhovalex/orwynn/commit/7c9996f757e181f66b39d6dea4b2c3dae81ece6a) by ryzhovalex).
- Add global middleware ([a7619ac](https://github.com/ryzhovalex/orwynn/commit/a7619acc8904a7287c69932b24f5d3f33adf8427) by ryzhovalex).
- Add http|websocket new exception handlers ([1aa85d4](https://github.com/ryzhovalex/orwynn/commit/1aa85d40d05245889f156f507ac888a3764296c2) by ryzhovalex).
- Add websocket toolset ([8c7349a](https://github.com/ryzhovalex/orwynn/commit/8c7349adcd34abb3fa0e0114a539590c2e6fce0f) by ryzhovalex).
- Add WebsocketMiddleware ([b5189e4](https://github.com/ryzhovalex/orwynn/commit/b5189e406c4f500094b9a3a2e159bc463ef91195) by ryzhovalex).
- Add EndpointResponse to shortcut import ([8201a8a](https://github.com/ryzhovalex/orwynn/commit/8201a8af4fef99b0ce9eb0c35f829bb349ecb76b) by ryzhovalex).
- Make route is not requred for Module ([48499a7](https://github.com/ryzhovalex/orwynn/commit/48499a72b9344836a182816114868594dde5867a) by ryzhovalex).
- Add global modules and rename DI->Di (breaking) ([27fba0f](https://github.com/ryzhovalex/orwynn/commit/27fba0fe0d02572f57a70c3a6c243431848b07e7) by ryzhovalex).
- Add HttpMiddleware ([c2667f0](https://github.com/ryzhovalex/orwynn/commit/c2667f0190f50c96cd29923633d05e4d3ca389af) by ryzhovalex).
- Go SQLAlchemy==2.0.3 ([0b35098](https://github.com/ryzhovalex/orwynn/commit/0b3509831f09e0857cbad1c698eaf2397147ed3a) by ryzhovalex).
- Add contextualized logs ([7307fa8](https://github.com/ryzhovalex/orwynn/commit/7307fa84fd179dd3acc2485a7d5aca072d65f614) by ryzhovalex).
- Transform the Log to a Service ([e475d66](https://github.com/ryzhovalex/orwynn/commit/e475d664892ea0834f063d48a1498986cfb3bf79) by ryzhovalex).
- Add context management (untested) ([1885cb2](https://github.com/ryzhovalex/orwynn/commit/1885cb26ea8be690e46e6aa5001688124d86f04e) by ryzhovalex).
- Make first steps towards request context ([d8615f5](https://github.com/ryzhovalex/orwynn/commit/d8615f5dc55e8bcd6150daee82dcd3e8231cbb3a) by ryzhovalex).
- Add global route prefix and API version ([67cc79c](https://github.com/ryzhovalex/orwynn/commit/67cc79c8ad25b14e166fc776dd6314d55da8b57b) by ryzhovalex).
- New indication type system ([3d0892d](https://github.com/ryzhovalex/orwynn/commit/3d0892d274fae72593893296eb6d73972bde63d7) by ryzhovalex).
- Finish LogMiddleware with some limitations ([daa452e](https://github.com/ryzhovalex/orwynn/commit/daa452e4a78cbfd242b2f952b4af5079bed7d664) by ryzhovalex).
- add LogMiddleware but something went wrong ([7a861a8](https://github.com/ryzhovalex/orwynn/commit/7a861a8fa9d5e3d0396b0bd0ef5e6d66e8087b2a) by ryzhovalex).

### Bug Fixes

- Module exports ([448d83d](https://github.com/ryzhovalex/orwynn/commit/448d83da543201f1e9d2a9ac7a34820dbf41a324) by ryzhovalex).
- Acceptors shouldn't access non-imported module's providers ([9b5c7cc](https://github.com/ryzhovalex/orwynn/commit/9b5c7ccc4c96e88021fd03e87df3c5a0b1c5b650) by ryzhovalex).
- Rename AppRC->AppRc ([2ca0370](https://github.com/ryzhovalex/orwynn/commit/2ca0370bbd6e0ba8a8142397d97b6e5e241d5db9) by ryzhovalex).
- Cors testing ([16f732f](https://github.com/ryzhovalex/orwynn/commit/16f732fb185ba6cf93122b43b7e4ddcd782ff3a7) by ryzhovalex).
- Middleware dispatch patterns ([2681a8e](https://github.com/ryzhovalex/orwynn/commit/2681a8e17288184703cfd229b5018b3f622a45a1) by ryzhovalex).
- Make smarter typehint checking for route handlers ([d5b6476](https://github.com/ryzhovalex/orwynn/commit/d5b64769ced94f7d81ffd9c62fcbf06233dd629e) by ryzhovalex).
- Remove routes for sql and mongo ([2cfc055](https://github.com/ryzhovalex/orwynn/commit/2cfc055d69d4fed154c7a082221604a7fab97372) by ryzhovalex).
- Introduce approach to log testing and fix Log bugs ([d6f32be](https://github.com/ryzhovalex/orwynn/commit/d6f32be46142c7f5a335322b157564afcd155d9f) by ryzhovalex).
- Revert Log back into replica of loguru.logger ([e2eea46](https://github.com/ryzhovalex/orwynn/commit/e2eea467baed540847c674f2004acc32f3c4aab1) by ryzhovalex).
- Remove logger handlers after tests ([a6ae0c6](https://github.com/ryzhovalex/orwynn/commit/a6ae0c693ea454c3b98cf8b8d97b9b249f077722) by ryzhovalex).
- Go from uuid -> id, sql ids now sql_id ([bade398](https://github.com/ryzhovalex/orwynn/commit/bade398112c1ee79b60c245f690b229135e86349) by ryzhovalex).
- Change Indicator enum to string values ([5be7e35](https://github.com/ryzhovalex/orwynn/commit/5be7e35494b7d98a7c44ccb69517a0f848a2a7ae) by ryzhovalex).
- Remove Model from ErrorHandler and ensure this is a correct ACCEPTOR ([a50615f](https://github.com/ryzhovalex/orwynn/commit/a50615f0c16b2892ea9b72411f87c438592271ef) by ryzhovalex).
- set LogHandler kwargs to default ([d3b4c33](https://github.com/ryzhovalex/orwynn/commit/d3b4c33b6ff3584839536d6d4d851968b1354eb8) by ryzhovalex).
- add correct type for next middleware function to call ([c4d9cb0](https://github.com/ryzhovalex/orwynn/commit/c4d9cb0dff27366119bfc184ff08de05b2ee7dbc) by ryzhovalex).

### Code Refactoring

- Remove __init__ imports ([53121d5](https://github.com/ryzhovalex/orwynn/commit/53121d5270f0e27d1dcff5561cf0f2adfd78fc1e) by ryzhovalex).
- Make separation for global_http_route ([004af23](https://github.com/ryzhovalex/orwynn/commit/004af232b7705ed56e92129c74bc6d79d534070c) by ryzhovalex).
- Rename file for ValidationError ([2216425](https://github.com/ryzhovalex/orwynn/commit/2216425821b5243fdd19f7697dbb542c5d78c285) by ryzhovalex).
- Remove status_code from base Error ([009703a](https://github.com/ryzhovalex/orwynn/commit/009703ab77bf2345e6d590d5f13cd3a0f0a9f517) by ryzhovalex).
- Remove Database not implemented methods ([00af31e](https://github.com/ryzhovalex/orwynn/commit/00af31e70d5e66d59acb2081ad8283ac01ecad8b) by ryzhovalex).
- Change error module structure ([25313f7](https://github.com/ryzhovalex/orwynn/commit/25313f7771f025068a4c964b2cda8ff480c468be) by ryzhovalex).
- Move http files to web/http ([be949de](https://github.com/ryzhovalex/orwynn/commit/be949de166434f2baf2a5d6cc73adcc7f0524a54) by ryzhovalex).
- Move ErrorHandlers ([37eff51](https://github.com/ryzhovalex/orwynn/commit/37eff51f760c6ca05d46a874e5e5d247ea1c07c9) by ryzhovalex).
- Rename SQLConfig->SqlConfig ([01483be](https://github.com/ryzhovalex/orwynn/commit/01483be08f67f3e378f6bfcbbb227835b4872133) by ryzhovalex).
- Rename uppercased names to just capitalized ([a4288d6](https://github.com/ryzhovalex/orwynn/commit/a4288d6788851f58368a196399fff6d877072f01) by ryzhovalex).
- Add comment about shortcut imports ([3d73e91](https://github.com/ryzhovalex/orwynn/commit/3d73e91179d09ae857ab953caeb5a61db6db0a75) by ryzhovalex).
- Remove print statement ([653dbcd](https://github.com/ryzhovalex/orwynn/commit/653dbcdcf25f1b33658e29e26d77db31e4587955) by ryzhovalex).
- remove redundant items from http controller test ([da622cf](https://github.com/ryzhovalex/orwynn/commit/da622cf247a9c7230cb3575dc2afb538658bbcd2) by ryzhovalex).
- rename makeid -> gen_uuid ([5df1b34](https://github.com/ryzhovalex/orwynn/commit/5df1b34a3b38a91884dbafd0dde12178ed59ff43) by ryzhovalex).
- remove deprecated Test ([43c80fc](https://github.com/ryzhovalex/orwynn/commit/43c80fcad7e5cde316b0719e69eb3d5d086fe88b) by ryzhovalex).

## [0.3.7](https://github.com/ryzhovalex/orwynn/releases/tag/0.3.7) - 2023-01-23

<small>[Compare with 0.3.6](https://github.com/ryzhovalex/orwynn/compare/0.3.6...0.3.7)</small>

## [0.3.6](https://github.com/ryzhovalex/orwynn/releases/tag/0.3.6) - 2023-01-23

<small>[Compare with 0.3.5](https://github.com/ryzhovalex/orwynn/compare/0.3.5...0.3.6)</small>

## [0.3.5](https://github.com/ryzhovalex/orwynn/releases/tag/0.3.5) - 2023-01-19

<small>[Compare with 0.3.4](https://github.com/ryzhovalex/orwynn/compare/0.3.4...0.3.5)</small>

## [0.3.4](https://github.com/ryzhovalex/orwynn/releases/tag/0.3.4) - 2023-01-18

<small>[Compare with 0.3.3](https://github.com/ryzhovalex/orwynn/compare/0.3.3...0.3.4)</small>

## [0.3.3](https://github.com/ryzhovalex/orwynn/releases/tag/0.3.3) - 2023-01-17

<small>[Compare with 0.3.2](https://github.com/ryzhovalex/orwynn/compare/0.3.2...0.3.3)</small>

## [0.3.2](https://github.com/ryzhovalex/orwynn/releases/tag/0.3.2) - 2023-01-17

<small>[Compare with 0.3.0](https://github.com/ryzhovalex/orwynn/compare/0.3.0...0.3.2)</small>

## [0.3.0](https://github.com/ryzhovalex/orwynn/releases/tag/0.3.0) - 2023-01-16

<small>[Compare with 0.2.4](https://github.com/ryzhovalex/orwynn/compare/0.2.4...0.3.0)</small>

## [0.2.4](https://github.com/ryzhovalex/orwynn/releases/tag/0.2.4) - 2023-01-13

<small>[Compare with 0.2.3](https://github.com/ryzhovalex/orwynn/compare/0.2.3...0.2.4)</small>

## [0.2.3](https://github.com/ryzhovalex/orwynn/releases/tag/0.2.3) - 2023-01-11

<small>[Compare with 0.2.2](https://github.com/ryzhovalex/orwynn/compare/0.2.2...0.2.3)</small>

## [0.2.2](https://github.com/ryzhovalex/orwynn/releases/tag/0.2.2) - 2023-01-10

<small>[Compare with 0.2.1](https://github.com/ryzhovalex/orwynn/compare/0.2.1...0.2.2)</small>

## [0.2.1](https://github.com/ryzhovalex/orwynn/releases/tag/0.2.1) - 2023-01-09

<small>[Compare with 0.2.0](https://github.com/ryzhovalex/orwynn/compare/0.2.0...0.2.1)</small>

## [0.2.0](https://github.com/ryzhovalex/orwynn/releases/tag/0.2.0) - 2023-01-08

<small>[Compare with first commit](https://github.com/ryzhovalex/orwynn/compare/0a92d692347747bdc7f088c6c210f5276a06d901...0.2.0)</small>

