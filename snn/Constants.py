class Constants:
    def __init__(self):
        self.rootDir = ""
        self.outputDir = ""
        self.saveVideo = False
        self.learning = False

        self.coordinated_run = False

        self.ll_reward = 0
        self.lr_reward = 0
        self.rl_reward = 0
        self.rr_reward = 0
        self.ll_reward_avg = 0
        self.lr_reward_avg = 0
        self.rl_reward_avg = 0
        self.rr_reward_avg = 0
        self.ll_reward_signal = 0
        self.lr_reward_signal = 0
        self.rl_reward_signal = 0
        self.rr_reward_signal = 0

        self.u_reward = 0
        self.d_reward = 0
        self.u_reward_avg = 0
        self.d_reward_avg = 0
        self.u_reward_signal = 0
        self.d_reward_signal = 0

        self.learning_window = 21
        self.learning_rate = 0.25
        self.window_size = self.learning_window

    instance_ = None

    @classmethod
    def instance(cls):
        if not cls.instance_:
            cls.instance_ = Constants()
        return cls.instance_
