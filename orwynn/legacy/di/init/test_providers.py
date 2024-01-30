

# TODO(ryzhovalex): this test strangely initializes the boot and for the
#   second time calls init_providers directly
# 0
# @pytest.mark.asyncio
# async def test_std(
#     std_struct: Module,
#     std_provider_dependencies_map: ProviderDependenciesMap
# ):
#     await Boot.create(std_struct)
#     container: DiContainer = init_providers(
#         std_provider_dependencies_map
#     )

#     for P in Assertion.COLLECTED_PROVIDERS:
#         isinstance(container.find(P.__name__), P)
