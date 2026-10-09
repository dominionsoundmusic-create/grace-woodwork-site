# Independent fact-check, Oct 9 2026

Three sub-agents that did not write the pages checked every new or rewritten page (21 pages: the
homepage, 4 hubs, 10 service pages, 6 guides). Each read the built HTML, compared every claim about the
business with INTAKE.md (and the pre-rebuild site at commit 6531506), checked third-party figures against
the cited sources, and scanned for banned phrases, dashes, British spellings and unsafe DIY advice.
They edited nothing; every fix below was applied afterwards and the site rebuilt.

**Limit of the check.** Direct page loads (WebFetch) failed on DNS for every domain from this
environment, so the checkers verified figures with web searches restricted to each source's own domain
and read the search excerpts. "Verified" below means the figure appeared in that source's excerpt.
Anything that could not be confirmed that way was removed or reworded, not left in.

## Results

| Group | Pages | Checker's result |
|---|---:|---|
| Cabinets and signs | 7 | About 45 third-party figures: 40 verified, 1 wrong, 1 overstated business claim, 2 not verifiable, 2 unsourced asides |
| Furniture repair section | 8 | Most figures verified; 9 figures wrong or out of date (mostly on the cost guide), several not confirmable, 4 invented frequency claims |
| Homepage, custom furniture, deck, porch | 6 | Most figures verified; 1 logic error, 1 likely misapplied interval, 1 unconfirmed attribution, 2 unconfirmed source links, loose arithmetic in one FAQ |

No page claimed a price, warranty, guarantee, license, insurance, year founded, job count, award or team
name for Grace Woodwork. Reviews appear only as "100% recommend on Facebook from 13 reviews", linked to the
Facebook page. No banned phrases, no visible em or en dashes, no British spellings on new pages. No page
gives power-tool, chemical-stripper or structural deck or porch instructions; deck and porch pages limit
homeowners to looking, pressing and probing with a screwdriver, and say when to stop and call.

## Corrections made

Cabinets
- Refacing hero: "It costs less than a new kitchen" became "It usually costs less" (published refacing and
  replacement ranges overlap).
- Refacing guide: laminate "cannot be refinished later" was wrong; it now says it can only be painted, not
  stained. "Clean, smooth surfaces" wording not found at HomeGuide; reworded to "structurally sound".
- Painting cost guide: "HomeGuide says labor is most of the bill" not confirmed; replaced with Angi's
  "70 to 80 percent". An unsourced explanation of why averages differ was cut back.
- Cabinet painting: "peels within a year" (unsourced timeframe) softened; "bring a door to the shop"
  removed because the address is not published.

Furniture repair
- Refinishing cost guide: HomeAdvisor figures updated to the current page ($637 average, $150 to $1,600);
  Thumbtack figures corrected to about $500 per piece ($358 to $582); a Thumbtack repair range that came
  from couch-repair pages removed; "dining tables and dressers costliest" corrected to "dressers and full
  dining sets"; an antique 20 to 50 percent surcharge not found at HomeAdvisor replaced with what it does
  say; Fixr hourly rate (actually HomeAdvisor's) removed; a Bob Vila chair figure from an uncited article
  removed; an unused Angi source removed.
- Chair caning guide: Chicago Magazine 2008 figures corrected to about $3.50 per hole and "$150 and up"
  for a pressed seat.
- Antique page: a specific Antiques Roadshow appraisal could not be found as described; replaced with what
  the Woodshop News column says, and the producer's quote stated accurately ("usually enhances the value").
- Veneer guide: The Henry Ford, Woodcraft and Conservation Center descriptions trimmed to what the sources
  say; a University of Delaware newsletter that could not be confirmed was removed with its source.
- Invented frequency claims removed ("problems we fix every week", "the jobs we see most", "the pieces we
  see most", "most chairs on the curb have one failed joint").

Homepage, custom furniture, deck, porch
- Dining tables: "air-conditioned winters" corrected to "drier, heated winters"; the woods offered cut to
  what the photos show; the leaves answer softened.
- Deck repair: a 3 to 8 year stain interval that appears to be for siding, not decks, removed; a once-a-year
  termite inspection not found at Texas A&M AgriLife replaced with what AgriLife does say; the safe-checks
  intro now mentions the screwdriver it describes.
- Porch repair: an unconfirmed Fine Homebuilding link and an unverified Craftsman Blog link removed; a
  cost comparison softened.
- Dining table guide: the 10-seat arithmetic corrected (96 in with end seats, 120 in without).
- Homepage FAQ: "nothing is quoted sight unseen" reworded so it does not contradict quoting from photos.
- Custom furniture hub: "Pine is the everyday choice around here" (unsourced) softened.

## Left for Maurice to confirm

These are not in INTAKE.md but were already on the live site, so they were kept (see docs/decisions.md 25
and 26): a price before work starts, pickup and delivery, photos sent as the work goes, long pieces built
to come apart, cabinets measured and installed, and the services named as not offered (upholstery,
leather, recliner mechanisms, in-home furniture repair).

## Links the checkers could not confirm resolve

The WVU Extension PDF (refinishing and antique pages), the Fine Woodworking Danish cord article and the
AIC furniture care sheet were cited by their URLs as found in search, but the checkers could not load
them. Worth a click before launch.
