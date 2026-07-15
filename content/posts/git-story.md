---
title: About my approach to git and how I squeeze more out of it compared to most of the teams.
date: 2026-07-15
excerpt: Oh, they're using a different Git-UI, looks confusing, where's the cherry-pick?. Somewhere along the line I got tired of all the "git friction" and actually learned it. Best few hours spent.
---

## About my approach to git and how I squeeze more out of it compared to most of the teams.

![I git you a story to tell](/assets/git-story/git-story.png)

***Oh, they're using a different Git-UI, looks confusing, where's the cherry-pick?***

I git you a story to tell.
Somewhere along the line I got tired of all the "git friction" and actually learned it. Best few hours spent, the only thing more valuable was working a month as a waiter (gives you so much practical skills and perspective on life). Felt like a wizard for a while - I demystified how a whole industry-standard tool works. So much power in my hands now. Right away I made myself a flow which was centered around making each commit an independent, self-sustained unit of logical changes. That means no "quick fix", no "update previous logic", no "dependencies update" after the code is already added in previous commit.

Why?
Because it makes PR so much easier: instead of +512/-137 you'll be looking at +12/-3 * 10 times.
Because it makes reverse engineering with "git blame" so much easier to investigate (mind yourself - it's like 80% of your coding day-to-day).
Because it makes your git history your documentation index. Literally.

But you know what the reality was? Take a wild guess.
It is nearly impossible to implement into day-to-day workflow of a team. Damn, a lot of teams still struggle with PR-reviews in general - they will literally train and implement a dedicated AI agent instead and justify "smashing that LGTM button". Let alone refusing a PR 'cause "The commits are out of structure". And of course - if such approach is not implemented by every commiting engineer, then it kinda loses its point.

So where I am now?
I still prefer to keep the commits atomic. I let my peers know that they can assess each step individually instead of grasping the whole mass of changes at once. I just don't expect the same from them anymore. And I stopped abusing the interactive rebase.
I still use git entirely from the console wherever I work, with zero dependencies on GUI tools. Besides - having that extra terminal window open where I'm actively typing is practical aura-farming.

Win-win in the end.
