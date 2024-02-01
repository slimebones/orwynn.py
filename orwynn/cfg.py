import importlib
from typing import Any, TypeVar

from pydantic import BaseModel
from pykit.log import log
from pykit.tree import ReversedTreeNode, TreeNode, TreeUtils


class Cfg(BaseModel):
    """
    Configurational object used to pass initial arguments to the systems.
    """
    # def __eq__(self, other) -> bool:
    #     return hash(self) == hash(other)

    def __hash__(self) -> int:
        return hash(repr(self))

TCfg = TypeVar("TCfg", bound=Cfg)
CfgPack = dict[str, list[Cfg]]

class CfgPackUtils:
    # async def _merge_cfgs_for_mode_or_action(
    #     self,
    #     mode: str,
    #     pack: CfgPack,
    #     action: Callable[[Any], None]
    # ) -> set[Cfg]:
    #     """
    #     Finds cfg for mode and if the mode has parent mode, merge it
    #     into the result recursively.

    #     Calls provided action on err.
    #     """
    #     f: set[Cfg] = set()

    @classmethod
    async def init_cfg_pack(cls) -> CfgPack:
        """
        User is able to define app run modes in cfg pack, as dict keys.

        Thus cfg pack is the single-truth place where run modes can be defined
        and configured.

        Later, the run modes are chosen by passing environ ORWYNN_MODE. If
        no mode is chosen, the first available (or __default__) is picked.
        """
        pack: CfgPack

        try:
            cfg_module = importlib.import_module("orwynn_cfg")
        except ModuleNotFoundError:
            log.info("config not found => ret empty", 2)
            return {}

        try:
            pack = cfg_module.default
        except AttributeError:
            log.err(
                "orwynn_cfg.py is defined, but no 'default' object"
                " is found there => ret empty",
                1
            )
            return {}

        if (
            not isinstance(pack, dict)
        ):
            log.err(
                "orwynn_cfg.py::default is expected to be"
                f" dict, got {type(pack)} => ret empty"
            )
            return {}

        # pack keys and values will be validated at baking stage

        return pack

    @classmethod
    async def bake_cfgs(cls, mode: str, pack: CfgPack) -> set[Cfg]:
        """
        Merges an appropriate cfg collections into one.

        Cfgs in cfg pack can be denoted by mode, but inherited modes can be
        used with notation "parent->child". This method finds parent and 
        merges it into child, if the chosen mode is "child".
        """

        # cfgsf = pack.get(mode, None)
        # if cfgsf is None:
        #     log.fatal(f"cannot find cfgs for mode {mode}")

    @classmethod
    async def _bake_cfg_pack_reversed_tree(
        cls, pack: CfgPack
    ) -> list[ReversedTreeNode[tuple[str, list[Cfg]]]]:
        """
        Bakes the cfg pack tree and returns list of its leaves.
        """
        # strat: build normal tree, then reverse

        # everyone inherits from default
        root_node: TreeNode[tuple[str, list[Cfg]]] = TreeNode(
            ("__default__", []),
            []
        )
        mode_to_node: dict[str, TreeNode] = {
            "__default__": root_node
        }

        for k, v in pack.items():
            await cls._check_cfg_pack_kv_shallow(k, v)

            if "->" in k:
                parts = k.split("->")
                if len(parts) != 2:
                    log.fatal(f"invalid mode {k} composition")

                parent_mode, child_mode = parts[0], parts[1]

                # note that these checks automatically mean that you can't
                # use structures like "__default__->mymode"
                await cls._check_mode_name_or_fatal(parent_mode)
                await cls._check_mode_name_or_fatal(child_mode)
                
                child_node: TreeNode
                if child_mode in mode_to_node:
                    child_node = mode_to_node[child_mode]
                    if not child_node.childs:
                        # if a child node has been registered, it should'd been
                        # in a context of assigning it as a parent to someone,
                        # thus, it must have childs
                        log.fatal(f"duplicate mode {child_mode}")
                else:
                    child_node = TreeNode((child_mode, []), [])
                    mode_to_node[child_mode] = child_node
                # both for new or existing child node we should attach
                # cfgs, since it hasn't been done when it was a parent
                child_node.val = (child_node.val[0], v)

                # create/get parent node and assign child
                parent_node: TreeNode
                if parent_mode in mode_to_node:
                    parent_node = mode_to_node[parent_mode] 
                else:
                    parent_node = TreeNode((parent_mode, []), [])
                    mode_to_node[parent_mode] = parent_node
                parent_node.childs.append(child_node)

                continue

            if not k == "__default__":
                await cls._check_mode_name_or_fatal(k)
            node: TreeNode
            if k in mode_to_node:
                node = mode_to_node[k]
            else:
                node = TreeNode((k, v), [])
                mode_to_node[k] = node
            # reassign cfgs for backup, we're not sure it's needed
            node.val = (node.val[0], v)
            if k != "__default__":
                root_node.childs.append(node)

        return await TreeUtils.reverse(root_node)
    
    @classmethod
    async def _check_cfg_pack_kv_shallow(cls, k: Any, v: Any):
        if not isinstance(k, str):
            log.fatal(
                "cfg pack keys are expected to"
                f" be an instance of str, got {type(k)}"
            )
        if not isinstance(v, list):
            log.fatal(
                "cfg pack value collection is expected to"
                f" be an instance of list, got {type(v)}"
            )
        occured_cfg_types: list[type[Cfg]] = []
        for cfg in v:
            cfg_type = type(cfg)
            if cfg_type in occured_cfg_types:
                log.fatal(
                    f"duplicate cfg type {cfg_type} for cfg pack key {k}"
                )
            occured_cfg_types.append(cfg_type)
            if not isinstance(cfg, Cfg):
                log.fatal(
                    "cfg pack values are expected to"
                    f" be an instance of Cfg, got {type(cfg)}"
                )

    @classmethod
    async def _check_mode_name_or_fatal(
        cls,
        name: str
    ):
        if (
            not name.islower()
            or not name[0].isalpha()
        ):
            log.fatal(
                "mode name is expected to"
                " be all lowercase, alnum in hebab-case,"
                f" starting with alpha, got {name}"
            )

        for c in name:
            if not c.isalnum() and c != "-":
                log.fatal(
                    f"only dashes are allowed in mode name, got {name}"
                )
