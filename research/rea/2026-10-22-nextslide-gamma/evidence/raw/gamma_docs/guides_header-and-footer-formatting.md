> For the complete documentation index, see [llms.txt](https://developers.gamma.app/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://developers.gamma.app/guides/header-and-footer-formatting.md).

# Format headers and footers

Detailed guide to customizing headers and footers in Gamma presentations.

Headers and footers let you add consistent branding elements, page numbers, and custom text across all cards in your presentation.

### Quick reference

| Position       | Description                       |
| -------------- | --------------------------------- |
| `topLeft`      | Top-left corner of every card     |
| `topCenter`    | Top-center of every card          |
| `topRight`     | Top-right corner of every card    |
| `bottomLeft`   | Bottom-left corner of every card  |
| `bottomCenter` | Bottom-center of every card       |
| `bottomRight`  | Bottom-right corner of every card |

| Element Type | Use Case                          |
| ------------ | --------------------------------- |
| `text`       | Company name, copyright, taglines |
| `image`      | Logo from theme or custom URL     |
| `cardNumber` | Slide/page numbers                |

### Basic structure

The `headerFooter` object goes inside `cardOptions`:

```json
{
  "cardOptions": {
    "headerFooter": {
      "topRight": {
        "type": "...",
        // type-specific properties
      },
      "bottomLeft": {
        "type": "...",
        // type-specific properties
      }
    }
  }
}
```

### Element types

#### Text elements

Add custom text like company names, copyright notices, or taglines.

```json
{
  "cardOptions": {
    "headerFooter": {
      "bottomRight": {
        "type": "text",
        "value": "© 2025 Acme Corp"
      },
      "topLeft": {
        "type": "text", 
        "value": "Confidential"
      }
    }
  }
}
```

The `value` field is required for text elements. Keep text short because headers and footers have limited space.

#### Image elements (theme logo)

Use the logo from your selected theme:

```json
{
  "cardOptions": {
    "headerFooter": {
      "topRight": {
        "type": "image",
        "source": "themeLogo",
        "size": "md"
      }
    }
  }
}
```

| Size | Description                       |
| ---- | --------------------------------- |
| `sm` | Small logo (subtle branding)      |
| `md` | Medium logo (default, balanced)   |
| `lg` | Large logo (prominent)            |
| `xl` | Extra large logo (very prominent) |

#### Image elements (custom URL)

Use your own logo image:

```json
{
  "cardOptions": {
    "headerFooter": {
      "topRight": {
        "type": "image",
        "source": "custom",
        "src": "https://example.com/your-logo.png",
        "size": "sm"
      }
    }
  }
}
```

When using `source: "custom"`, the `src` field is required and must be a valid, publicly accessible URL to an image file.

#### Card numbers

Add automatic page/slide numbers:

```json
{
  "cardOptions": {
    "headerFooter": {
      "bottomRight": {
        "type": "cardNumber"
      }
    }
  }
}
```

Card numbers have no additional configuration. Just specify the position and type.

### Hiding from first and last cards

You often want to hide headers/footers from title cards or closing cards. Add these properties **at the `headerFooter` level** (they apply to all positions):

```json
{
  "cardOptions": {
    "headerFooter": {
      "topRight": {
        "type": "image",
        "source": "themeLogo"
      },
      "bottomRight": {
        "type": "cardNumber"
      },
      "hideFromFirstCard": true,
      "hideFromLastCard": true
    }
  }
}
```

| Property            | Default | Description                                    |
| ------------------- | ------- | ---------------------------------------------- |
| `hideFromFirstCard` | `false` | Set `true` to hide from title/intro card       |
| `hideFromLastCard`  | `false` | Set `true` to hide from closing/thank you card |

### Complete examples

#### Professional presentation (logo and page numbers)

```json
{
  "inputText": "Create a quarterly business review for Q4 2024",
  "textMode": "generate",
  "format": "presentation",
  "numCards": 12,
  "cardOptions": {
    "dimensions": "16x9",
    "headerFooter": {
      "topRight": {
        "type": "image",
        "source": "custom",
        "src": "https://example.com/company-logo.png",
        "size": "sm"
      },
      "bottomRight": {
        "type": "cardNumber"
      },
      "bottomLeft": {
        "type": "text",
        "value": "Confidential - Internal Use Only"
      },
      "hideFromFirstCard": true,
      "hideFromLastCard": true
    }
  }
}
```

#### Social media carousel (minimal branding)

```json
{
  "inputText": "5 tips for better productivity",
  "textMode": "generate",
  "format": "social",
  "numCards": 6,
  "cardOptions": {
    "dimensions": "1x1",
    "headerFooter": {
      "bottomCenter": {
        "type": "text",
        "value": "@yourhandle"
      }
    }
  }
}
```

#### Document with theme logo

```json
{
  "inputText": "Technical specification for Project X",
  "textMode": "generate",
  "format": "document",
  "numCards": 8,
  "cardOptions": {
    "dimensions": "letter",
    "headerFooter": {
      "topLeft": {
        "type": "image",
        "source": "themeLogo",
        "size": "md"
      },
      "topRight": {
        "type": "text",
        "value": "Technical Specification"
      },
      "bottomRight": {
        "type": "cardNumber"
      }
    }
  }
}
```

### Common mistakes

#### Missing `value` for text elements

```json
// ❌ Wrong - missing value
{ "type": "text" }

// ✅ Correct
{ "type": "text", "value": "My Text" }
```

#### Missing `src` for custom images

```json
// ❌ Wrong - missing src
{ "type": "image", "source": "custom" }

// ✅ Correct  
{ "type": "image", "source": "custom", "src": "https://..." }
```

#### Boolean values as strings

```json
// ❌ Wrong - string instead of boolean
{ "hideFromFirstCard": "true" }

// ✅ Correct
{ "hideFromFirstCard": true }
```

### Limitations

* **Not available for `webpage` format** — web pages don't have fixed headers/footers
* **Six positions maximum** — you can only use the six defined positions
* **One element per position** — each position can only hold one type of content

### Related

* [Generate from text](/guides/generate-api-parameters-explained.md) for the full `cardOptions` and `sharingOptions` context
* [Image model accepted values](/reference/image-model-accepted-values.md) if you are pairing branding with AI-generated images
* [API Overview](/get-started/understanding-the-api-options.md) for the broader generation workflow


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://developers.gamma.app/guides/header-and-footer-formatting.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
