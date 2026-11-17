# Narration script

**The Working Copy — The harness is not the model**

Narrated by Uncle Burt. Measured duration 7:01 (421.39 seconds). Generated 2026-11-17 with the local Voicebox service.

The written article is authoritative. This is the companion spoken edition.

---

You are listening to The Working Copy, a developer publication from Legacy AI. Ideas you can run.

This is the first edition. Our subject is the layer between your editor and your model provider: the harness.

A recent Visual Studio Code change gives us a good reason to look at it. GitHub has announced that the older Local harness will be retired in February of next year, and that session coordination will move to the newer Copilot harness. If you use Visual Studio Code, Cursor, VSCodium, or another editor with a coding agent, that announcement sounds like a simple version update. It is not. It points at a layer most of us never inspect.

A coding session feels like one thing. You type into an editor, you ask a question, and a model answers. But three layers are involved. The editor is where you type, and where extensions run. The harness decides how the agent session is coordinated, which tools it can use, and what permissions apply. The model provider decides which model answers, and through which endpoint. Those layers can change independently, and that is the trap. A model that still answers through a different endpoint does not prove that your harness still starts the way you expect.

Think about a session that looks healthy. The editor opens, the chat panel responds, and the model answers. You ask the agent to inspect a file. It does. Nothing looks wrong. But the harness may be starting from an older preference, or a profile you forgot about, or an extension that has not been updated. The model is doing its job, so the session feels correct. The layer that decides how the work is coordinated is invisible until it changes.

That is why the first useful move is not to upgrade anything. It is to look. We are going to run a small, read-only audit. It reads your editor settings and reports only the keys related to the harness or the session target. It does not print your whole settings file, and it does not change anything. The goal is a short, factual answer to a simple question: which harness is this editor actually using?

The audit checks the common settings locations for Visual Studio Code, Visual Studio Code Insiders, Cursor, and VSCodium. It handles the different locations used by Mac, Linux, and Windows. It searches for key names containing harness or session target. When it finds one, it prints the key and its value. When it finds nothing, it says so. It never prints your credentials. It never uploads anything. It is a local read.

Run it with the Python that is already on your machine. There are no packages to install. Open the full example, save it, and run it. Or copy the shorter version from the article and run that. The result is a short report: a settings path, and either a list of harness-related keys or a line saying no harness-related keys were found.

Three outcomes matter. First, no keys. That means your settings do not override the default harness. It is not proof that you are on a supported path. Check your editor and extension versions, because the default can change with an update. Second, an explicit Local harness setting. You may see a setting whose name refers to a local harness, or a session target set to local. That is the case to put on a calendar. It is an explicit preference, and the retirement date applies to it. Third, an endpoint or base address. That belongs to the provider layer. It tells you where the model comes from. It does not tell you which harness is coordinating the session. Keep those two findings separate.

If you find a Local harness preference, do not migrate just because the date exists. Update the editor or the extension first. Then check whether the harness default changed on its own. Keep the provider configuration separate from the harness setting. Verify a real session with tool calls and permissions, not only a chat reply. Keep a rollback note with the previous setting and the date. Four small checks, and you have a change you can defend.

Here is the ten-minute version you can try today. Run the audit. Write down the three outcomes in a note. If you see an explicit Local harness setting, record the editor version and the date. If you see an endpoint, label it as the provider layer and leave it alone for now. Then copy the agent prompt from the article. Open the coding agent you already use. Ask it to inspect your setup and produce the short report. Do not ask it to change anything yet. You are asking it to look, explain, and recommend. That is the useful first step, and it is small enough to finish before your coffee gets cold.

Now, the part that makes this reusable. A snippet can tell you what your settings contain. It cannot see your extensions, your profiles, or the provider configuration that lives outside the editor. Your coding agent can. The article includes a prompt you can copy into the agent you already use. It tells the agent to inspect first, to find the editor, the extensions, the harness settings, and the provider, and to explain which layer each finding belongs to. It tells the agent not to print keys, tokens, or credential-bearing addresses. It tells the agent to propose the smallest migration, list the exact files and commands, and wait for your approval before editing. And it asks for a short report: current state, risk, recommended change, verification step, and what could not be verified.

A useful agent prompt has five parts. It names the scope. It requires evidence. It separates the layers. It sets an approval boundary. And it asks for a verification step. The prompt in the article is written that way. You can replace the example with your own environment, but keep those five parts. That is what turns a generic instruction into something your agent can actually do on your machine, with your editor, your extensions, and your provider.

That prompt is the difference between a one-time audit and a repeatable practice. The audit gives you facts. The agent turns the facts into a plan for your setup. You stay in control of the change. This is the part readers can take with them: not a fixed answer for one machine, but a way to ask their own agent the right question about their own environment.

A few cautions. First, do not hand your agent a prompt that says fix this without a boundary. Read-only first, approval before edits. Second, do not treat a working model as proof that the harness is healthy. The layers are independent. Check them independently. Third, do not assume a settings path is the whole configuration. Extensions, profiles, and portable installs can keep their own state. The agent prompt is written to look for those, and the audit itself is honest about what it does not cover.

Finally, repeat the audit after an editor update. The default can change without a setting changing on your machine. A short read before and after the update is more useful than a long investigation after something breaks. Keep the report with the date and the versions. That is the working copy: a note about the system as it actually is, not as we assumed it was.

The Working Copy is a developer publication from Legacy AI. The written article is authoritative. This spoken edition is a companion. If you want the audit script, the agent prompt, or the source links, they are on the page. Ideas you can run.
