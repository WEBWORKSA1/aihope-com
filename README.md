# AiHope.com: future-proof your work in the age of AI

AiHope.com helps people see how AI affects their job and what to do about it. It includes:

- an interactive AI Job Exposure Checker (pick a job, or score your own week)
- 38 task-by-task occupation reports
- a 5-step free AI Career Plan funnel
- learning paths and a 23-video library
- 36 AI tools and 30 prompts for work
- six in-depth guides and hope stories

It is monetized with Google AdSense, lead generation (consumer and B2B), sponsorships, the Hope Fund (donations), the AI Hope Challenge contest and a talent and volunteer hub.

**Live:** https://webworksa1.github.io/Aihope-com/ (GitHub Pages, free plan)

## Project layout

The repository root is the published site. Every page carries the partner bar linking to https://web.works/contact and the AdSense code for `ca-pub-6620975821265271`.

```
*.html                 pages; edit the content between <!--BODY--> and <!--/BODY-->
jobs/*.html            occupation reports (generated: edit _source/data/jobs.json)
assets/css/style.css   design system (light + dark)
assets/js/config.js    the only script you normally edit: form alias, AdSense slots, donation links, GA4, YouTube
assets/js/app.js       menu, theme, forms, filters, video, checker, career plan, donations, ads, consent
assets/js/data.js      generated job and course data
_source/build.py       generator: re-wraps pages with header, footer, SEO and JSON-LD; regenerates data blocks
_source/site.json      site URL, custom domain, AdSense id, partner link, contest dates
_source/data/*.json    jobs, tools, videos, courses, prompts
_source/tests/qa.py    checks links, anchors, ids, JSON-LD, partner bar, AdSense, inbox exposure
_source/docs/          RESEARCH.md (concept choice, 41-site teardown), PROMPTS.md (phase-wise build prompts)
```

## Build and check

```bash
python3 _source/build.py      # no dependencies
python3 _source/tests/qa.py   # must print "No problems found."
```

To add a job, add an entry to `_source/data/jobs.json`. Task shares must add up to 100. Then rebuild. Tools, videos, courses and prompts work the same way.

## Go-live checklist

1. **Forms.** All forms go through FormSubmit to the site inbox, which never appears on the site. Submit any form once on the live site, then click **Activate** in the email FormSubmit sends. Optionally paste the random-string alias FormSubmit gives you into `formAlias` in `assets/js/config.js`.
2. **Custom domain AiHope.com.**
   - Point DNS A records to `185.199.108.153`, `185.199.109.153`, `185.199.110.153` and `185.199.111.153`.
   - Point `www` with a CNAME to `webworksa1.github.io`.
   - Set `"custom_domain": "aihope.com"` in `_source/site.json` and rebuild. This writes `CNAME` and updates canonicals and the sitemap.
   - Push, then tick **Enforce HTTPS** under Settings > Pages.
3. **AdSense.**
   - Add aihope.com in AdSense. Google requires a domain you own; a github.io address does not qualify.
   - Enable Auto ads.
   - Turn on Google's consent message for the EEA, UK and Switzerland.
   - `ads.txt` is already generated. To use fixed units, paste their slot ids into `adsense.slots` in `config.js`.
4. **Donations.** Paste Stripe Payment Links, PayPal or Buy Me a Coffee URLs into `donate.oneTime` and `donate.monthly`. Until then, the support page collects pledges.
5. **Search Console.** Verify the domain and submit `sitemap.xml`.
6. **Contest.** Season 1 has a $500 prize pool and closes December 15, 2026. Edit the dates in `_source/site.json`, `contests.html` and `contest-rules.html` if needed.

## Legal

“AI Hope” is used descriptively. No rights are claimed in the words “AI” or “hope”, and the site is not affiliated with any organization, product or app with a similar name. Third-party trademarks belong to their owners. See `disclaimer.html`.

Inquiries about this website, the domain, sponsorship, advertising or partnership: https://web.works/contact
