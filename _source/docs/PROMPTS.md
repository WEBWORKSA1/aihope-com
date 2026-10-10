# AiHope.com: phase-wise build prompts

These are the prompts used to build AiHope.com, in order. Each phase is self-contained, so you can rerun any of them with an AI coding assistant to rebuild, extend or clone the site for another domain. Replace anything in `[brackets]`.

**Fixed requirements that apply to every phase**

- Static site only (HTML, CSS, vanilla JS). Must run on the GitHub Pages free plan. No server, no database, no build step required to serve.
- Every page carries, at the very top, a bar reading “Contact, if you are interested in this website / domain name / Sponsorship / Advertisement / Partnership” linking to https://web.works/contact.
- Every page carries the AdSense code for publisher `ca-pub-6620975821265271` in `<head>`, plus `<meta name="google-adsense-account">`.
- All forms deliver to one site inbox through FormSubmit's AJAX endpoint. The inbox address must never appear on any page, in the HTML source, in the README or in any published file in readable form. It is rebuilt in JavaScript from an encoded array only at submit time, and can be replaced by FormSubmit's random-string alias.
- Use relative links everywhere so the site works both at `https://webworksa1.github.io/aihope-com/` and at the custom domain.
- Avoid any trademark conflict with the name “AI Hope”: use it descriptively, claim no rights in the words, and publish a trademark and copyright disclosure.

---

## Phase 1: Concept and research

> You are a digital product strategist. The domain is AiHope.com (“AI Hope”). Propose four website concepts that fit the name, and score each on: search demand, AdSense RPM potential, AdSense approval risk, lead-generation value, donation and community fit, competition and build cost. Recommend one with numbers and reasoning. Then visit at least 35 world-class websites in the chosen niche (automation-risk checkers, AI tool directories, AI learning platforms, career platforms, AI-for-good nonprofits, donation platforms, contest platforms, AI newsletters). For each, record the features, forms, content types, monetization and lead-capture mechanics, and design patterns worth copying. Synthesize the must-have features ranked by impact on SEO, AdSense approval and RPM, lead conversion, and donations. Verify every statistic you plan to publish against the primary source.

## Phase 2: Information architecture and data model

> Design the sitemap and data model for “AI Hope: future-proof your work in the age of AI”. Pages: home, AI job exposure checker, jobs A–Z hub, one page per occupation, methodology, free AI career plan (lead funnel plus team inquiry form), learning paths, video library, AI tools directory, prompt library, guides hub plus six long-form guides, hope stories, contest plus official rules, support (donations), careers and volunteering, advertise and partner, about, editorial policy, contact, privacy, terms, disclaimer and trademark notice, 404. Define JSON data files for jobs (five tasks each with share of time, AI exposure 0–100, and automate or assist), tools, videos (only verified embeddable YouTube IDs), free courses and prompts. Define the exposure score as the time-weighted average of task ratings and the automation share as the part coming from “automate” tasks.

## Phase 3: Design system

> Create one responsive CSS design system with a warm, hopeful identity that avoids the generic purple AI look: a sunrise palette (deep ink navy, orange-to-amber gradient, teal accent), Fraunces for display and Inter for text, light and dark mode (system preference plus a toggle), 16px+ mobile gutters, no horizontal scroll. Components: partner bar, sticky header with collapsible mobile menu, buttons, cards, pills and exposure meters, score dial, job cards, filter bar with chips, tool, prompt and video cards, tables, FAQ accordions, multi-step form, donation widget, contest countdown, lead band, ad slots that collapse when empty, cookie notice, sticky mobile CTA, modal and footer. Meet WCAG AA contrast and visible focus states.

## Phase 4: Static site generator

> Write a dependency-free Python generator (`_source/build.py`). Each top-level page is its own source: editable content between `<!--BODY-->` and `<!--/BODY-->`, with page settings in a `<!--PAGE {json}-->` comment. The generator re-wraps every page with the shared head (title, description, canonical, Open Graph, AdSense code and meta, fonts, JSON-LD for Organization, WebSite with SearchAction, BreadcrumbList, Article and FAQPage built automatically from `<details class="faq">`), partner bar, header, footer with newsletter form and disclosures. Blocks written as `<!--@name args--><!--@/name-->` are regenerated from JSON (job grid, popular jobs, most and least exposed, tools, videos, courses by path, prompts, stats, lead band, contest facts). Generate one occupation page per job, `assets/js/data.js`, `sitemap.xml`, `robots.txt`, `ads.txt`, `site.webmanifest`, and a `CNAME` file when a custom domain is set. The build must be idempotent.

## Phase 5: Interactive features

> In one vanilla JS file: theme toggle, mobile menu, live filters, click-to-load YouTube embeds (privacy-enhanced domain), copy buttons, share buttons, job search autocomplete in the hero, the exposure checker (pick a job, or score your own week with twelve hour sliders), the five-step career-plan funnel (job, goal, experience and hours, AI comfort and worry, contact with consent and optional partner opt-in) that shows a personalized plan on screen and emails the lead, the donation widget (monthly default, presets, custom amount, live button label, impact line; opens payment links from config or falls back to a pledge form), contest countdown, AdSense units only when slot IDs are configured, optional GA4, cookie notice, sticky mobile CTA and an exit-intent newsletter offer shown at most every 14 days. All browser storage calls wrapped in try/catch.

## Phase 6: Content

> Write original, sourced, people-first content: 38 occupation profiles (summary, tasks, skills, adjacent careers, tools, outlook), six guides of 1,000+ words each (will AI take my job; AI-proof careers; AI skills to learn; how to use AI at work; AI in the job search; a 90-day career change plan), eight hope stories with links to the organizations, a methodology page with sources, and complete trust pages: about, editorial policy (including disclosure of AI assistance), privacy (with Google's required advertising-cookie disclosures and opt-out links), terms, disclaimer with trademark and copyright notice, and contest rules (skill-based, 18+, no purchase necessary). Paraphrase all third-party material; never invent statistics, testimonials, traffic figures or people.

## Phase 7: Monetization and lead generation

> Wire every revenue stream: AdSense auto ads plus reserved in-article, sidebar and in-feed slots; a lead funnel whose opt-in partner field lets leads be referred to course providers, bootcamps and coaches; a B2B team-readiness form; an advertise page with packages (featured tool listing, newsletter, job category sponsor, learning partner per lead, contest sponsor, scholarship partner) and an inquiry form; the Hope Fund donation page with allocation (tools and hosting, scholarships, contest prizes, hiring, promotion); a careers page for hiring writers, mentors, reviewers, developers and video creators; and the AI Hope Challenge with prizes. Label sponsored content, keep ads away from buttons and forms, and state clearly that donations are not tax-deductible.

## Phase 8: QA

> Write `_source/tests/qa.py` and make it pass: no inbox address anywhere in published files, partner bar and AdSense code on every page, one H1 per page, meta descriptions present, valid JSON-LD, no duplicate IDs, every internal link and anchor resolves, ads.txt correct. Then load key pages in a headless browser at 390px and 1366px, step through the funnel, checker and donation widget, and fix any layout or script errors.

## Phase 9: Publish

> Commit the site to the `main` branch of `WEBWORKSA1/Aihope-com` and publish it with GitHub Pages (free plan) from a `gh-pages` branch or from `main` / root. Verify the live URL. Then: activate FormSubmit by submitting one form and clicking the activation link; point AiHope.com DNS at GitHub Pages and set the custom domain in `_source/site.json`; apply to AdSense with the custom domain and enable Google's consent message for the EEA, UK and Switzerland; submit `sitemap.xml` in Search Console.

## Phase 10: Growth roadmap

> Expand to 150+ occupation pages, add country-specific salary and outlook data, launch the weekly newsletter and YouTube channel, publish quarterly Hope Fund reports, recruit named expert reviewers, add reader polls and comments on job pages for fresh content, and sign the first learning partners on a per-lead basis.
