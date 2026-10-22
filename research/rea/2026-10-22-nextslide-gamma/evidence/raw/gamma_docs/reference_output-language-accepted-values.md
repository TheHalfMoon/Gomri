> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/reference/output-language-accepted-values.md).

# Output languages

Specify the output language of your gamma.

You can create gammas in different languages. To specify the output language of your gamma, use the appropriate string in the `textOptions.language` parameter. If nothing is specified in this parameter, Gamma creates your output in `en`, ie English (US).

### Quick reference

* Set `textOptions.language` to one of the keys below.
* Each generation request produces output in a single language.
* If you need multiple language variants, make separate generation requests.

| Language                | Key      |
| ----------------------- | -------- |
| Afrikaans               | `af`     |
| Albanian                | `sq`     |
| Arabic                  | `ar`     |
| Arabic (Saudi Arabia)   | `ar-sa`  |
| Bengali                 | `bn`     |
| Bosnian                 | `bs`     |
| Bulgarian               | `bg`     |
| Catalan                 | `ca`     |
| Croatian                | `hr`     |
| Czech                   | `cs`     |
| Danish                  | `da`     |
| Dutch                   | `nl`     |
| English (India)         | `en-in`  |
| English (UK)            | `en-gb`  |
| English (US)            | `en`     |
| Estonian                | `et`     |
| Finnish                 | `fi`     |
| French                  | `fr`     |
| German                  | `de`     |
| Greek                   | `el`     |
| Gujarati                | `gu`     |
| Hausa                   | `ha`     |
| Hebrew                  | `he`     |
| Hindi                   | `hi`     |
| Hungarian               | `hu`     |
| Icelandic               | `is`     |
| Indonesian              | `id`     |
| Italian                 | `it`     |
| Japanese (です/ます style)  | `ja`     |
| Japanese (だ/である style)  | `ja-da`  |
| Kannada                 | `kn`     |
| Kazakh                  | `kk`     |
| Korean                  | `ko`     |
| Latvian                 | `lv`     |
| Lithuanian              | `lt`     |
| Macedonian              | `mk`     |
| Malay                   | `ms`     |
| Malayalam               | `ml`     |
| Marathi                 | `mr`     |
| Norwegian               | `nb`     |
| Persian                 | `fa`     |
| Polish                  | `pl`     |
| Portuguese (Brazil)     | `pt-br`  |
| Portuguese (Portugal)   | `pt-pt`  |
| Romanian                | `ro`     |
| Russian                 | `ru`     |
| Serbian                 | `sr`     |
| Simplified Chinese      | `zh-cn`  |
| Slovenian               | `sl`     |
| Spanish                 | `es`     |
| Spanish (Latin America) | `es-419` |
| Spanish (Mexico)        | `es-mx`  |
| Spanish (Spain)         | `es-es`  |
| Swahili                 | `sw`     |
| Swedish                 | `sv`     |
| Tagalog                 | `tl`     |
| Tamil                   | `ta`     |
| Telugu                  | `te`     |
| Thai                    | `th`     |
| Traditional Chinese     | `zh-tw`  |
| Turkish                 | `tr`     |
| Ukrainian               | `uk`     |
| Urdu                    | `ur`     |
| Uzbek                   | `uz`     |
| Vietnamese              | `vi`     |
| Welsh                   | `cy`     |
| Yoruba                  | `yo`     |

### Related

* [Generate from text](/guides/generate-api-parameters-explained.md) for where `textOptions.language` fits into the full request
* [Create from template](/guides/create-from-template-api-parameters-explained.md) if you want to reuse a layout in multiple languages


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/reference/output-language-accepted-values.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
