# Generic Summary: Reflexion

Reflexion is a framework for improving language agents through verbal
reinforcement instead of updating model weights. It lets an agent reflect on
feedback from failed attempts, store lessons in memory, and use those lessons in
later trials.

The paper describes an actor that performs actions, an evaluator that scores
outcomes, and a self-reflection model that converts feedback into natural
language advice. The approach is tested on decision-making, reasoning, and
programming tasks, where it improves over several baselines.

The paper also notes limitations: agents can still get stuck, memory is bounded
by a simple window, and some tasks require more creative behavior than the
method reliably discovers.

