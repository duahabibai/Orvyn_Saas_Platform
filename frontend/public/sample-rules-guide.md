# Predefined Mode JSON Import Guide

This guide explains how to format your JSON files for importing predefined bot rules into ORVYN.

## Supported JSON Formats

ORVYN supports multiple JSON formats to make importing your rules as easy as possible.

### Format 1: Simple Key-Value Object (Recommended)

This is the simplest and most common format:

```json
{
  "hello": "Hi there! Welcome to our service. How can I help you today?",
  "price": "Our products start at $10. Contact us for a custom quote!",
  "hours": "We're open Monday to Friday, 9 AM to 6 PM EST.",
  "support": "Our support team is here to help. Please describe your issue.",
  "shipping": "We offer free shipping on orders over $50. Delivery takes 3-5 business days."
}
```

### Format 2: Array of Objects

Use this format if you have rules in an array structure:

```json
[
  {
    "keyword": "hello",
    "response": "Hi there! Welcome to our service."
  },
  {
    "keyword": "price",
    "response": "Our products start at $10."
  },
  {
    "trigger": "hours",
    "message": "We're open Monday to Friday, 9 AM to 6 PM."
  }
]
```

**Note:** The system recognizes these field names:
- Keywords: `keyword`, `trigger`, or `key`
- Responses: `response`, `message`, or `reply`

### Format 3: Nested Object with Rules Property

If your JSON has a wrapper object:

```json
{
  "rules": {
    "hello": "Hello! How can we help you?",
    "help": "Type 'price' for pricing or 'hours' for business hours."
  }
}
```

## Using Placeholders

Make your responses dynamic with these placeholders:

| Placeholder | Replaced With |
|-------------|---------------|
| `{name}` | Customer's name (if available) |
| `{phone}` | Customer's phone number |
| `{last_message}` | The customer's last message |

### Example with Placeholders:

```json
{
  "hello": "Hi {name}! Welcome to ORVYN. How can we assist you today?",
  "contact": "You can reach us at {phone} during business hours.",
  "thanks": "You're welcome, {name}! Is there anything else I can help with?"
}
```

## Import Limits

- **Maximum rules per import:** 50 keyword-response pairs
- **File size limit:** 1MB
- **File type:** `.json` only

If your file has more than 50 rules, only the first 50 will be imported.

## How to Import

1. Go to **Automation Settings** in your ORVYN dashboard
2. Select **Predefined** mode
3. Click **Import JSON** button
4. Select your `.json` file
5. Review the imported rules
6. Click **Save Settings** to apply

## Sample File

You can download a sample rules file directly from the settings page by clicking the **Download Sample** button. This gives you a template to customize.

## Tips for Best Results

1. **Use lowercase keywords** - The system matches case-insensitively, but lowercase is cleaner
2. **Be specific** - Avoid overly generic keywords like "the" or "a"
3. **Test your rules** - Use the Sandbox to verify rules work as expected
4. **Backup your rules** - Export your current rules before importing new ones
5. **Use placeholders** - Personalize responses with `{name}` and `{phone}`

## Troubleshooting

### "No valid rules found in the file"
- Ensure your JSON is properly formatted
- Check that you have keyword-response pairs
- Verify the JSON syntax is valid (use a JSON validator)

### "File size must be less than 1MB"
- Reduce the number of rules
- Shorten response messages
- Split into multiple smaller files

### "Maximum limit of 50 rules reached"
- You already have 50 rules - delete some before adding more
- Or import a file with 50 or fewer rules to replace existing ones

### Rules not matching
- Ensure keywords are spelled correctly
- Remember: matching is substring-based (e.g., "price" matches "what is the price?")
- Check that Predefined mode is active

## Need Help?

If you need assistance with your JSON file or rules configuration, visit the **Help Center** in your dashboard or contact support.
