# SWE-agent Task-Local Procedural Slice

4. Localize code with LM-friendly search and navigation commands such as find_file, search_file, and search_dir: ... an issue. We introduce the special commands find_file, search_file, and search_dir, which output a summary of search results when searching for filenames and strings within files .... Source anchors: lines 178-182.

5. Inspect code through the file viewer with bounded windows, line numbers, scrolling, and goto: ... that the agent write a more specific query. File viewer. After finding a file they want to view, agents use the interactive file viewer by calling the command open on the .... Source anchors: lines 235-239.

6. Apply focused multiline edits through the edit command and immediately inspect the updated file view: ... with the file viewer, allowing agents to replace a specific range of lines in the open file. This command takes 3 required arguments: the start line, end line, and replacement .... Source anchors: lines 244-248.

7. Use editing guardrails such as linting feedback and discarded invalid edits to avoid error propagation: ... files in an IDE, we integrate a code linter into the edit function to alert the agent of mistakes it may have introduced when editing a file. Select errors from the linter .... Source anchors: lines 250-254.

- Report % Resolved or pass@1, average cost, and the per-instance budget boundary: ... after interaction. Metrics. We report % Resolved or pass@1 as the main metric, which is the proportion of instances for which all tests pass successfully after the model .... Source anchors: lines 294-298.
