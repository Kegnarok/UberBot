from policy import *
# TODO: Implement online exploration with fixed depth (exact computation)


class Qstar(Botnet):
    """
    This class performs the computation of the Q* function.
    """

    def __init__(self, network, gamma):

        Botnet.__init__(self, network, gamma)

        self.q_value = dict()                     # Maps (state, action) to its Q*-value
        self.best_value = dict()                  # Maps a state s to max_a Q*(s,a)
        self.best_actions = dict()                # Maps a state to its best actions

        self.type = "Qstar"

        # Initialization for the full state (infinite horizon)
        self.best_value[State.full_state(network.size)] = self.network.total_power() / (1. - self.gamma)

    def compute_q_value(self, state, action):
        """
        Returns the q_value of (state, action), computing it if needed.
        The result may be smaller than its real exact value if it isn't the maximum.
        :param state:  a not full state
        :param action: a legal action (not already hijacked)
        :return:       Q*(state, action)
        """
        try:
            return self.q_value[state, action]
        except KeyError:
            reward_imm = self.network.immediate_reward(state, action)

            next_state = State.added(state, action)
            success_proba = self.network.success_probability(action, state)

            max_q = self.compute_best_value(next_state)

            value = (reward_imm + self.gamma * success_proba * max_q) / float(1 - self.gamma * (1 - success_proba))

            self.q_value[state, action] = value
            return value

    def compute_best_value(self, state):
        """
        Updates best_value[state] and best_actions[state] 
        :param state: a state (which may be full)
        :return:      max_a Q*(state,a)
        """
        try:
            return self.best_value[state]
        except KeyError:
            # Here the state is not full thanks to initialization
            best_q = -float("inf")
            best_actions = []

            for action in self.network.get_actions(state):
                # assert action not in state

                q = self.compute_q_value(state, action)

                if q > best_q:
                    best_q = q
                    best_actions = [action]
                elif q == best_q:
                    best_actions.append(action)

            self.best_value[state] = best_q
            self.best_actions[state] = best_actions
            return best_q

    def compute_best_action(self, state):
        """
        Returns the (an) optimal action to take in state 
        :param state: a non-full state
        :return:      the action
        """
        self.compute_best_value(state)      # Ensures the value has been computed
        return self.best_actions[state][0]

    def compute_policy(self):
        """
        Computes the optimal policy from self.best_actions
        :return: the policy
        """
        return make_policy(self.compute_best_action, self.network)

    # def clear(self):
    #     """
    #     Clears internal storage of Q*
    #     :return:
    #     """
    #     self.reset()
    #     self.content = dict()
    #     self.best_actions = dict()
    #
    # def choose_action(self, tot_nb_invasions=1, cur_nb_invasions=1):
    #     """
    #     Useless, wrapper for ex_policy to conform to the Qlearning interface
    #     :param tot_nb_invasions:
    #     :param cur_nb_invasions:
    #     :return:
    #     """
    #     return self.compute_best_action(self.state)
