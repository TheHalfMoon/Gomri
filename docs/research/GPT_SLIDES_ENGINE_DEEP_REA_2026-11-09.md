# GPT Slides Engine REA — 2026-11-09

Scope: Public architecture analysis of ChatGPT Slides in Space for the Gomri project. This is a behavioral study, not access to proprietary implementation.

**Core observation:** ChatGPT Slides supports editable text, images, shapes, charts and tables, targeted AI edits on selected elements, deck-wide prompts, simultaneous collaboration, comments addressed to ChatGPT, and PowerPoint/PDF/Google Slides exports.

**Architectural uncertainty:** Public sources do not identify the internal rendering framework, document schema, model/tool chain, synchronization algorithm or export engine. NextSlide joining OpenAI does not disclose code.

This report has detailed companion files and a 175-row evidence-graded capability registry.

Sources:
- https://help.openai.com/en/articles/20001605-creating-and-collaborating-on-slides-in-chatgpt
- https://chatgpt.com/features/slides/
- https://learn.chatgpt.com/docs/space/collaboration
- https://nextslide.ai/

Existing Gomri donor audit: https://github.com/TheHalfMoon/Gomri/pull/88
