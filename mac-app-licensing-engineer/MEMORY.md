# MEMORY

Nora's reference case is Jason Sorge's July 15, 2026 article “Licensing a Mac App with RevenueCat.” The durable pattern is RevenueCat entitlement authority, a CloudKit current-user record ID used as a custom App User ID, a Stripe-backed RevenueCat Web Purchase Link opened in the default browser, deep-link return, and a fresh RevenueCat customer-info fetch before unlocking.

The article's product logic matters as much as its SDK calls: direct distribution can be necessary for an unsandboxed power-user app; Apple Pay can justify a browser round trip; automatic recognition on Macs using the same iCloud account can be simpler than email accounts or license keys; and a small developer may rationally pay higher fees for a merchant of record that handles tax collection/remittance.

Current RevenueCat documentation adds a critical caveat: Stripe Managed Payments applies per eligible transaction. If an offering contains an ineligible product, checkout may fall back to ordinary Stripe Billing and return merchant responsibility to the seller. Product tax codes, eligibility, and actual transaction mode must be verified.

CloudKit identity avoids collecting names/emails directly but remains a persistent pseudonymous identifier. iCloud absence, restriction, account changes, URL/log exposure, support lookup, and a non-iCloud fallback must be treated as product and privacy concerns.

A checkout redirect or deep link never proves purchase. It triggers a current entitlement fetch. Lost callbacks, delayed propagation, stale cache, offline use, provider outages, duplicate actions, refunds/revocations, and sandbox/production mixing require explicit tests and recovery paths.
