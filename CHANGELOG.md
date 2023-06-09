# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## Unreleased

<small>[Compare with latest](https://github.com/ryzhovalex/orwynn/compare/1.0.0b4...HEAD)</small>

### Bug Fixes

- types checking across the framework ([62f011c](https://github.com/ryzhovalex/orwynn/commit/62f011c5e0459136bcd4095e5a6f30d837500e1a) by ryzhovalex).

### Code Refactoring

- rename error_code -> code ([47f117f](https://github.com/ryzhovalex/orwynn/commit/47f117f4e4b6fd921d32ca62d11c94224aa810a7) by ryzhovalex).
- additional changes to lint ([f7db643](https://github.com/ryzhovalex/orwynn/commit/f7db64364b703a9d674bf27c41bef8ecfc19d251) by ryzhovalex).
- global refactoring to recommended naming ([bb2fba1](https://github.com/ryzhovalex/orwynn/commit/bb2fba1540c744e13527282e933462bcdbfac9c1) by ryzhovalex).

<!-- insertion marker -->
## [1.0.0b4](https://github.com/ryzhovalex/orwynn/releases/tag/1.0.0b4) - 2023-05-22

<small>[Compare with 1.0.0b3](https://github.com/ryzhovalex/orwynn/compare/1.0.0b3...1.0.0b4)</small>

### Features

- App.core_app property ([46d079e](https://github.com/ryzhovalex/orwynn/commit/46d079efde4179be6311709f4a81519cd70435a6) by ryzhovalex).
- catchr shortcut ([581e572](https://github.com/ryzhovalex/orwynn/commit/581e5726b94465a9d87b2e18a1ea641de6c20f13) by ryzhovalex).
- error log catching at handlers ([f2b5f04](https://github.com/ryzhovalex/orwynn/commit/f2b5f04ff1131d26a507c72883bdc17ae9b1f57f) by ryzhovalex).

### Bug Fixes

- redirect blocking due to HttpLogger problem ([efcb5f5](https://github.com/ryzhovalex/orwynn/commit/efcb5f5cb101c3d29330792ed0362cba7575af21) by ryzhovalex).
- catch log at error hanlders in tests ([63e2c70](https://github.com/ryzhovalex/orwynn/commit/63e2c7009239082d97d0151f4246224740a14152) by ryzhovalex).

### Code Refactoring

- rename unproperly formatted environ ([55aedec](https://github.com/ryzhovalex/orwynn/commit/55aedec61d4f02440b5e68a78865c323bb34f7ec) by ryzhovalex).
- rename sql_id to sid ([b43d360](https://github.com/ryzhovalex/orwynn/commit/b43d360d3897054cab917f13400112776a62a830) by ryzhovalex).

## [1.0.0b3](https://github.com/ryzhovalex/orwynn/releases/tag/1.0.0b3) - 2023-05-15

<small>[Compare with 1.0.0b2](https://github.com/ryzhovalex/orwynn/compare/1.0.0b2...1.0.0b3)</small>

### Features

- root_dir property for boot proxy ([6ecc68a](https://github.com/ryzhovalex/orwynn/commit/6ecc68afd6bc8644f83cfdc7f6398b781d31798b) by ryzhovalex).
- multiple query for examle ([5f87d69](https://github.com/ryzhovalex/orwynn/commit/5f87d696d68993167b786ba916d322ed9e9a3ff4) by ryzhovalex).
- file http response ([c728dd4](https://github.com/ryzhovalex/orwynn/commit/c728dd42999e9d341b543631cf1ffe5cddd424e6) by ryzhovalex).
- decrease privacy of Sql ([30426ed](https://github.com/ryzhovalex/orwynn/commit/30426ed4f3d17ffb45b47bfe8af0ef7e77275afb) by ryzhovalex).
- additional arguments to sql create engine ([dbf1b59](https://github.com/ryzhovalex/orwynn/commit/dbf1b59d71cf294a69e77de0ccf274fd142d66a8) by ryzhovalex).
- add example deps ([5e4119c](https://github.com/ryzhovalex/orwynn/commit/5e4119c877fe837a2e49082475596af702e3152a) by ryzhovalex).
- extend example ([634b147](https://github.com/ryzhovalex/orwynn/commit/634b1478bc9e17368e7b5a4216ac3193daec0cb2) by ryzhovalex).

### Bug Fixes

- lint ([3358aa7](https://github.com/ryzhovalex/orwynn/commit/3358aa7103d4f6d0deca12a0d751fee7f54a8e26) by ryzhovalex).
- remove error for wrong return handler type ([efd65d6](https://github.com/ryzhovalex/orwynn/commit/efd65d6c28fd296e5c0f048a9505f6298f947ffd) by ryzhovalex).
- error code digesting ([7287b9f](https://github.com/ryzhovalex/orwynn/commit/7287b9f1118f472abb2dca10380b30c6c9a539b1) by ryzhovalex).
- log json decoding ([f32aa5e](https://github.com/ryzhovalex/orwynn/commit/f32aa5e886fd791be27679dc6e6021a653c2675d) by ryzhovalex).
- remove code workspace ([bddfa68](https://github.com/ryzhovalex/orwynn/commit/bddfa6894c0a025c1939cbf78750f403281a04be) by ryzhovalex).

## [1.0.0b2](https://github.com/ryzhovalex/orwynn/releases/tag/1.0.0b2) - 2023-04-07

<small>[Compare with 1.0.0b1](https://github.com/ryzhovalex/orwynn/compare/1.0.0b1...1.0.0b2)</small>

### Features

- add formatting for error message ([d0885b1](https://github.com/ryzhovalex/orwynn/commit/d0885b1ed1f146ae9cbc350f6d7350c8015c231c) by ryzhovalex).
- add possibility to set own docs and redoc route ([14771e4](https://github.com/ryzhovalex/orwynn/commit/14771e4a5b904a303e548b8c3e59b7e001b71e37) by ryzhovalex).
- error codes ([7e5b169](https://github.com/ryzhovalex/orwynn/commit/7e5b1698bcfeb15babd5ac43fbd0de180812c107) by ryzhovalex).

### Bug Fixes

- no final routes were set for ws controller ([d16d522](https://github.com/ryzhovalex/orwynn/commit/d16d522ee7a3a57d6890a0b2640de820684dcb0b) by ryzhovalex).

### Code Refactoring

- rename ucls -> klass ([3cd46c1](https://github.com/ryzhovalex/orwynn/commit/3cd46c1b5134cb46af51102fe6e85648f4f9af08) by ryzhovalex).
- change environs name formatting ([f986522](https://github.com/ryzhovalex/orwynn/commit/f986522d02fcd6bbdf8f6a10bd29b3f5c3191e65) by ryzhovalex).

## [1.0.0b1](https://github.com/ryzhovalex/orwynn/releases/tag/1.0.0b1) - 2023-04-03

<small>[Compare with 1.0.0a4](https://github.com/ryzhovalex/orwynn/compare/1.0.0a4...1.0.0b1)</small>

### Bug Fixes

- incorrect condition for controller handler return typehint ([fd02547](https://github.com/ryzhovalex/orwynn/commit/fd02547b0c3c5a4afe9468be7b6bec16b7c2b164) by ryzhovalex).
- circular import problem on uvicorn app factory launch, also create an example app ([8f675cd](https://github.com/ryzhovalex/orwynn/commit/8f675cdee0bc8fa42468d71ee189792a5e156444) by ryzhovalex).

### Code Refactoring

- add REQUEST_METHODS_BY_PROTOCOL instead of HttpMethod and WebsocketMethod ([ac0f36a](https://github.com/ryzhovalex/orwynn/commit/ac0f36af570a6db4f0abe53386423ad240f3614c) by ryzhovalex).
- rename cls -> ucls ([40f8623](https://github.com/ryzhovalex/orwynn/commit/40f862354c118fedd7aefca2d6c0389f5e00bb92) by ryzhovalex).
- rename util -> utils ([5e60f9e](https://github.com/ryzhovalex/orwynn/commit/5e60f9ebcdc557c9ed2c3c62b61da58ed6e11ab8) by ryzhovalex).
- dependency versions setup ([48315ce](https://github.com/ryzhovalex/orwynn/commit/48315cecb859eeeb17befbe02a09bd46fd81610d) by ryzhovalex).
- move circular error to module ([8cf52f5](https://github.com/ryzhovalex/orwynn/commit/8cf52f566c84acc6c95432eaac3dd14208639fec) by ryzhovalex).

## [1.0.0a4](https://github.com/ryzhovalex/orwynn/releases/tag/1.0.0a4) - 2023-03-07

<small>[Compare with 1.0.0a3](https://github.com/ryzhovalex/orwynn/compare/1.0.0a3...1.0.0a4)</small>

### Features

- Add base module's import shortcuts ([0fdbfec](https://github.com/ryzhovalex/orwynn/commit/0fdbfecc57ae76dbe2ed9923ef15207d620aecd9) by ryzhovalex).
- Add request method ([48dc93b](https://github.com/ryzhovalex/orwynn/commit/48dc93bdfe6125123009a7da6361d014598baa88) by ryzhovalex).
- bootscripts ([22ca6ce](https://github.com/ryzhovalex/orwynn/commit/22ca6ce2de8e941f2c721cc27f5b7bc3418430fb) by ryzhovalex).
- Add controller's final routes ([9f477c2](https://github.com/ryzhovalex/orwynn/commit/9f477c24e7cca51da5167d8911f68425129eb062) by ryzhovalex).

### Bug Fixes

- Client stacking binded headers ([ba173d6](https://github.com/ryzhovalex/orwynn/commit/ba173d663e986043a6f501164243f98902a1cf13) by ryzhovalex).
- Error handlers got initialized twice ([83b4e96](https://github.com/ryzhovalex/orwynn/commit/83b4e96ec5950e56566df216080595559b2461db) by ryzhovalex).
- Resolve fastapi get_dependant issue ([36bbaba](https://github.com/ryzhovalex/orwynn/commit/36bbabadacb79d38a36ead903750bbab46d6fd1d) by ryzhovalex).
- Add exception for dict return types of controllers ([4fd17c9](https://github.com/ryzhovalex/orwynn/commit/4fd17c9e05d6caca5585624549a23224b831a0b8) by ryzhovalex).

### Code Refactoring

- Move worker module to base folder ([26520da](https://github.com/ryzhovalex/orwynn/commit/26520da34f12890a2d6c4c8cf9f4796597ed7a0c) by ryzhovalex).
- Restructure util and helpers ([4063532](https://github.com/ryzhovalex/orwynn/commit/40635328e231d204b337f9d034c21a7335cd059b) by ryzhovalex).
- Pass linter ([6c82561](https://github.com/ryzhovalex/orwynn/commit/6c82561773b88afb5f904e3c01ab6cfe87133bff) by ryzhovalex).
- Rename ExceptionHandler -> ErrorHandler ([74d5a38](https://github.com/ryzhovalex/orwynn/commit/74d5a38e1ac375f97138a7d38b91d46d11b2d4c4) by ryzhovalex).
- Remove Error ([0365571](https://github.com/ryzhovalex/orwynn/commit/0365571387da4829fab7a62cad6bc13fcb72da37) by ryzhovalex).

## [1.0.0a3](https://github.com/ryzhovalex/orwynn/releases/tag/1.0.0a3) - 2023-02-28

<small>[Compare with 1.0.0a2](https://github.com/ryzhovalex/orwynn/compare/1.0.0a2...1.0.0a3)</small>

### Features

- Add option to pass poolclass to sql ([ce9c7bf](https://github.com/ryzhovalex/orwynn/commit/ce9c7bfa7804a350a4d9c7867119ddf07242fc24) by ryzhovalex).
- Add support for websocket path and query variables ([67f45b6](https://github.com/ryzhovalex/orwynn/commit/67f45b68ace74bdc7167cee2ed164a87888e7377) by ryzhovalex).

### Code Refactoring

- Restructure project layout ([3294d0b](https://github.com/ryzhovalex/orwynn/commit/3294d0bcd2faf0aededd86fa2fe4f7f960e11e92) by ryzhovalex).
- Move websocket handlers ([ccce226](https://github.com/ryzhovalex/orwynn/commit/ccce22649d21a92cc3da94202dd11344673c5ba1) by ryzhovalex).

## [1.0.0a2](https://github.com/ryzhovalex/orwynn/releases/tag/1.0.0a2) - 2023-02-21

<small>[Compare with 1.0.0a1](https://github.com/ryzhovalex/orwynn/compare/1.0.0a1...1.0.0a2)</small>

### Code Refactoring

- Unpack shared module ([98a2ef1](https://github.com/ryzhovalex/orwynn/commit/98a2ef1f81035c42fa9250b381ed94ad00d6059f) by ryzhovalex).

## [1.0.0a1](https://github.com/ryzhovalex/orwynn/releases/tag/1.0.0a1) - 2023-02-21

<small>[Compare with 1.0.0a0](https://github.com/ryzhovalex/orwynn/compare/1.0.0a0...1.0.0a1)</small>

## [1.0.0a0](https://github.com/ryzhovalex/orwynn/releases/tag/1.0.0a0) - 2023-02-21

<small>[Compare with 0.3.7](https://github.com/ryzhovalex/orwynn/compare/0.3.7...1.0.0a0)</small>

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

- Add src subfolder ([9fffc4d](https://github.com/ryzhovalex/orwynn/commit/9fffc4d131b54e8d72c24ddc3bf2af85f6f38e9e) by ryzhovalex).
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

