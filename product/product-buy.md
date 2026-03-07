# product-buy — Execute a Purchase

Navigate the user to the purchase page for a specific product so they can complete checkout.


## Step 1: Confirm the Purchase Target

Establish the exact product and retailer. The user may provide:
- A direct URL — use it as-is
- A product name + retailer — search for the exact product page
- Just a product name — run `/product find` first to identify the retailer

**Required before proceeding:**
- Exact product (single SKU, no ambiguity)
- Specific retailer
- Purchase URL


## Step 2: Verify the URL

Before surfing, confirm the URL points to the right product:
- Fetch the page and check the product name/price match expectations
- If the URL is a search results page rather than a product page, find the direct product link
- If the product is out of stock at this retailer, inform the user and suggest alternatives


## Step 3: Surf to Purchase Page

Open the purchase page for the user:
```bash
ctrl surf "<purchase_url>"
```

The user completes the checkout manually from here.


## Step 4: Log the Purchase (Optional)

If the user confirms they completed the purchase, offer to log it:
- Date, product name, retailer, price, URL
- Append to a purchase log if one exists

*Automatic purchasing via the agent is a future upgrade. For now, the agent's job ends at surfing the correct page.*
