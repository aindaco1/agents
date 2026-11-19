---
name: interface-interaction-review
description: Use when choosing how an interface control should behave.
metadata:
  version: 1.0.0
  author: Dust Wave
  hermes:
    tags: [interface-design, interaction-design, prototyping]
    related_skills: [show-me]
---

# Interface interaction review

Resolve a question someone could encounter while using the product. “What happens to my edit if I close this panel while it saves?” gives a reviewer more to work with than “review the panel.” Start with the user's task, the current behavior if known, and any product or platform decision already made.

1. **Compare plausible behaviors.** Walk through the same action with the same content in each alternative. Describe what the person sees, what happens to their work, and what they can do next. If the behavior is already fixed, review where it breaks and how to preserve it.
2. **Change one condition that could change the choice.** Try the action while an operation is pending, with a different input method, or after focus moves. Choose a condition that matters to this control. Identify where an option hides an action, loses work, or makes an unexpected commitment.
3. **Decide at the level of the control.** Give the deciding reason. Specify the trigger, the resulting state and feedback, and any recovery or focus behavior the user needs. If the choice depends on an unknown product capability or user expectation, name it and say how to resolve it.
4. **Hand off one replayable acceptance check.** Give the starting state, user action, and observable result that distinguishes the choice from its nearest alternative. If you exercised the sequence, record what you observed and on which surface. Label an unrun check as proposed.

A short review can fit in a paragraph or table. Yuki can use it to specify behavior across states and input methods. Mansur can use it to prototype the sequence that would settle an open question. Either can complete a review independently.

For an example of the same method applied to attachment removal, text composition, and overlapping requests, read the [Composer worked example](references/composer.md).
