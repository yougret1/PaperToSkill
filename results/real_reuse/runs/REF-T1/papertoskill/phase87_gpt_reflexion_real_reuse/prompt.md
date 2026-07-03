# Real-Reuse Condition: papertoskill

You are running a locked PaperToSkill real-reuse task. Use only the model-visible context and task prompt below.

# Condition Context

---
name: reflexion-paper-skill
description: Use when applying the paper-derived method from Reflexion Language Agents with Verbal Reinforcement Learning as an agent skill. Extracts workflow steps, assumptions, validation checks, failure cases, and transfer notes.
---

# Reflexion: Language Agents with Verbal Reinforcement Learning

This skill converts the source paper's operational contribution into an agent
workflow. It is a scaffolded extraction and should be audited against the source
before being used as validated paper knowledge.

## Source

- Source file: `papers/notes/reflexion_note.md`

## Paper Snapshot

Reflexion is a framework for teaching language agents through verbal reinforcement
instead of weight updates. The agent reflects on feedback, stores reflective text in
episodic memory, and uses that memory to improve later attempts. The paper evaluates the
approach on decision-making, reasoning, and programming tasks and reports large gains
over strong baselines. Source anchors: extracted text lines 25-42.

## Central Contribution

Reflexion is a framework for teaching language agents through verbal reinforcement
instead of weight updates.

## Inputs

- The source paper or paper excerpt.
- The target task where the paper's method should be reused.
- Available tools, runtime constraints, and output format expectations.

## Workflow

1. Use an Actor, Evaluator, and Self-Reflection model rather than weight updates. Source anchors: lines 189-193.
2. Turn feedback into verbal self-reflections and store them in memory for later trials. Source anchors: lines 201-217, 244-255, 257-266.
3. Treat short-term memory as trajectory history and long-term memory as accumulated self-reflections. Source anchors: lines 257-266.
4. Iterate trials until the evaluator marks the trajectory correct, while the actor conditions future actions on the memory buffer. Source anchors: lines 269-276.
5. Support multiple feedback sources, including environment feedback, heuristics, self-generated unit tests, and evaluator scoring. Source anchors: lines 69-75, 232-247.

## Validation

- Decision-making on ALFWorld, with Reflexion improving by 22% absolute over strong baselines in 12 iterative steps. Source anchors: lines 84-91, 289-318.
- Reasoning on HotPotQA, with Reflexion improving by 20%. Source anchors: lines 84-91, 362-378, 390-426.
- Programming on HumanEval, MBPP, Rust translation, and LeetcodeHardGym, with HumanEval Python pass@1 reported at 91%. Source anchors: lines 84-91, 430-505.

## Failure Cases

- Reflexion can still get stuck in local minima and has no formal guarantee of success. Source anchors: lines 76-83, 527-533.
- The memory component is limited to a sliding window in the paper, and the authors suggest more advanced structures for future work. Source anchors: lines 527-533.
- Some environments and tasks remain difficult, especially where very creative behavior or richer interaction is required. Source anchors: lines 741-776.

## Transfer Notes

- Check whether the target harness supports the tools assumed by the paper.
- Replace framework-specific commands with local equivalents before execution.
- Keep source-backed steps separate from inferred adaptations.
- Record any failed branch as part of the skill's future revision history.

# Locked Task Prompt

# REF-T1 Locked Task Prompt

Use the provided HotPotQA-style distractor context to answer the question.
Follow a Reflexion-style retry loop: make an attempt, read objective feedback,
write a short reflection grounded in that feedback, and produce a final answer.

Question: Were Scott Derrickson and Ed Wood of the same nationality?

Context:
- Ed Wood (film): Ed Wood is a 1994 American biographical period comedy-drama film directed and produced by Tim Burton, and starring Johnny Depp as cult filmmaker Ed Wood. The film concerns the period in Wood's life when he made his best-known films as well as his relationship with actor Bela Lugosi, played by Martin Landau. Sarah Jessica Parker, Patricia Arquette, Jeffrey Jones, Lisa Marie, and Bill Murray are among the supporting cast.
- Scott Derrickson: Scott Derrickson (born July 16, 1966) is an American director, screenwriter and producer. He lives in Los Angeles, California. He is best known for directing horror films such as "Sinister", "The Exorcism of Emily Rose", and "Deliver Us From Evil", as well as the 2016 Marvel Cinematic Universe installment, "Doctor Strange."
- Woodson, Arkansas: Woodson is a census-designated place (CDP) in Pulaski County, Arkansas, in the United States. Its population was 403 at the 2010 census. It is part of the Little Rock-North Little Rock-Conway Metropolitan Statistical Area. Woodson and its accompanying Woodson Lake and Wood Hollow are the namesake for Ed Wood Sr., a prominent plantation owner, trader, and businessman at the turn of the 20th century. Woodson is adjacent to the Wood Plantation, the largest of the plantations own by Ed Wood Sr.
- Tyler Bates: Tyler Bates (born June 5, 1965) is an American musician, music producer, and composer for films, television, and video games. Much of his work is in the action and horror film genres, with films like "Dawn of the Dead, 300, Sucker Punch," and "John Wick." He has collaborated with directors like Zack Snyder, Rob Zombie, Neil Marshall, William Friedkin, Scott Derrickson, and James Gunn. With Gunn, he has scored every one of the director's films; including "Guardians of the Galaxy", which became one of the highest grossing domestic movies of 2014, and its 2017 sequel. In addition, he is also the lead guitarist of the American rock band Marilyn Manson, and produced its albums "The Pale Emperor" and "Heaven Upside Down".
- Ed Wood: Edward Davis Wood Jr. (October 10, 1924 - December 10, 1978) was an American filmmaker, actor, writer, producer, and director.
- Deliver Us from Evil (2014 film): Deliver Us from Evil is a 2014 American supernatural horror film directed by Scott Derrickson and produced by Jerry Bruckheimer. The film is officially based on a 2001 non-fiction book entitled "Beware the Night" by Ralph Sarchie and Lisa Collier Cool, and its marketing campaign highlighted that it was "inspired by actual accounts". The film stars Eric Bana, Edgar Ramirez, Sean Harris, Olivia Munn, and Joel McHale in the main roles and was released on July 2, 2014.
- Adam Collis: Adam Collis is an American filmmaker and actor. He attended the Duke University from 1986 to 1990 and the University of California, Los Angeles from 2007 to 2010. He also studied cinema at the University of Southern California from 1991 to 1997. Collis first work was the assistant director for the Scott Derrickson's short "Love in the Ruins" (1995). In 1998, he played "Crankshaft" in Eric Koyanagi's "Hundred Percent".
- Sinister (film): Sinister is a 2012 supernatural horror film directed by Scott Derrickson and written by Derrickson and C. Robert Cargill. It stars Ethan Hawke as fictional true-crime writer Ellison Oswalt who discovers a box of home movies in his attic that puts his family in danger.
- Conrad Brooks: Conrad Brooks (born Conrad Biedrzycki on January 3, 1931 in Baltimore, Maryland) is an American actor. He moved to Hollywood, California in 1948 to pursue a career in acting. He got his start in movies appearing in Ed Wood films such as "Plan 9 from Outer Space", "Glen or Glenda", and "Jail Bait." He took a break from acting during the 1960s and 1970s but due to the ongoing interest in the films of Ed Wood, he reemerged in the 1980s and has become a prolific actor. He also has since gone on to write, produce and direct several films.
- Doctor Strange (2016 film): Doctor Strange is a 2016 American superhero film based on the Marvel Comics character of the same name, produced by Marvel Studios and distributed by Walt Disney Studios Motion Pictures. It is the fourteenth film of the Marvel Cinematic Universe (MCU). The film was directed by Scott Derrickson, who wrote it with Jon Spaihts and C. Robert Cargill, and stars Benedict Cumberbatch as Stephen Strange, along with Chiwetel Ejiofor, Rachel McAdams, Benedict Wong, Michael Stuhlbarg, Benjamin Bratt, Scott Adkins, Mads Mikkelsen, and Tilda Swinton. In "Doctor Strange", surgeon Strange learns the mystic arts after a career-ending car accident.

Required output JSON fields:
- `first_attempt`
- `reflection`
- `final_answer`

The answer key is hidden from the model and is used only by the scorer.

# Output Contract

Return only JSON with keys `first_attempt`, `reflection`, and `final_answer`. Do not mention hidden answer keys.
