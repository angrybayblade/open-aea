# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This package contains a the behaviours."""

import datetime
from typing import Optional, cast

from aea.helpers.search.models import Description
from aea.skills.base import Behaviour

from packages.fetchai.protocols.oef_search.message import OefSearchMessage
from packages.fetchai.protocols.tac.message import TacMessage
from packages.fetchai.skills.tac_control.dialogues import (
    OefSearchDialogues,
    TacDialogues,
)
from packages.fetchai.skills.tac_control.game import Game, Phase
from packages.fetchai.skills.tac_control.parameters import Parameters


class TacBehaviour(Behaviour):
    """This class implements the TAC control behaviour."""

    def __init__(self, **kwargs):
        """Instantiate the behaviour."""
        super().__init__(**kwargs)
        self._registered_description = None  # type: Optional[Description]

    def setup(self) -> None:
        """
        Implement the setup.

        :return: None
        """
        pass

    def act(self) -> None:
        """
        Implement the act.

        :return: None
        """
        game = cast(Game, self.context.game)
        parameters = cast(Parameters, self.context.parameters)
        now = datetime.datetime.now()
        if (
            game.phase.value == Phase.PRE_GAME.value
            and parameters.registration_start_time < now < parameters.start_time
        ):
            game.phase = Phase.GAME_REGISTRATION
            self._register_tac()
            self.context.logger.info(
                "[{}]: TAC open for registration until: {}".format(
                    self.context.agent_name, parameters.start_time
                )
            )
        elif (
            game.phase.value == Phase.GAME_REGISTRATION.value
            and parameters.start_time < now < parameters.end_time
        ):
            if game.registration.nb_agents < parameters.min_nb_agents:
                self._cancel_tac(game)
                game.phase = Phase.POST_GAME
                self._unregister_tac()
            else:
                game.phase = Phase.GAME_SETUP
                self._start_tac(game)
                self._unregister_tac()
                game.phase = Phase.GAME
        elif game.phase.value == Phase.GAME.value and now > parameters.end_time:
            self._cancel_tac(game)
            game.phase = Phase.POST_GAME

    def teardown(self) -> None:
        """
        Implement the task teardown.

        :return: None
        """
        if self._registered_description is not None:
            self._unregister_tac()

    def _register_tac(self) -> None:
        """
        Register on the OEF as a TAC controller agent.

        :return: None.
        """
        game = cast(Game, self.context.game)
        self._registered_description = game.get_tac_description()
        oef_search_dialogues = cast(
            OefSearchDialogues, self.context.oef_search_dialogues
        )
        oef_search_msg = OefSearchMessage(
            performative=OefSearchMessage.Performative.REGISTER_SERVICE,
            dialogue_reference=oef_search_dialogues.new_self_initiated_dialogue_reference(),
            service_description=self._registered_description,
        )
        oef_search_msg.counterparty = self.context.search_service_address
        oef_search_dialogues.update(oef_search_msg)
        self.context.outbox.put_message(message=oef_search_msg)
        self.context.logger.info(
            "[{}]: Registering TAC data model".format(self.context.agent_name)
        )

    def _unregister_tac(self) -> None:
        """
        Unregister from the OEF as a TAC controller agent.

        :return: None.
        """
        if self._registered_description is not None:
            oef_search_dialogues = cast(
                OefSearchDialogues, self.context.oef_search_dialogues
            )
            oef_search_msg = OefSearchMessage(
                performative=OefSearchMessage.Performative.UNREGISTER_SERVICE,
                dialogue_reference=oef_search_dialogues.new_self_initiated_dialogue_reference(),
                service_description=self._registered_description,
            )
            oef_search_msg.counterparty = self.context.search_service_address
            oef_search_dialogues.update(oef_search_msg)
            self.context.outbox.put_message(message=oef_search_msg)
            self._registered_description = None
            self.context.logger.info(
                "[{}]: Unregistering TAC data model".format(self.context.agent_name)
            )

    def _start_tac(self, game: Game):
        """Create a game and send the game configuration to every registered agent."""
        game.create()
        self.context.logger.info(
            "[{}]: Started competition:\n{}".format(
                self.context.agent_name, game.holdings_summary
            )
        )
        self.context.logger.info(
            "[{}]: Computed equilibrium:\n{}".format(
                self.context.agent_name, game.equilibrium_summary
            )
        )
        tac_dialogues = cast(TacDialogues, self.context.tac_dialogues)
        for agent_address in game.conf.agent_addr_to_name.keys():
            agent_state = game.current_agent_states[agent_address]
            tac_msg = TacMessage(
                performative=TacMessage.Performative.GAME_DATA,
                dialogue_reference=tac_dialogues.new_self_initiated_dialogue_reference(),  # TODO: continue correct dialogue
                amount_by_currency_id=agent_state.amount_by_currency_id,
                exchange_params_by_currency_id=agent_state.exchange_params_by_currency_id,
                quantities_by_good_id=agent_state.quantities_by_good_id,
                utility_params_by_good_id=agent_state.utility_params_by_good_id,
                tx_fee=game.conf.tx_fee,
                currency_id_to_name=game.conf.currency_id_to_name,
                agent_addr_to_name=game.conf.agent_addr_to_name,
                good_id_to_name=game.conf.good_id_to_name,
                version_id=game.conf.version_id,
            )
            tac_msg.counterparty = agent_address
            tac_dialogues.update(tac_msg)
            self.context.outbox.put_message(message=tac_msg)
            self.context.logger.debug(
                "[{}]: sending game data to '{}': {}".format(
                    self.context.agent_name, agent_address, str(tac_msg)
                )
            )

    def _cancel_tac(self, game: Game):
        """Notify agents that the TAC is cancelled."""
        self.context.logger.info(
            "[{}]: Notifying agents that TAC is cancelled.".format(
                self.context.agent_name
            )
        )
        tac_dialogues = cast(TacDialogues, self.context.tac_dialogues)
        for agent_addr in game.registration.agent_addr_to_name.keys():
            tac_msg = TacMessage(
                performative=TacMessage.Performative.CANCELLED,
                dialogue_reference=tac_dialogues.new_self_initiated_dialogue_reference(),  # TODO: continue correct dialogue
            )
            tac_msg.counterparty = agent_addr
            tac_dialogues.update(tac_msg)
            self.context.outbox.put_message(message=tac_msg)
        if game.phase == Phase.GAME:
            self.context.logger.info(
                "[{}]: Finished competition:\n{}".format(
                    self.context.agent_name, game.holdings_summary
                )
            )
            self.context.logger.info(
                "[{}]: Computed equilibrium:\n{}".format(
                    self.context.agent_name, game.equilibrium_summary
                )
            )
            self.context.is_active = False
