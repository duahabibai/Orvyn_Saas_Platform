export default function DocsPage() {
  return (
    <div>
      {/* ORVYN Help Center */}

      This documentation provides technical guidance for setting up, configuring, and maintaining your ORVYN WhatsApp automation platform.

      ## Overview
      ORVYN allows you to connect your website with a WhatsApp business account to automate sales, inquiries, and customer support.

      ## Configuration Guide

      ### 1. Account Setup
      To begin, log into your dashboard and navigate to the Integrations section.
      - Provide your WhatsApp Cloud API phone number ID.
      - Generate and provide your Meta Access Token.
      - Enter your website URL.

      ### 2. Website Sync
      The platform supports two business types:
      - **Product Based**: Recommended for WooCommerce stores. Syncs products and categories.
      - **Service Based**: Recommended for WordPress or custom sites. Extracts service details and contact information.

      Changes to these settings trigger a data refresh.

      ### 3. Bot Modes
      - **Default Mode**: Uses built-in sales logic integrated with your website data.
      - **Predefined Mode**: Uses keyword-based triggers to respond to specific customer messages.
      - **AI Powered Mode**: Uses large language models (such as GPT-4 or Gemini) to answer based on your provided website content.

      ## Troubleshooting

      ### Connectivity Issues
      If the bot is not replying, check the following:
      - Verify that your Meta Access Token has not expired.
      - Confirm your WhatsApp number is correctly linked in the Integrations dashboard.
      - Ensure the webhook URL provided in the Meta Developers portal matches the URL on your Integrations page.

      ### Data Synchronization Errors
      If the bot provides empty or outdated responses:
      - Update your website URL in the dashboard.
      - Ensure the website is publicly accessible.
      - Check if your product/service pages are using standard HTML structures that the ORVYN crawler can recognize.

      ## API Reference
      The platform exposes internal REST endpoints. Integration with custom systems should use the provided API endpoints found in the Settings tab.
    </div>
  );
}
