


# TODO(ryzhovalex): in development
# 0
# @pytest.mark.parametrize(
#     "raw,expected",
#     [
#         (
#             "http://github.com",
#             Address(
#                 host="github.com",
#                 top_domain="com",
#                 second_domain="github",
#                 scheme=Scheme.HTTP
#             )
#         ),

#         (
#             "https://github.com/ryzhovalex/staze/blob/master/staze/core/cli/cli.py#L67",
#             Address(
#                 host="github.com",
#                 top_domain="com",
#                 second_domain="github",
#                 scheme=Scheme.HTTPS,
#             )
#         ),

#         (
#             "stackoverflow.com/questions/39625696/regex-url-capturing-group?hello=1&ids=22",
#             Address()
#         ),

#         (
#             "https://jsc-rpe-almaz.kaiten.ru/space/505050",
#             Address()
#         ),

#         (
#             "10.2.16.4:5000/hello",
#             Address()
#         ),
#     ]
# )
# def test_parse(raw: str, expected: Address):
#     pass
