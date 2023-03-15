# IBM Confidential - OCO Source Materials
# (C) Copyright IBM Corp. 2022
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.

__author__ = "IBM"

import src.utils.definition as consts
from src.attack_orchestrator.orchestrator import AttackOrchestrator
from src.utils.config import Config
from src.utils.entities import AttackConfig
from src.utils.singleton import singleton
from src.utils.tool import create_dir, os
from src.client.factory import AttackFactoryClient


@singleton
class ServerInterface(object):
    def __init__(self, **kwargs):
        self._config: Config = kwargs.get('config', Config())
        self._factory = AttackFactoryClient()
        self._init_project()
        self._orchestrator = AttackOrchestrator(factory=self._factory)

    async def run_attack_simulation(self, attack_config: dict = None) -> dict:
        sub_techniques = attack_config.pop(consts.SIMULATOR_ADAPTER_MITRE_TECHNIQUE, "")
        tactic = attack_config.pop(consts.SIMULATOR_ADAPTER_MITRE_TACTIC, "")
        # The workout id from the manager for the current attacks
        workout_id = attack_config.get(consts.WORKOUT_PLAN_ID_TOKEN, None)

        attack_config = AttackConfig(sub_techniques, tactic, **attack_config)
        if not sub_techniques and tactic:
            return await self._orchestrator.generate_attacks_from_tactics(attack_config)

        return await self._orchestrator.generate_attack(attack_config, workout_id)

    def _init_project(self):
        store_dir_path = self._config.get(consts.SYSTEM_SECTION, consts.STORE_DIR_PATH_CONFIG_TOKEN)
        create_dir(store_dir_path)
        store_inside_dirs = self._config.get(consts.SYSTEM_SECTION, consts.STORE_DIRS_CONFIG_TOKEN).split(",")
        for dir in store_inside_dirs:
            path = os.path.join(store_dir_path, dir)
            create_dir(path)
