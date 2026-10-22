> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/guides/charts-and-structured-content.md).

# Add charts and structured content

How to get the best chart, table, and structured visual results from the Gamma API.

The Gamma API can generate charts, tables, and infographics as part of your output. Generation is non-deterministic — results may vary across runs, even with identical inputs. There are no API parameters to directly control chart type, styling, or data formatting, but you can steer the output through your prompts.

### Quick reference

* Charts are prompted through `inputText` and `additionalInstructions`, not through dedicated API parameters.
* Provide explicit data values and chart type for best results.
* Use the Create from Template API for consistent chart layouts across repeated generations.
* Output varies between runs -- test a few generations to calibrate your prompts.

### How to prompt for charts

You influence chart output through `inputText` and `additionalInstructions`. The more specific you are, the better the results.

{% tabs %}
{% tab title="Vague (less predictable)" %}

```json
{
  "inputText": "Revenue data for 2024",
  "additionalInstructions": "Include a chart"
}
```

{% endtab %}

{% tab title="Specific (more predictable)" %}

```json
{
  "inputText": "Revenue by quarter:\nQ1: $1.2M\nQ2: $1.5M\nQ3: $1.8M\nQ4: $2.1M",
  "additionalInstructions": "Display this data as a bar chart with quarters on the x-axis and revenue on the y-axis"
}
```

{% endtab %}
{% endtabs %}

### Tips for better results

* **Specify the chart type.** "Bar chart comparing X and Y" produces more predictable output than "include a chart."
* **Provide structured data.** Explicit values (tables, bullet points with numbers) give the AI clear data to work with.
* **Use `additionalInstructions`** to reinforce preferences: "Use bar charts for comparisons, pie charts for proportions."
* **Keep data labels unambiguous.** Labels that resemble numeric values (e.g. `$100` as a category name) may be interpreted as data.
* **Test a few runs.** Since output varies, run a few generations to see the range and refine your prompts accordingly.

### Using templates for more consistent output

If you need predictable chart layouts, the [Create from Template API](/guides/create-from-template-api-parameters-explained.md) is a better fit. Design a gamma in the app with the exact chart types and layouts you want, then use the API to generate new content into that structure.

### Tables and infographics

The same prompting principles apply:

* Provide structured data (rows, columns, key-value pairs) in your input for best table results
* Infographics such as timelines and process flows can be prompted for, but the AI determines the final layout
* Your theme controls styling for all structured content

### Related

* [Generate from text](/guides/generate-api-parameters-explained.md) for `inputText` and `additionalInstructions` usage
* [Generate from template](/guides/create-from-template-api-parameters-explained.md) for consistent chart layouts
* [Image URL best practices](/guides/image-url-best-practices.md) if you want to include your own chart images


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/guides/charts-and-structured-content.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
